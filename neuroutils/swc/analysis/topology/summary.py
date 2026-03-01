"""Topology summary analysis."""

from __future__ import annotations

from dataclasses import dataclass

from neuroutils.core.types import SWCNode
from neuroutils.swc.analysis.connectivity import compute_connectivity_metrics
from neuroutils.swc.analysis.keypoints import compute_keypoint_metrics


@dataclass(frozen=True, slots=True)
class TopologySummary:
    """Combined topology summary."""

    roots: int
    bifurcations: int
    leaves: int
    edge_count: int


def summarize_topology(nodes: list[SWCNode]) -> TopologySummary:
    """Compute compact topology summary."""
    c = compute_connectivity_metrics(nodes)
    k = compute_keypoint_metrics(nodes)
    return TopologySummary(
        roots=k.roots,
        bifurcations=k.bifurcations,
        leaves=k.leaves,
        edge_count=c.edge_count,
    )
