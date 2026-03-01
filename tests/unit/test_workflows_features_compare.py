from __future__ import annotations

import csv
import json
from pathlib import Path

from neuroutils.workflows import compare_global_feature_csvs


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["id", "Length", "Tips"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def test_compare_global_feature_csvs(tmp_path: Path) -> None:
    file_a = tmp_path / "a.csv"
    file_b = tmp_path / "b.csv"
    _write_csv(
        file_a,
        [
            {"id": "n1", "Length": 10.0, "Tips": 5},
            {"id": "n2", "Length": 20.0, "Tips": 7},
        ],
    )
    _write_csv(
        file_b,
        [
            {"id": "n1", "Length": 12.0, "Tips": 6},
            {"id": "n2", "Length": 16.0, "Tips": 8},
            {"id": "n3", "Length": 30.0, "Tips": 10},
        ],
    )
    csv_out = tmp_path / "out" / "compare.csv"
    json_out = tmp_path / "out" / "compare.json"
    report = compare_global_feature_csvs(
        file_a,
        file_b,
        csv_outfile=csv_out,
        json_outfile=json_out,
    )
    assert report["summary"]["num_shared_ids"] == 2
    assert report["summary"]["num_features"] == 2
    assert csv_out.exists()
    assert json_out.exists()
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["summary"]["num_rows_a"] == 2
    assert payload["summary"]["num_rows_b"] == 3
