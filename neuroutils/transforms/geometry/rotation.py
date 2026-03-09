"""Rotation-related geometry helpers."""

from __future__ import annotations

import math

import numpy as np


def random_rotation_matrix(rng: np.random.Generator | None = None) -> np.ndarray:
    """Sample a proper rotation matrix from SO(3) via QR decomposition."""
    gen = rng if rng is not None else np.random.default_rng()
    h = gen.normal(size=(3, 3))
    q, _ = np.linalg.qr(h)
    if np.linalg.det(q) < 0:
        q[:, 0] = -q[:, 0]
    return q.astype(np.float64, copy=False)


def unit_vector(v: np.ndarray, *, eps: float = 1e-12) -> np.ndarray | None:
    """Normalize a vector; return ``None`` for near-zero norm."""
    arr = np.asarray(v, dtype=np.float64)
    n = float(np.linalg.norm(arr))
    if n < eps:
        return None
    return arr / n


def rotation_matrix_from_vectors(
    src: np.ndarray,
    dst: np.ndarray,
    *,
    eps: float = 1e-12,
) -> np.ndarray | None:
    """Compute Rodrigues rotation matrix that maps ``src`` direction to ``dst``."""
    v = unit_vector(src, eps=eps)
    w = unit_vector(dst, eps=eps)
    if v is None or w is None:
        return None

    c = float(np.clip(np.dot(v, w), -1.0, 1.0))
    if c > 1.0 - eps:
        return np.eye(3, dtype=np.float64)

    if c < -1.0 + eps:
        axis = np.cross(v, np.array([1.0, 0.0, 0.0], dtype=np.float64))
        if np.linalg.norm(axis) < eps:
            axis = np.cross(v, np.array([0.0, 1.0, 0.0], dtype=np.float64))
        axis = unit_vector(axis, eps=eps)
        if axis is None:
            return np.eye(3, dtype=np.float64)
        x, y, z = axis
        return np.array(
            [
                [2 * x * x - 1, 2 * x * y, 2 * x * z],
                [2 * x * y, 2 * y * y - 1, 2 * y * z],
                [2 * x * z, 2 * y * z, 2 * z * z - 1],
            ],
            dtype=np.float64,
        )

    k = np.cross(v, w)
    s = float(np.linalg.norm(k))
    if s < eps:
        return np.eye(3, dtype=np.float64)
    k = k / s
    x, y, z = k
    kx = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]], dtype=np.float64)
    i = np.eye(3, dtype=np.float64)
    theta = math.acos(c)
    return i + math.sin(theta) * kx + (1.0 - math.cos(theta)) * (kx @ kx)


def rotate_points(
    points: np.ndarray,
    *,
    center: np.ndarray,
    rotation_matrix: np.ndarray,
) -> np.ndarray:
    """Rigidly rotate 3D points around ``center`` with a 3x3 matrix."""
    pts = np.asarray(points, dtype=np.float64)
    c = np.asarray(center, dtype=np.float64).reshape(1, 3)
    r = np.asarray(rotation_matrix, dtype=np.float64)
    if pts.ndim != 2 or pts.shape[1] != 3:
        raise ValueError("points must have shape (N,3)")
    if r.shape != (3, 3):
        raise ValueError("rotation_matrix must have shape (3,3)")
    return ((pts - c) @ r.T) + c
