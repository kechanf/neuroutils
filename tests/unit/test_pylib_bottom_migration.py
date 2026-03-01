from __future__ import annotations

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.swc.pruning import is_in_bbox, is_in_box, remove_disconnected, trim_out_of_box
from neuroutils.utils.filesystem import file_extension, file_prefix, get_tera_res_paths
from neuroutils.utils.math import get_exponent_and_mantissa, included_angles_from_vectors


def test_path_helpers() -> None:
    assert file_prefix("a/b/c.swc") == "c"
    assert file_extension("a/b/c.swc") == ".swc"


def test_math_helpers() -> None:
    exp, man = get_exponent_and_mantissa(123.4, ndigits=1)
    assert exp == 2
    assert man == 1.2
    ang = included_angles_from_vectors(np.array([1, 0, 0]), np.array([0, 1, 0]))
    assert np.isclose(float(ang[0]), 90.0)


def test_spatial_helpers() -> None:
    assert is_in_box(3, 3, 3, (10, 10, 10))
    assert not is_in_box(-1, 0, 0, (10, 10, 10))
    assert is_in_bbox(1, 2, 3, ((0, 0, 0), (5, 5, 5)))
    assert not is_in_bbox(10, 2, 3, ((0, 0, 0), (5, 5, 5)))


def test_terafly_path_aliases(tmp_path) -> None:
    (tmp_path / "RES(001x001x001)").mkdir()
    (tmp_path / "RES(004x004x004)").mkdir()
    paths = get_tera_res_paths(tmp_path)
    assert len(paths) == 2
    one = get_tera_res_paths(tmp_path, res_ids=0)
    assert isinstance(one, str)


def test_trim_and_disconnect() -> None:
    nodes = [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(2, 3, 1, 0, 0, 1, 1),
        SWCNode(3, 3, 2, 0, 0, 1, 2),
        SWCNode(10, 1, 50, 50, 50, 1, -1),
        SWCNode(11, 3, 51, 50, 50, 1, 10),
    ]
    trimmed = trim_out_of_box(nodes, (10, 10, 10), keep_candidate_points=False)
    assert {n.node_id for n in trimmed} == {1, 2, 3}

    connected = remove_disconnected(nodes, anchor_id=2)
    assert {n.node_id for n in connected} == {1, 2, 3}
