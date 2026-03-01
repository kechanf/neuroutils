"""Utilities on morphology structures."""

from __future__ import annotations

import numpy as np

from neuroutils.morph_topo.morphology import Morphology


def get_outside_soma_mask(morph: Morphology, dist_thresh: float) -> dict[int, bool]:
    """Return node-id mask for nodes outside sphere centered at soma."""
    soma = np.array(morph.pos_dict[morph.idx_soma][2:5], dtype=np.float64)
    coords = np.array([morph.pos_dict[node[0]][2:5] for node in morph.tree], dtype=np.float64)
    ids = [node[0] for node in morph.tree]
    d = np.linalg.norm(coords - soma, axis=1)
    mask = d > dist_thresh
    return {idx: bool(v) for idx, v in zip(ids, mask)}
