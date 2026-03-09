"""Image projection utilities."""

from __future__ import annotations

import numpy as np

from neuroutils.visualization.base import normalize_to_uint8


def project_volume(volume: np.ndarray, projection: str = "xy") -> np.ndarray:
    """Maximum-intensity projection with uint8 normalization.

    - 2D input: normalize directly to uint8 [0,255].
    - 3D input: do MIP first, then normalize to uint8 [0,255].
    """
    arr = np.asarray(volume)
    if arr.ndim == 2:
        return normalize_to_uint8(arr)
    if arr.ndim != 3:
        raise ValueError("Volume must be 2D or 3D")
    axis_map = {"xy": 0, "xz": 1, "yz": 2}
    axis = axis_map.get(projection)
    if axis is None:
        raise ValueError(f"Unsupported projection: {projection}")
    mip = np.max(arr, axis=axis)
    return normalize_to_uint8(mip)
