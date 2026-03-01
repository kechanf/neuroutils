"""Image projection utilities."""

from __future__ import annotations

import numpy as np


def project_volume(volume: np.ndarray, projection: str = "xy") -> np.ndarray:
    """Maximum-intensity projection for 3D volume or passthrough for 2D."""
    if volume.ndim == 2:
        return volume
    if volume.ndim != 3:
        raise ValueError("Volume must be 2D or 3D")
    axis_map = {"xy": 0, "xz": 1, "yz": 2}
    axis = axis_map.get(projection)
    if axis is None:
        raise ValueError(f"Unsupported projection: {projection}")
    return np.max(volume, axis=axis)
