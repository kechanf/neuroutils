"""Connectivity metrics."""

from __future__ import annotations

from dataclasses import dataclass

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import children_map, find_root_ids


@dataclass(frozen=True, slots=True)
class ConnectivityMetrics:
    """Topology-level connectivity summary."""

    node_count: int
    edge_count: int
    root_count: int
    branch_point_count: int
    leaf_count: int


def compute_connectivity_metrics(nodes: list[SWCNode]) -> ConnectivityMetrics:
    """Compute simple connectivity metrics."""
    cmap = children_map(nodes)
    roots = find_root_ids(nodes)
    branch_points = sum(1 for n in nodes if len(cmap.get(n.node_id, [])) > 1)
    leaves = sum(1 for n in nodes if len(cmap.get(n.node_id, [])) == 0)
    return ConnectivityMetrics(
        node_count=len(nodes),
        edge_count=max(0, len(nodes) - len(roots)),
        root_count=len(roots),
        branch_point_count=branch_points,
        leaf_count=leaves,
    )
