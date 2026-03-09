"""Core typed data models used across neuroutils."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SWCNode:
    """Single SWC node."""

    node_id: int
    node_type: int
    x: float
    y: float
    z: float
    radius: float
    parent_id: int


@dataclass(frozen=True, slots=True)
class Marker:
    """3D marker with optional radius."""

    x: float
    y: float
    z: float
    radius: float = 1.0


def ensure_unique_node_ids(nodes: Iterable[SWCNode]) -> bool:
    """Return True when node ids are unique."""
    ids = [node.node_id for node in nodes]
    return len(ids) == len(set(ids))
