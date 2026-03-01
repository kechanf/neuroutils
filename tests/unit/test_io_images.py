from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from neuroutils.io.images import load_image, save_image


def test_load_save_image_npy_roundtrip(tmp_path: Path) -> None:
    arr = np.arange(2 * 3 * 4, dtype=np.uint8).reshape(2, 3, 4)
    p = tmp_path / "x.npy"
    save_image(p, arr)
    out = load_image(p)
    assert np.array_equal(out, arr)


def test_load_save_image_tiff_flip_roundtrip(tmp_path: Path) -> None:
    pytest.importorskip("tifffile")
    arr = np.arange(2 * 4 * 5, dtype=np.uint8).reshape(2, 4, 5)
    p = tmp_path / "x.tif"
    save_image(p, arr, flip_tif=True)
    out = load_image(p, flip_tif=True)
    assert np.array_equal(out, arr)


def test_load_image_unsupported_suffix(tmp_path: Path) -> None:
    p = tmp_path / "x.foo"
    p.write_text("dummy", encoding="utf-8")
    with pytest.raises(ValueError):
        load_image(p)
