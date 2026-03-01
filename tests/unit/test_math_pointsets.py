from __future__ import annotations

import numpy as np
import pytest

from neuroutils.utils.math import (
    memory_safe_min_distances,
    min_distances_between_sets,
)


def test_min_distances_between_sets_one_way() -> None:
    p1 = np.array([[0.0, 0.0], [1.0, 1.0]])
    p2 = np.array([[0.0, 1.0], [2.0, 2.0]])
    (d1,) = min_distances_between_sets(p1, p2, reciprocal=False)
    assert np.allclose(d1, np.array([1.0, 1.0]))


def test_min_distances_between_sets_reciprocal_with_indices() -> None:
    p1 = np.array([[0.0, 0.0], [3.0, 0.0]])
    p2 = np.array([[1.0, 0.0], [10.0, 0.0]])
    d1, d2, i1, i2 = min_distances_between_sets(p1, p2, return_indices=True)
    assert np.allclose(d1, np.array([1.0, 2.0]))
    assert np.allclose(d2, np.array([1.0, 7.0]))
    assert np.array_equal(i1, np.array([0, 0]))
    assert np.array_equal(i2, np.array([0, 1]))


def test_min_distances_between_sets_validates_inputs() -> None:
    with pytest.raises(ValueError):
        min_distances_between_sets(np.empty((0, 3)), np.ones((1, 3)))
    with pytest.raises(ValueError):
        min_distances_between_sets(np.ones((2, 2)), np.ones((2, 3)))


def test_memory_safe_min_distances_alias() -> None:
    p1 = np.array([[0.0, 0.0], [1.0, 0.0]])
    p2 = np.array([[0.0, 1.0], [2.0, 0.0]])
    d1, d2 = memory_safe_min_distances(p1, p2, chunk_size=1)
    assert d1.shape == (2,)
    assert d2.shape == (2,)
