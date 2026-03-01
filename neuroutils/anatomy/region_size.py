"""Brain-region voxel size statistics."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np


def compute_region_voxel_stats(mask: np.ndarray, ana_tree: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute direct/descendant/total voxel counts per region."""
    arr = np.asarray(mask)
    if arr.ndim != 3:
        raise ValueError("mask must be 3D array")

    id_to_direct: dict[int, int] = {}
    unique_ids, counts = np.unique(arr, return_counts=True)
    for uid, cnt in zip(unique_ids.tolist(), counts.tolist()):
        if int(uid) != 0:
            id_to_direct[int(uid)] = int(cnt)

    id_to_descendants: dict[int, list[int]] = defaultdict(list)
    for region_id, info in ana_tree.items():
        path = info.get("structure_id_path", [])
        for anc in path[:-1]:
            id_to_descendants[int(anc)].append(int(region_id))

    results: list[dict[str, Any]] = []
    for region_id, info in ana_tree.items():
        rid = int(region_id)
        direct = id_to_direct.get(rid, 0)
        desc_ids = id_to_descendants.get(rid, [])
        desc_vox = sum(id_to_direct.get(int(did), 0) for did in desc_ids)
        results.append(
            {
                "id": rid,
                "acronym": info.get("acronym", ""),
                "name": info.get("name", ""),
                "direct_voxels": int(direct),
                "descendant_voxels": int(desc_vox),
                "total_voxels": int(direct + desc_vox),
            }
        )
    results.sort(key=lambda x: int(x["id"]))
    return results
