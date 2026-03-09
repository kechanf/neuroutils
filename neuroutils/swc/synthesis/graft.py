"""SWC graft operators: full-tree graft and branch-segment graft."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import children_map, node_map
from neuroutils.transforms.geometry import (
    random_rotation_matrix,
    rotate_fragment_points_to_match_angle,
    rotate_points,
    unit_vector,
)


@dataclass(frozen=True, slots=True)
class GraftResult:
    """Result of a graft operation."""

    nodes: list[SWCNode]
    grafted_node_ids: list[int]
    donor_id_mapping: dict[int, int]


def _rng(rng: np.random.Generator | None = None) -> np.random.Generator:
    return rng if rng is not None else np.random.default_rng()


def _undirected_neighbors(nodes: list[SWCNode]) -> dict[int, set[int]]:
    nmap = node_map(nodes)
    adj: dict[int, set[int]] = {n.node_id: set() for n in nodes}
    for n in nodes:
        pid = n.parent_id
        if pid == -1 or pid not in nmap:
            continue
        adj[n.node_id].add(pid)
        adj[pid].add(n.node_id)
    return adj


def _pick_or_validate_node_id(
    nodes: list[SWCNode],
    *,
    value: int | None,
    rng: np.random.Generator,
) -> int:
    if not nodes:
        raise ValueError("nodes must not be empty")
    ids = [n.node_id for n in nodes]
    if value is None:
        return int(rng.choice(np.array(ids, dtype=np.int64)))
    if value not in set(ids):
        raise ValueError(f"node id not found: {value}")
    return value


def _transform_donor_points(
    donor_nodes: list[SWCNode],
    *,
    donor_attach_id: int,
    target_attach_xyz: np.ndarray,
    rng: np.random.Generator,
    apply_rotation: bool,
) -> dict[int, np.ndarray]:
    dmap = node_map(donor_nodes)
    attach = dmap[donor_attach_id]
    center = np.array([attach.x, attach.y, attach.z], dtype=np.float64)
    points = np.array([[n.x, n.y, n.z] for n in donor_nodes], dtype=np.float64)
    if apply_rotation:
        rot = random_rotation_matrix(rng)
        points = rotate_points(points, center=center, rotation_matrix=rot)
    delta = np.asarray(target_attach_xyz, dtype=np.float64) - center
    points = points + delta
    return {n.node_id: points[i] for i, n in enumerate(donor_nodes)}


def _bfs_parent_map_from_attach(
    donor_nodes: list[SWCNode],
    donor_attach_id: int,
) -> dict[int, int]:
    adj = _undirected_neighbors(donor_nodes)
    parent: dict[int, int] = {}
    q: deque[int] = deque([donor_attach_id])
    visited = {donor_attach_id}
    while q:
        cur = q.popleft()
        for nb in sorted(adj[cur]):
            if nb in visited:
                continue
            visited.add(nb)
            parent[nb] = cur
            q.append(nb)
    return parent


def _choose_reference_direction(target_nodes: list[SWCNode], target_attach_id: int) -> np.ndarray:
    tmap = node_map(target_nodes)
    attach = tmap[target_attach_id]
    base = np.array([attach.x, attach.y, attach.z], dtype=np.float64)
    if attach.parent_id != -1 and attach.parent_id in tmap:
        p = tmap[attach.parent_id]
        v = base - np.array([p.x, p.y, p.z], dtype=np.float64)
        u = unit_vector(v)
        if u is not None:
            return u
    cmap = children_map(target_nodes)
    for cid in cmap.get(target_attach_id, []):
        c = tmap[cid]
        v = np.array([c.x, c.y, c.z], dtype=np.float64) - base
        u = unit_vector(v)
        if u is not None:
            return u
    return np.array([1.0, 0.0, 0.0], dtype=np.float64)


def graft_full_tree(
    target_nodes: list[SWCNode],
    donor_nodes: list[SWCNode],
    *,
    target_attach_id: int | None = None,
    donor_attach_id: int | None = None,
    rng: np.random.Generator | None = None,
    apply_rotation: bool = True,
) -> GraftResult:
    """Graft a full donor tree onto a target node by removing donor attach node."""
    gen = _rng(rng)
    target_attach = _pick_or_validate_node_id(target_nodes, value=target_attach_id, rng=gen)
    donor_attach = _pick_or_validate_node_id(donor_nodes, value=donor_attach_id, rng=gen)
    tmap = node_map(target_nodes)
    dmap = node_map(donor_nodes)
    target_attach_xyz = np.array(
        [tmap[target_attach].x, tmap[target_attach].y, tmap[target_attach].z],
        dtype=np.float64,
    )
    transformed = _transform_donor_points(
        donor_nodes,
        donor_attach_id=donor_attach,
        target_attach_xyz=target_attach_xyz,
        rng=gen,
        apply_rotation=apply_rotation,
    )
    donor_parent = _bfs_parent_map_from_attach(donor_nodes, donor_attach)

    max_target_id = max(n.node_id for n in target_nodes)
    kept_old_ids = [n.node_id for n in donor_nodes if n.node_id != donor_attach]
    donor_id_mapping = {old: max_target_id + i + 1 for i, old in enumerate(sorted(kept_old_ids))}

    out_nodes: list[SWCNode] = []
    for n in target_nodes:
        if n.node_id == target_attach:
            out_nodes.append(
                SWCNode(
                    node_id=n.node_id,
                    node_type=n.node_type,
                    x=n.x,
                    y=n.y,
                    z=n.z,
                    radius=max(float(n.radius), float(dmap[donor_attach].radius)),
                    parent_id=n.parent_id,
                )
            )
        else:
            out_nodes.append(n)

    grafted_ids: list[int] = []
    for old_id in sorted(kept_old_ids):
        old = dmap[old_id]
        xyz = transformed[old_id]
        old_parent = donor_parent.get(old_id, donor_attach)
        if old_parent == donor_attach:
            new_parent = target_attach
        else:
            new_parent = donor_id_mapping[old_parent]
        new_id = donor_id_mapping[old_id]
        grafted_ids.append(new_id)
        out_nodes.append(
            SWCNode(
                node_id=new_id,
                node_type=old.node_type,
                x=float(xyz[0]),
                y=float(xyz[1]),
                z=float(xyz[2]),
                radius=old.radius,
                parent_id=new_parent,
            )
        )
    return GraftResult(nodes=out_nodes, grafted_node_ids=grafted_ids, donor_id_mapping=donor_id_mapping)


def graft_branch_segment(
    target_nodes: list[SWCNode],
    donor_nodes: list[SWCNode],
    *,
    target_attach_id: int | None = None,
    donor_attach_id: int | None = None,
    max_hops: int = 10,
    angle_limit_deg: float = 45.0,
    first_step_id: int | None = None,
    rng: np.random.Generator | None = None,
    apply_rotation: bool = True,
) -> GraftResult:
    """Graft one donor branch segment onto target node."""
    if max_hops < 1:
        raise ValueError("max_hops must be >= 1")
    gen = _rng(rng)
    target_attach = _pick_or_validate_node_id(target_nodes, value=target_attach_id, rng=gen)
    donor_attach = _pick_or_validate_node_id(donor_nodes, value=donor_attach_id, rng=gen)
    dmap = node_map(donor_nodes)
    tmap = node_map(target_nodes)
    adj = _undirected_neighbors(donor_nodes)
    neighbors = sorted(adj[donor_attach])
    if not neighbors:
        return GraftResult(nodes=list(target_nodes), grafted_node_ids=[], donor_id_mapping={})
    if first_step_id is not None and first_step_id not in neighbors:
        raise ValueError("first_step_id must be a neighbor of donor_attach_id")
    cur = first_step_id if first_step_id is not None else int(gen.choice(np.array(neighbors, dtype=np.int64)))
    prev = donor_attach
    segment: list[int] = [cur]
    for _ in range(max_hops - 1):
        next_candidates = [nid for nid in sorted(adj[cur]) if nid != prev]
        if not next_candidates:
            break
        nxt = int(gen.choice(np.array(next_candidates, dtype=np.int64)))
        segment.append(nxt)
        prev, cur = cur, nxt

    target_attach_xyz = np.array(
        [tmap[target_attach].x, tmap[target_attach].y, tmap[target_attach].z],
        dtype=np.float64,
    )
    transformed = _transform_donor_points(
        donor_nodes,
        donor_attach_id=donor_attach,
        target_attach_xyz=target_attach_xyz,
        rng=gen,
        apply_rotation=apply_rotation,
    )

    points = np.array([transformed[sid] for sid in segment], dtype=np.float64)
    if len(points) > 0:
        points = rotate_fragment_points_to_match_angle(
            points,
            base_point=target_attach_xyz,
            fragment_root_point=points[0],
            reference_direction=_choose_reference_direction(target_nodes, target_attach),
            max_deg=angle_limit_deg,
            rng=gen,
        )

    max_target_id = max(n.node_id for n in target_nodes)
    donor_id_mapping = {old: max_target_id + i + 1 for i, old in enumerate(segment)}
    out_nodes = list(target_nodes)
    out_nodes = [
        SWCNode(
            node_id=n.node_id,
            node_type=n.node_type,
            x=n.x,
            y=n.y,
            z=n.z,
            radius=max(float(n.radius), float(dmap[donor_attach].radius))
            if n.node_id == target_attach
            else n.radius,
            parent_id=n.parent_id,
        )
        for n in out_nodes
    ]

    grafted_ids: list[int] = []
    for i, old_id in enumerate(segment):
        old = dmap[old_id]
        xyz = points[i]
        new_id = donor_id_mapping[old_id]
        parent = target_attach if i == 0 else donor_id_mapping[segment[i - 1]]
        grafted_ids.append(new_id)
        out_nodes.append(
            SWCNode(
                node_id=new_id,
                node_type=old.node_type,
                x=float(xyz[0]),
                y=float(xyz[1]),
                z=float(xyz[2]),
                radius=old.radius,
                parent_id=parent,
            )
        )
    return GraftResult(nodes=out_nodes, grafted_node_ids=grafted_ids, donor_id_mapping=donor_id_mapping)
