"""Neurite shape descriptors from SWC and image."""

from __future__ import annotations

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.io.images import load_image
from neuroutils.io.swc import read_swc
from neuroutils.morph_topo.morphology import Morphology
from neuroutils.swc.pruning import trim_swc


class AbstractNeuriteShape:
    """Branch-level utilities based on morphology."""

    def __init__(self, morph: Morphology):
        self.morph = morph
        if not hasattr(self.morph, "tips"):
            self.morph.get_critical_points()

    def get_branch_dict(self) -> dict[int, list[int]]:
        branch_dict: dict[int, list[int]] = {}
        nodes_with_parents = self.morph.tips | self.morph.multifurcation
        for midx in nodes_with_parents:
            up_nodes: list[int] = []
            idx = midx
            while idx in self.morph.pos_dict:
                pidx = self.morph.pos_dict[idx][6]
                up_nodes.append(pidx)
                if pidx not in self.morph.unifurcation:
                    break
                idx = pidx
            branch_dict[midx] = up_nodes
        return branch_dict

    def resample_tree(self) -> list[tuple[int, int, float, float, float, float, int]]:
        """Split single-edge branches once by midpoint insertion."""
        branch_dict = self.get_branch_dict()
        new_pos_dict = dict(self.morph.pos_dict)
        idx_max = max(self.morph.pos_dict.keys()) + 1
        for idx, ups in branch_dict.items():
            if len(ups) != 1:
                continue
            pidx = ups[0]
            c = (np.array(new_pos_dict[idx][2:5]) + np.array(new_pos_dict[pidx][2:5])) / 2.0
            node = new_pos_dict[idx]
            new_pos_dict[idx] = (node[0], node[1], node[2], node[3], node[4], node[5], idx_max)
            new_pos_dict[idx_max] = (idx_max, node[1], float(c[0]), float(c[1]), float(c[2]), node[5], pidx)
            idx_max += 1
        return [it[-1] for it in sorted(new_pos_dict.items(), key=lambda x: x[0])]


class NeuriteShapeSingle:
    """Single-neuron shape descriptors from one SWC-image pair."""

    def __init__(
        self,
        swc: str | list[SWCNode],
        image: str | np.ndarray,
        *,
        use_local_maximal: bool = True,
        lsize: int = 2,
        normalize_image: bool = True,
    ):
        self.use_local_maximal = use_local_maximal
        self.lsize = lsize
        if isinstance(image, str):
            img = load_image(image)
        else:
            img = np.asarray(image)
        if normalize_image:
            dtype = img.dtype
            arr = img.astype(np.float32)
            arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-7)
            img = (arr * 255.0).astype(dtype)
        self.img = img[:, ::-1, :] if img.ndim == 3 else img[::-1, :]
        self.imgshape = self.img.shape
        self.resampled_tree = self.get_resampled_tree(swc)

    def get_resampled_tree(self, swc: str | list[SWCNode]) -> list[tuple[int, int, float, float, float, float, int]]:
        tree = read_swc(swc) if isinstance(swc, str) else swc
        trimmed = trim_swc(tree, shape_zyx=self.imgshape if len(self.imgshape) == 3 else (1, *self.imgshape))
        morph = Morphology(trimmed)
        ns = AbstractNeuriteShape(morph)
        resampled = ns.resample_tree()
        if not self.use_local_maximal or self.img.ndim != 3:
            return resampled
        s = self.lsize
        for i, node in enumerate(resampled):
            xi, yi, zi = map(int, map(round, node[2:5]))
            block = self.img[max(zi - s, 0) : zi + s + 1, max(yi - s, 0) : yi + s + 1, max(xi - s, 0) : xi + s + 1]
            if block.size == 0:
                continue
            mz, my, mx = np.unravel_index(int(np.argmax(block)), block.shape)
            zn = mz + max(zi - s, 0)
            yn = my + max(yi - s, 0)
            xn = mx + max(xi - s, 0)
            resampled[i] = (node[0], node[1], float(xn), float(yn), float(zn), node[5], node[6])
        return resampled

    def get_branch_intensity_dict(self) -> tuple[dict[int, float], dict[int, float]]:
        morph = Morphology(self.resampled_tree)
        ns = AbstractNeuriteShape(morph)
        branch_dict = ns.get_branch_dict()
        ins_dict: dict[int, float] = {}
        ins_std_dict: dict[int, float] = {}
        for idx, pidxs in branch_dict.items():
            if morph.idx_soma in pidxs:
                continue
            vals: list[float] = []
            for pi in pidxs[:-1]:
                x, y, z = np.round(morph.pos_dict[pi][2:5]).astype(int).tolist()
                z = int(np.clip(z, 0, self.img.shape[0] - 1))
                y = int(np.clip(y, 0, self.img.shape[1] - 1))
                x = int(np.clip(x, 0, self.img.shape[2] - 1))
                vals.append(float(self.img[z, y, x]))
            if not vals:
                continue
            arr = np.array(vals, dtype=np.float64)
            ins_dict[idx] = float(np.median(arr))
            if arr.shape[0] > 2:
                ins_std_dict[idx] = float(arr.std())
        self.morph = morph
        self.ins_dict = ins_dict
        self.ins_std_dict = ins_std_dict
        return ins_dict, ins_std_dict

    def get_branch_radius_dict(self) -> tuple[dict[int, float], dict[int, float]]:
        morph = Morphology(self.resampled_tree)
        ns = AbstractNeuriteShape(morph)
        branch_dict = ns.get_branch_dict()
        rad_dict: dict[int, float] = {}
        rad_std_dict: dict[int, float] = {}
        for idx, pidxs in branch_dict.items():
            if morph.idx_soma in pidxs:
                continue
            vals = [float(morph.pos_dict[pi][5]) for pi in pidxs[:-1]]
            if not vals:
                continue
            arr = np.array(vals, dtype=np.float64)
            rad_dict[idx] = float(np.median(arr))
            if arr.shape[0] > 2:
                rad_std_dict[idx] = float(arr.std())
        self.morph = morph
        self.rad_dict = rad_dict
        self.rad_std_dict = rad_std_dict
        return rad_dict, rad_std_dict
