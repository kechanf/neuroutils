from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from neuroutils.imaging import normalize_tiff_to_uint8_uncompressed


def test_normalize_tiff_to_uint8_uncompressed(tmp_path: Path) -> None:
    tiff = pytest.importorskip("tifffile")
    src = tmp_path / "in.tif"
    out = tmp_path / "out.tif"

    arr = np.linspace(100.0, 400.0, num=2 * 3 * 5, dtype=np.float32).reshape(2, 3, 5)
    tiff.imwrite(src, arr, compression=None)

    normalize_tiff_to_uint8_uncompressed(src, out)

    with tiff.TiffFile(out) as tf:
        got = tf.asarray(maxworkers=1)
        assert len(tf.pages) == 2
        assert tf.pages[0].compression == 1
    assert got.dtype == np.uint8
    assert int(got.min()) == 0
    assert int(got.max()) == 255
