"""Near-node merge utilities for SWC trees."""

from __future__ import annotations

from dataclasses import dataclass

from scipy.spatial import KDTree

from neuroutils.core.types import SWCNode


@dataclass(frozen=True, slots=True)
class MergeCloseNodesResult:
    """Result of close-node merging."""

    nodes: list[SWCNode]
    merge_map: dict[int, int]


class _UnionFind:
    def __init__(self, ids: list[int]) -> None:
        self.parent: dict[int, int] = {i: i for i in ids}

    def find(self, x: int) -> int:
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if ra < rb:
            self.parent[rb] = ra
        else:
            self.parent[ra] = rb


def merge_close_nodes(
    nodes: list[SWCNode],
    *,
    dist_threshold: float = 1.0,
    priority_node_ids: list[int] | set[int] | tuple[int, ...] | None = None,
    secondary_priority_node_ids: list[int] | set[int] | tuple[int, ...] | None = None,
) -> MergeCloseNodesResult:
    """Merge nodes with pairwise distance <= threshold using deterministic priorities.

    Priority order for survivor selection within one merged cluster:
    1. ``priority_node_ids``
    2. ``secondary_priority_node_ids``
    3. smaller node id
    """
    if not nodes:
        return MergeCloseNodesResult(nodes=[], merge_map={})
    if dist_threshold <= 0.0:
        identity = {n.node_id: n.node_id for n in nodes}
        return MergeCloseNodesResult(nodes=list(nodes), merge_map=identity)

    p1 = set(priority_node_ids or [])
    p2 = set(secondary_priority_node_ids or [])
    uf = _UnionFind([n.node_id for n in nodes])
    ids = [n.node_id for n in nodes]
    coords = [(float(n.x), float(n.y), float(n.z)) for n in nodes]
    tree = KDTree(coords)
    for i, j in tree.query_pairs(r=dist_threshold):
        uf.union(ids[i], ids[j])

    components: dict[int, list[int]] = {}
    for n in nodes:
        root = uf.find(n.node_id)
        components.setdefault(root, []).append(n.node_id)

    nmap = {n.node_id: n for n in nodes}
    merge_map: dict[int, int] = {}
    survivor_radius: dict[int, float] = {}

    for comp in components.values():
        survivor = min(
            comp,
            key=lambda nid: (
                0 if nid in p1 else 1,
                0 if nid in p2 else 1,
                nid,
            ),
        )
        max_r = max(float(nmap[nid].radius) for nid in comp)
        survivor_radius[survivor] = max_r
        for nid in comp:
            merge_map[nid] = survivor

    survivors_seen: set[int] = set()
    merged_nodes: list[SWCNode] = []
    valid_ids = set(nmap)
    for n in nodes:
        sid = merge_map[n.node_id]
        if sid in survivors_seen:
            continue
        survivors_seen.add(sid)
        src = nmap[sid]
        parent = src.parent_id
        if parent != -1 and parent in merge_map:
            parent = merge_map[parent]
        if parent == sid or (parent != -1 and parent not in valid_ids):
            parent = -1
        merged_nodes.append(
            SWCNode(
                node_id=src.node_id,
                node_type=src.node_type,
                x=src.x,
                y=src.y,
                z=src.z,
                radius=survivor_radius[sid],
                parent_id=parent,
            )
        )
    return MergeCloseNodesResult(nodes=merged_nodes, merge_map=merge_map)
