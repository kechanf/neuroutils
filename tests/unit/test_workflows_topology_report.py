from __future__ import annotations

import json
from pathlib import Path

from neuroutils.workflows import evaluate_topology_directory_report


def test_evaluate_topology_directory_report(tmp_path: Path) -> None:
    gt_dir = tmp_path / "gt"
    pred_dir = tmp_path / "pred"
    gt_dir.mkdir()
    pred_dir.mkdir()

    swc = "1 1 0 0 0 1 -1\n2 3 1 0 0 1 1\n"
    (gt_dir / "a.swc").write_text(swc, encoding="utf-8")
    (pred_dir / "a.swc").write_text(swc, encoding="utf-8")
    (gt_dir / "b.swc").write_text(swc, encoding="utf-8")

    csv_out = tmp_path / "topo.csv"
    json_out = tmp_path / "topo.json"
    report = evaluate_topology_directory_report(
        gt_dir,
        pred_dir,
        csv_outfile=csv_out,
        json_outfile=json_out,
        strict=False,
    )
    assert report["summary"]["num_shared"] == 1
    assert report["summary"]["num_gt_only"] == 1
    assert csv_out.exists()
    assert json_out.exists()
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert "rows" in payload
