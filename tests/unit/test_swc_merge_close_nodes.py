from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.swc.clean import merge_close_nodes


def test_merge_close_nodes_priority_and_radius() -> None:
    nodes = [
        SWCNode(1, 1, 0.00, 0.00, 0.00, 1.0, -1),
        SWCNode(2, 3, 0.05, 0.00, 0.00, 2.0, 1),
        SWCNode(3, 3, 5.00, 0.00, 0.00, 1.0, 2),
    ]
    out = merge_close_nodes(
        nodes,
        dist_threshold=0.1,
        priority_node_ids=[2],
    )
    merged = out.nodes
    merge_map = out.merge_map
    assert merge_map[1] == 2
    assert merge_map[2] == 2
    survivor = next(n for n in merged if n.node_id == 2)
    assert survivor.radius == 2.0


def test_merge_close_nodes_parent_remap_self_loop_to_root() -> None:
    nodes = [
        SWCNode(10, 1, 0.00, 0.00, 0.00, 1.0, -1),
        SWCNode(11, 3, 0.01, 0.00, 0.00, 1.0, 10),
        SWCNode(12, 3, 1.00, 0.00, 0.00, 1.0, 11),
    ]
    out = merge_close_nodes(nodes, dist_threshold=0.1)
    merged = {n.node_id: n for n in out.nodes}
    assert 10 in merged
    assert 11 not in merged
    assert merged[10].parent_id == -1
    assert merged[12].parent_id == 10
