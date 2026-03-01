"""Spatial autocorrelation utilities."""

from __future__ import annotations

import numpy as np


def _pairwise_dist(coords: np.ndarray) -> np.ndarray:
    diff = coords[:, None, :] - coords[None, :, :]
    return np.sqrt(np.sum(diff * diff, axis=2))


def _build_weights(
    coords: np.ndarray,
    *,
    weight_type: str,
    threshold: float,
    k: int,
) -> np.ndarray:
    n = coords.shape[0]
    dist = _pairwise_dist(coords)
    np.fill_diagonal(dist, np.inf)
    w = np.zeros((n, n), dtype=np.float64)
    if weight_type == "distance":
        w[dist <= threshold] = 1.0
    elif weight_type == "knn":
        if k <= 0:
            raise ValueError("k must be > 0 for knn weights")
        idx = np.argsort(dist, axis=1)[:, :k]
        rows = np.arange(n)[:, None]
        w[rows, idx] = 1.0
    else:
        raise ValueError("weight_type must be 'distance' or 'knn'")
    return w


def _moran_i_single(feat: np.ndarray, w: np.ndarray) -> float:
    x = feat.astype(np.float64)
    x_mean = float(np.mean(x))
    xc = x - x_mean
    w_sum = float(np.sum(w))
    if w_sum <= 0:
        return 0.0
    denom = float(np.sum(xc * xc))
    if denom <= 0:
        return 0.0
    num = float(np.sum(w * (xc[:, None] * xc[None, :])))
    n = x.shape[0]
    return (n / w_sum) * (num / denom)


def moran_i_score(
    coords: np.ndarray,
    feats: np.ndarray,
    *,
    eval_ids: list[int] | None = None,
    reduce_type: str = "average",
    weight_type: str = "distance",
    threshold: float = 0.5,
    k: int = 5,
) -> float | list[float]:
    """Compute Moran's I scores for one or multiple features."""
    c = np.asarray(coords, dtype=np.float64)
    f = np.asarray(feats, dtype=np.float64)
    if c.ndim != 2:
        raise ValueError("coords must be shape (n_samples, n_dims)")
    if f.ndim == 1:
        f = f.reshape(-1, 1)
    if f.ndim != 2:
        raise ValueError("feats must be 1D or 2D")
    if c.shape[0] != f.shape[0]:
        raise ValueError("coords and feats must have same number of samples")

    ids = list(range(f.shape[1])) if eval_ids is None else list(eval_ids)
    w = _build_weights(c, weight_type=weight_type, threshold=threshold, k=k)
    scores = [_moran_i_single(f[:, i], w) for i in ids]

    if reduce_type == "all":
        return scores
    if reduce_type == "max":
        return float(np.max(scores)) if scores else 0.0
    if reduce_type == "average":
        return float(np.mean(scores)) if scores else 0.0
    raise ValueError("reduce_type must be one of: average, max, all")


def moranI_score(
    coords: np.ndarray,
    feats: np.ndarray,
    *,
    eval_ids: list[int] | None = None,
    reduce_type: str = "average",
    weight_type: str = "distance",
    threshold: float = 0.5,
    k: int = 5,
) -> float | list[float]:
    """Compatibility alias for Moran's I."""
    return moran_i_score(
        coords,
        feats,
        eval_ids=eval_ids,
        reduce_type=reduce_type,
        weight_type=weight_type,
        threshold=threshold,
        k=k,
    )
