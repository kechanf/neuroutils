"""SWC validation wrappers."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.validation.swc import validate_swc


def assert_valid_swc(nodes: list[SWCNode]) -> list[SWCNode]:
    """Validate and return nodes for pipeline chaining."""
    validate_swc(nodes)
    return nodes
