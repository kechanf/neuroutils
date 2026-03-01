from __future__ import annotations

import numpy as np

from neuroutils.ml import (
    clip_outliers,
    normalize_features_by_sum,
    normalize_features_minmax,
    standardize_features,
    whitening,
)


def test_whitening_basic() -> None:
    x = np.array([[1.0, 2.0], [3.0, 6.0], [5.0, 10.0]])
    y = whitening(x)
    assert np.allclose(np.mean(y, axis=0), np.array([0.0, 0.0]), atol=1e-6)


def test_clip_outliers_numpy() -> None:
    x = np.array([[1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [4.0, 5.0], [100.0, 6.0]])
    y = clip_outliers(x, col_ids=[0], inplace=False)
    assert y.shape == x.shape
    assert y[-1, 0] < 100.0


def test_standardize_minmax_and_sum() -> None:
    x = np.array([[1.0, 3.0], [2.0, 4.0], [3.0, 5.0]])
    z = standardize_features(x, feat_names=[0, 1], inplace=False)
    assert z.shape == x.shape
    m = normalize_features_minmax(x, feat_names=[0, 1], inplace=False)
    assert np.all(m >= 0) and np.all(m <= 1)
    s = normalize_features_by_sum(x, feat_names=[0, 1], inplace=False)
    assert np.allclose(np.sum(s, axis=1), np.ones(x.shape[0]))
