"""Quality correction helpers for SWC."""

from __future__ import annotations

from pathlib import Path

from neuroutils.core.types import SWCNode
from neuroutils.io.swc import read_swc, write_swc
from neuroutils.swc.base import node_map


def remove_duplicate_parent_coordinate_nodes(nodes: list[SWCNode]) -> list[SWCNode]:
    """Remove nodes whose coordinates exactly equal their parent coordinates."""
    nmap = node_map(nodes)
    dup_ids: set[int] = set()
    for n in nodes:
        if n.parent_id == -1 or n.parent_id not in nmap:
            continue
        p = nmap[n.parent_id]
        if n.x == p.x and n.y == p.y and n.z == p.z:
            dup_ids.add(n.node_id)

    if not dup_ids:
        return list(nodes)

    out: list[SWCNode] = []
    remap = {nid: nmap[nid].parent_id for nid in dup_ids}
    for n in nodes:
        if n.node_id in dup_ids:
            continue
        pid = n.parent_id
        while pid in remap:
            pid = remap[pid]
        out.append(
            SWCNode(
                node_id=n.node_id,
                node_type=n.node_type,
                x=n.x,
                y=n.y,
                z=n.z,
                radius=n.radius,
                parent_id=pid,
            )
        )
    return out


def remove_duplicate_nodes_file(swc_in: str | Path, swc_out: str | Path | None = None) -> Path:
    """Remove duplicate-parent-coordinate nodes from SWC file."""
    src = Path(swc_in)
    dst = Path(swc_out) if swc_out is not None else src
    nodes = read_swc(src)
    out = remove_duplicate_parent_coordinate_nodes(nodes)
    write_swc(dst, out)
    return dst
