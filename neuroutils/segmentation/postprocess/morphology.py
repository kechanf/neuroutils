"""Segmentation post-processing."""

from __future__ import annotations

import numpy as np


def threshold_mask(image: np.ndarray, threshold: float) -> np.ndarray:
    """Binary threshold."""
    return (image >= threshold).astype(np.uint8)
