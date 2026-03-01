from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.topology import composite_topology_score


def test_composite_score_range() -> None:
    gt = [SWCNode(1, 1, 0, 0, 0, 1, -1), SWCNode(2, 3, 1, 0, 0, 1, 1)]
    pred = [SWCNode(1, 1, 0, 0, 0, 1, -1), SWCNode(2, 3, 1, 0, 0, 1, 1)]
    scores = composite_topology_score(gt, pred)
    assert 0.0 <= scores["total"] <= 1.0
