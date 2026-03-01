"""Point matching algorithms."""

from __future__ import annotations

import math

from neuroutils.core.types import SWCNode


def match_by_nearest(gt: list[SWCNode], pred: list[SWCNode], max_dist: float = 5.0) -> list[tuple[int, int]]:
    """Greedy nearest-neighbor matching with one-to-one assignment."""
    used_pred: set[int] = set()
    pairs: list[tuple[int, int]] = []
    for g in gt:
        best_dist = max_dist
        best_id = -1
        for p in pred:
            if p.node_id in used_pred:
                continue
            dist = math.sqrt((g.x - p.x) ** 2 + (g.y - p.y) ** 2 + (g.z - p.z) ** 2)
            if dist <= best_dist:
                best_dist = dist
                best_id = p.node_id
        if best_id != -1:
            pairs.append((g.node_id, best_id))
            used_pred.add(best_id)
    return pairs
