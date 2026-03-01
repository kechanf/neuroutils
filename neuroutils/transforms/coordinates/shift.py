"""Coordinate transform utilities."""

from __future__ import annotations

from neuroutils.core.types import SWCNode


def shift_nodes(nodes: list[SWCNode], dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> list[SWCNode]:
    """Shift node coordinates by constant offset."""
    return [
        SWCNode(
            node_id=n.node_id,
            node_type=n.node_type,
            x=n.x + dx,
            y=n.y + dy,
            z=n.z + dz,
            radius=n.radius,
            parent_id=n.parent_id,
        )
        for n in nodes
    ]
