"""Feature preprocessing utilities."""

from __future__ import annotations

from typing import Any

import numpy as np


def whitening(features: np.ndarray, epsilon: float = 1e-9) -> np.ndarray:
    """Standard score normalization by column."""
    arr = np.asarray(features, dtype=np.float64)
    return (arr - arr.mean(axis=0)) / (arr.std(axis=0) + epsilon)


def _to_numpy_table(table: Any) -> tuple[np.ndarray, bool]:
    """Return table as numpy array and whether input looked like pandas DataFrame."""
    if hasattr(table, "to_numpy") and hasattr(table, "iloc"):
        return np.asarray(table.to_numpy(dtype=np.float64), dtype=np.float64), True
    return np.asarray(table, dtype=np.float64), False


def _assign_back(table: Any, values: np.ndarray, columns: list[Any] | None, inplace: bool) -> Any:
    if hasattr(table, "iloc") and hasattr(table, "copy"):
        target = table if inplace else table.copy()
        if columns is None:
            target.iloc[:, :] = values
        else:
            target.loc[:, columns] = values
        return None if inplace else target
    if inplace:
        if isinstance(table, np.ndarray):
            table[...] = values
            return None
        raise TypeError("inplace=True requires numpy array or pandas-like DataFrame")
    return values


def clip_outliers(table: Any, col_ids: list[int] | np.ndarray | None = None, *, inplace: bool = True) -> Any:
    """Clip outliers using IQR rule on selected columns."""
    arr, is_df = _to_numpy_table(table)
    n_cols = arr.shape[1]
    ids = np.arange(n_cols) if col_ids is None else np.asarray(col_ids, dtype=int)
    sub = arr[:, ids]
    q25 = np.percentile(sub, 25, axis=0)
    q75 = np.percentile(sub, 75, axis=0)
    iqr = q75 - q25
    lower = q25 - 1.5 * iqr
    upper = q75 + 1.5 * iqr
    clipped = np.clip(sub, lower, upper)

    out = arr.copy()
    out[:, ids] = clipped
    if is_df:
        cols = [table.columns[i] for i in ids]
        return _assign_back(table, clipped, cols, inplace)
    return _assign_back(table, out, None, inplace)


def clip_outliners(table: Any, col_ids: list[int] | np.ndarray | None = None) -> None:
    """Backward-compatible alias with original typo name."""
    _ = clip_outliers(table, col_ids=col_ids, inplace=True)


def standardize_features(
    table: Any,
    feat_names: list[Any],
    epsilon: float = 1e-8,
    *,
    inplace: bool = True,
) -> Any:
    """Column-wise z-score normalization."""
    if hasattr(table, "loc"):
        vals = np.asarray(table.loc[:, feat_names].to_numpy(dtype=np.float64), dtype=np.float64)
        vals = (vals - vals.mean(axis=0)) / (vals.std(axis=0) + epsilon)
        return _assign_back(table, vals, feat_names, inplace)
    arr = np.asarray(table, dtype=np.float64)
    ids = np.asarray(feat_names, dtype=int)
    out = arr.copy()
    sub = out[:, ids]
    out[:, ids] = (sub - sub.mean(axis=0)) / (sub.std(axis=0) + epsilon)
    return _assign_back(table, out, None, inplace)


def normalize_features_minmax(
    table: Any,
    feat_names: list[Any],
    epsilon: float = 1e-8,
    *,
    inplace: bool = True,
) -> Any:
    """Column-wise min-max normalization."""
    if hasattr(table, "loc"):
        vals = np.asarray(table.loc[:, feat_names].to_numpy(dtype=np.float64), dtype=np.float64)
        vals = (vals - vals.min(axis=0)) / (vals.max(axis=0) - vals.min(axis=0) + epsilon)
        return _assign_back(table, vals, feat_names, inplace)
    arr = np.asarray(table, dtype=np.float64)
    ids = np.asarray(feat_names, dtype=int)
    out = arr.copy()
    sub = out[:, ids]
    out[:, ids] = (sub - sub.min(axis=0)) / (sub.max(axis=0) - sub.min(axis=0) + epsilon)
    return _assign_back(table, out, None, inplace)


def normalize_features_by_sum(
    table: Any,
    feat_names: list[Any],
    epsilon: float = 1e-8,
    *,
    inplace: bool = True,
) -> Any:
    """Row-wise normalize selected features by row sum."""
    if hasattr(table, "loc"):
        vals = np.asarray(table.loc[:, feat_names].to_numpy(dtype=np.float64), dtype=np.float64)
        vals = vals / (vals.sum(axis=1, keepdims=True) + epsilon)
        return _assign_back(table, vals, feat_names, inplace)
    arr = np.asarray(table, dtype=np.float64)
    ids = np.asarray(feat_names, dtype=int)
    out = arr.copy()
    sub = out[:, ids]
    out[:, ids] = sub / (sub.sum(axis=1, keepdims=True) + epsilon)
    return _assign_back(table, out, None, inplace)
