from __future__ import annotations

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.swc.synthesis import add_break_fragment_attach, add_local_spur, add_small_cluster_attach


def _base_nodes() -> list[SWCNode]:
    return [
        SWCNode(1, 1, 0.0, 0.0, 0.0, 1.0, -1),
        SWCNode(2, 3, 1.0, 0.0, 0.0, 1.0, 1),
        SWCNode(3, 3, 2.0, 0.0, 0.0, 1.0, 2),
        SWCNode(4, 3, 3.0, 0.0, 0.0, 1.0, 3),
    ]


def test_add_local_spur_adds_nodes() -> None:
    nodes = _base_nodes()
    out = add_local_spur(
        nodes,
        spur_count=2,
        spur_len_range=(2, 2),
        step_length=1.0,
        angle_jitter_deg=20.0,
        rng=np.random.default_rng(0),
    )
    assert len(out.affected_node_ids) == 4
    assert len(out.nodes) == len(nodes) + 4


def test_add_small_cluster_attach_chain_mode() -> None:
    nodes = _base_nodes()
    out = add_small_cluster_attach(
        nodes,
        cluster_size=5,
        cluster_radius=2.0,
        connect_mode="chain",
        rng=np.random.default_rng(1),
    )
    assert len(out.affected_node_ids) == 5
    nmap = {n.node_id: n for n in out.nodes}
    first = out.affected_node_ids[0]
    assert nmap[first].parent_id in {1, 2, 3, 4}
    for i in range(1, len(out.affected_node_ids)):
        nid = out.affected_node_ids[i]
        assert nmap[nid].parent_id == out.affected_node_ids[i - 1]


def test_add_break_fragment_attach_dangling() -> None:
    nodes = _base_nodes()
    out = add_break_fragment_attach(
        nodes,
        break_ratio=0.5,
        offset=(3.0, 3.0),
        reconnect_prob=0.0,
        rng=np.random.default_rng(2),
    )
    nmap_before = {n.node_id: n for n in nodes}
    nmap_after = {n.node_id: n for n in out.nodes}
    assert len(out.affected_node_ids) >= 1
    cut_root = min(out.affected_node_ids)
    assert nmap_after[cut_root].parent_id == -1
    moved = any(
        abs(nmap_after[nid].x - nmap_before[nid].x) > 1e-6
        or abs(nmap_after[nid].y - nmap_before[nid].y) > 1e-6
        or abs(nmap_after[nid].z - nmap_before[nid].z) > 1e-6
        for nid in out.affected_node_ids
    )
    assert moved
