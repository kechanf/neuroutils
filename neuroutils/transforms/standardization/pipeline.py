"""Canonical standardization pipeline."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.swc.sorting import reindex_swc
from neuroutils.transforms.normalization import center_at_root


def standardize_swc(nodes: list[SWCNode]) -> list[SWCNode]:
    """Apply deterministic SWC standardization."""
    return center_at_root(reindex_swc(nodes))
