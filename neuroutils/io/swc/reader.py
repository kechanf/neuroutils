"""SWC reader."""

from __future__ import annotations

from pathlib import Path

from neuroutils.core.exceptions import SWCFormatError
from neuroutils.core.types import SWCNode


def read_swc(path: str | Path) -> list[SWCNode]:
    """Read SWC file into typed nodes."""
    nodes: list[SWCNode] = []
    for line_no, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 7:
            raise SWCFormatError(f"Invalid SWC line {line_no}: expected 7 columns")
        try:
            node = SWCNode(
                node_id=int(parts[0]),
                node_type=int(parts[1]),
                x=float(parts[2]),
                y=float(parts[3]),
                z=float(parts[4]),
                radius=float(parts[5]),
                parent_id=int(parts[6]),
            )
        except ValueError as exc:
            raise SWCFormatError(f"Invalid SWC numeric value at line {line_no}") from exc
        nodes.append(node)
    return nodes
