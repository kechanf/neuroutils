from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.io.swc import read_swc, write_swc
from neuroutils.swc.synthesis import graft_branch_segment, graft_full_tree


def _root_id(nodes):
    for n in nodes:
        if n.parent_id == -1:
            return n.node_id
    return nodes[0].node_id


def main() -> None:
    in_dir = Path(r"E:\neuroutils\examples\auto8k_resampled_10um")
    out_dir = Path(r"E:\neuroutils\examples\auto8k_resampled_10um_synth_tmp")
    out_dir.mkdir(parents=True, exist_ok=True)

    swc_files = sorted(in_dir.glob("*.swc"))
    if len(swc_files) < 2:
        raise RuntimeError("Need at least 2 SWC files to generate synthetic graft samples.")

    target_path = swc_files[0]
    donor_path = swc_files[1]
    target_nodes = read_swc(target_path)
    donor_nodes = read_swc(donor_path)
    donor_root = _root_id(donor_nodes)

    full = graft_full_tree(
        target_nodes,
        donor_nodes,
        donor_attach_id=donor_root,
        rng=np.random.default_rng(20260309),
        apply_rotation=True,
    )
    full_out = out_dir / f"{target_path.stem}__synth_full_tree_graft.swc"
    write_swc(
        full_out,
        full.nodes,
        header=[
            "synthetic_strategy: full_tree_graft",
            f"target: {target_path.name}",
            f"donor: {donor_path.name}",
            "seed: 20260309",
        ],
    )

    seg = graft_branch_segment(
        target_nodes,
        donor_nodes,
        donor_attach_id=donor_root,
        max_hops=12,
        angle_limit_deg=45.0,
        rng=np.random.default_rng(20260310),
        apply_rotation=True,
    )
    seg_out = out_dir / f"{target_path.stem}__synth_branch_segment_graft.swc"
    write_swc(
        seg_out,
        seg.nodes,
        header=[
            "synthetic_strategy: branch_segment_graft",
            f"target: {target_path.name}",
            f"donor: {donor_path.name}",
            "seed: 20260310",
            "max_hops: 12",
            "angle_limit_deg: 45.0",
        ],
    )

    print(f"Generated: {full_out}")
    print(f"Generated: {seg_out}")


if __name__ == "__main__":
    main()
