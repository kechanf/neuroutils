from __future__ import annotations

from pathlib import Path

from neuroutils.workflows.pipelines import process_swc_directory


def test_process_swc_directory(tmp_path: Path) -> None:
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    swc_text = "10 1 0 0 0 1 -1\n12 3 1 0 0 1 10\n"
    (in_dir / "a.swc").write_text(swc_text, encoding="utf-8")
    (in_dir / "b.swc").write_text(swc_text, encoding="utf-8")

    outputs = process_swc_directory(in_dir, out_dir, robust=False)
    assert len(outputs) == 2
    assert (out_dir / "a.swc").exists()
    assert (out_dir / "b.swc").exists()
