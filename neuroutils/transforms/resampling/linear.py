"""Linear resampling for SWC edges."""

from __future__ import annotations

import math

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import node_map


def resample_edges(nodes: list[SWCNode], step: float) -> list[SWCNode]:
    """Resample long edges by inserting intermediate nodes."""
    if step <= 0:
        return nodes
    nmap = node_map(nodes)
    out: list[SWCNode] = []
    next_id = max((n.node_id for n in nodes), default=0) + 1
    for node in nodes:
        if node.parent_id == -1:
            out.append(node)
            continue
        parent = nmap[node.parent_id]
        dist = math.sqrt((node.x - parent.x) ** 2 + (node.y - parent.y) ** 2 + (node.z - parent.z) ** 2)
        if dist <= step:
            out.append(node)
            continue
        segments = int(dist // step) + 1
        prev_parent = parent.node_id
        for i in range(1, segments):
            t = i / segments
            inter = SWCNode(
                node_id=next_id,
                node_type=node.node_type,
                x=parent.x + (node.x - parent.x) * t,
                y=parent.y + (node.y - parent.y) * t,
                z=parent.z + (node.z - parent.z) * t,
                radius=(parent.radius + node.radius) / 2.0,
                parent_id=prev_parent,
            )
            out.append(inter)
            prev_parent = next_id
            next_id += 1
        out.append(
            SWCNode(
                node_id=node.node_id,
                node_type=node.node_type,
                x=node.x,
                y=node.y,
                z=node.z,
                radius=node.radius,
                parent_id=prev_parent,
            )
        )
    return out
