"""Statistical utilities."""

from __future__ import annotations

import math

import numpy as np


def _rankdata_average(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    sorted_vals = values[order]
    ranks = np.zeros(values.shape[0], dtype=np.float64)
    i = 0
    n = values.shape[0]
    while i < n:
        j = i + 1
        while j < n and sorted_vals[j] == sorted_vals[i]:
            j += 1
        avg_rank = 0.5 * (i + 1 + j)
        ranks[order[i:j]] = avg_rank
        i = j
    return ranks


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def my_mannwhitneyu(
    data1: np.ndarray,
    data2: np.ndarray,
    *,
    size_correction: bool = True,
    size_thresh: int = 1000,
    alternative: str = "two-sided",
) -> tuple[float, float, float, str]:
    """Mann-Whitney U with optional size-aware significance annotation."""
    x = np.asarray(data1, dtype=np.float64).ravel()
    y = np.asarray(data2, dtype=np.float64).ravel()
    if x.size == 0 or y.size == 0:
        raise ValueError("Both samples must be non-empty")
    if alternative not in {"two-sided", "less", "greater"}:
        raise ValueError("alternative must be one of: two-sided, less, greater")

    n1, n2 = x.size, y.size
    combined = np.concatenate([x, y])
    ranks = _rankdata_average(combined)
    r1 = float(np.sum(ranks[:n1]))
    u1 = r1 - n1 * (n1 + 1) / 2.0
    cles = u1 / float(n1 * n2)

    mean_u = n1 * n2 / 2.0
    _, counts = np.unique(combined, return_counts=True)
    tie_term = float(np.sum(counts**3 - counts))
    n = n1 + n2
    var_u = n1 * n2 / 12.0 * ((n + 1.0) - tie_term / (n * (n - 1.0))) if n > 1 else 0.0
    if var_u <= 0:
        mw_p = 1.0
    else:
        z = (u1 - mean_u - 0.5 * np.sign(u1 - mean_u)) / math.sqrt(var_u)
        if alternative == "two-sided":
            mw_p = 2.0 * (1.0 - _normal_cdf(abs(z)))
        elif alternative == "greater":
            mw_p = 1.0 - _normal_cdf(z)
        else:
            mw_p = _normal_cdf(z)
        mw_p = float(min(max(mw_p, 0.0), 1.0))

    n_total = n1 + n2
    if n_total > size_thresh and size_correction:
        delta = abs(cles - 0.5)
        if mw_p < 0.001 and delta > 0.1:
            significance = "***"
        elif mw_p < 0.01 and delta > 0.08:
            significance = "**"
        elif mw_p < 0.05 and delta > 0.05:
            significance = "*"
        else:
            significance = "n.s."
    else:
        if mw_p < 0.001:
            significance = "***"
        elif mw_p < 0.01:
            significance = "**"
        elif mw_p < 0.05:
            significance = "*"
        else:
            significance = "n.s."

    return float(u1), float(mw_p), float(cles), significance
