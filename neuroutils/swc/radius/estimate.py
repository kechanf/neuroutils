"""Simple radius estimation."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import children_map


def estimate_missing_radii(nodes: list[SWCNode], default_radius: float = 1.0) -> list[SWCNode]:
    """Replace non-positive radii using parent/child averages or default."""
    cmap = children_map(nodes)
    nmap = {n.node_id: n for n in nodes}
    out: list[SWCNode] = []
    for node in nodes:
        if node.radius > 0:
            out.append(node)
            continue
        candidates: list[float] = []
        if node.parent_id in nmap:
            p = nmap[node.parent_id]
            if p.radius > 0:
                candidates.append(p.radius)
        for child_id in cmap.get(node.node_id, []):
            c = nmap[child_id]
            if c.radius > 0:
                candidates.append(c.radius)
        radius = sum(candidates) / len(candidates) if candidates else default_radius
        out.append(
            SWCNode(
                node_id=node.node_id,
                node_type=node.node_type,
                x=node.x,
                y=node.y,
                z=node.z,
                radius=radius,
                parent_id=node.parent_id,
            )
        )
    return out
