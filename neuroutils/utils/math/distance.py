"""Distance helpers."""

from __future__ import annotations

import math

from neuroutils.core.types import SWCNode


def euclidean_3d(a: SWCNode, b: SWCNode) -> float:
    """3D Euclidean distance between two nodes."""
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)
