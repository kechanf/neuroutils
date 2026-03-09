from __future__ import annotations

from pathlib import Path

from neuroutils.io.swc import read_swc
from neuroutils.workflows.pipelines import process_swc_directory, reroot_swc_with_soma_ids


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


def test_reroot_swc_with_soma_ids(tmp_path: Path) -> None:
    src = tmp_path / "in.swc"
    dst = tmp_path / "out.swc"
    src.write_text(
        (
            "1 3 0 0 0 1 -1\n"
            "2 3 1 0 0 1 1\n"
            "3 3 2 0 0 1 2\n"
            "4 3 10 0 0 1 -1\n"
            "5 3 11 0 0 1 4\n"
            "6 3 10 1 0 1 4\n"
        ),
        encoding="utf-8",
    )
    somas = reroot_swc_with_soma_ids(src, dst, soma_node_ids=[3])
    assert somas == [3, 4]
    out = {n.node_id: n for n in read_swc(dst)}
    assert out[3].parent_id == -1
    assert out[4].parent_id == -1
