from __future__ import annotations

import numpy as np

from neuroutils.anatomy import (
    generate_mask314,
    get_regional_neighbors,
    get_salient_regions_mask,
)


def test_get_regional_neighbors() -> None:
    mask = np.zeros((5, 5, 5), dtype=np.int32)
    mask[2, 2, 2] = 1
    mask[2, 2, 3] = 2
    rn = get_regional_neighbors(mask, radius=1, exclude_zero=True)
    assert 1 in rn and 2 in rn
    assert 2 in rn[1]


def test_generate_mask314_and_salient() -> None:
    mask = np.array([[[1, 2], [3, 4]]], dtype=np.int32)
    mapped = generate_mask314(mask, {1: 10, 2: 20, 4: 40}, ventricles={3})
    assert int(mapped[0, 0, 0]) == 10
    assert int(mapped[0, 1, 0]) == 999999
    salient = get_salient_regions_mask(mask, all_regions={1, 2, 3, 4}, ventricles={3}, fiber_tracts={4})
    assert salient.dtype == np.uint8
    assert int(salient[0, 0, 0]) == 1
    assert int(salient[0, 1, 1]) == 0
