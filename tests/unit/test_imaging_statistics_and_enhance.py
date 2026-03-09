from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from neuroutils.imaging.preprocess import (
    crop_nonzero_mask,
    do_gamma,
    extend_skel_to_boundary,
    gamma_correction,
    get_longest_skeleton,
    get_mip_image,
    histogram_equalize,
    image_histeq,
    mip,
    montage_images_for_folder,
)
from neuroutils.utils.filesystem import get_tera_res_paths


def test_mip_and_crop_nonzero_mask() -> None:
    img = np.arange(2 * 3 * 4, dtype=np.uint8).reshape(2, 3, 4)
    out = mip(img, axis=0, mode="max")
    assert out.shape == (3, 4)

    mask = np.zeros((5, 6, 7), dtype=np.uint8)
    mask[2, 3, 4] = 1
    sub, bounds = crop_nonzero_mask(mask, pad=1)
    assert sub.shape == (3, 3, 3)
    assert bounds == (1, 4, 2, 5, 3, 6)


def test_histogram_equalize_and_gamma() -> None:
    img = np.array([[0.0, 0.5], [0.75, 1.0]], dtype=np.float32)
    eq, cdf = histogram_equalize(img)
    assert eq.shape == img.shape
    assert cdf.ndim == 1
    gm = gamma_correction(img, gamma=2.0, normalize=False)
    assert np.all(gm >= 0)
    gm2 = do_gamma(img, gamma=2.0, normalize=False)
    assert np.allclose(gm, gm2)
    eq2, _ = image_histeq(img, number_bins=16)
    assert eq2.shape == img.shape
    assert np.array_equal(get_mip_image(img[None, ...], axis=0, mode="MAX"), img)


def test_get_tera_res_paths(tmp_path: Path) -> None:
    (tmp_path / "RES(32x32x32)").mkdir()
    (tmp_path / "RES(8x8x8)").mkdir()
    (tmp_path / "RES(16x16x16)").mkdir()
    ordered = get_tera_res_paths(tmp_path, bracket_escape=False)
    assert isinstance(ordered, list)
    assert ordered[0].endswith("RES(8x8x8)")
    top = get_tera_res_paths(tmp_path, res_ids=-1, bracket_escape=False)
    assert isinstance(top, str) and top.endswith("RES(32x32x32)")


def test_clahe_optional_dependency() -> None:
    try:
        __import__("skimage")
    except Exception:
        pytest.skip("skimage unavailable in current environment")
    from neuroutils.imaging.preprocess import clahe_enhance

    img = np.linspace(0, 1, 32 * 32, dtype=np.float32).reshape(32, 32)
    out = clahe_enhance(img, kernel_size=8, clip_limit=0.01)
    assert out.shape == img.shape


def test_montage_and_skeleton_helpers(tmp_path: Path) -> None:
    pil = pytest.importorskip("PIL")
    if pil is None:
        return
    from PIL import Image

    for i in range(3):
        img = Image.fromarray(np.ones((8, 8), dtype=np.uint8) * (i + 1) * 50)
        img.save(tmp_path / f"{i}.png")
    outs = montage_images_for_folder(tmp_path, sw=2, sh=2, prefix="t")
    assert len(outs) >= 1 and outs[0].exists()

    scipy = pytest.importorskip("scipy")
    skimage = pytest.importorskip("skimage")
    if scipy is None or skimage is None:
        return
    mask = np.zeros((32, 32), dtype=np.uint8)
    mask[8:24, 15:17] = 1
    skel, path = get_longest_skeleton(mask, is_3D=False, extend_to_boundary=True, smoothing=False)
    assert skel.ndim == 2
    assert path.ndim == 2 and path.shape[1] == 2

    boundaries = np.argwhere(mask > 0)
    ext = extend_skel_to_boundary(boundaries, path, is_start=True)
    assert ext.shape[1] == 2
