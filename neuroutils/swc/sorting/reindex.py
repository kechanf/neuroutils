"""SWC sorting and reindexing."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import bfs_order, find_root_ids, node_map


def reindex_swc(nodes: list[SWCNode]) -> list[SWCNode]:
    """Reindex SWC to contiguous ids using BFS order from root."""
    roots = find_root_ids(nodes)
    if not roots:
        return nodes
    nmap = node_map(nodes)
    order = bfs_order(nodes, roots[0])
    id_mapping = {old_id: idx + 1 for idx, old_id in enumerate(order)}

    out: list[SWCNode] = []
    for old_id in order:
        node = nmap[old_id]
        new_parent = -1 if node.parent_id == -1 else id_mapping[node.parent_id]
        out.append(
            SWCNode(
                node_id=id_mapping[old_id],
                node_type=node.node_type,
                x=node.x,
                y=node.y,
                z=node.z,
                radius=node.radius,
                parent_id=new_parent,
            )
        )
    return out
