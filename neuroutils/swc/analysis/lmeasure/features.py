"""L-measure-like global features."""

from __future__ import annotations

from dataclasses import dataclass

from neuroutils.core.types import SWCNode
from neuroutils.swc.analysis.connectivity import compute_connectivity_metrics
from neuroutils.swc.analysis.geodesic import compute_geodesic_metrics


@dataclass(frozen=True, slots=True)
class LMeasureLike:
    """Portable subset of global morphology features."""

    node_count: int
    branch_count: int
    tip_count: int
    total_length: float
    max_path_length: float


def compute_lmeasure_like(nodes: list[SWCNode]) -> LMeasureLike:
    """Compute lightweight L-measure-like summary."""
    conn = compute_connectivity_metrics(nodes)
    geo = compute_geodesic_metrics(nodes)
    return LMeasureLike(
        node_count=conn.node_count,
        branch_count=conn.branch_point_count,
        tip_count=conn.leaf_count,
        total_length=geo.total_length,
        max_path_length=geo.max_root_to_leaf_length,
    )
