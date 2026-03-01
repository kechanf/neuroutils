"""Topology and image-aware feature extraction."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.io.images import load_image
from neuroutils.morph_topo.morphology import Morphology, Topology
from neuroutils.swc.ops import scale_swc
from neuroutils.utils.math import included_angles_from_coords


def _find_point_by_distance_local(
    pt: np.ndarray,
    anchor_idx: int,
    is_parent: bool,
    morph: Morphology,
    dist: float,
    epsilon: float = 1e-7,
) -> np.ndarray:
    d = 0.0
    ci = np.array(pt, dtype=np.float64)
    cc = ci
    while d < dist:
        if anchor_idx not in morph.pos_dict:
            break
        cc = np.array(morph.pos_dict[anchor_idx][2:5], dtype=np.float64)
        d0 = float(np.linalg.norm(ci - cc))
        d += d0
        if d < dist:
            ci = cc
            if is_parent:
                anchor_idx = morph.pos_dict[anchor_idx][6]
            else:
                ch = morph.child_dict.get(anchor_idx, [])
                if not ch:
                    break
                anchor_idx = ch[0]
    dd = d - dist
    if dd < 0:
        return cc
    dcur = float(np.linalg.norm(cc - ci))
    return ci + (cc - ci) * (dcur - dd) / (dcur + epsilon)


class TopoFeatures:
    """Feature extraction from morphology and topology trees."""

    def __init__(self, swc: str | Path | list[SWCNode], *, line_length: float = 8.0, z_factor: float = 1.0):
        if isinstance(swc, (str, Path)):
            from neuroutils.io.swc import read_swc

            nodes = read_swc(swc)
        else:
            nodes = swc
        if z_factor != 1.0:
            nodes = scale_swc(nodes, (1.0, 1.0, z_factor))

        self.morph = Morphology(nodes)
        topo_tree, seg_dict = self.morph.convert_to_topology_tree()
        self.topo = Topology(topo_tree)
        self.seg_dict = seg_dict
        self.line_length = line_length

    def dists_to_soma(self, morph_lengths_dict: dict[int, float]) -> tuple[dict[int, float], dict[int, float]]:
        path_dists: dict[int, float] = {}

        def dfs(idx: int) -> None:
            if idx == self.morph.idx_soma:
                path_dists[idx] = 0.0
            else:
                pidx = self.morph.pos_dict[idx][6]
                path_dists[idx] = path_dists[pidx] + morph_lengths_dict.get(pidx, 0.0)
            for ch in self.morph.child_dict.get(idx, []):
                dfs(ch)

        dfs(self.morph.idx_soma)
        spatial_dists = {node[0]: float(d) for node, d in zip(self.morph.tree, self.morph.get_distances_to_soma())}
        return path_dists, spatial_dists

    def dists_to_parent_seg(
        self, morph_lengths_dict: dict[int, float], topo_lengths_dict: dict[int, float]
    ) -> tuple[dict[int, float], dict[int, float]]:
        path_dists = self.morph.calc_seg_path_lengths(self.seg_dict, morph_lengths_dict)
        return path_dists, topo_lengths_dict

    def get_angles(self) -> tuple[dict[int, float], dict[int, float]]:
        local = {self.morph.idx_soma: float(np.pi)}
        global_a = {self.morph.idx_soma: float(np.pi)}
        soma = np.array(self.morph.pos_dict[self.morph.idx_soma][2:5], dtype=np.float64)
        for seg_id, seg_nodes in self.seg_dict.items():
            if seg_id == self.topo.idx_soma:
                continue
            par_topo = self.topo.pos_dict[seg_id][6]
            if par_topo == self.morph.idx_soma:
                local[seg_id] = float(np.pi)
                global_a[seg_id] = float(np.pi)
                continue
            c = np.array(self.topo.pos_dict[par_topo][2:5], dtype=np.float64)
            start1 = seg_id if len(seg_nodes) == 0 else seg_nodes[-1]
            c1 = _find_point_by_distance_local(c, start1, False, self.morph, self.line_length)
            seg2 = self.seg_dict.get(par_topo, [])
            start2 = self.topo.pos_dict[par_topo][6] if len(seg2) == 0 else seg2[0]
            c2 = _find_point_by_distance_local(c, start2, True, self.morph, self.line_length)
            local[seg_id] = float(included_angles_from_coords(c, c1, c2, return_rad=True)[0])
            global_a[seg_id] = float(included_angles_from_coords(c, c1, soma, return_rad=True)[0])
        return local, global_a

    def get_num_childs(self) -> dict[int, tuple[int, int]]:
        out: dict[int, tuple[int, int]] = {}
        for idx in self.topo.pos_dict:
            pid = self.topo.pos_dict[idx][6]
            if idx == self.topo.idx_soma:
                out[idx] = (1, 0)
            else:
                parent_n = len(self.topo.child_dict.get(pid, []))
                cur_n = len(self.topo.child_dict.get(idx, []))
                out[idx] = (parent_n, cur_n)
        return out

    def calc_all_features(self) -> dict[str, dict[int, float] | dict[int, tuple[int, int]]]:
        _, morph_lengths = self.morph.calc_frag_lengths()
        _, topo_lengths = self.topo.calc_frag_lengths()
        self.topo.calc_order_dict()
        pd_soma, sd_soma = self.dists_to_soma(morph_lengths)
        pd_seg, sd_seg = self.dists_to_parent_seg(morph_lengths, topo_lengths)
        local_angs, global_angs = self.get_angles()
        return {
            "pdists_soma": pd_soma,
            "sdists_soma": sd_soma,
            "pdists_seg": pd_seg,
            "sdists_seg": sd_seg,
            "local_angs": local_angs,
            "global_angs": global_angs,
            "nchilds_dict": self.get_num_childs(),
            "order_dict": self.topo.order_dict,
        }


class TopoImFeatures:
    """Image-aware per-segment statistics."""

    def __init__(self, swc: str | Path | list[SWCNode], image: str | Path | np.ndarray):
        if isinstance(swc, (str, Path)):
            from neuroutils.io.swc import read_swc

            nodes = read_swc(swc)
        else:
            nodes = swc
        self.morph = Morphology(nodes)
        topo_tree, seg_dict = self.morph.convert_to_topology_tree()
        self.topo = Topology(topo_tree)
        self.seg_dict = seg_dict
        if isinstance(image, (str, Path)):
            self.img = load_image(image)
        else:
            self.img = np.asarray(image)

    def get_node_intensities(self, *, y_reversed: bool = True) -> dict[int, float]:
        out: dict[int, float] = {}
        yshape = int(self.img.shape[1]) if self.img.ndim >= 2 else 0
        for node in self.morph.tree:
            idx, _, x, y, z, _, _ = node
            xi, yi, zi = int(round(x)), int(round(y)), int(round(z))
            if self.img.ndim == 3:
                yi_read = yshape - yi - 1 if y_reversed else yi
                yi_read = int(np.clip(yi_read, 0, self.img.shape[1] - 1))
                xi = int(np.clip(xi, 0, self.img.shape[2] - 1))
                zi = int(np.clip(zi, 0, self.img.shape[0] - 1))
                out[idx] = float(self.img[zi, yi_read, xi])
            elif self.img.ndim == 2:
                yi_read = yshape - yi - 1 if y_reversed else yi
                yi_read = int(np.clip(yi_read, 0, self.img.shape[0] - 1))
                xi = int(np.clip(xi, 0, self.img.shape[1] - 1))
                out[idx] = float(self.img[yi_read, xi])
            else:
                out[idx] = 0.0
        return out

    def seg_intensities(self) -> dict[int, tuple[float, float, float, float]]:
        ints = self.get_node_intensities()
        out: dict[int, tuple[float, float, float, float]] = {}
        for seg_id, seg_nodes in self.seg_dict.items():
            vals = [ints[nid] for nid in seg_nodes if nid in ints]
            if not vals:
                out[seg_id] = (-1.0, -1.0, -1.0, -1.0)
            else:
                arr = np.array(vals, dtype=np.float64)
                out[seg_id] = (float(arr.max()), float(arr.min()), float(arr.mean()), float(np.median(arr)))
        return out

    def seg_radii(self) -> dict[int, tuple[float, float, float, float]]:
        radius = {node[0]: float(node[5]) for node in self.morph.tree}
        out: dict[int, tuple[float, float, float, float]] = {}
        for seg_id, seg_nodes in self.seg_dict.items():
            vals = [radius[nid] for nid in seg_nodes if nid in radius]
            if not vals:
                out[seg_id] = (-1.0, -1.0, -1.0, -1.0)
            else:
                arr = np.array(vals, dtype=np.float64)
                out[seg_id] = (float(arr.max()), float(arr.min()), float(arr.mean()), float(np.median(arr)))
        return out

    def calc_all_features(self) -> dict[str, dict[int, tuple[float, float, float, float]]]:
        return {"intensity": self.seg_intensities(), "radii": self.seg_radii()}
