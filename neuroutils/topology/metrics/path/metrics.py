"""Path-level topology metrics."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.swc.analysis import compute_geodesic_metrics


def opt_p_score(gt: list[SWCNode], pred: list[SWCNode]) -> float:
    """Path score by max root-to-leaf path agreement."""
    g = compute_geodesic_metrics(gt)
    p = compute_geodesic_metrics(pred)
    denom = g.max_root_to_leaf_length + 1e-9
    err = abs(g.max_root_to_leaf_length - p.max_root_to_leaf_length)
    return max(0.0, min(1.0, 1.0 - err / denom))
