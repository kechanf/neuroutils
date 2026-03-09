from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from neuroutils.io.swc import read_swc
from neuroutils.swc import extent_xyz, node_count


def _pick_root() -> Path:
    candidates = [
        Path(r"E:\neuroutils\examples\auto8k_resampled_10um_synth_batches_v2_200"),
        Path(r"E:\neuroutils\examples\auto8k_resampled_10um_synth_batches"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("No synth batch root found.")


def _stat(x: list[float]) -> tuple[float, float]:
    arr = np.asarray(x, dtype=np.float64)
    if arr.size == 0:
        return float("nan"), float("nan")
    return float(arr.mean()), float(arr.std(ddof=0))


def main() -> None:
    root = _pick_root()
    group_dirs = sorted([p for p in root.iterdir() if p.is_dir()])
    rows: list[dict[str, object]] = []

    all_count: list[float] = []
    all_w: list[float] = []
    all_h: list[float] = []
    all_d: list[float] = []

    for g in group_dirs:
        swcs = sorted(g.glob("*.swc"))
        counts: list[float] = []
        widths: list[float] = []
        heights: list[float] = []
        depths: list[float] = []
        for swc in swcs:
            nodes = read_swc(swc)
            c = float(node_count(nodes))
            e = extent_xyz(nodes)
            counts.append(c)
            widths.append(float(e.x))
            heights.append(float(e.y))
            depths.append(float(e.z))

        c_mean, c_std = _stat(counts)
        w_mean, w_std = _stat(widths)
        h_mean, h_std = _stat(heights)
        d_mean, d_std = _stat(depths)
        rows.append(
            {
                "group": g.name,
                "n_files": len(swcs),
                "node_count_mean": c_mean,
                "node_count_std": c_std,
                "width_mean": w_mean,
                "width_std": w_std,
                "height_mean": h_mean,
                "height_std": h_std,
                "depth_mean": d_mean,
                "depth_std": d_std,
            }
        )

        all_count.extend(counts)
        all_w.extend(widths)
        all_h.extend(heights)
        all_d.extend(depths)

    c_mean, c_std = _stat(all_count)
    w_mean, w_std = _stat(all_w)
    h_mean, h_std = _stat(all_h)
    d_mean, d_std = _stat(all_d)
    rows.append(
        {
            "group": "__TOTAL__",
            "n_files": len(all_count),
            "node_count_mean": c_mean,
            "node_count_std": c_std,
            "width_mean": w_mean,
            "width_std": w_std,
            "height_mean": h_mean,
            "height_std": h_std,
            "depth_mean": d_mean,
            "depth_std": d_std,
        }
    )

    out_csv = root / "group_stats_nodecount_extent.csv"
    fieldnames = [
        "group",
        "n_files",
        "node_count_mean",
        "node_count_std",
        "width_mean",
        "width_std",
        "height_mean",
        "height_std",
        "depth_mean",
        "depth_std",
    ]
    with out_csv.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"root={root}")
    print(",".join(fieldnames))
    for r in rows:
        print(",".join(str(r[k]) for k in fieldnames))
    print(f"saved_csv={out_csv}")


if __name__ == "__main__":
    main()
