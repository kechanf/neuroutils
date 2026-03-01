"""Junction-level topology metrics."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.swc.analysis import compute_keypoint_metrics


def opt_j_score(gt: list[SWCNode], pred: list[SWCNode]) -> float:
    """Junction score by bifurcation agreement."""
    g = compute_keypoint_metrics(gt)
    p = compute_keypoint_metrics(pred)
    denom = g.bifurcations + 1e-9
    err = abs(g.bifurcations - p.bifurcations)
    return max(0.0, min(1.0, 1.0 - err / denom))
