"""Additional SWC synthesis operators."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import children_map, node_map
from neuroutils.transforms.geometry import sample_direction_in_cone, unit_vector


@dataclass(frozen=True, slots=True)
class OperatorResult:
    """Result of an SWC operator."""

    nodes: list[SWCNode]
    affected_node_ids: list[int]


def _rng(rng: np.random.Generator | None = None) -> np.random.Generator:
    return rng if rng is not None else np.random.default_rng()


def _pick_attach_nodes(
    nodes: list[SWCNode],
    *,
    count: int,
    rng: np.random.Generator,
) -> list[int]:
    if not nodes:
        raise ValueError("nodes must not be empty")
    ids = np.array([n.node_id for n in nodes], dtype=np.int64)
    if count <= len(ids):
        chosen = rng.choice(ids, size=count, replace=False)
    else:
        chosen = rng.choice(ids, size=count, replace=True)
    return [int(v) for v in chosen.tolist()]


def _local_reference_direction(nodes: list[SWCNode], node_id: int) -> np.ndarray:
    nmap = node_map(nodes)
    cmap = children_map(nodes)
    base = nmap[node_id]
    p0 = np.array([base.x, base.y, base.z], dtype=np.float64)

    if base.parent_id != -1 and base.parent_id in nmap:
        p = nmap[base.parent_id]
        d = p0 - np.array([p.x, p.y, p.z], dtype=np.float64)
        u = unit_vector(d)
        if u is not None:
            return u

    for cid in cmap.get(node_id, []):
        c = nmap[cid]
        d = np.array([c.x, c.y, c.z], dtype=np.float64) - p0
        u = unit_vector(d)
        if u is not None:
            return u
    return np.array([1.0, 0.0, 0.0], dtype=np.float64)


def _range_to_int_pair(v: tuple[int, int] | list[int]) -> tuple[int, int]:
    if len(v) != 2:
        raise ValueError("range must contain exactly two values")
    a, b = int(v[0]), int(v[1])
    if a <= 0 or b <= 0:
        raise ValueError("range values must be positive")
    return (a, b) if a <= b else (b, a)


def _range_to_float_pair(v: tuple[float, float] | list[float]) -> tuple[float, float]:
    if len(v) != 2:
        raise ValueError("range must contain exactly two values")
    a, b = float(v[0]), float(v[1])
    return (a, b) if a <= b else (b, a)


def add_local_spur(
    nodes: list[SWCNode],
    *,
    spur_count: int = 5,
    spur_len_range: tuple[int, int] = (1, 3),
    step_length: float = 1.0,
    angle_jitter_deg: float = 35.0,
    rng: np.random.Generator | None = None,
) -> OperatorResult:
    """Generate short local spur branches around random nodes."""
    if spur_count <= 0:
        return OperatorResult(nodes=list(nodes), affected_node_ids=[])
    lo, hi = _range_to_int_pair(spur_len_range)
    if step_length <= 0:
        raise ValueError("step_length must be positive")

    gen = _rng(rng)
    nmap = node_map(nodes)
    out = list(nodes)
    next_id = max((n.node_id for n in nodes), default=0) + 1
    attach_ids = _pick_attach_nodes(nodes, count=spur_count, rng=gen)
    added_ids: list[int] = []

    for attach_id in attach_ids:
        base = nmap[attach_id]
        parent_id = attach_id
        p = np.array([base.x, base.y, base.z], dtype=np.float64)
        length = int(gen.integers(lo, hi + 1))
        ref = _local_reference_direction(out, attach_id)
        for _ in range(length):
            direction = sample_direction_in_cone(ref, angle_jitter_deg, rng=gen)
            p = p + direction * step_length
            new_node = SWCNode(
                node_id=next_id,
                node_type=base.node_type if base.node_type > 0 else 3,
                x=float(p[0]),
                y=float(p[1]),
                z=float(p[2]),
                radius=max(0.2, float(base.radius) * 0.7),
                parent_id=parent_id,
            )
            out.append(new_node)
            nmap[next_id] = new_node
            added_ids.append(next_id)
            parent_id = next_id
            next_id += 1
    return OperatorResult(nodes=out, affected_node_ids=added_ids)


def add_small_cluster_attach(
    nodes: list[SWCNode],
    *,
    cluster_size: int = 8,
    cluster_radius: float = 3.0,
    connect_mode: str = "mixed",
    rng: np.random.Generator | None = None,
) -> OperatorResult:
    """Inject a local small cluster and connect it to the tree."""
    if cluster_size <= 0:
        return OperatorResult(nodes=list(nodes), affected_node_ids=[])
    if cluster_radius <= 0:
        raise ValueError("cluster_radius must be positive")
    if connect_mode not in {"chain", "star", "mixed"}:
        raise ValueError("connect_mode must be one of: chain, star, mixed")

    gen = _rng(rng)
    nmap = node_map(nodes)
    out = list(nodes)
    next_id = max((n.node_id for n in nodes), default=0) + 1
    attach_id = _pick_attach_nodes(nodes, count=1, rng=gen)[0]
    attach = nmap[attach_id]
    center = np.array([attach.x, attach.y, attach.z], dtype=np.float64)

    new_ids: list[int] = []
    for _ in range(cluster_size):
        u = gen.normal(size=3)
        uu = unit_vector(u)
        if uu is None:
            uu = np.array([1.0, 0.0, 0.0], dtype=np.float64)
        r = float(gen.uniform(0.2 * cluster_radius, cluster_radius))
        pos = center + uu * r
        node_id = next_id
        next_id += 1
        new_ids.append(node_id)
        out.append(
            SWCNode(
                node_id=node_id,
                node_type=attach.node_type if attach.node_type > 0 else 3,
                x=float(pos[0]),
                y=float(pos[1]),
                z=float(pos[2]),
                radius=max(0.2, float(attach.radius) * 0.65),
                parent_id=-1,
            )
        )

    updated: list[SWCNode] = []
    new_set = set(new_ids)
    for node in out:
        if node.node_id not in new_set:
            updated.append(node)
            continue

        idx = new_ids.index(node.node_id)
        if idx == 0:
            parent = attach_id
        elif connect_mode == "star":
            parent = new_ids[0]
        elif connect_mode == "chain":
            parent = new_ids[idx - 1]
        else:
            parent = new_ids[idx - 1] if (idx % 2 == 0) else new_ids[0]

        updated.append(
            SWCNode(
                node_id=node.node_id,
                node_type=node.node_type,
                x=node.x,
                y=node.y,
                z=node.z,
                radius=node.radius,
                parent_id=parent,
            )
        )
    return OperatorResult(nodes=updated, affected_node_ids=new_ids)


def _collect_subtree_node_ids(nodes: list[SWCNode], root_id: int) -> set[int]:
    cmap = children_map(nodes)
    keep = {root_id}
    stack = [root_id]
    while stack:
        cur = stack.pop()
        for cid in cmap.get(cur, []):
            if cid in keep:
                continue
            keep.add(cid)
            stack.append(cid)
    return keep


def add_break_fragment_attach(
    nodes: list[SWCNode],
    *,
    break_ratio: float = 0.1,
    offset: float | tuple[float, float] = (2.0, 8.0),
    reconnect_prob: float = 0.5,
    angle_jitter_deg: float = 30.0,
    rng: np.random.Generator | None = None,
) -> OperatorResult:
    """Cut a subtree fragment, offset/rotate it, then reconnect or keep dangling."""
    if not 0.0 <= break_ratio <= 1.0:
        raise ValueError("break_ratio must be in [0,1]")
    if not 0.0 <= reconnect_prob <= 1.0:
        raise ValueError("reconnect_prob must be in [0,1]")
    if break_ratio == 0.0:
        return OperatorResult(nodes=list(nodes), affected_node_ids=[])

    gen = _rng(rng)
    nmap = node_map(nodes)
    candidates = [n.node_id for n in nodes if n.parent_id != -1]
    if not candidates:
        return OperatorResult(nodes=list(nodes), affected_node_ids=[])

    break_count = max(1, int(math.ceil(len(candidates) * break_ratio)))
    chosen = gen.choice(np.array(candidates, dtype=np.int64), size=break_count, replace=False)
    cut_root = int(chosen[0])
    fragment_ids = _collect_subtree_node_ids(nodes, cut_root)

    if isinstance(offset, (tuple, list)):
        o0, o1 = _range_to_float_pair(offset)
        offset_mag = float(gen.uniform(o0, o1))
    else:
        offset_mag = float(offset)

    root = nmap[cut_root]
    root_xyz = np.array([root.x, root.y, root.z], dtype=np.float64)
    move_dir = sample_direction_in_cone(np.array([1.0, 0.0, 0.0]), angle_jitter_deg, rng=gen)
    delta = move_dir * offset_mag

    available_attach = [n.node_id for n in nodes if n.node_id not in fragment_ids]
    reconnect = (len(available_attach) > 0) and (float(gen.random()) < reconnect_prob)
    new_parent = int(gen.choice(np.array(available_attach, dtype=np.int64))) if reconnect else -1

    out: list[SWCNode] = []
    for n in nodes:
        if n.node_id in fragment_ids:
            p = np.array([n.x, n.y, n.z], dtype=np.float64) + delta
            parent_id = n.parent_id
            if n.node_id == cut_root:
                parent_id = new_parent
            out.append(
                SWCNode(
                    node_id=n.node_id,
                    node_type=n.node_type,
                    x=float(p[0]),
                    y=float(p[1]),
                    z=float(p[2]),
                    radius=n.radius,
                    parent_id=parent_id,
                )
            )
        else:
            out.append(n)
    _ = root_xyz
    return OperatorResult(nodes=out, affected_node_ids=sorted(fragment_ids))


def local_spur(*args, **kwargs) -> OperatorResult:
    """Alias of :func:`add_local_spur`."""
    return add_local_spur(*args, **kwargs)


def small_cluster_attach(*args, **kwargs) -> OperatorResult:
    """Alias of :func:`add_small_cluster_attach`."""
    return add_small_cluster_attach(*args, **kwargs)


def break_fragment_attach(*args, **kwargs) -> OperatorResult:
    """Alias of :func:`add_break_fragment_attach`."""
    return add_break_fragment_attach(*args, **kwargs)
