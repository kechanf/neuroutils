from __future__ import annotations

import numpy as np

from neuroutils.anatomy import compute_region_voxel_stats


def test_compute_region_voxel_stats() -> None:
    mask = np.zeros((2, 3, 3), dtype=np.int32)
    mask[:, :2, :2] = 1
    mask[:, 2:, 2:] = 2
    tree = {
        1: {"id": 1, "acronym": "A", "name": "A", "structure_id_path": [10, 1]},
        2: {"id": 2, "acronym": "B", "name": "B", "structure_id_path": [10, 2]},
        10: {"id": 10, "acronym": "R", "name": "Root", "structure_id_path": [10]},
    }
    out = compute_region_voxel_stats(mask, tree)
    d = {r["id"]: r for r in out}
    assert d[1]["direct_voxels"] > 0
    assert d[10]["descendant_voxels"] >= d[1]["direct_voxels"] + d[2]["direct_voxels"]
