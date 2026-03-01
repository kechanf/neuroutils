"""SWC writer."""

from __future__ import annotations

from pathlib import Path

from neuroutils.core.types import SWCNode


def write_swc(path: str | Path, nodes: list[SWCNode], header: list[str] | None = None) -> None:
    """Write nodes to SWC file."""
    lines: list[str] = []
    if header:
        lines.extend([f"# {h}" for h in header])
    for node in nodes:
        lines.append(
            f"{node.node_id} {node.node_type} {node.x:.6f} {node.y:.6f} "
            f"{node.z:.6f} {node.radius:.6f} {node.parent_id}"
        )
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
