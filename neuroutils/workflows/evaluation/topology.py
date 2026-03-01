"""Topology evaluation workflows for SWC directories."""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

from neuroutils.workflows.evaluation.compare import evaluate_pair


def _summarize_scores(rows: list[dict[str, float | str]]) -> dict[str, float]:
    keys = ("opt_g", "opt_j", "opt_p", "ccq", "total")
    out: dict[str, float] = {}
    if not rows:
        for k in keys:
            out[f"{k}_mean"] = 0.0
            out[f"{k}_median"] = 0.0
        return out
    for k in keys:
        vals = [float(r[k]) for r in rows]
        out[f"{k}_mean"] = float(statistics.fmean(vals))
        out[f"{k}_median"] = float(statistics.median(vals))
    return out


def evaluate_topology_directory_report(
    gt_dir: str | Path,
    pred_dir: str | Path,
    *,
    suffix: str = ".swc",
    strict: bool = False,
    robust: bool = True,
    csv_outfile: str | Path | None = None,
    json_outfile: str | Path | None = None,
) -> dict[str, object]:
    """Evaluate topology for shared SWC stems and build a report object."""
    gt_files = {p.stem: p for p in sorted(Path(gt_dir).glob(f"*{suffix}"))}
    pred_files = {p.stem: p for p in sorted(Path(pred_dir).glob(f"*{suffix}"))}
    gt_only = sorted(set(gt_files) - set(pred_files))
    pred_only = sorted(set(pred_files) - set(gt_files))
    if strict and (gt_only or pred_only):
        raise ValueError(f"Unmatched files found. gt_only={len(gt_only)} pred_only={len(pred_only)}")

    shared = sorted(set(gt_files) & set(pred_files))
    rows: list[dict[str, float | str]] = []
    failed: list[dict[str, str]] = []
    for stem in shared:
        try:
            scores = evaluate_pair(gt_files[stem], pred_files[stem])
            rows.append({"id": stem, **scores})
        except Exception as exc:
            if not robust:
                raise
            failed.append({"id": stem, "error": str(exc)})

    summary = {
        "num_gt": len(gt_files),
        "num_pred": len(pred_files),
        "num_shared": len(shared),
        "num_evaluated": len(rows),
        "num_failed": len(failed),
        "num_gt_only": len(gt_only),
        "num_pred_only": len(pred_only),
        **_summarize_scores(rows),
    }
    report: dict[str, object] = {
        "summary": summary,
        "rows": rows,
        "failed": failed,
        "gt_only": gt_only,
        "pred_only": pred_only,
    }

    if csv_outfile is not None:
        csv_path = Path(csv_outfile)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=["id", "opt_g", "opt_j", "opt_p", "ccq", "total"])
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    if json_outfile is not None:
        json_path = Path(json_outfile)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return report
