from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from joblib import Parallel, delayed

from neuroutils.workflows.pipelines import synthesize_swc_with_strategies


GRAFT_STRATEGIES = {"full_tree_graft", "branch_segment_graft"}


def _make_output_dirs(base: Path) -> dict[str, Path]:
    dirs = {
        "graft_branch_x5": base / "嫁接枝干x5",
        "graft_tree_x5": base / "嫁接树x5",
        "small_spur_x5": base / "小毛刺x5",
        "cluster_noise_x5": base / "簇状噪声x5",
        "break_x5": base / "断裂x5",
        "all5_each_x1": base / "五策略各x1",
    }
    for p in dirs.values():
        p.mkdir(parents=True, exist_ok=True)
    return dirs


def _strategy_map() -> dict[str, list[dict]]:
    return {
        "graft_branch_x5": [{"name": "branch_segment_graft", "params": {"max_hops": 10}}] * 5,
        "graft_tree_x5": [{"name": "full_tree_graft"}] * 5,
        "small_spur_x5": [
            {"name": "local_spur", "params": {"spur_count": 8, "spur_len_range": (1, 3)}}
        ]
        * 5,
        "cluster_noise_x5": [
            {"name": "small_cluster_attach", "params": {"cluster_size": 10, "cluster_radius": 4.0}}
        ]
        * 5,
        "break_x5": [
            {
                "name": "break_fragment_attach",
                "params": {"break_ratio": 0.12, "offset": (2.0, 8.0), "reconnect_prob": 0.5},
            }
        ]
        * 5,
        "all5_each_x1": [
            {"name": "branch_segment_graft", "params": {"max_hops": 10}},
            {"name": "full_tree_graft"},
            {"name": "local_spur", "params": {"spur_count": 8, "spur_len_range": (1, 3)}},
            {"name": "small_cluster_attach", "params": {"cluster_size": 10, "cluster_radius": 4.0}},
            {
                "name": "break_fragment_attach",
                "params": {"break_ratio": 0.12, "offset": (2.0, 8.0), "reconnect_prob": 0.5},
            },
        ],
    }


def _requires_donor(strategies: list[dict]) -> bool:
    return any(str(step.get("name", "")) in GRAFT_STRATEGIES for step in strategies)


@dataclass(frozen=True, slots=True)
class Task:
    group_key: str
    target_swc: str
    output_swc: str
    seed: int
    strategies: list[dict]
    donor_pool: list[str] | None


def _run_one(task: Task, overwrite: bool) -> tuple[str, str, str]:
    out = Path(task.output_swc)
    if out.exists() and not overwrite:
        return task.group_key, "skipped", task.output_swc

    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        synthesize_swc_with_strategies(
            input_swc=task.target_swc,
            output_swc=task.output_swc,
            strategies=task.strategies,
            donor_swc_paths=task.donor_pool,
            seed=task.seed,
        )
        return task.group_key, "generated", task.output_swc
    except Exception as exc:
        return task.group_key, f"failed:{type(exc).__name__}:{exc}", task.output_swc


