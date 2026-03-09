from __future__ import annotations

import csv
from pathlib import Path

from neuroutils.workflows.common import compute_directory_metrics, process_directory_files


def test_process_directory_files(tmp_path: Path) -> None:
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    (in_dir / "a").mkdir(parents=True)
    (in_dir / "a" / "x.swc").write_text("x", encoding="utf-8")
    (in_dir / "a" / "y.swc").write_text("yy", encoding="utf-8")

    def _copy_with_len(src: Path, dst: Path) -> dict[str, int]:
        text = src.read_text(encoding="utf-8")
        dst.write_text(text, encoding="utf-8")
        return {"chars": len(text)}

    rows = process_directory_files(
        in_dir,
        out_dir,
        _copy_with_len,
        pattern="*.swc",
        n_jobs=1,
        show_progress=False,
    )
    assert len(rows) == 2
    assert (out_dir / "a" / "x.swc").exists()
    assert (out_dir / "a" / "y.swc").exists()
    assert {int(r["chars"]) for r in rows} == {1, 2}


def test_compute_directory_metrics_writes_detail_and_summary(tmp_path: Path) -> None:
    in_dir = tmp_path / "metrics_in"
    in_dir.mkdir()
    (in_dir / "a.txt").write_text("abc", encoding="utf-8")
    (in_dir / "b.txt").write_text("abcde", encoding="utf-8")

    detail_csv = tmp_path / "detail.csv"
    out = compute_directory_metrics(
        in_dir,
        lambda p: {"length": len(p.read_text(encoding="utf-8"))},
        output_csv=detail_csv,
        pattern="*.txt",
        n_jobs=1,
        show_progress=False,
    )

    summary_csv = Path(out["summary_csv"])
    assert detail_csv.exists()
    assert summary_csv.exists()

    with detail_csv.open("r", encoding="utf-8", newline="") as f:
        detail_rows = list(csv.DictReader(f))
    assert len(detail_rows) == 2

    with summary_csv.open("r", encoding="utf-8", newline="") as f:
        summary_rows = list(csv.DictReader(f))
    assert len(summary_rows) == 1
    summary = summary_rows[0]
    assert float(summary["n_files"]) == 2.0
    assert float(summary["length_mean"]) == 4.0
    assert "length_std" in summary

