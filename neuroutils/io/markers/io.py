"""Marker IO."""

from __future__ import annotations

from pathlib import Path

from neuroutils.core.types import Marker


def read_markers(path: str | Path) -> list[Marker]:
    """Read simple CSV markers: x,y,z[,radius]."""
    markers: list[Marker] = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [x.strip() for x in line.split(",")]
        if len(parts) < 3:
            continue
        if parts[0].lower() in {"x", "coord_x"}:
            continue
        try:
            radius = float(parts[3]) if len(parts) > 3 else 1.0
            x = float(parts[0])
            y = float(parts[1])
            z = float(parts[2])
        except ValueError:
            continue
        markers.append(Marker(x=x, y=y, z=z, radius=radius))
    return markers


def write_markers(path: str | Path, markers: list[Marker]) -> None:
    """Write marker CSV."""
    lines = ["x,y,z,radius"]
    lines.extend([f"{m.x:.6f},{m.y:.6f},{m.z:.6f},{m.radius:.6f}" for m in markers])
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
