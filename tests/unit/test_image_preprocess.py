from __future__ import annotations

import numpy as np

from neuroutils.imaging.preprocess import flip_y_axis, to_uint8


def test_to_uint8_from_uint16() -> None:
    img = np.array([[0, 1000], [2000, 4000]], dtype=np.uint16)
    out = to_uint8(img)
    assert out.dtype == np.uint8
    assert out.min() == 0
    assert out.max() == 255


def test_to_uint8_passthrough_copy() -> None:
    img = np.array([[1, 2], [3, 4]], dtype=np.uint8)
    out = to_uint8(img)
    assert out.dtype == np.uint8
    assert np.array_equal(out, img)
    assert out is not img


def test_flip_y_axis_2d() -> None:
    img = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.uint8)
    out = flip_y_axis(img)
    assert np.array_equal(out, img[::-1, :])


def test_flip_y_axis_3d() -> None:
    img = np.arange(2 * 3 * 4, dtype=np.uint8).reshape(2, 3, 4)
    out = flip_y_axis(img)
    assert np.array_equal(out, img[:, ::-1, :])
