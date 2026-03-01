"""Normalization transforms."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.transforms.coordinates import shift_nodes


def center_at_root(nodes: list[SWCNode]) -> list[SWCNode]:
    """Translate nodes so root is at origin."""
    if not nodes:
        return nodes
    root = next((n for n in nodes if n.parent_id == -1), nodes[0])
    return shift_nodes(nodes, dx=-root.x, dy=-root.y, dz=-root.z)
