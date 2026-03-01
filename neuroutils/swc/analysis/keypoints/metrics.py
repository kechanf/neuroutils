"""Topology keypoint metrics."""

from __future__ import annotations

from dataclasses import dataclass

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import children_map


@dataclass(frozen=True, slots=True)
class KeypointMetrics:
    """Counts of key topology points."""

    roots: int
    bifurcations: int
    leaves: int


def compute_keypoint_metrics(nodes: list[SWCNode]) -> KeypointMetrics:
    """Compute keypoint counts."""
    cmap = children_map(nodes)
    roots = sum(1 for n in nodes if n.parent_id == -1)
    bif = sum(1 for n in nodes if len(cmap.get(n.node_id, [])) > 1)
    leaves = sum(1 for n in nodes if len(cmap.get(n.node_id, [])) == 0)
    return KeypointMetrics(roots=roots, bifurcations=bif, leaves=leaves)
