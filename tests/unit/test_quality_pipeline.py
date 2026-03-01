from __future__ import annotations

from pathlib import Path

from neuroutils.quality import evaluate_swc_quality, repair_and_validate_swc


def test_evaluate_swc_quality(tmp_path: Path) -> None:
    swc = tmp_path / "q.swc"
    swc.write_text(
        "1 1 0 0 0 1 -1\n"
        "2 3 1 0 0 1 1\n"
        "3 3 1 0 0 1 2\n",
        encoding="utf-8",
    )
    summary = evaluate_swc_quality(swc)
    assert not summary.passed
    assert summary.checks["DuplicateNodes"] is False


def test_repair_and_validate_swc(tmp_path: Path) -> None:
    src = tmp_path / "in.swc"
    dst = tmp_path / "out.swc"
    src.write_text(
        "10 1 0 0 0 1 -1\n"
        "20 3 1 0 0 1 10\n"
        "30 3 1 0 0 1 20\n",
        encoding="utf-8",
    )
    out_path = repair_and_validate_swc(src, dst)
    assert out_path.exists()
    summary = evaluate_swc_quality(out_path)
    assert summary.passed
