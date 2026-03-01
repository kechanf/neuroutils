"""TeraFly tiled-volume reader."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np

from neuroutils.io.images.io import load_image
from neuroutils.io.images.terafly.block import Block
from neuroutils.io.images.terafly.config import MDATA_BIN_FILE_NAME, MDATA_BIN_FILE_VERSION, Rect
from neuroutils.io.images.terafly.virtual_volume import VirtualVolume


class TiledVolume(VirtualVolume):
    """Minimal TeraFly tiled volume reader."""

    def __init__(self, root_dir: str | Path):
        super().__init__(str(root_dir))
        self.VXL_1 = self.VXL_2 = self.VXL_3 = 0.0
        self.N_ROWS = self.N_COLS = 0
        self.BLOCKS: list[list[Block]] = []
        self.reference_system_first = 0
        self.reference_system_second = 0
        self.reference_system_third = 0

        mdata = Path(root_dir) / MDATA_BIN_FILE_NAME
        if not mdata.is_file():
            raise FileNotFoundError(f"Unable to find metadata file: {mdata}")
        self.load(mdata)
        self.init_channels()

    def load(self, mdata_filepath: str | Path) -> None:
        with Path(mdata_filepath).open("rb") as f:
            mdata_version_read = struct.unpack("f", f.read(4))[0]
            if mdata_version_read != MDATA_BIN_FILE_VERSION:
                f.seek(0)
                str_size = struct.unpack("H", f.read(2))[0]
                _ = f.read(str_size)
            (
                self.reference_system_first,
                self.reference_system_second,
                self.reference_system_third,
                self.VXL_1,
                self.VXL_2,
                self.VXL_3,
                self.VXL_V,
                self.VXL_H,
                self.VXL_D,
                self.ORG_V,
                self.ORG_H,
                self.ORG_D,
                self.DIM_V,
                self.DIM_H,
                self.DIM_D,
                self.N_ROWS,
                self.N_COLS,
            ) = struct.unpack("iiifffffffffIIIHH", f.read(64))
            self.BLOCKS = [[Block(self, i, j, f) for j in range(self.N_COLS)] for i in range(self.N_ROWS)]

    def init_channels(self) -> None:
        self.DIM_C = self.BLOCKS[0][0].N_CHANS
        self.BYTESxCHAN = int(self.BLOCKS[0][0].N_BYTESxCHAN)
        self.n_active = self.DIM_C
        self.active = list(range(self.n_active))

    def load_subvolume(
        self,
        *,
        v0: int = -1,
        v1: int = -1,
        h0: int = -1,
        h1: int = -1,
        d0: int = -1,
        d1: int = -1,
    ) -> np.ndarray:
        v0, h0, d0 = max(0, v0), max(0, h0), max(0, d0)
        v1 = v1 if 0 <= v1 <= self.DIM_V else self.DIM_V
        h1 = h1 if 0 <= h1 <= self.DIM_H else self.DIM_H
        d1 = d1 if 0 <= d1 <= self.DIM_D else self.DIM_D
        if not (v1 > v0 and h1 > h0 and d1 > d0):
            raise ValueError("Invalid subvolume bounds")

        sbv_height, sbv_width, sbv_depth = v1 - v0, h1 - h0, d1 - d0
        subvol_area = Rect(h0, v0, h1, v1)
        first_time = True
        segm = self.BLOCKS[0][0].intersects_segm(d0, d1)
        if segm is None:
            raise ValueError("Depth interval out of range")

        buffer: np.ndarray | None = None
        for row in range(self.N_ROWS):
            for col in range(self.N_COLS):
                block = self.BLOCKS[row][col]
                inter = block.intersects_rect(subvol_area)
                if inter is None:
                    continue
                for k in range(segm.ind0, segm.ind1 + 1):
                    if first_time:
                        first_time = False
                        if self.DIM_C != 1:
                            raise ValueError("Only single-channel volumes are supported")
                        if self.BYTESxCHAN == 1:
                            dt = np.uint8
                        elif self.BYTESxCHAN == 2:
                            dt = np.uint16
                        elif self.BYTESxCHAN == 4:
                            dt = np.float32
                        else:
                            raise ValueError("Unsupported channel datatype")
                        buffer = np.zeros((sbv_depth, sbv_height, sbv_width), dtype=dt)

                    assert buffer is not None
                    slice_path = Path(self.root_dir or ".") / str(block.DIR_NAME) / block.FILENAMES[k]

                    sv0 = 0 if v0 < inter.V0 else v0 - block.ABS_V
                    sv1 = block.HEIGHT if v1 > inter.V1 else v1 - block.ABS_V
                    sh0 = 0 if h0 < inter.H0 else h0 - block.ABS_H
                    sh1 = block.WIDTH if h1 > inter.H1 else h1 - block.ABS_H
                    sd0 = 0 if d0 < block.BLOCK_ABS_D[k] else d0 - block.BLOCK_ABS_D[k]
                    sd1 = (
                        block.BLOCK_SIZE[k]
                        if d1 > block.BLOCK_ABS_D[k] + block.BLOCK_SIZE[k]
                        else d1 - block.BLOCK_ABS_D[k]
                    )

                    bv0 = 0 if v0 > inter.V0 else inter.V0 - v0
                    bh0 = 0 if h0 > inter.H0 else inter.H0 - h0
                    bd0 = 0 if d0 > block.BLOCK_ABS_D[k] else block.BLOCK_ABS_D[k] - d0

                    if "NULL.tif" in str(slice_path):
                        continue
                    img = load_image(slice_path, flip_tif=False)
                    if img.ndim == 4:
                        img = img[0]
                    buffer[bd0 : bd0 + sd1 - sd0, bv0 : bv0 + sv1 - sv0, bh0 : bh0 + sh1 - sh0] = img[
                        sd0:sd1, sv0:sv1, sh0:sh1
                    ]

        if buffer is None:
            raise ValueError("No intersecting blocks found")
        return buffer
