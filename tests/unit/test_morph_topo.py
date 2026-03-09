from __future__ import annotations

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.morph_topo import (
    MorphAngles,
    MorphCurvature,
    Morphology,
    Topology,
    get_outside_soma_mask,
)


def _toy_tree() -> list[SWCNode]:
    return [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(2, 2, 1, 0, 0, 1, 1),
        SWCNode(3, 2, 2, 0, 0, 1, 2),
        SWCNode(4, 3, 2, 1, 0, 1, 2),
        SWCNode(5, 3, 3, 1, 0, 1, 4),
    ]


def test_morphology_and_topology_basic() -> None:
    morph = Morphology(_toy_tree())
    assert morph.idx_soma == 1
    assert 3 in morph.tips and 5 in morph.tips
    assert 2 in morph.bifurcation
    topo_tree, seg = morph.convert_to_topology_tree()
    assert len(topo_tree) > 0
    assert isinstance(seg, dict)
    topo = Topology(topo_tree)
    assert topo.get_num_branches() >= 0
    assert topo.get_topo_depth() >= 0


def test_morph_angles_curvature_and_mask() -> None:
    morph = Morphology(_toy_tree())
    ma = MorphAngles()
    angs = ma.calc_outgrowth_angles(morph)
    assert isinstance(angs, np.ndarray)
    mc = MorphCurvature(morph)
    _ = mc.estimate_angular_dependence()
    _ = mc.estimate_coplanarity()
    mask = get_outside_soma_mask(morph, dist_thresh=0.5)
    assert mask[1] is False
