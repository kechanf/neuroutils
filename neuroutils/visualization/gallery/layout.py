"""Gallery composition helpers."""

from __future__ import annotations

import numpy as np

from neuroutils.visualization.base import to_rgb


def side_by_side(images: list[np.ndarray], padding: int = 8) -> np.ndarray:
    """Stack images horizontally with constant spacing."""
    if not images:
        return np.zeros((1, 1, 3), dtype=np.uint8)
    rgb_images = [to_rgb(img) for img in images]
    h = max(img.shape[0] for img in rgb_images)
    padded: list[np.ndarray] = []
    for img in rgb_images:
        pad_h = h - img.shape[0]
        if pad_h:
            img = np.pad(img, ((0, pad_h), (0, 0), (0, 0)), mode="constant")
        padded.append(img)
    spacer = np.zeros((h, padding, 3), dtype=np.uint8)
    out = padded[0]
    for img in padded[1:]:
        out = np.concatenate([out, spacer, img], axis=1)
    return out
