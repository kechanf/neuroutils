"""V3DRAW image format reader/writer."""

from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

import numpy as np

_FORMAT_KEY = "raw_image_stack_by_hpeng"


def load_v3draw(path: str | Path) -> np.ndarray:
    """Load V3DRAW image as ndarray in (c, z, y, x) compatible shape."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    with p.open("rb") as f:
        filesize = os.path.getsize(p)
        header_len = len(_FORMAT_KEY) + 1 + 2 + 4 * 4
        if filesize < header_len:
            raise ValueError("Invalid v3draw file: too small")
        fmt = f.read(len(_FORMAT_KEY)).decode("utf-8")
        if fmt != _FORMAT_KEY:
            raise ValueError("Invalid v3draw format key")
        endian_code = f.read(1).decode("utf-8")
        if endian_code == "B":
            endian = ">"
        elif endian_code == "L":
            endian = "<"
        else:
            raise ValueError("Invalid endian code in v3draw")

        datatype = struct.unpack(endian + "h", f.read(2))[0]
        if datatype == 1:
            dt = "u1"
        elif datatype == 2:
            dt = "u2"
        elif datatype == 4:
            dt = "f4"
        else:
            raise ValueError("Unsupported datatype in v3draw")

        sx, sy, sz, sc = struct.unpack(endian + "iiii", f.read(4 * 4))
        total = sx * sy * sz * sc
        data = np.frombuffer(f.read(total * datatype), dtype=endian + dt)
        return data.reshape((sc, sz, sy, sx))


def save_v3draw(img: np.ndarray, path: str | Path) -> None:
    """Save ndarray to V3DRAW format."""
    p = Path(path)
    arr = np.asarray(img)
    if arr.ndim < 3 or arr.ndim > 4:
        raise ValueError("Expected 3D or 4D array for v3draw")
    if arr.ndim == 3:
        arr = arr[None, ...]

    with p.open("wb") as f:
        f.write(_FORMAT_KEY.encode("utf-8"))

        byteorder = arr.dtype.byteorder
        if byteorder == "|":
            endian_code = "L" if sys.byteorder == "little" else "B"
        elif byteorder == "<":
            endian_code = "L"
        elif byteorder == ">":
            endian_code = "B"
        else:
            endian_code = "L" if sys.byteorder == "little" else "B"
        f.write(endian_code.encode("utf-8"))
        endian = "<" if endian_code == "L" else ">"

        if arr.dtype == np.uint8:
            datatype = 1
        elif arr.dtype == np.uint16:
            datatype = 2
        elif arr.dtype == np.float32:
            datatype = 4
        else:
            arr = arr.astype(np.float32, copy=False)
            datatype = 4
        f.write(struct.pack(endian + "h", datatype))

        sc, sz, sy, sx = arr.shape
        f.write(struct.pack(endian + "iiii", sx, sy, sz, sc))
        f.write(arr.tobytes(order="C"))
