"""Tile metadata helpers."""

from __future__ import annotations


def tile_resolution_um(xy_nm: float = 300.0, z_nm: float = 1000.0) -> tuple[float, float]:
    """Return XY and Z resolution in micrometers."""
    return (xy_nm / 1000.0, z_nm / 1000.0)
