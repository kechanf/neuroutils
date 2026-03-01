from __future__ import annotations

import json
from pathlib import Path

from neuroutils.swc.analysis.sholl import bhattacharyya_distance, earth_movers_distance
from neuroutils.workflows import compare_sholl_directories, sholl_profiles_for_directory


def test_sholl_profiles_for_directory(tmp_path: Path) -> None:
    swc_dir = tmp_path / "swc"
    swc_dir.mkdir()
    swc = "1 1 0 0 0 1 -1\n2 3 5 0 0 1 1\n3 3 10 0 0 1 2\n"
    (swc_dir / "a.swc").write_text(swc, encoding="utf-8")
    rows = sholl_profiles_for_directory(swc_dir, step=5.0)
    assert len(rows) >= 1
    assert rows[0]["id"] == "a"


def test_compare_sholl_directories(tmp_path: Path) -> None:
    gt_dir = tmp_path / "gt"
    pred_dir = tmp_path / "pred"
    gt_dir.mkdir()
    pred_dir.mkdir()
    swc_gt = "1 1 0 0 0 1 -1\n2 3 5 0 0 1 1\n3 3 10 0 0 1 2\n"
    swc_pred = "1 1 0 0 0 1 -1\n2 3 6 0 0 1 1\n3 3 12 0 0 1 2\n"
    (gt_dir / "a.swc").write_text(swc_gt, encoding="utf-8")
    (pred_dir / "a.swc").write_text(swc_pred, encoding="utf-8")
    csv_file = tmp_path / "out" / "sholl.csv"
    json_file = tmp_path / "out" / "sholl.json"
    rows = compare_sholl_directories(
        gt_dir,
        pred_dir,
        step=5.0,
        csv_outfile=csv_file,
        json_outfile=json_file,
    )
    assert len(rows) == 1
    assert rows[0]["id"] == "a"
    assert rows[0]["l1"] >= 0
    assert rows[0]["bhattacharyya"] >= 0
    assert rows[0]["emd"] >= 0
    assert csv_file.exists()
    assert json_file.exists()
    payload = json.loads(json_file.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    assert payload[0]["id"] == "a"


def test_sholl_distance_metrics_are_zero_for_same_distribution() -> None:
    counts = [10, 8, 5, 1]
    assert bhattacharyya_distance(counts, counts) == 0.0
    assert earth_movers_distance(counts, counts) == 0.0
