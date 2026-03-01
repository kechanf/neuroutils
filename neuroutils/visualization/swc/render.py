"""SWC and marker rendering on 2D images."""

from __future__ import annotations

import numpy as np

from neuroutils.core.types import Marker, SWCNode
from neuroutils.swc.base import node_map
from neuroutils.visualization.base import to_rgb


def _project(node: SWCNode, projection: str) -> tuple[int, int]:
    if projection == "xy":
        return int(round(node.x)), int(round(node.y))
    if projection == "xz":
        return int(round(node.x)), int(round(node.z))
    if projection == "yz":
        return int(round(node.y)), int(round(node.z))
    raise ValueError(f"Unsupported projection: {projection}")


def _draw_disc(img: np.ndarray, x: int, y: int, radius: int, color: tuple[int, int, int]) -> None:
    h, w = img.shape[:2]
    r = max(1, radius)
    x0, x1 = max(0, x - r), min(w - 1, x + r)
    y0, y1 = max(0, y - r), min(h - 1, y + r)
    yy, xx = np.ogrid[y0 : y1 + 1, x0 : x1 + 1]
    mask = (xx - x) ** 2 + (yy - y) ** 2 <= r * r
    img[y0 : y1 + 1, x0 : x1 + 1][mask] = color


def _draw_line(img: np.ndarray, p0: tuple[int, int], p1: tuple[int, int], color: tuple[int, int, int]) -> None:
    x0, y0 = p0
    x1, y1 = p1
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    xs = np.linspace(x0, x1, steps + 1, dtype=int)
    ys = np.linspace(y0, y1, steps + 1, dtype=int)
    h, w = img.shape[:2]
    valid = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
    img[ys[valid], xs[valid]] = color


def draw_swc(
    image: np.ndarray,
    nodes: list[SWCNode],
    projection: str = "xy",
    line_color: tuple[int, int, int] = (255, 0, 0),
    soma_color: tuple[int, int, int] = (0, 0, 255),
) -> np.ndarray:
    """Render SWC graph on image."""
    out = to_rgb(image).copy()
    nmap = node_map(nodes)
    for node in nodes:
        if node.parent_id == -1:
            continue
        parent = nmap.get(node.parent_id)
        if parent is None:
            continue
        _draw_line(out, _project(parent, projection), _project(node, projection), line_color)
    root = next((n for n in nodes if n.parent_id == -1), None)
    if root is not None:
        x, y = _project(root, projection)
        _draw_disc(out, x, y, int(round(max(2.0, root.radius))), soma_color)
    return out


def draw_markers(
    image: np.ndarray,
    markers: list[Marker],
    projection: str = "xy",
    color: tuple[int, int, int] = (0, 255, 0),
) -> np.ndarray:
    """Render markers on image."""
    out = to_rgb(image).copy()
    for m in markers:
        if projection == "xy":
            x, y = int(round(m.x)), int(round(m.y))
        elif projection == "xz":
            x, y = int(round(m.x)), int(round(m.z))
        elif projection == "yz":
            x, y = int(round(m.y)), int(round(m.z))
        else:
            raise ValueError(f"Unsupported projection: {projection}")
        _draw_disc(out, x, y, int(round(max(1.0, m.radius))), color)
    return out
