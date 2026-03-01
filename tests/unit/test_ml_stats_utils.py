from __future__ import annotations

import numpy as np

from neuroutils.ml import my_mannwhitneyu


def test_my_mannwhitneyu_detects_shift() -> None:
    a = np.array([1, 2, 3, 4, 5], dtype=np.float64)
    b = np.array([10, 11, 12, 13, 14], dtype=np.float64)
    stat, p, cles, sig = my_mannwhitneyu(a, b, size_correction=False)
    assert stat >= 0
    assert 0 <= p <= 1
    assert 0 <= cles <= 1
    assert isinstance(sig, str)
