"""Direction sampling and angle-constrained fragment rotation utilities."""

from __future__ import annotations

import math

import numpy as np

from neuroutils.transforms.geometry.rotation import (
    rotate_points,
    rotation_matrix_from_vectors,
    unit_vector,
)


def sample_direction_in_cone(
    axis: np.ndarray,
    max_deg: float,
    *,
    rng: np.random.Generator | None = None,
    eps: float = 1e-12,
) -> np.ndarray:
    """Uniformly sample a unit direction within a cone around ``axis``."""
    if max_deg < 0.0 or max_deg > 180.0:
        raise ValueError("max_deg must be in [0, 180]")

    u = unit_vector(axis, eps=eps)
    if u is None:
        raise ValueError("axis must be non-zero")

    gen = rng if rng is not None else np.random.default_rng()
    max_rad = math.radians(max_deg)
    cos_theta = gen.uniform(math.cos(max_rad), 1.0)
    sin_theta = math.sqrt(max(0.0, 1.0 - cos_theta * cos_theta))
    psi = gen.uniform(0.0, 2.0 * math.pi)

    if abs(u[0]) < 0.9:
        tmp = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    else:
        tmp = np.array([0.0, 1.0, 0.0], dtype=np.float64)
    e1 = unit_vector(np.cross(u, tmp), eps=eps)
    if e1 is None:
        e1 = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    e2 = unit_vector(np.cross(u, e1), eps=eps)
    if e2 is None:
        e2 = np.array([0.0, 1.0, 0.0], dtype=np.float64)

    sampled = cos_theta * u + sin_theta * (math.cos(psi) * e1 + math.sin(psi) * e2)
    out = unit_vector(sampled, eps=eps)
    if out is None:
        raise RuntimeError("failed to sample direction in cone")
    return out


def rotate_fragment_points_to_match_angle(
    points: np.ndarray,
    *,
    base_point: np.ndarray,
    fragment_root_point: np.ndarray,
    reference_direction: np.ndarray,
    max_deg: float,
    rng: np.random.Generator | None = None,
    eps: float = 1e-12,
) -> np.ndarray:
    """Rotate fragment points so the root direction lies within a cone constraint."""
    base = np.asarray(base_point, dtype=np.float64).reshape(3)
    root = np.asarray(fragment_root_point, dtype=np.float64).reshape(3)
    current_dir = unit_vector(root - base, eps=eps)
    if current_dir is None:
        return np.asarray(points, dtype=np.float64).copy()

    target_dir = sample_direction_in_cone(
        axis=np.asarray(reference_direction, dtype=np.float64),
        max_deg=max_deg,
        rng=rng,
        eps=eps,
    )
    rot = rotation_matrix_from_vectors(current_dir, target_dir, eps=eps)
    if rot is None:
        return np.asarray(points, dtype=np.float64).copy()
    return rotate_points(points, center=base, rotation_matrix=rot)
