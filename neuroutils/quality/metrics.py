"""Quality metrics for neuron reconstructions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.io.swc import read_swc
from neuroutils.swc import tree_to_voxels
from neuroutils.utils.math import min_distances_between_sets


@dataclass(frozen=True, slots=True)
class DistanceMetrics:
    """Distance metrics in forward/backward/symmetric form."""

    esa: tuple[float, float, float]
    dsa: tuple[float, float, float]
    pds: tuple[float, float, float]


class DistanceEvaluation:
    """Distance-based evaluation between two SWC reconstructions."""

    def __init__(
        self,
        *,
        dsa_thr: float = 2.0,
        resample1: bool = True,
        resample2: bool = True,
        aggregation_type: str = "mean",
    ) -> None:
        self.dsa_thr = dsa_thr
        self.resample1 = resample1
        self.resample2 = resample2
        self.aggregation_type = aggregation_type

    def _aggregate(self, d1: np.ndarray, d2: np.ndarray) -> tuple[float, float, float]:
        if self.aggregation_type == "mean":
            a, b = float(np.mean(d1)), float(np.mean(d2))
            s = float((np.sum(d1) + np.sum(d2)) / (len(d1) + len(d2)))
            return a, b, s
        if self.aggregation_type == "median":
            a, b = float(np.median(d1)), float(np.median(d2))
            s = float((a + b) / 2.0)
            return a, b, s
        raise ValueError("aggregation_type must be 'mean' or 'median'")

    def calc_dist(self, voxels1: np.ndarray, voxels2: np.ndarray) -> DistanceMetrics:
        d1, d2 = min_distances_between_sets(voxels1, voxels2, reciprocal=True)
        dsa1 = d1[d1 > self.dsa_thr] if np.any(d1 > self.dsa_thr) else np.array([0.0])
        dsa2 = d2[d2 > self.dsa_thr] if np.any(d2 > self.dsa_thr) else np.array([0.0])
        pds1 = (d1 > self.dsa_thr).astype(np.float64)
        pds2 = (d2 > self.dsa_thr).astype(np.float64)
        return DistanceMetrics(
            esa=self._aggregate(d1, d2),
            dsa=self._aggregate(dsa1, dsa2),
            pds=self._aggregate(pds1, pds2),
        )

    def run(self, recon: str | list[SWCNode], gt: str | list[SWCNode]) -> DistanceMetrics:
        tree1 = read_swc(recon) if isinstance(recon, str) else recon
        tree2 = read_swc(gt) if isinstance(gt, str) else gt
        vox1 = (
            tree_to_voxels(tree1, shape_zyx=(10000, 10000, 10000))
            if self.resample1
            else np.array([[n.x, n.y, n.z] for n in tree1], dtype=np.float64)
        )
        vox2 = (
            tree_to_voxels(tree2, shape_zyx=(10000, 10000, 10000))
            if self.resample2
            else np.array([[n.x, n.y, n.z] for n in tree2], dtype=np.float64)
        )
        if vox1.shape[0] == 0 or vox2.shape[0] == 0:
            raise ValueError("Empty voxel set after conversion")
        return self.calc_dist(vox1, vox2)
