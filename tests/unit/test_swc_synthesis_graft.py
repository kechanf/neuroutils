from __future__ import annotations

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.swc.synthesis import graft_branch_segment, graft_full_tree


def test_graft_full_tree_connects_all_donor_nodes_except_attach() -> None:
    target = [
        SWCNode(1, 1, 0.0, 0.0, 0.0, 1.0, -1),
        SWCNode(2, 3, 1.0, 0.0, 0.0, 1.0, 1),
    ]
    donor = [
        SWCNode(10, 1, 10.0, 10.0, 10.0, 2.0, -1),
        SWCNode(11, 3, 11.0, 10.0, 10.0, 1.0, 10),
        SWCNode(12, 3, 10.0, 11.0, 10.0, 1.0, 10),
    ]
    out = graft_full_tree(
        target,
        donor,
        target_attach_id=2,
        donor_attach_id=10,
        apply_rotation=False,
        rng=np.random.default_rng(0),
    )
    nmap = {n.node_id: n for n in out.nodes}
    assert len(out.grafted_node_ids) == 2
    assert nmap[2].radius == 2.0
    for nid in out.grafted_node_ids:
        assert nmap[nid].parent_id == 2


def test_graft_branch_segment_builds_chain() -> None:
    target = [
        SWCNode(1, 1, 0.0, 0.0, 0.0, 1.0, -1),
        SWCNode(2, 3, 1.0, 0.0, 0.0, 1.0, 1),
    ]
    donor = [
        SWCNode(10, 1, 5.0, 0.0, 0.0, 1.5, -1),
        SWCNode(11, 3, 6.0, 0.0, 0.0, 1.0, 10),
        SWCNode(12, 3, 7.0, 0.0, 0.0, 1.0, 11),
        SWCNode(13, 3, 8.0, 0.0, 0.0, 1.0, 12),
    ]
    out = graft_branch_segment(
        target,
        donor,
        target_attach_id=2,
        donor_attach_id=10,
        first_step_id=11,
        max_hops=3,
        angle_limit_deg=30.0,
        apply_rotation=False,
        rng=np.random.default_rng(1),
    )
    nmap = {n.node_id: n for n in out.nodes}
    assert len(out.grafted_node_ids) == 3
    first = out.grafted_node_ids[0]
    assert nmap[first].parent_id == 2
    assert nmap[out.grafted_node_ids[1]].parent_id == first
    assert nmap[out.grafted_node_ids[2]].parent_id == out.grafted_node_ids[1]
