"""Segmentation overlay rendering."""

from __future__ import annotations

import numpy as np

from neuroutils.visualization.base import to_rgb


def overlay_mask(
    image: np.ndarray,
    mask: np.ndarray,
    color: tuple[int, int, int] = (255, 0, 0),
    alpha: float = 0.35,
) -> np.ndarray:
    """Overlay binary mask onto image."""
    rgb = to_rgb(image).astype(np.float32)
    if mask.shape != rgb.shape[:2]:
        raise ValueError("Mask shape must match image HxW")
    m = mask > 0
    out = rgb.copy()
    out[m, 0] = (1 - alpha) * out[m, 0] + alpha * color[0]
    out[m, 1] = (1 - alpha) * out[m, 1] + alpha * color[1]
    out[m, 2] = (1 - alpha) * out[m, 2] + alpha * color[2]
    return np.clip(out, 0, 255).astype(np.uint8)
