"""Point-set distance utilities."""

from __future__ import annotations

import math

import numpy as np


def _validate_point_set(points: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(points, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be a 2D array of shape (n_points, n_dims)")
    if arr.shape[0] == 0:
        raise ValueError(f"{name} must contain at least one point")
    return arr


def _min_dists_one_way(
    src: np.ndarray,
    dst: np.ndarray,
    *,
    chunk_size: int = 4096,
    return_indices: bool = False,
) -> tuple[np.ndarray, np.ndarray | None]:
    """Compute nearest-neighbor distance from each src point to dst points."""
    n_src = src.shape[0]
    dists = np.full(n_src, np.inf, dtype=np.float64)
    indices = np.full(n_src, -1, dtype=np.int64) if return_indices else None

    n_chunks = int(math.ceil(n_src / float(chunk_size)))
    for chunk_id in range(n_chunks):
        start = chunk_id * chunk_size
        end = min((chunk_id + 1) * chunk_size, n_src)
        src_chunk = src[start:end]
        diff = src_chunk[:, None, :] - dst[None, :, :]
        dist2 = np.sum(diff * diff, axis=2)
        local_idx = np.argmin(dist2, axis=1)
        local_dist = np.sqrt(dist2[np.arange(dist2.shape[0]), local_idx])
        dists[start:end] = local_dist
        if indices is not None:
            indices[start:end] = local_idx

    return dists, indices


def min_distances_between_sets(
    points1: np.ndarray,
    points2: np.ndarray,
    *,
    reciprocal: bool = True,
    chunk_size: int = 4096,
    return_indices: bool = False,
) -> tuple[np.ndarray, ...]:
    """Nearest-neighbor distances between two point sets.

    Returns one-way distances by default (points1 -> points2). If ``reciprocal``
    is True, also returns points2 -> points1.
    """
    p1 = _validate_point_set(points1, "points1")
    p2 = _validate_point_set(points2, "points2")
    if p1.shape[1] != p2.shape[1]:
        raise ValueError("points1 and points2 must have same dimensionality")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")

    d1, i1 = _min_dists_one_way(p1, p2, chunk_size=chunk_size, return_indices=return_indices)
    if not reciprocal:
        if return_indices:
            return d1, i1
        return (d1,)

    d2, i2 = _min_dists_one_way(p2, p1, chunk_size=chunk_size, return_indices=return_indices)
    if return_indices:
        return d1, d2, i1, i2
    return d1, d2


def memory_safe_min_distances(
    points1: np.ndarray,
    points2: np.ndarray,
    *,
    chunk_size: int = 4096,
    return_indices: bool = False,
) -> tuple[np.ndarray, ...]:
    """Backward-style alias for reciprocal nearest-neighbor distance computation."""
    return min_distances_between_sets(
        points1,
        points2,
        reciprocal=True,
        chunk_size=chunk_size,
        return_indices=return_indices,
    )


def min_distances_between_two_sets(
    voxels1: np.ndarray,
    voxels2: np.ndarray,
    *,
    topk: int = 1,
    reciprocal: bool = True,
    return_index: bool = False,
    chunk_size: int = 4096,
) -> tuple[np.ndarray, ...]:
    """Compatibility alias with legacy signature."""
    if topk != 1:
        raise ValueError("Only topk=1 is supported")
    return min_distances_between_sets(
        voxels1,
        voxels2,
        reciprocal=reciprocal,
        chunk_size=chunk_size,
        return_indices=return_index,
    )
