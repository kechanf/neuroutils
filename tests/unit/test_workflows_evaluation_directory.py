from __future__ import annotations

from pathlib import Path

from neuroutils.workflows import evaluate_directory_pairs


def test_evaluate_directory_pairs(tmp_path: Path) -> None:
    gt_dir = tmp_path / "gt"
    pred_dir = tmp_path / "pred"
    gt_dir.mkdir()
    pred_dir.mkdir()

    swc_text = "1 1 0 0 0 1 -1\n2 3 1 0 0 1 1\n"
    (gt_dir / "a.swc").write_text(swc_text, encoding="utf-8")
    (pred_dir / "a.swc").write_text(swc_text, encoding="utf-8")
    (gt_dir / "b.swc").write_text(swc_text, encoding="utf-8")

    out_csv = tmp_path / "scores.csv"
    rows = evaluate_directory_pairs(gt_dir, pred_dir, outfile=out_csv, strict=False)
    assert len(rows) == 1
    assert rows[0]["id"] == "a"
    assert out_csv.exists()


def test_evaluate_directory_pairs_strict_unmatched(tmp_path: Path) -> None:
    gt_dir = tmp_path / "gt2"
    pred_dir = tmp_path / "pred2"
    gt_dir.mkdir()
    pred_dir.mkdir()
    swc_text = "1 1 0 0 0 1 -1\n2 3 1 0 0 1 1\n"
    (gt_dir / "a.swc").write_text(swc_text, encoding="utf-8")
    (pred_dir / "b.swc").write_text(swc_text, encoding="utf-8")

    try:
        evaluate_directory_pairs(gt_dir, pred_dir, strict=True)
        assert False, "expected strict unmatched error"
    except ValueError:
        pass
