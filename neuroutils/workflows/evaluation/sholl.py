"""Sholl analysis workflows for SWC directories."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from neuroutils.io.swc import read_swc
from neuroutils.swc.analysis.sholl import (
    bhattacharyya_distance,
    earth_movers_distance,
    sholl_intersections,
)


def sholl_profile_for_swc(
    swc_file: str | Path,
    *,
    step: float = 10.0,
) -> dict[str, list[float] | list[int]]:
    """Compute a Sholl profile for one SWC file."""
    result = sholl_intersections(read_swc(swc_file), step=step)
    return {"radii": result.radii, "intersections": result.intersections}


def sholl_profiles_for_directory(
    swc_dir: str | Path,
    *,
    suffix: str = ".swc",
    step: float = 10.0,
    outfile: str | Path | None = None,
) -> list[dict[str, float | int | str]]:
    """Compute Sholl profiles for all SWC files and return long-format rows."""
    rows: list[dict[str, float | int | str]] = []
    for swc_path in sorted(Path(swc_dir).glob(f"*{suffix}")):
        profile = sholl_profile_for_swc(swc_path, step=step)
        radii = profile["radii"]
        intersections = profile["intersections"]
        for radius, count in zip(radii, intersections):
            rows.append(
                {
                    "id": swc_path.stem,
                    "radius": float(radius),
                    "intersections": int(count),
                }
            )

    if outfile is not None:
        out_path = Path(outfile)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=["id", "radius", "intersections"])
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
    return rows


def compare_sholl_directories(
    gt_dir: str | Path,
    pred_dir: str | Path,
    *,
    suffix: str = ".swc",
    step: float = 10.0,
    csv_outfile: str | Path | None = None,
    json_outfile: str | Path | None = None,
) -> list[dict[str, float | str]]:
    """Compare Sholl profiles by L1/L2 differences for shared SWC stems."""
    gt_files = {p.stem: p for p in sorted(Path(gt_dir).glob(f"*{suffix}"))}
    pred_files = {p.stem: p for p in sorted(Path(pred_dir).glob(f"*{suffix}"))}
    rows: list[dict[str, float | str]] = []
    for stem in sorted(set(gt_files) & set(pred_files)):
        p_gt = sholl_profile_for_swc(gt_files[stem], step=step)
        p_pred = sholl_profile_for_swc(pred_files[stem], step=step)
        gt_map = {float(r): int(v) for r, v in zip(p_gt["radii"], p_gt["intersections"])}
        pred_map = {float(r): int(v) for r, v in zip(p_pred["radii"], p_pred["intersections"])}
        all_radii = sorted(set(gt_map) | set(pred_map))
        gt_counts = [int(gt_map.get(r, 0)) for r in all_radii]
        pred_counts = [int(pred_map.get(r, 0)) for r in all_radii]
        diffs = [float(a - b) for a, b in zip(gt_counts, pred_counts)]
        l1 = float(sum(abs(d) for d in diffs))
        l2 = float(sum(d * d for d in diffs) ** 0.5)
        rows.append(
            {
                "id": stem,
                "l1": l1,
                "l2": l2,
                "bhattacharyya": bhattacharyya_distance(gt_counts, pred_counts),
                "emd": earth_movers_distance(gt_counts, pred_counts),
                "num_radii": float(len(all_radii)),
            }
        )

    if csv_outfile is not None:
        out_path = Path(csv_outfile)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(
                fp,
                fieldnames=["id", "l1", "l2", "bhattacharyya", "emd", "num_radii"],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    if json_outfile is not None:
        out_path = Path(json_outfile)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    return rows
