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


def _pad_counts(a: list[int], b: list[int]) -> tuple[list[float], list[float]]:
    n = max(len(a), len(b))
    pa = [float(v) for v in a] + [0.0] * (n - len(a))
    pb = [float(v) for v in b] + [0.0] * (n - len(b))
    return pa, pb


def _normalize_hist(values: list[float]) -> list[float]:
    total = sum(values)
    if total <= 0.0:
        return [0.0 for _ in values]
    return [v / total for v in values]


def bhattacharyya_distance(counts_a: list[int], counts_b: list[int], *, eps: float = 1e-12) -> float:
    """Bhattacharyya distance for two Sholl count vectors."""
    pa, pb = _pad_counts(counts_a, counts_b)
    ha = _normalize_hist(pa)
    hb = _normalize_hist(pb)
    coeff = sum(math.sqrt(max(a, 0.0) * max(b, 0.0)) for a, b in zip(ha, hb))
    coeff = min(max(coeff, eps), 1.0)
    return float(-math.log(coeff))


def earth_movers_distance(counts_a: list[int], counts_b: list[int]) -> float:
    """1D EMD (equal bin width) for two Sholl count vectors."""
    pa, pb = _pad_counts(counts_a, counts_b)
    ha = _normalize_hist(pa)
    hb = _normalize_hist(pb)
    cum = 0.0
    emd = 0.0
    for a, b in zip(ha, hb):
        cum += a - b
        emd += abs(cum)
    return float(emd)


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
