from __future__ import annotations

import pytest

from neuroutils.core.exceptions import ValidationError
from neuroutils.core.types import SWCNode
from neuroutils.transforms import center_at_root, scale_nodes, standardize_swc
from neuroutils.validation import validate_swc


def test_validate_swc_rejects_duplicate_ids() -> None:
    nodes = [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(1, 3, 1, 0, 0, 1, 1),
    ]
    with pytest.raises(ValidationError):
        validate_swc(nodes)


def test_standardize_centers_root() -> None:
    nodes = [
        SWCNode(10, 1, 5, 6, 7, 1, -1),
        SWCNode(20, 3, 6, 6, 7, 1, 10),
    ]
    centered = center_at_root(nodes)
    root = next(n for n in centered if n.parent_id == -1)
    assert (root.x, root.y, root.z) == (0.0, 0.0, 0.0)

    std = standardize_swc(nodes)
    assert [n.node_id for n in std] == [1, 2]


def test_scale_nodes_radius_default_enabled() -> None:
    nodes = [SWCNode(1, 1, 10, 20, 30, 2.0, -1)]
    scaled = scale_nodes(nodes, sx=0.7, sy=0.7, sz=1.0)
    assert scaled[0].x == 7.0
    assert scaled[0].y == 14.0
    assert scaled[0].z == 30.0
    assert scaled[0].radius == pytest.approx(2.0 * (0.7 * 0.7 * 1.0) ** (1.0 / 3.0))
