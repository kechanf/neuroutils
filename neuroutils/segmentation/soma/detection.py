"""Soma detection primitives."""

from __future__ import annotations

import numpy as np


def mask_centroid(mask: np.ndarray) -> tuple[float, float, float]:
    """Centroid of non-zero voxels in z,y,x order."""
    coords = np.argwhere(mask > 0)
    if coords.size == 0:
        return (0.0, 0.0, 0.0)
    zyx = coords.mean(axis=0)
    return (float(zyx[0]), float(zyx[1]), float(zyx[2]))


def largest_component_bbox(mask: np.ndarray) -> tuple[int, int, int, int, int, int]:
    """Axis-aligned bbox of all positive voxels."""
    coords = np.argwhere(mask > 0)
    if coords.size == 0:
        return (0, 0, 0, 0, 0, 0)
    mins = coords.min(axis=0)
    maxs = coords.max(axis=0)
    return (int(mins[0]), int(maxs[0]), int(mins[1]), int(maxs[1]), int(mins[2]), int(maxs[2]))
