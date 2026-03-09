from __future__ import annotations

from pathlib import Path

from neuroutils.workflows.pipelines import synthesize_swc_with_strategies


def _make_output_dirs(base: Path) -> dict[str, Path]:
    dirs = {
        "graft_branch_x3": base / "嫁接枝干x3",
        "graft_tree_x3": base / "嫁接树x3",
        "small_spur_x3": base / "小毛刺x3",
        "cluster_noise_x3": base / "簇状噪声x3",
        "break_x3": base / "断裂x3",
        "all5_each_x3": base / "五策略各x3",
    }
    for p in dirs.values():
        p.mkdir(parents=True, exist_ok=True)
    return dirs


def _strategy_map() -> dict[str, list[dict]]:
    return {
        "graft_branch_x3": [
            {"name": "branch_segment_graft", "params": {"max_hops": 10}},
            {"name": "branch_segment_graft", "params": {"max_hops": 10}},
            {"name": "branch_segment_graft", "params": {"max_hops": 10}},
        ],
        "graft_tree_x3": [
            {"name": "full_tree_graft"},
            {"name": "full_tree_graft"},
            {"name": "full_tree_graft"},
        ],
        "small_spur_x3": [
            {"name": "local_spur", "params": {"spur_count": 8, "spur_len_range": (1, 3)}},
            {"name": "local_spur", "params": {"spur_count": 8, "spur_len_range": (1, 3)}},
            {"name": "local_spur", "params": {"spur_count": 8, "spur_len_range": (1, 3)}},
        ],
        "cluster_noise_x3": [
            {"name": "small_cluster_attach", "params": {"cluster_size": 10, "cluster_radius": 4.0}},
            {"name": "small_cluster_attach", "params": {"cluster_size": 10, "cluster_radius": 4.0}},
            {"name": "small_cluster_attach", "params": {"cluster_size": 10, "cluster_radius": 4.0}},
        ],
        "break_x3": [
            {"name": "break_fragment_attach", "params": {"break_ratio": 0.12, "offset": (2.0, 8.0), "reconnect_prob": 0.5}},
            {"name": "break_fragment_attach", "params": {"break_ratio": 0.12, "offset": (2.0, 8.0), "reconnect_prob": 0.5}},
            {"name": "break_fragment_attach", "params": {"break_ratio": 0.12, "offset": (2.0, 8.0), "reconnect_prob": 0.5}},
        ],
        "all5_each_x3": (
            [{"name": "branch_segment_graft", "params": {"max_hops": 10}}] * 3
            + [{"name": "full_tree_graft"}] * 3
            + [{"name": "local_spur", "params": {"spur_count": 8, "spur_len_range": (1, 3)}}] * 3
            + [{"name": "small_cluster_attach", "params": {"cluster_size": 10, "cluster_radius": 4.0}}] * 3
            + [{"name": "break_fragment_attach", "params": {"break_ratio": 0.12, "offset": (2.0, 8.0), "reconnect_prob": 0.5}}] * 3
        ),
    }


def main() -> None:
    in_dir = Path(r"E:\neuroutils\examples\auto8k_resampled_10um")
    out_root = Path(r"E:\neuroutils\examples\auto8k_resampled_10um_synth_batches")
    out_root.mkdir(parents=True, exist_ok=True)
    out_dirs = _make_output_dirs(out_root)
    strategy_map = _strategy_map()

    swcs = sorted(in_dir.glob("*.swc"))
    if len(swcs) < 10:
        raise RuntimeError("Need at least 10 SWC files in source directory.")

    targets = swcs[:5]
    donor_pool = [str(p) for p in swcs[5:]]

    for key, steps in strategy_map.items():
        out_dir = out_dirs[key]
        for i, target in enumerate(targets, start=1):
            out_file = out_dir / f"{target.stem}__{key}__n{i:02d}.swc"
            logs = synthesize_swc_with_strategies(
                input_swc=target,
                output_swc=out_file,
                strategies=steps,
                donor_swc_paths=donor_pool,
                seed=20260309 + i,
            )
            print(f"[{key}] {target.name} -> {out_file.name} | steps={len(logs)} nodes={logs[-1].total_nodes_after}")


if __name__ == "__main__":
    main()
