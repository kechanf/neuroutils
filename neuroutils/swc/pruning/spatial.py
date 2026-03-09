"""Spatial pruning helpers for SWC nodes."""

from __future__ import annotations

import math
from collections import deque

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import children_map, find_soma_index, index_map


def is_in_box(x: float, y: float, z: float, shape_zyx: tuple[int, int, int]) -> bool:
    """Return whether xyz lies in image shape bounds (z,y,x)."""
    zmax, ymax, xmax = shape_zyx
    return 0 <= x < xmax and 0 <= y < ymax and 0 <= z < zmax


def is_in_bbox(
    x: float,
    y: float,
    z: float,
    bbox_zyxzyx: tuple[tuple[float, float, float], tuple[float, float, float]],
) -> bool:
    """Return whether xyz lies in bbox ((zmin,ymin,xmin),(zmax,ymax,xmax))."""
    (zmin, ymin, xmin), (zmax, ymax, xmax) = bbox_zyxzyx
    return xmin <= x <= xmax and ymin <= y <= ymax and zmin <= z <= zmax


def trim_out_of_box(
    nodes: list[SWCNode],
    shape_zyx: tuple[int, int, int],
    *,
    keep_candidate_points: bool = True,
) -> list[SWCNode]:
    """Trim nodes outside image box, optionally keeping boundary-crossing candidates."""
    cmap = children_map(nodes)
    nmap = {n.node_id: n for n in nodes}
    kept: list[SWCNode] = []
    for node in nodes:
        inside = is_in_box(node.x, node.y, node.z, shape_zyx)
        if inside:
            kept.append(node)
            continue
        if not keep_candidate_points:
            continue
        parent_inside = node.parent_id in nmap and is_in_box(
            nmap[node.parent_id].x, nmap[node.parent_id].y, nmap[node.parent_id].z, shape_zyx
        )
        child_inside = any(
            is_in_box(nmap[ch].x, nmap[ch].y, nmap[ch].z, shape_zyx)
            for ch in cmap.get(node.node_id, [])
            if ch in nmap
        )
        if parent_inside or child_inside:
            kept.append(node)
    return kept


def prune_subtrees(nodes: list[SWCNode], prune_node_ids: set[int]) -> list[SWCNode]:
    """Remove each seed node in ``prune_node_ids`` and all its descendants."""
    if not prune_node_ids:
        return list(nodes)
    cmap = children_map(nodes)
    idx = index_map(nodes)
    alive = [True] * len(nodes)

    for seed in prune_node_ids:
        if seed not in idx:
            continue
        q: deque[int] = deque([seed])
        while q:
            head = q.popleft()
            if head not in idx:
                continue
            row = idx[head]
            if not alive[row]:
                continue
            alive[row] = False
            q.extend(cmap.get(head, []))

    return [n for keep, n in zip(alive, nodes) if keep]


def trim_swc(
    nodes: list[SWCNode],
    shape_zyx: tuple[int, int, int],
    *,
    keep_candidate_points: bool = True,
) -> list[SWCNode]:
    """Trim SWC by image box; keep branch-crossing candidates when configured."""
    return trim_out_of_box(
        nodes,
        shape_zyx=shape_zyx,
        keep_candidate_points=keep_candidate_points,
    )


def crop_tree_by_bbox(
    nodes: list[SWCNode],
    bbox_zyxzyx: tuple[tuple[float, float, float], tuple[float, float, float]],
    *,
    keep_candidate_points: bool = True,
) -> list[SWCNode]:
    """Crop SWC by arbitrary bbox ((zmin,ymin,xmin),(zmax,ymax,xmax))."""
    cmap = children_map(nodes)
    nmap = {n.node_id: n for n in nodes}
    kept: list[SWCNode] = []
    for node in nodes:
        inside = is_in_bbox(node.x, node.y, node.z, bbox_zyxzyx)
        if inside:
            kept.append(node)
            continue
        if not keep_candidate_points:
            continue
        parent_inside = node.parent_id in nmap and is_in_bbox(
            nmap[node.parent_id].x,
            nmap[node.parent_id].y,
            nmap[node.parent_id].z,
            bbox_zyxzyx,
        )
        child_inside = any(
            is_in_bbox(nmap[ch].x, nmap[ch].y, nmap[ch].z, bbox_zyxzyx)
            for ch in cmap.get(node.node_id, [])
            if ch in nmap
        )
        if parent_inside or child_inside:
            kept.append(node)
    return kept


def crop_sphere_from_soma(nodes: list[SWCNode], radius: float) -> list[SWCNode]:
    """Keep nodes within Euclidean radius from soma and connected to soma."""
    if radius <= 0:
        return []
    si = find_soma_index(nodes)
    if si < 0:
        return list(nodes)
    soma = nodes[si]
    keep_by_dist = {
        n.node_id
        for n in nodes
        if math.sqrt((n.x - soma.x) ** 2 + (n.y - soma.y) ** 2 + (n.z - soma.z) ** 2) < radius
    }
    filtered = [n for n in nodes if n.node_id in keep_by_dist]
    return remove_disconnected(filtered, anchor_id=soma.node_id)


def remove_disconnected(nodes: list[SWCNode], anchor_id: int) -> list[SWCNode]:
    """Keep only the connected component containing anchor in undirected SWC graph."""
    nmap = {n.node_id: n for n in nodes}
    if anchor_id not in nmap:
        return nodes

    adjacency: dict[int, set[int]] = {n.node_id: set() for n in nodes}
    for n in nodes:
        if n.parent_id != -1 and n.parent_id in adjacency:
            adjacency[n.node_id].add(n.parent_id)
            adjacency[n.parent_id].add(n.node_id)

    visited: set[int] = set()
    q: deque[int] = deque([anchor_id])
    while q:
        head = q.popleft()
        if head in visited:
            continue
        visited.add(head)
        q.extend(adjacency.get(head, set()) - visited)

    return [n for n in nodes if n.node_id in visited]
