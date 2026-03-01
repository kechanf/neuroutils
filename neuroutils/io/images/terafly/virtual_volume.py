"""Base virtual-volume type for TeraFly readers."""

from __future__ import annotations


class VirtualVolume:
    """Base volume metadata container."""

    def __init__(self, root_dir: str | None = None, vxl_1: float = 0, vxl_2: float = 0, vxl_3: float = 0):
        self.root_dir = root_dir
        self.VXL_V = vxl_1
        self.VXL_H = vxl_2
        self.VXL_D = vxl_3
        self.ORG_V = self.ORG_H = self.ORG_D = 0.0
        self.DIM_V = self.DIM_H = self.DIM_D = self.DIM_C = 0
        self.BYTESxCHAN = 0
        self.active: list[int] | None = None
        self.n_active = 0
        self.t0 = self.t1 = 0
        self.DIM_T = 1
