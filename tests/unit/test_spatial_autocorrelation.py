from __future__ import annotations

import numpy as np

from neuroutils.spatial import moran_i_score


def test_moran_i_score_distance_and_knn() -> None:
    coords = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
        ]
    )
    feats = np.array([1.0, 1.2, 2.8, 3.0])
    score_d = moran_i_score(coords, feats, weight_type="distance", threshold=1.1)
    assert isinstance(score_d, float)
    score_k = moran_i_score(coords, feats, weight_type="knn", k=2)
    assert isinstance(score_k, float)
    score_all = moran_i_score(coords, np.column_stack([feats, feats[::-1]]), reduce_type="all")
    assert isinstance(score_all, list) and len(score_all) == 2
