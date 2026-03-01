"""Evaluation workflows."""

from __future__ import annotations

import csv
from pathlib import Path

from neuroutils.io.swc import read_swc
from neuroutils.topology import composite_topology_score


def evaluate_pair(gt_swc: str | Path, pred_swc: str | Path) -> dict[str, float]:
    """Evaluate one prediction SWC against ground truth SWC."""
    gt_nodes = read_swc(gt_swc)
    pred_nodes = read_swc(pred_swc)
    return composite_topology_score(gt_nodes, pred_nodes)


def evaluate_directory_pairs(
    gt_dir: str | Path,
    pred_dir: str | Path,
    *,
    suffix: str = ".swc",
    outfile: str | Path | None = None,
    strict: bool = False,
) -> list[dict[str, float | str]]:
    """Evaluate matched SWC pairs from two directories by filename stem.

    - Matching rule: `<stem><suffix>` in `gt_dir` and `pred_dir`.
    - When `strict=False`, unmatched files are skipped.
    - When `strict=True`, raises if either side has unmatched stems.
    """
    gt_files = {p.stem: p for p in sorted(Path(gt_dir).glob(f"*{suffix}"))}
    pred_files = {p.stem: p for p in sorted(Path(pred_dir).glob(f"*{suffix}"))}

    gt_only = sorted(set(gt_files) - set(pred_files))
    pred_only = sorted(set(pred_files) - set(gt_files))
    if strict and (gt_only or pred_only):
        raise ValueError(
            f"Unmatched SWC files found. gt_only={len(gt_only)} pred_only={len(pred_only)}"
        )

    shared_stems = sorted(set(gt_files) & set(pred_files))
    rows: list[dict[str, float | str]] = []
    for stem in shared_stems:
        scores = evaluate_pair(gt_files[stem], pred_files[stem])
        rows.append({"id": stem, **scores})

    if outfile is not None:
        out_path = Path(outfile)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fields = ["id", "opt_g", "opt_j", "opt_p", "ccq", "total"]
        with out_path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    return rows
