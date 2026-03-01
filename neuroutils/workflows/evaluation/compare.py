"""Evaluation workflows."""

from __future__ import annotations

from pathlib import Path

from neuroutils.io.swc import read_swc
from neuroutils.topology import composite_topology_score


def evaluate_pair(gt_swc: str | Path, pred_swc: str | Path) -> dict[str, float]:
    """Evaluate one prediction SWC against ground truth SWC."""
    gt_nodes = read_swc(gt_swc)
    pred_nodes = read_swc(pred_swc)
    return composite_topology_score(gt_nodes, pred_nodes)
