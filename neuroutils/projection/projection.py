"""Projection matrix computation from SWC axons to atlas regions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from neuroutils.io.swc import read_swc


@dataclass(frozen=True, slots=True)
class ProjectionResult:
    """Projection matrix and labels."""

    matrix: np.ndarray
    neuron_labels: list[str]
    region_ids: list[int]


class Projection:
    """Projection matrix builder against a 3D region atlas."""

    def __init__(
        self,
        atlas: np.ndarray,
        *,
        use_two_hemispheres: bool = True,
        resample_scale: float = 8.0,
        atlas_voxel_um: float = 25.0,
        salient_regions: set[int] | None = None,
    ) -> None:
        atlas_arr = np.asarray(atlas)
        if atlas_arr.ndim != 3:
            raise ValueError("atlas must be 3D array in (z,y,x)")
        self.resample_scale = float(resample_scale)
        self.atlas_voxel_um = float(atlas_voxel_um)
        self.salient_regions = salient_regions

        if use_two_hemispheres:
            zdim = atlas_arr.shape[0]
            atlas_lr = np.zeros_like(atlas_arr, dtype=np.int64)
            atlas_lr[: zdim // 2] = atlas_arr[: zdim // 2]
            atlas_lr[zdim // 2 :] = -atlas_arr[zdim // 2 :].astype(np.int64)
            self.atlas = atlas_lr
        else:
            self.atlas = atlas_arr.astype(np.int64)

    def calc_proj_matrix(self, axon_files: list[str | Path]) -> ProjectionResult:
        """Compute neuron-region projection matrix."""
        zdim, ydim, xdim = self.atlas.shape
        regids = sorted(int(v) for v in np.unique(self.atlas) if int(v) != 0)
        rdict = {rid: i for i, rid in enumerate(regids)}
        neuron_labels = [Path(p).stem for p in axon_files]
        mat = np.zeros((len(axon_files), len(regids)), dtype=np.float64)

        for i, swc_file in enumerate(axon_files):
            nodes = read_swc(swc_file)
            if not nodes:
                continue
            soma = next((n for n in nodes if n.parent_id == -1), nodes[0])
            coords = np.array([[n.x, n.y, n.z] for n in nodes if n.parent_id != -1], dtype=np.float64)
            if coords.size == 0:
                continue
            coords = coords / self.atlas_voxel_um

            # Mirror to same hemisphere if soma is in second half of z-axis.
            if soma.z / self.atlas_voxel_um > (zdim / 2.0):
                coords[:, 2] = (zdim - 1) - coords[:, 2]

            xi = np.clip(np.round(coords[:, 0]).astype(np.int64), 0, xdim - 1)
            yi = np.clip(np.round(coords[:, 1]).astype(np.int64), 0, ydim - 1)
            zi = np.clip(np.round(coords[:, 2]).astype(np.int64), 0, zdim - 1)
            proj = self.atlas[zi, yi, xi]
            rids, rcnts = np.unique(proj[proj != 0], return_counts=True)
            for rid, cnt in zip(rids.tolist(), rcnts.tolist()):
                j = rdict.get(int(rid))
                if j is not None:
                    mat[i, j] = float(cnt)

        mat *= self.resample_scale

        if self.salient_regions:
            keep_mask = np.array([abs(rid) in self.salient_regions for rid in regids], dtype=bool)
            mat = mat[:, keep_mask]
            regids = [rid for rid, keep in zip(regids, keep_mask.tolist()) if keep]

        return ProjectionResult(matrix=mat, neuron_labels=neuron_labels, region_ids=regids)


def preprocess_projections(
    result: ProjectionResult,
    *,
    min_proj: float = 1000.0,
    log: bool = True,
    remove_non_proj_neuron: bool = False,
    keep_only_salient_regions: bool = False,
    salient_regions: set[int] | None = None,
) -> ProjectionResult:
    """Post-process projection matrix with thresholding/filtering/log transform."""
    mat = np.array(result.matrix, copy=True, dtype=np.float64)
    labels = list(result.neuron_labels)
    regids = list(result.region_ids)

    if min_proj > 0:
        mat[mat < min_proj] = 0.0

    if keep_only_salient_regions and salient_regions:
        keep_mask = np.array([abs(rid) in salient_regions for rid in regids], dtype=bool)
        mat = mat[:, keep_mask]
        regids = [rid for rid, keep in zip(regids, keep_mask.tolist()) if keep]

    col_keep = np.sum(mat, axis=0) != 0
    mat = mat[:, col_keep]
    regids = [rid for rid, keep in zip(regids, col_keep.tolist()) if keep]

    if remove_non_proj_neuron:
        row_keep = np.sum(mat, axis=1) != 0
        mat = mat[row_keep]
        labels = [name for name, keep in zip(labels, row_keep.tolist()) if keep]

    if log:
        mat = np.log(mat + 1.0)

    return ProjectionResult(matrix=mat, neuron_labels=labels, region_ids=regids)
