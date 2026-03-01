"""Geodesic/path metrics."""

from __future__ import annotations

from dataclasses import dataclass

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import children_map, node_map
from neuroutils.utils.math import euclidean_3d


@dataclass(frozen=True, slots=True)
class GeodesicMetrics:
    """Path-length summary."""

    total_length: float
    max_root_to_leaf_length: float


def compute_geodesic_metrics(nodes: list[SWCNode]) -> GeodesicMetrics:
    """Compute total edge length and longest root-to-leaf path length."""
    nmap = node_map(nodes)
    cmap = children_map(nodes)
    total = 0.0
    for node in nodes:
        if node.parent_id == -1:
            continue
        total += euclidean_3d(node, nmap[node.parent_id])

    max_len = 0.0
    for node in nodes:
        if cmap.get(node.node_id):
            continue
        cur = node
        cur_len = 0.0
        while cur.parent_id != -1:
            parent = nmap[cur.parent_id]
            cur_len += euclidean_3d(cur, parent)
            cur = parent
        max_len = max(max_len, cur_len)
    return GeodesicMetrics(total_length=total, max_root_to_leaf_length=max_len)
