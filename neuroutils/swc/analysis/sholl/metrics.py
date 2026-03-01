"""Sholl-like analysis."""

from __future__ import annotations

import math
from dataclasses import dataclass

from neuroutils.core.types import SWCNode


@dataclass(frozen=True, slots=True)
class ShollResult:
    """Sholl intersections per radius."""

    radii: list[float]
    intersections: list[int]


def sholl_intersections(nodes: list[SWCNode], step: float = 10.0) -> ShollResult:
    """Count nodes crossing spherical shells from root."""
    if not nodes:
        return ShollResult(radii=[], intersections=[])
    root = next((n for n in nodes if n.parent_id == -1), nodes[0])
    distances = [
        math.sqrt((n.x - root.x) ** 2 + (n.y - root.y) ** 2 + (n.z - root.z) ** 2) for n in nodes
    ]
    max_dist = max(distances) if distances else 0.0
    radii = [step * (i + 1) for i in range(max(1, int(max_dist // step) + 1))]
    counts = [sum(1 for d in distances if d >= r) for r in radii]
    return ShollResult(radii=radii, intersections=counts)
