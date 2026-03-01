"""Local morphometric features."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import node_map
from neuroutils.utils.math import euclidean_3d


def edge_lengths(nodes: list[SWCNode]) -> list[float]:
    """Return per-edge lengths for all non-root nodes."""
    nmap = node_map(nodes)
    return [euclidean_3d(n, nmap[n.parent_id]) for n in nodes if n.parent_id != -1]
