from __future__ import annotations

from pathlib import Path

from neuroutils.api import compare, features, process


def test_api_process_features_compare(tmp_path: Path) -> None:
    src = tmp_path / "src.swc"
    src.write_text("\n".join([
        "10 1 5 6 7 1 -1",
        "12 3 6 6 7 1 10",
        "20 3 7 6 7 1 12",
    ]) + "\n", encoding="utf-8")

    out = tmp_path / "out.swc"
    process(src, out)
    assert out.exists()

    f = features(out)
    assert "node_count" in f

    c = compare(out, out)
    assert c["total"] >= 0.99
