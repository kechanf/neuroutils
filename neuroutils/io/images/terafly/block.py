"""TeraFly block metadata and intersection helpers."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import BinaryIO

from neuroutils.io.images.terafly.config import Rect
from neuroutils.io.images.terafly.virtual_volume import VirtualVolume


@dataclass(frozen=True, slots=True)
class Segm:
    D0: int
    D1: int
    ind0: int
    ind1: int


class Block(VirtualVolume):
    """One tiled block descriptor."""

    def __init__(self, container: VirtualVolume, row_index: int, col_index: int, file: BinaryIO):
        super().__init__()
        self.CONTAINER = container
        self.ROW_INDEX = row_index
        self.COL_INDEX = col_index

        self.DIR_NAME: str | None = None
        self.FILENAMES: list[str] = []
        self.HEIGHT = self.WIDTH = self.DEPTH = 0
        self.N_BLOCKS = 0
        self.N_CHANS = 0
        self.N_BYTESxCHAN = 0
        self.ABS_V = self.ABS_H = 0
        self.BLOCK_SIZE: list[int] = []
        self.BLOCK_ABS_D: list[int] = []

        self.unbinarize_from(file)

    def unbinarize_from(self, file: BinaryIO) -> None:
        (
            self.HEIGHT,
            self.WIDTH,
            self.DEPTH,
            self.N_BLOCKS,
            self.N_CHANS,
            self.ABS_V,
            self.ABS_H,
            str_size,
        ) = struct.unpack("IIIIIiiH", file.read(30))
        self.DIR_NAME = file.read(str_size).decode("utf-8").rstrip("\x00")
        self.FILENAMES = []
        self.BLOCK_SIZE = []
        self.BLOCK_ABS_D = []
        for _ in range(self.N_BLOCKS):
            str_size = struct.unpack("H", file.read(2))[0]
            self.FILENAMES.append(file.read(str_size).decode("utf-8").rstrip("\x00"))
            self.BLOCK_SIZE.append(struct.unpack("I", file.read(4))[0])
            self.BLOCK_ABS_D.append(struct.unpack("i", file.read(4))[0])
        self.N_BYTESxCHAN = struct.unpack("I", file.read(4))[0]

    def intersects_segm(self, d0: int, d1: int) -> Segm | None:
        if self.N_BLOCKS == 0:
            return None
        if d0 >= self.BLOCK_ABS_D[self.N_BLOCKS - 1] + self.BLOCK_SIZE[self.N_BLOCKS - 1] or d1 <= 0:
            return None
        i0 = 0
        while i0 < self.N_BLOCKS - 1:
            if d0 < self.BLOCK_ABS_D[i0 + 1]:
                break
            i0 += 1
        i1 = self.N_BLOCKS - 1
        while i1 > 0:
            if d1 > self.BLOCK_ABS_D[i1]:
                break
            i1 -= 1
        return Segm(max(d0, 0), min(d1, self.DEPTH), i0, i1)

    def intersects_rect(self, area: Rect) -> Rect | None:
        if (
            area.H0 < self.ABS_H + self.WIDTH
            and area.H1 > self.ABS_H
            and area.V0 < self.ABS_V + self.HEIGHT
            and area.V1 > self.ABS_V
        ):
            return Rect(
                max(self.ABS_H, area.H0),
                max(self.ABS_V, area.V0),
                min(self.ABS_H + self.WIDTH, area.H1),
                min(self.ABS_V + self.HEIGHT, area.V1),
            )
        return None
