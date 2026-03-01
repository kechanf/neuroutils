from __future__ import annotations

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.morph_topo import TopoFeatures, TopoImFeatures


def _tree() -> list[SWCNode]:
    return [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(2, 2, 1, 0, 0, 1, 1),
        SWCNode(3, 2, 2, 0, 0, 1, 2),
        SWCNode(4, 3, 2, 1, 0, 1, 2),
        SWCNode(5, 3, 3, 1, 0, 1, 4),
    ]


def test_topo_features_calc_all_features() -> None:
    tf = TopoFeatures(_tree(), line_length=2.0, z_factor=1.0)
    feats = tf.calc_all_features()
    assert "pdists_soma" in feats
    assert "local_angs" in feats
    assert len(feats["order_dict"]) > 0


def test_topo_im_features_calc_all_features() -> None:
    img = np.zeros((4, 4, 4), dtype=np.uint8)
    img[0, 0, 0] = 10
    img[0, 1, 2] = 20
    tif = TopoImFeatures(_tree(), img)
    feats = tif.calc_all_features()
    assert "intensity" in feats and "radii" in feats
