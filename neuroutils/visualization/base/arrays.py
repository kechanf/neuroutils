"""Array utilities for rendering."""

from __future__ import annotations

import numpy as np


def normalize_to_uint8(arr: np.ndarray) -> np.ndarray:
    """Normalize numeric array into uint8 [0, 255]."""
    if arr.size == 0:
        return np.zeros_like(arr, dtype=np.uint8)
    arr_f = arr.astype(np.float32)
    vmin = float(arr_f.min())
    vmax = float(arr_f.max())
    if vmax <= vmin:
        return np.zeros(arr.shape, dtype=np.uint8)
    out = (arr_f - vmin) / (vmax - vmin)
    return np.clip(out * 255.0, 0, 255).astype(np.uint8)


def to_rgb(gray_or_rgb: np.ndarray) -> np.ndarray:
    """Convert 2D grayscale or 3D RGB array to RGB uint8 image."""
    if gray_or_rgb.ndim == 2:
        g = normalize_to_uint8(gray_or_rgb)
        return np.stack([g, g, g], axis=-1)
    if gray_or_rgb.ndim == 3 and gray_or_rgb.shape[2] == 3:
        if gray_or_rgb.dtype == np.uint8:
            return gray_or_rgb.copy()
        return normalize_to_uint8(gray_or_rgb)
    raise ValueError("Expected 2D grayscale or 3D RGB input")
