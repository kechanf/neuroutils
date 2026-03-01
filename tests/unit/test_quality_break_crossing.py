from __future__ import annotations

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.morph_topo import Morphology
from neuroutils.quality import BreakFinder, CrossingFinder, find_point_by_distance


def _tree_for_break() -> list[SWCNode]:
    return [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(2, 2, 1, 0, 0, 1, 1),
        SWCNode(3, 2, 2, 0, 0, 1, 2),
        SWCNode(4, 2, 2, 1, 0, 1, 2),
    ]


def test_find_point_by_distance() -> None:
    morph = Morphology(_tree_for_break())
    pt = np.array([2.0, 0.0, 0.0])
    out = find_point_by_distance(pt, anchor_idx=2, is_parent=True, morph=morph, dist=1.0)
    assert out.shape == (3,)


def test_break_and_crossing_finders() -> None:
    morph = Morphology(_tree_for_break())
    bf = BreakFinder(morph, soma_radius=0.0, dist_thresh=2.0, angle_thresh=0.0)
    pairs = bf.find_break_pairs()
    assert isinstance(pairs, dict)
    cf = CrossingFinder(morph, soma_radius=0.0, dist_thresh=2.0)
    points, cpairs = cf.find_crossing_pairs()
    assert isinstance(points, list)
    assert isinstance(cpairs, list)
