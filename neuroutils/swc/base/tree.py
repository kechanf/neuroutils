"""SWC tree utilities."""

from __future__ import annotations

from collections import defaultdict, deque

from neuroutils.core.types import SWCNode


def node_map(nodes: list[SWCNode]) -> dict[int, SWCNode]:
    """Map node id -> node."""
    return {n.node_id: n for n in nodes}


def index_map(nodes: list[SWCNode]) -> dict[int, int]:
    """Map node id -> row index."""
    return {n.node_id: i for i, n in enumerate(nodes)}


def children_map(nodes: list[SWCNode]) -> dict[int, list[int]]:
    """Build parent -> children mapping."""
    cmap: dict[int, list[int]] = defaultdict(list)
    for node in nodes:
        cmap[node.parent_id].append(node.node_id)
    return dict(cmap)


def find_root_ids(nodes: list[SWCNode]) -> list[int]:
    """Return root ids (parent == -1)."""
    return [n.node_id for n in nodes if n.parent_id == -1]


def find_soma_node_id(nodes: list[SWCNode], *, parent_id: int = -1) -> int:
    """Find soma/root node id by parent marker; return -99 when absent."""
    for n in nodes:
        if n.parent_id == parent_id:
            return n.node_id
    return -99


def find_soma_index(nodes: list[SWCNode], *, parent_id: int = -1) -> int:
    """Find soma/root row index by parent marker; return -99 when absent."""
    for i, n in enumerate(nodes):
        if n.parent_id == parent_id:
            return i
    return -99


def bfs_order(nodes: list[SWCNode], root_id: int) -> list[int]:
    """Breadth-first traversal order."""
    cmap = children_map(nodes)
    order: list[int] = []
    queue: deque[int] = deque([root_id])
    while queue:
        nid = queue.popleft()
        order.append(nid)
        queue.extend(cmap.get(nid, []))
    return order
