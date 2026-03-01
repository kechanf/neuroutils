"""TeraFly metadata constants."""

from __future__ import annotations

from dataclasses import dataclass

MDATA_BIN_FILE_NAME = "mdata.bin"
MDATA_BIN_FILE_VERSION = 2


@dataclass(frozen=True, slots=True)
class Rect:
    """Axis-aligned 2D rectangle."""

    H0: int
    V0: int
    H1: int
    V1: int
