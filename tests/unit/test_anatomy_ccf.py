from __future__ import annotations

import numpy as np
import pytest

from neuroutils.anatomy import (
    ccf_to_stereotactic_mask_res25,
    ccf2stereotactic_mask_res25,
    get_center,
    matrix_from_axis_angle,
    resample,
)


def test_matrix_from_axis_angle_identity() -> None:
    r = matrix_from_axis_angle((0, 0, 1, 0.0))
    assert np.allclose(r, np.eye(3))


def test_ccf_to_stereotactic_mask_res25() -> None:
    scipy = pytest.importorskip("scipy")
    if scipy is None:
        return
    mask = np.zeros((10, 10, 10), dtype=np.uint8)
    mask[:, 3:7, 3:7] = 1
    out = ccf_to_stereotactic_mask_res25(mask, rotate_z_deg=0.0, scale_y=0.5)
    assert out.ndim == 3
    assert out.shape[1] <= mask.shape[1]
    out2 = ccf2stereotactic_mask_res25(mask)
    assert out2.ndim == 3


def test_resample_and_center() -> None:
    scipy = pytest.importorskip("scipy")
    if scipy is None:
        return
    img = np.zeros((6, 8, 10), dtype=np.uint8)
    img[3, 4, 5] = 1
    c = get_center(img)
    assert np.allclose(c, np.array([5.0, 4.0, 3.0]))
    t = np.eye(4, dtype=np.float64)
    out = resample(img, t)
    assert out.shape == img.shape
