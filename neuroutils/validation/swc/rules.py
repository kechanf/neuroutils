"""SWC validation rules."""

from __future__ import annotations

from neuroutils.core.exceptions import ValidationError
from neuroutils.core.types import SWCNode, ensure_unique_node_ids


def validate_swc(nodes: list[SWCNode]) -> None:
    """Validate SWC node list; raises ValidationError if invalid."""
    if not nodes:
        raise ValidationError("SWC is empty")
    if not ensure_unique_node_ids(nodes):
        raise ValidationError("SWC contains duplicate node ids")
    ids = {n.node_id for n in nodes}
    roots = [n for n in nodes if n.parent_id == -1]
    if len(roots) != 1:
        raise ValidationError("SWC must have exactly one root")
    for node in nodes:
        if node.radius < 0:
            raise ValidationError(f"Node {node.node_id} has negative radius")
        if node.parent_id != -1 and node.parent_id not in ids:
            raise ValidationError(f"Node {node.node_id} references missing parent {node.parent_id}")