def _build_tasks(
    input_dir: Path,
    output_root: Path,
    n_each: int,
    seed_base: int,
    selected_groups: set[str] | None = None,
) -> list[Task]:
    strategies_by_group = _strategy_map()
    out_dirs = _make_output_dirs(output_root)

    swcs = sorted(input_dir.glob("*.swc"))
    if len(swcs) < 20:
        raise RuntimeError("Need at least 20 SWC files in source directory.")

    tasks: list[Task] = []
    for group_index, (group_key, strategies) in enumerate(strategies_by_group.items()):
        if selected_groups is not None and group_key not in selected_groups:
            continue
        out_dir = out_dirs[group_key]
        need_donor = _requires_donor(strategies)
        for i in range(n_each):
            target = swcs[i % len(swcs)]
            donors = [str(p) for p in swcs if p != target] if need_donor else None
            output_swc = out_dir / f"{target.stem}__{group_key}__n{i + 1:03d}.swc"
            seed = seed_base + group_index * 1_000_000 + (i + 1)
            tasks.append(
                Task(
                    group_key=group_key,
                    target_swc=str(target),
                    output_swc=str(output_swc),
                    seed=seed,
                    strategies=strategies,
                    donor_pool=donors,
                )
            )
    return tasks


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synth SWC batches with resume + joblib.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(r"E:\neuroutils\examples\auto8k_resampled_10um"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(r"E:\neuroutils\examples\auto8k_resampled_10um_synth_batches_v2_200"),
    )
    parser.add_argument("--n-each", type=int, default=200, help="Samples per group.")
    parser.add_argument("--seed-base", type=int, default=202603090000)
    parser.add_argument("--n-jobs", type=int, default=-1, help="joblib n_jobs.")
    parser.add_argument(
        "--backend",
        type=str,
        default="loky",
        choices=["loky", "threading"],
        help="joblib backend; use loky for CPU-bound work.",
    )
    parser.add_argument(
        "--fallback-threading",
        action="store_true",
        help="If loky backend fails, retry with threading backend.",
    )
    parser.add_argument(
        "--fallback-sequential",
        action="store_true",
        help="If joblib backend fails, run sequentially in current process.",
    )
    parser.add_argument(
        "--groups",
        type=str,
        default="",
        help="Comma-separated subset: graft_branch_x5,graft_tree_x5,...",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate existing outputs. Default is resume/skip existing.",
    )
    parser.add_argument("--verbose", type=int, default=10, help="joblib verbose level.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    selected = {x.strip() for x in args.groups.split(",") if x.strip()} or None
    tasks = _build_tasks(
        input_dir=args.input_dir,
        output_root=args.output_root,
        n_each=args.n_each,
        seed_base=args.seed_base,
        selected_groups=selected,
    )
    print(
        json.dumps(
            {
                "input_dir": str(args.input_dir),
                "output_root": str(args.output_root),
                "n_tasks": len(tasks),
                "n_jobs": args.n_jobs,
                "backend": args.backend,
                "overwrite": args.overwrite,
                "groups": sorted(selected) if selected else "ALL",
            },
            ensure_ascii=False,
        )
    )

    try:
        results = Parallel(n_jobs=args.n_jobs, backend=args.backend, verbose=args.verbose)(
            delayed(_run_one)(task, args.overwrite) for task in tasks
        )
    except Exception as exc:
        if args.backend == "loky" and args.fallback_threading:
            print(f"loky_failed={type(exc).__name__}: {exc}")
            print("retry_with=threading")
            try:
                results = Parallel(n_jobs=args.n_jobs, backend="threading", verbose=args.verbose)(
                    delayed(_run_one)(task, args.overwrite) for task in tasks
                )
            except Exception as exc2:
                if args.fallback_sequential:
                    print(f"threading_failed={type(exc2).__name__}: {exc2}")
                    print("retry_with=sequential")
                    results = [_run_one(task, args.overwrite) for task in tasks]
                else:
                    raise
        elif args.fallback_sequential:
            print(f"backend_failed={type(exc).__name__}: {exc}")
            print("retry_with=sequential")
            results = [_run_one(task, args.overwrite) for task in tasks]
        else:
            raise

    status_by_group: dict[str, Counter] = defaultdict(Counter)
    failed: list[tuple[str, str, str]] = []
    for group_key, status, output in results:
        status_by_group[group_key][status] += 1
        if status.startswith("failed:"):
            failed.append((group_key, status, output))

    print("=== Summary ===")
    for group_key in sorted(status_by_group):
        counter = status_by_group[group_key]
        total = sum(counter.values())
        generated = counter.get("generated", 0)
        skipped = counter.get("skipped", 0)
        failed_count = total - generated - skipped
        print(
            f"{group_key}: total={total}, generated={generated}, "
            f"skipped={skipped}, failed={failed_count}"
        )

    log_path = args.output_root / "run_log_v2.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        for group_key, status, output in results:
            f.write(
                json.dumps({"group": group_key, "status": status, "output": output}, ensure_ascii=False)
                + "\n"
            )
    print(f"log={log_path}")

    if failed:
        failed_path = args.output_root / "failed_v2.jsonl"
        with failed_path.open("w", encoding="utf-8") as f:
            for group_key, status, output in failed:
                f.write(
                    json.dumps(
                        {"group": group_key, "status": status, "output": output}, ensure_ascii=False
                    )
                    + "\n"
                )
        print(f"failed={len(failed)} saved={failed_path}")


if __name__ == "__main__":
    main()
