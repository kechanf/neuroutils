"""Basic geometry statistics for SWC trees."""

from __future__ import annotations

from dataclasses import dataclass

from neuroutils.core.types import SWCNode


@dataclass(frozen=True, slots=True)
class BBoxXYZ:
    """Axis-aligned bounding box in xyz."""

    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float
    zmax: float


@dataclass(frozen=True, slots=True)
class ExtentXYZ:
    """Extent along xyz axes."""

    x: float
    y: float
    z: float


def node_count(nodes: list[SWCNode]) -> int:
    """Return number of nodes."""
    return len(nodes)


def bbox_xyz(nodes: list[SWCNode]) -> BBoxXYZ:
    """Compute xyz bounding box of nodes."""
    if not nodes:
        raise ValueError("nodes must not be empty")
    xs = [n.x for n in nodes]
    ys = [n.y for n in nodes]
    zs = [n.z for n in nodes]
    return BBoxXYZ(
        xmin=float(min(xs)),
        xmax=float(max(xs)),
        ymin=float(min(ys)),
        ymax=float(max(ys)),
        zmin=float(min(zs)),
        zmax=float(max(zs)),
    )


def extent_xyz(nodes: list[SWCNode]) -> ExtentXYZ:
    """Compute xyz extents (`max-min`) of nodes."""
    b = bbox_xyz(nodes)
    return ExtentXYZ(x=b.xmax - b.xmin, y=b.ymax - b.ymin, z=b.zmax - b.zmin)
