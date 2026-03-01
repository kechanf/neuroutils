"""Feature extraction workflows."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from neuroutils.swc.analysis.lmeasure.external import calc_global_features_from_folder


def evaluate_global_features_for_directory(
    swc_dir: str | Path,
    *,
    outfile: str | Path | None = None,
    robust: bool = True,
    nworkers: int = 4,
    timeout: int = 60,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    use_xvfb: bool = False,
) -> list[dict[str, float | str]]:
    """Run Vaa3D global-feature extraction for all SWCs in one directory."""
    return calc_global_features_from_folder(
        swc_dir,
        outfile=outfile,
        robust=robust,
        nworkers=nworkers,
        timeout=timeout,
        vaa3d_bin=vaa3d_bin,
        vaa3d_version=vaa3d_version,
        use_xvfb=use_xvfb,
    )


def _read_feature_table(path: str | Path) -> tuple[list[str], dict[str, dict[str, float]]]:
    table_path = Path(path)
    with table_path.open("r", newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        if reader.fieldnames is None:
            raise ValueError(f"Empty CSV: {table_path}")
        fieldnames = list(reader.fieldnames)
        if not fieldnames:
            raise ValueError(f"Invalid CSV header: {table_path}")

        id_key = "id" if "id" in fieldnames else fieldnames[0]
        features = [k for k in fieldnames if k != id_key]
        rows: dict[str, dict[str, float]] = {}
        for row in reader:
            row_id = str(row.get(id_key, "")).strip()
            if not row_id:
                continue
            feat_values: dict[str, float] = {}
            for key in features:
                raw = str(row.get(key, "")).strip()
                if not raw:
                    continue
                try:
                    feat_values[key] = float(raw)
                except ValueError:
                    continue
            rows[row_id] = feat_values
    return features, rows


def compare_global_feature_csvs(
    csv_a: str | Path,
    csv_b: str | Path,
    *,
    features: list[str] | None = None,
    csv_outfile: str | Path | None = None,
    json_outfile: str | Path | None = None,
) -> dict[str, object]:
    """Compare two global-feature CSV files and return feature-level deltas."""
    features_a, rows_a = _read_feature_table(csv_a)
    features_b, rows_b = _read_feature_table(csv_b)

    selected = list(features) if features is not None else sorted(set(features_a) & set(features_b))
    shared_ids = sorted(set(rows_a) & set(rows_b))
    per_feature: list[dict[str, float | str | int]] = []

    for feat in selected:
        vals_a: list[float] = []
        vals_b: list[float] = []
        abs_deltas: list[float] = []
        rel_deltas: list[float] = []
        for rid in shared_ids:
            if feat not in rows_a[rid] or feat not in rows_b[rid]:
                continue
            va = float(rows_a[rid][feat])
            vb = float(rows_b[rid][feat])
            vals_a.append(va)
            vals_b.append(vb)
            abs_delta = vb - va
            abs_deltas.append(abs_delta)
            denom = abs(va) if abs(va) > 1e-12 else 1.0
            rel_deltas.append(abs_delta / denom)

        if not vals_a:
            continue

        n = float(len(vals_a))
        per_feature.append(
            {
                "feature": feat,
                "num_samples": int(n),
                "mean_a": float(sum(vals_a) / n),
                "mean_b": float(sum(vals_b) / n),
                "mean_abs_delta": float(sum(abs_deltas) / n),
                "mean_rel_delta": float(sum(rel_deltas) / n),
            }
        )

    report: dict[str, object] = {
        "summary": {
            "num_features": len(per_feature),
            "num_rows_a": len(rows_a),
            "num_rows_b": len(rows_b),
            "num_shared_ids": len(shared_ids),
        },
        "per_feature": per_feature,
    }

    if csv_outfile is not None:
        out_path = Path(csv_outfile)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(
                fp,
                fieldnames=[
                    "feature",
                    "num_samples",
                    "mean_a",
                    "mean_b",
                    "mean_abs_delta",
                    "mean_rel_delta",
                ],
            )
            writer.writeheader()
            for row in per_feature:
                writer.writerow(row)

    if json_outfile is not None:
        out_path = Path(json_outfile)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return report
