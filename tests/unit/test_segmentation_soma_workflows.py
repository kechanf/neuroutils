from __future__ import annotations

import numpy as np

from neuroutils.segmentation import (
    detect_soma_region_from_image,
    detect_soma_region_from_segmentation,
    detect_soma_region_smart,
)


def test_detect_soma_region_from_segmentation_keeps_largest() -> None:
    mask = np.zeros((5, 8, 8), dtype=np.uint8)
    mask[1, 1:3, 1:3] = 1  # 4 voxels
    mask[3, 4:7, 4:7] = 1  # 9 voxels
    res = detect_soma_region_from_segmentation(mask, keep_largest_component=True)
    assert res.voxel_count == 9
    assert res.bbox_zyxzyx == (3, 3, 4, 6, 4, 6)


def test_detect_soma_region_from_image_threshold() -> None:
    image = np.zeros((4, 6, 6), dtype=np.float32)
    image[2, 2:5, 2:5] = 10.0
    res = detect_soma_region_from_image(image, threshold=5.0, padding=1)
    assert res.voxel_count == 9
    assert res.bbox_zyxzyx == (1, 3, 1, 5, 1, 5)


def test_detect_soma_region_smart_prefers_large_bright_component() -> None:
    image = np.zeros((6, 12, 12), dtype=np.float32)
    image[1, 1:3, 1:3] = 80.0
    image[3, 6:10, 6:10] = 60.0
    res = detect_soma_region_smart(image, percentiles=(95.0, 90.0, 80.0), min_voxel_count=4)
    assert res.voxel_count == 16
    assert res.bbox_zyxzyx == (3, 3, 6, 9, 6, 9)
