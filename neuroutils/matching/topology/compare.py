"""Topology-level similarity."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.swc.analysis import summarize_topology


def topology_similarity(gt: list[SWCNode], pred: list[SWCNode]) -> float:
    """Similarity score in [0, 1] using key topology counts."""
    g = summarize_topology(gt)
    p = summarize_topology(pred)
    denom = g.leaves + g.bifurcations + g.edge_count + 1e-9
    err = abs(g.leaves - p.leaves) + abs(g.bifurcations - p.bifurcations) + abs(g.edge_count - p.edge_count)
    score = 1.0 - err / denom
    return max(0.0, min(1.0, score))
