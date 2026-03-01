"""Graph-level topology metrics."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.matching import topology_similarity


def opt_g_score(gt: list[SWCNode], pred: list[SWCNode]) -> float:
    """Graph score proxy."""
    return topology_similarity(gt, pred)
