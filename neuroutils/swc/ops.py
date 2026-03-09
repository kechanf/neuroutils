"""SWC utility operations."""

from __future__ import annotations

import re
from collections import deque
from pathlib import Path

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import node_map
from neuroutils.swc.pruning import remove_disconnected
from neuroutils.transforms import scale_nodes, shift_nodes

NEURITE_TYPES: dict[str, tuple[int, ...]] = {
    "soma": (1,),
    "axon": (2,),
    "basal_dendrite": (3,),
    "apical_dendrite": (4,),
    "dendrite": (3, 4),
}


def load_spacings_csv(path: str | Path, *, zxy_order: bool = False) -> dict[int, tuple[float, float, float]]:
    """Load per-brain spacing CSV: ``brain_id,x,y,z``."""
    spacing: dict[int, tuple[float, float, float]] = {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4 or not parts[0].isdigit():
            continue
        brain_id = int(parts[0])
        xyz = (float(parts[1]), float(parts[2]), float(parts[3]))
        if zxy_order:
            spacing[brain_id] = (xyz[2], xyz[0], xyz[1])
        else:
            spacing[brain_id] = xyz
    return spacing


def prune(nodes: list[SWCNode], keep_node_ids: set[int]) -> list[SWCNode]:
    """Keep only selected nodes and reroute parents to nearest kept ancestor."""
    id_map = node_map(nodes)
    keep = set(keep_node_ids)
    out: list[SWCNode] = []
    for n in nodes:
        if n.node_id not in keep:
            continue
        pid = n.parent_id
        while pid not in keep and pid in id_map and pid != -1:
            pid = id_map[pid].parent_id
        out.append(
            SWCNode(
                node_id=n.node_id,
                node_type=n.node_type,
                x=n.x,
                y=n.y,
                z=n.z,
                radius=n.radius,
                parent_id=pid if pid in keep or pid == -1 else -1,
            )
        )
    return out


def filter_neurite_types(nodes: list[SWCNode], type_ids: int | list[int] | tuple[int, ...]) -> list[SWCNode]:
    """Filter nodes by SWC type ids."""
    if isinstance(type_ids, int):
        allow = {type_ids}
    else:
        allow = set(type_ids)
    return [n for n in nodes if n.node_type in allow]


def get_specific_neurite(nodes: list[SWCNode], type_id: int | str) -> list[SWCNode]:
    """Filter one neurite class by type id or known type name."""
    if isinstance(type_id, str):
        key = type_id.lower()
        if key not in NEURITE_TYPES:
            raise ValueError(f"Unsupported neurite type: {type_id}")
        return filter_neurite_types(nodes, NEURITE_TYPES[key])
    return filter_neurite_types(nodes, type_id)


def flip_nodes_axis(nodes: list[SWCNode], *, axis: str, dim: float) -> list[SWCNode]:
    """Flip SWC nodes along one axis by ``coord' = dim - coord``."""
    if axis not in {"x", "y", "z"}:
        raise ValueError("axis must be one of: x,y,z")
    out: list[SWCNode] = []
    for n in nodes:
        x, y, z = n.x, n.y, n.z
        if axis == "x":
            x = dim - x
        elif axis == "y":
            y = dim - y
        else:
            z = dim - z
        out.append(
            SWCNode(
                node_id=n.node_id,
                node_type=n.node_type,
                x=x,
                y=y,
                z=z,
                radius=n.radius,
                parent_id=n.parent_id,
            )
        )
    return out


def get_soma_line_fast(path: str | Path, *, pattern: str = r".* -1\s*$") -> str | None:
    """Return first matched soma line from SWC file, else None."""
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(pattern, text, flags=re.MULTILINE)
    return m.group(0) if m is not None else None


def tree_to_voxels(nodes: list[SWCNode], shape_zyx: tuple[int, int, int]) -> np.ndarray:
    """Rasterize SWC edges into voxel coordinates array of shape (N,3) in xyz order."""
    depth, height, width = shape_zyx
    nmap = node_map(nodes)
    voxels: set[tuple[int, int, int]] = set()

    for n in nodes:
        if n.parent_id == -1 or n.parent_id not in nmap:
            continue
        p = nmap[n.parent_id]
        length = int(
            max(
                abs(n.x - p.x),
                abs(n.y - p.y),
                abs(n.z - p.z),
            )
        )
        nsteps = max(length, 1)
        for i in range(nsteps + 1):
            t = i / float(nsteps)
            x = int(round(p.x + (n.x - p.x) * t))
            y = int(round(p.y + (n.y - p.y) * t))
            z = int(round(p.z + (n.z - p.z) * t))
            if 0 <= x < width and 0 <= y < height and 0 <= z < depth:
                voxels.add((x, y, z))

    if not voxels:
        return np.zeros((0, 3), dtype=np.float32)
    out = np.array(sorted(voxels), dtype=np.float32)
    return out


def shift_swc(nodes: list[SWCNode], sx: float, sy: float, sz: float) -> list[SWCNode]:
    """Compatibility wrapper for SWC shift."""
    return shift_nodes(nodes, dx=-sx, dy=-sy, dz=-sz)


def scale_swc(nodes: list[SWCNode], scale: float | tuple[float, float, float]) -> list[SWCNode]:
    """Compatibility wrapper for SWC coordinate scaling."""
    if isinstance(scale, (float, int)):
        sx = sy = sz = float(scale)
    else:
        sx, sy, sz = float(scale[0]), float(scale[1]), float(scale[2])
    return scale_nodes(nodes, sx=sx, sy=sy, sz=sz, scale_radius=False)


def rm_disconnected(nodes: list[SWCNode], anchor: int) -> list[SWCNode]:
    """Compatibility wrapper for disconnected-component removal."""
    return remove_disconnected(nodes, anchor_id=anchor)


def _undirected_adjacency(nodes: list[SWCNode]) -> dict[int, set[int]]:
    adj: dict[int, set[int]] = {n.node_id: set() for n in nodes}
    ids = set(adj)
    for n in nodes:
        pid = n.parent_id
        if pid == -1 or pid not in ids:
            continue
        adj[n.node_id].add(pid)
        adj[pid].add(n.node_id)
    return adj


def _connected_components(adj: dict[int, set[int]]) -> list[set[int]]:
    comps: list[set[int]] = []
    seen: set[int] = set()
    for nid in sorted(adj):
        if nid in seen:
            continue
        stack = [nid]
        comp: set[int] = set()
        seen.add(nid)
        while stack:
            cur = stack.pop()
            comp.add(cur)
            for nb in adj[cur]:
                if nb in seen:
                    continue
                seen.add(nb)
                stack.append(nb)
        comps.append(comp)
    return comps


def reroot_forest_by_soma_ids(
    nodes: list[SWCNode],
    soma_node_ids: list[int] | tuple[int, ...] | set[int],
    *,
    set_soma_type: bool = True,
) -> tuple[list[SWCNode], list[int]]:
    """Reroot each connected component using manual/auto soma selection.

    Selection rule:
    - If a component contains any `soma_node_ids`, pick one of them (smallest id).
    - Otherwise choose the highest-degree node in that component; tie -> smallest id.

    Returns:
    - rerooted nodes (same node ids, updated parent ids)
    - resolved soma ids, one per connected component
    """
    if not nodes:
        return [], []

    nmap = node_map(nodes)
    manual = set(int(x) for x in soma_node_ids)
    missing = sorted(manual - set(nmap))
    if missing:
        raise ValueError(f"Manual soma node ids not found in SWC: {missing}")

    adj = _undirected_adjacency(nodes)
    comps = _connected_components(adj)
    new_parent: dict[int, int] = {}
    resolved_somas: list[int] = []

    for comp in comps:
        manual_here = sorted(nid for nid in comp if nid in manual)
        if manual_here:
            soma = manual_here[0]
        else:
            soma = min(comp, key=lambda nid: (-len(adj[nid]), nid))
        resolved_somas.append(soma)

        q: deque[int] = deque([soma])
        visited = {soma}
        new_parent[soma] = -1
        while q:
            cur = q.popleft()
            for nb in sorted(adj[cur]):
                if nb in visited:
                    continue
                visited.add(nb)
                new_parent[nb] = cur
                q.append(nb)

    out: list[SWCNode] = []
    soma_set = set(resolved_somas)
    for n in nodes:
        out.append(
            SWCNode(
                node_id=n.node_id,
                node_type=1 if (set_soma_type and n.node_id in soma_set) else n.node_type,
                x=n.x,
                y=n.y,
                z=n.z,
                radius=n.radius,
                parent_id=new_parent.get(n.node_id, -1),
            )
        )
    return out, resolved_somas
