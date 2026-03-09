from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.swc.analysis import bbox_xyz, extent_xyz, node_count


def test_node_count_bbox_extent() -> None:
    nodes = [
        SWCNode(1, 1, 1.0, 2.0, 3.0, 1.0, -1),
        SWCNode(2, 3, 5.0, 7.0, 11.0, 1.0, 1),
        SWCNode(3, 3, -1.0, 4.0, 6.0, 1.0, 2),
    ]
    assert node_count(nodes) == 3
    b = bbox_xyz(nodes)
    assert (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax) == (-1.0, 5.0, 2.0, 7.0, 3.0, 11.0)
    e = extent_xyz(nodes)
    assert (e.x, e.y, e.z) == (6.0, 5.0, 8.0)
