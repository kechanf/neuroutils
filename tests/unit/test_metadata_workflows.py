from __future__ import annotations

import csv
from pathlib import Path

from neuroutils.metadata import (
    build_metadata_consistency_report,
    extract_neuron_id_from_filename,
    load_neuron_metadata_record,
    map_neuron_id,
    rebuild_metadata_cache,
    split_metadata_table_by_neuron_id,
    tile_id_from_record,
    validate_metadata_table_consistency,
    v3dpbd_relative_path_from_cell_id,
    xy_z_resolution_from_record,
)


def _write_meta_csv(path: Path) -> None:
    rows = [
        {
            "cell_id": "1001",
            "document_name": "tile_a",
            "xy_resolution": "0.3",
            "z_resolution": "1.0",
        },
        {
            "cell_id": "1002",
            "document_name": "tile_b",
            "xy_resolution": "0.4",
            "z_resolution": "1.2",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def test_extract_and_path_builder() -> None:
    assert extract_neuron_id_from_filename("image_00123_0000.tif") == 123
    p = v3dpbd_relative_path_from_cell_id(101386, min_digits=5)
    assert p.endswith("101000_101999\\101300_101399\\101386.v3dpbd") or p.endswith(
        "101000_101999/101300_101399/101386.v3dpbd"
    )


def test_split_load_and_cache_metadata(tmp_path: Path) -> None:
    table = tmp_path / "meta.csv"
    cache = tmp_path / "cache"
    _write_meta_csv(table)

    out_files = split_metadata_table_by_neuron_id(table, cache)
    assert len(out_files) == 2
    rec = load_neuron_metadata_record(1001, table_file=table, cache_dir=cache, use_cache=True)
    assert rec["document_name"] == "tile_a"
    assert tile_id_from_record(rec) == "tile_a"
    assert xy_z_resolution_from_record(rec) == (0.3, 1.0)


def test_rebuild_cache_and_id_mapping(tmp_path: Path) -> None:
    table = tmp_path / "meta.csv"
    cache = tmp_path / "cache"
    _write_meta_csv(table)
    n = rebuild_metadata_cache(table, cache)
    assert n == 2

    mapping_rows = [{"old_id": "1", "new_id": "101"}, {"old_id": "2", "new_id": "202"}]
    assert map_neuron_id(101, mapping_rows, old_to_new=False) == 1
    assert map_neuron_id(2, mapping_rows, old_to_new=True) == 202


def test_metadata_consistency_report(tmp_path: Path) -> None:
    bad_records = [
        {"cell_id": "1", "xy_resolution": "0.3", "z_resolution": "1.0"},
        {"cell_id": "1", "xy_resolution": "bad", "z_resolution": "1.1"},
        {"cell_id": "", "xy_resolution": "0.2", "z_resolution": "1.0"},
    ]
    report = build_metadata_consistency_report(
        bad_records,
        required_keys=("cell_id", "xy_resolution"),
        numeric_keys=("xy_resolution", "z_resolution"),
    )
    assert report["summary"]["num_duplicate_id_rows"] == 1
    assert report["summary"]["num_invalid_numeric"] == 1
    assert report["summary"]["num_missing_required"] == 1
    assert report["summary"]["passed"] is False

    table = tmp_path / "bad_meta.csv"
    with table.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=["cell_id", "xy_resolution", "z_resolution"])
        writer.writeheader()
        for row in bad_records:
            writer.writerow(row)
    out_json = tmp_path / "meta_report.json"
    report2 = validate_metadata_table_consistency(table, json_outfile=out_json)
    assert out_json.exists()
    assert report2["summary"]["num_records"] == 3
