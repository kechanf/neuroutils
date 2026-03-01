"""Angle and numeric decomposition helpers."""

from __future__ import annotations

import math

import numpy as np


def get_exponent_and_mantissa(value: float, ndigits: int = 2) -> tuple[int | None, float]:
    """Return base-10 exponent and mantissa for a float value."""
    if value == 0:
        return None, 0.0
    exponent = math.floor(math.log10(abs(value)))
    mantissa = round(abs(value) * 10 ** (-exponent), ndigits)
    return exponent, mantissa


def included_angles_from_vectors(
    vecs1: np.ndarray,
    vecs2: np.ndarray,
    *,
    return_rad: bool = False,
    return_cos: bool = False,
    spacing: tuple[float, ...] | None = None,
    epsilon: float = 1e-7,
) -> np.ndarray:
    """Compute included angles between vector arrays."""
    v1 = np.asarray(vecs1, dtype=np.float64)
    v2 = np.asarray(vecs2, dtype=np.float64)
    if v1.ndim == 1:
        v1 = v1.reshape(1, -1)
    if v2.ndim == 1:
        v2 = v2.reshape(1, -1)
    if v1.shape != v2.shape:
        raise ValueError("vecs1 and vecs2 must have same shape")
    if spacing is not None:
        s = np.asarray(spacing, dtype=np.float64).reshape(1, -1)
        if s.shape[1] != v1.shape[1]:
            raise ValueError("spacing dimensionality mismatch")
        v1 = v1 * s
        v2 = v2 * s

    inner = np.sum(v1 * v2, axis=1)
    norms = np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1)
    cos_v = inner / (norms + epsilon)
    cos_v = np.clip(cos_v, -1.0, 1.0)

    if return_cos:
        return cos_v
    rad = np.arccos(cos_v)
    if return_rad:
        return rad
    return np.rad2deg(rad)


def included_angles_from_coords(
    anchors: np.ndarray,
    coords1: np.ndarray,
    coords2: np.ndarray,
    *,
    return_rad: bool = False,
    return_cos: bool = False,
    spacing: tuple[float, ...] | None = None,
    epsilon: float = 1e-7,
) -> np.ndarray:
    """Compute included angles between anchor->coords1 and anchor->coords2."""
    a = np.asarray(anchors, dtype=np.float64)
    c1 = np.asarray(coords1, dtype=np.float64)
    c2 = np.asarray(coords2, dtype=np.float64)
    return included_angles_from_vectors(
        c1 - a,
        c2 - a,
        return_rad=return_rad,
        return_cos=return_cos,
        spacing=spacing,
        epsilon=epsilon,
    )
