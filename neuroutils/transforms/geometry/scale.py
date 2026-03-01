"""Geometry transforms."""

from __future__ import annotations

import math

from neuroutils.core.types import SWCNode


def _radius_scale_factor(sx: float, sy: float, sz: float, mode: str) -> float:
    if mode == "xy_geometric_mean":
        return math.sqrt(abs(sx * sy))
    if mode == "mean_axes":
        return (abs(sx) + abs(sy) + abs(sz)) / 3.0
    if mode == "volume_equivalent":
        return abs(sx * sy * sz) ** (1.0 / 3.0)
    raise ValueError(f"Unsupported radius scaling mode: {mode}")


def scale_nodes(
    nodes: list[SWCNode],
    sx: float = 1.0,
    sy: float = 1.0,
    sz: float = 1.0,
    *,
    scale_radius: bool = True,
    radius_mode: str = "volume_equivalent",
) -> list[SWCNode]:
    """Scale node coordinates and, by default, scale radius with a deterministic rule.

    Default radius rule:
    - ``volume_equivalent``: radius *= (sx * sy * sz) ** (1/3)
    This preserves local volume scaling consistency under anisotropic transforms.
    """
    r_factor = _radius_scale_factor(sx, sy, sz, radius_mode) if scale_radius else 1.0
    return [
        SWCNode(
            node_id=n.node_id,
            node_type=n.node_type,
            x=n.x * sx,
            y=n.y * sy,
            z=n.z * sz,
            radius=n.radius * r_factor,
            parent_id=n.parent_id,
        )
        for n in nodes
    ]
