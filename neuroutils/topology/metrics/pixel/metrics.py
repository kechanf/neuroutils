"""Pixel-like proxy metric from point matches."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.matching import match_by_nearest


def corr_comp_qual_score(gt: list[SWCNode], pred: list[SWCNode], max_dist: float = 3.0) -> float:
    """F1-style point correspondence score in [0, 1]."""
    if not gt and not pred:
        return 1.0
    pairs = match_by_nearest(gt, pred, max_dist=max_dist)
    precision = len(pairs) / (len(pred) + 1e-9)
    recall = len(pairs) / (len(gt) + 1e-9)
    if precision + recall == 0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)
