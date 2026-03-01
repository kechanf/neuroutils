from __future__ import annotations

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.transforms.coordinates import auto_flip_nodes_y_by_intensity, flip_nodes_y, mean_intensity_at_nodes


def test_flip_nodes_y_formula() -> None:
    nodes = [SWCNode(1, 1, 10.0, 2.0, 3.0, 1.0, -1)]
    out = flip_nodes_y(nodes, image_height=10)
    assert out[0].y == 7.0
    assert out[0].x == 10.0
    assert out[0].z == 3.0


def test_mean_intensity_at_nodes_3d() -> None:
    img = np.zeros((2, 6, 6), dtype=np.uint8)
    img[1, 4, 3] = 100
    nodes = [SWCNode(1, 1, 3.0, 4.0, 1.0, 1.0, -1)]
    mean_value, count = mean_intensity_at_nodes(img, nodes)
    assert count == 1
    assert mean_value == 100.0


def test_auto_flip_nodes_y_by_intensity_flips_when_brighter() -> None:
    img = np.zeros((1, 10, 10), dtype=np.uint8)
    img[0, 8, 4] = 200
    img[0, 1, 4] = 50
    nodes = [SWCNode(1, 1, 4.0, 1.0, 0.0, 1.0, -1)]

    result = auto_flip_nodes_y_by_intensity(img, nodes)
    assert result.flipped is True
    assert result.original_mean_intensity == 50.0
    assert result.flipped_mean_intensity == 200.0
    assert result.nodes[0].y == 8.0


def test_auto_flip_nodes_y_by_intensity_keeps_when_not_better() -> None:
    img = np.zeros((1, 10, 10), dtype=np.uint8)
    img[0, 1, 4] = 200
    img[0, 8, 4] = 50
    nodes = [SWCNode(1, 1, 4.0, 1.0, 0.0, 1.0, -1)]

    result = auto_flip_nodes_y_by_intensity(img, nodes)
    assert result.flipped is False
    assert result.nodes[0].y == 1.0
