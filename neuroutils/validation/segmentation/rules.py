"""Segmentation validation."""

from __future__ import annotations

import numpy as np

from neuroutils.core.exceptions import ValidationError


def validate_binary_mask(mask: np.ndarray) -> None:
    """Ensure mask is binary-like."""
    unique = np.unique(mask)
    if not set(unique.tolist()).issubset({0, 1}):
        raise ValidationError("Mask must be binary (0/1)")
