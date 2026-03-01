from __future__ import annotations

from pathlib import Path

import pytest

from neuroutils.io.images.terafly import Block, Rect, TiledVolume


def test_block_intersects_rect_and_segm() -> None:
    b = Block.__new__(Block)
    b.ABS_H = 10
    b.ABS_V = 20
    b.WIDTH = 100
    b.HEIGHT = 80
    b.N_BLOCKS = 3
    b.BLOCK_ABS_D = [0, 50, 100]
    b.BLOCK_SIZE = [50, 50, 50]
    b.DEPTH = 150

    inter = b.intersects_rect(Rect(0, 0, 40, 40))
    assert inter is not None
    assert inter.H0 == 10 and inter.V0 == 20

    segm = b.intersects_segm(10, 120)
    assert segm is not None
    assert segm.ind0 == 0 and segm.ind1 == 2


def test_tiled_volume_missing_mdata(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        TiledVolume(tmp_path)
