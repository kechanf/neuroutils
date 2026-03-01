from __future__ import annotations

import numpy as np

from neuroutils.anatomy import (
    detect_edges2d,
    detect_edges3d,
    get_brain_mask2d,
    get_brain_outline2d,
    get_section_boundary,
    get_section_boundary_with_outline,
)


def test_detect_edges_2d_3d() -> None:
    img2 = np.zeros((5, 5), dtype=np.uint8)
    img2[2:, 2:] = 1
    e2 = detect_edges2d(img2)
    assert e2.shape == img2.shape

    img3 = np.zeros((3, 5, 5), dtype=np.uint8)
    img3[:, 2:, 2:] = 1
    e3 = detect_edges3d(img3)
    assert e3.shape == img3.shape


def test_section_outline_and_mask() -> None:
    mask = np.zeros((4, 6, 6), dtype=np.uint8)
    mask[:, 2:5, 2:5] = 7
    b = get_section_boundary(mask, axis=0, c=1, v=255)
    o = get_brain_outline2d(mask, axis=0, v=255)
    m = get_brain_mask2d(mask, axis=0, v=255)
    assert b.shape == (6, 6)
    assert o.shape == (6, 6)
    assert m.shape == (6, 6)
    fused = get_section_boundary_with_outline(mask, axis=0, section_x=1, v=255, fuse=True)
    assert fused.shape == (6, 6)
