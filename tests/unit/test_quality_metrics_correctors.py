from __future__ import annotations

from pathlib import Path

from neuroutils.core.types import SWCNode
from neuroutils.quality import (
    DistanceEvaluation,
    remove_duplicate_nodes,
    remove_duplicate_nodes_file,
    remove_duplicate_parent_coordinate_nodes,
)


def test_remove_duplicate_parent_coordinate_nodes() -> None:
    nodes = [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(2, 3, 0, 0, 0, 1, 1),
        SWCNode(3, 3, 1, 0, 0, 1, 2),
    ]
    out = remove_duplicate_parent_coordinate_nodes(nodes)
    assert [n.node_id for n in out] == [1, 3]
    assert out[1].parent_id == 1


def test_remove_duplicate_nodes_file(tmp_path: Path) -> None:
    src = tmp_path / "a.swc"
    src.write_text("1 1 0 0 0 1 -1\n2 3 0 0 0 1 1\n3 3 1 0 0 1 2\n", encoding="utf-8")
    dst = tmp_path / "b.swc"
    remove_duplicate_nodes_file(src, dst)
    text = dst.read_text(encoding="utf-8")
    assert " 2 " not in text


def test_remove_duplicate_nodes_wrapper(tmp_path: Path) -> None:
    src = tmp_path / "a.swc"
    src.write_text("1 1 0 0 0 1 -1\n2 3 0 0 0 1 1\n3 3 1 0 0 1 2\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    dst = remove_duplicate_nodes(src, out_dir=out_dir)
    assert dst.exists()
    text = dst.read_text(encoding="utf-8")
    assert " 2 " not in text


def test_distance_evaluation() -> None:
    a = [SWCNode(1, 1, 0, 0, 0, 1, -1), SWCNode(2, 3, 1, 0, 0, 1, 1)]
    b = [SWCNode(1, 1, 0, 0, 0, 1, -1), SWCNode(2, 3, 2, 0, 0, 1, 1)]
    ev = DistanceEvaluation(resample1=False, resample2=False)
    m = ev.run(a, b)
    assert m.esa[2] >= 0
    assert m.pds[2] >= 0
