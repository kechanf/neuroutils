from __future__ import annotations

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.morph_topo import Morphology, NeuriteShapeSingle, PDist


def _tree() -> list[SWCNode]:
    return [
        SWCNode(1, 1, 1, 1, 1, 2, -1),
        SWCNode(2, 2, 2, 1, 1, 1, 1),
        SWCNode(3, 2, 3, 1, 1, 1, 2),
        SWCNode(4, 3, 2, 2, 1, 1, 2),
    ]


def test_pdist_crossing_candidates() -> None:
    morph = Morphology(_tree())
    pd = PDist(ignore_radius_from_soma=0.0, offspring_thresh=2)
    pd.set_morph(morph)
    near, away = pd.get_soma_nearby_nodes()
    assert away.shape[0] >= 1
    pairs = pd.find_crossing_pairs(crossing_thresh=2.0)
    assert isinstance(pairs, dict)


def test_neurite_shape_single_intensity_radius() -> None:
    img = np.zeros((5, 5, 5), dtype=np.uint8)
    img[1, 1, 1] = 100
    ns = NeuriteShapeSingle(_tree(), img, use_local_maximal=False, normalize_image=False)
    ins, _ = ns.get_branch_intensity_dict()
    rad, _ = ns.get_branch_radius_dict()
    assert isinstance(ins, dict)
    assert isinstance(rad, dict)
