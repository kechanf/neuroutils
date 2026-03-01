"""nnUNet adapter boundary."""

from __future__ import annotations

import numpy as np


def predict_segmentation_stub(volume: np.ndarray) -> np.ndarray:
    """Dependency-free placeholder segmentation predictor."""
    threshold = float(np.percentile(volume, 95))
    return (volume >= threshold).astype(np.uint8)
