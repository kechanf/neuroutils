"""Metadata consistency validation workflows."""

from __future__ import annotations

import json
from pathlib import Path

from neuroutils.metadata.workflows.catalog import load_metadata_table_records


def build_metadata_consistency_report(
    records: list[dict[str, str]],
    *,
    id_columns: tuple[str, ...] = ("cell_id", "Cell ID"),
    required_keys: tuple[str, ...] = ("cell_id",),
    numeric_keys: tuple[str, ...] = ("xy_resolution", "z_resolution"),
) -> dict[str, object]:
    """Build consistency report for metadata records."""
    missing_required: list[dict[str, object]] = []
    invalid_numeric: list[dict[str, object]] = []
    duplicate_id_rows: list[dict[str, object]] = []
    seen_ids: dict[int, int] = {}

    for idx, record in enumerate(records):
        missing = [k for k in required_keys if k not in record or not str(record[k]).strip()]
        if missing:
            missing_required.append({"row_index": idx, "missing_keys": missing})

        for key in numeric_keys:
            if key not in record or not str(record[key]).strip():
                continue
            try:
                float(str(record[key]).strip())
            except Exception:
                invalid_numeric.append({"row_index": idx, "key": key, "value": str(record[key])})

        rid: int | None = None
        for col in id_columns:
            if col not in record or not str(record[col]).strip():
                continue
            try:
                rid = int(float(str(record[col]).strip()))
                break
            except Exception:
                continue
        if rid is None:
            continue
        if rid in seen_ids:
            duplicate_id_rows.append({"row_index": idx, "id": rid, "first_row_index": seen_ids[rid]})
        else:
            seen_ids[rid] = idx

    summary = {
        "num_records": len(records),
        "num_missing_required": len(missing_required),
        "num_invalid_numeric": len(invalid_numeric),
        "num_duplicate_id_rows": len(duplicate_id_rows),
        "passed": len(missing_required) == 0 and len(invalid_numeric) == 0 and len(duplicate_id_rows) == 0,
    }
    return {
        "summary": summary,
        "missing_required": missing_required,
        "invalid_numeric": invalid_numeric,
        "duplicate_id_rows": duplicate_id_rows,
    }


def validate_metadata_table_consistency(
    table_file: str | Path,
    *,
    id_columns: tuple[str, ...] = ("cell_id", "Cell ID"),
    required_keys: tuple[str, ...] = ("cell_id",),
    numeric_keys: tuple[str, ...] = ("xy_resolution", "z_resolution"),
    json_outfile: str | Path | None = None,
) -> dict[str, object]:
    """Validate metadata table and optionally write report JSON."""
    records = load_metadata_table_records(table_file)
    report = build_metadata_consistency_report(
        records,
        id_columns=id_columns,
        required_keys=required_keys,
        numeric_keys=numeric_keys,
    )
    if json_outfile is not None:
        out = Path(json_outfile)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report
