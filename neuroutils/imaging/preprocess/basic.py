"""Image preprocessing helpers."""

from __future__ import annotations

import numpy as np


def min_max_normalize(image: np.ndarray) -> np.ndarray:
    """Normalize image to [0, 1]."""
    img = image.astype(np.float32)
    vmin = float(img.min())
    vmax = float(img.max())
    if vmax <= vmin:
        return np.zeros_like(img)
    return (img - vmin) / (vmax - vmin)


def to_uint8(image: np.ndarray) -> np.ndarray:
    """Convert arbitrary numeric image to uint8 using min-max normalization."""
    if image.dtype == np.uint8:
        return image.copy()
    norm = min_max_normalize(image)
    return np.clip(norm * 255.0, 0, 255).astype(np.uint8)


def flip_y_axis(image: np.ndarray) -> np.ndarray:
    """Flip image along Y axis.

    Axis convention:
    - 2D image: (y, x), flip axis 0
    - 3D+ image: (..., y, x), flip axis -2
    """
    if image.ndim < 2:
        raise ValueError("flip_y_axis requires at least 2D image input")
    y_axis = image.ndim - 2
    return np.flip(image, axis=y_axis).copy()


def pad_to_shape(image: np.ndarray, target_shape: tuple[int, int, int]) -> np.ndarray:
    """Pad 3D image to target shape with zeros."""
    z, y, x = image.shape
    tz, ty, tx = target_shape
    out = np.zeros(target_shape, dtype=image.dtype)
    out[: min(z, tz), : min(y, ty), : min(x, tx)] = image[: min(z, tz), : min(y, ty), : min(x, tx)]
    return out
