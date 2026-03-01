from __future__ import annotations

import json
from pathlib import Path

from neuroutils.quality import evaluate_swc_quality_directory


def test_evaluate_swc_quality_directory(tmp_path: Path) -> None:
    swc_dir = tmp_path / "swc"
    swc_dir.mkdir()
    good = "1 1 0 0 0 1 -1\n2 3 1 0 0 1 1\n"
    bad = "1 1 0 0 0 1 -1\n2 3 1 0 0 1 1\n3 3 1 0 0 1 2\n"
    (swc_dir / "a.swc").write_text(good, encoding="utf-8")
    (swc_dir / "b.swc").write_text(bad, encoding="utf-8")

    csv_out = tmp_path / "quality.csv"
    json_out = tmp_path / "quality.json"
    report = evaluate_swc_quality_directory(
        swc_dir,
        csv_outfile=csv_out,
        json_outfile=json_out,
        robust=False,
    )
    assert report["summary"]["num_files"] == 2
    assert report["summary"]["num_evaluated"] == 2
    assert csv_out.exists()
    assert json_out.exists()
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert "rows" in payload
