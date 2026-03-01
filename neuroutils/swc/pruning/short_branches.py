"""Branch pruning."""

from __future__ import annotations

import math

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import children_map, node_map


def _distance(a: SWCNode, b: SWCNode) -> float:
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def prune_short_leaf_branches(nodes: list[SWCNode], min_branch_length: float) -> list[SWCNode]:
    """Prune leaf nodes whose terminal edge length is below threshold."""
    nmap = node_map(nodes)
    cmap = children_map(nodes)
    remove_ids: set[int] = set()
    for node in nodes:
        if cmap.get(node.node_id):
            continue
        if node.parent_id == -1:
            continue
        parent = nmap[node.parent_id]
        if _distance(node, parent) < min_branch_length:
            remove_ids.add(node.node_id)
    return [n for n in nodes if n.node_id not in remove_ids]
