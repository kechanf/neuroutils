"""Composite scoring from topology metric components."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.topology.metrics import corr_comp_qual_score, opt_g_score, opt_j_score, opt_p_score


def composite_topology_score(gt: list[SWCNode], pred: list[SWCNode]) -> dict[str, float]:
    """Compute component and weighted total scores."""
    s_g = opt_g_score(gt, pred)
    s_j = opt_j_score(gt, pred)
    s_p = opt_p_score(gt, pred)
    s_q = corr_comp_qual_score(gt, pred)
    total = 0.30 * s_g + 0.25 * s_j + 0.25 * s_p + 0.20 * s_q
    return {"opt_g": s_g, "opt_j": s_j, "opt_p": s_p, "ccq": s_q, "total": total}
