from __future__ import annotations

import numpy as np

from neuroutils.transforms.geometry import (
    random_rotation_matrix,
    rotate_fragment_points_to_match_angle,
    rotation_matrix_from_vectors,
    sample_direction_in_cone,
    unit_vector,
)


def test_random_rotation_matrix_properties() -> None:
    rng = np.random.default_rng(123)
    r = random_rotation_matrix(rng)
    should_be_i = r.T @ r
    assert np.allclose(should_be_i, np.eye(3), atol=1e-8)
    assert np.isclose(np.linalg.det(r), 1.0, atol=1e-8)


def test_sample_direction_in_cone_respects_max_angle() -> None:
    rng = np.random.default_rng(1)
    axis = np.array([0.0, 0.0, 1.0], dtype=np.float64)
    max_deg = 35.0
    for _ in range(100):
        d = sample_direction_in_cone(axis, max_deg, rng=rng)
        cosang = np.clip(float(np.dot(d, axis)), -1.0, 1.0)
        ang = np.degrees(np.arccos(cosang))
        assert ang <= max_deg + 1e-8


def test_rotation_matrix_from_vectors_maps_direction() -> None:
    src = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    dst = np.array([0.0, 1.0, 0.0], dtype=np.float64)
    r = rotation_matrix_from_vectors(src, dst)
    assert r is not None
    out = unit_vector(r @ src)
    assert out is not None
    assert np.allclose(out, unit_vector(dst), atol=1e-8)


def test_rotate_fragment_points_to_match_angle() -> None:
    points = np.array([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]], dtype=np.float64)
    base = np.array([0.0, 0.0, 0.0], dtype=np.float64)
    root = points[0]
    ref = np.array([0.0, 1.0, 0.0], dtype=np.float64)
    max_deg = 25.0
    out = rotate_fragment_points_to_match_angle(
        points,
        base_point=base,
        fragment_root_point=root,
        reference_direction=ref,
        max_deg=max_deg,
        rng=np.random.default_rng(42),
    )
    new_dir = unit_vector(out[0] - base)
    assert new_dir is not None
    cosang = np.clip(float(np.dot(new_dir, unit_vector(ref))), -1.0, 1.0)
    ang = np.degrees(np.arccos(cosang))
    assert ang <= max_deg + 1e-8
