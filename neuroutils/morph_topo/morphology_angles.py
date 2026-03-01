"""Angle and curvature estimation on morphology."""

from __future__ import annotations

import numpy as np

from neuroutils.morph_topo.morphology import Morphology
from neuroutils.swc.ops import NEURITE_TYPES
from neuroutils.utils.math import included_angles_from_coords


class MorphAngles:
    def calc_outgrowth_angles(
        self,
        morph: Morphology,
        *,
        spacing: tuple[float, float, float] | None = None,
        indices_set: set[int] | None = None,
    ) -> np.ndarray:
        if indices_set is None:
            indices_set = set(morph.pos_dict.keys())

        cur = []
        par = []
        chi = []
        for idx in indices_set:
            pidx = morph.pos_dict[idx][6]
            if pidx not in morph.pos_dict or idx not in morph.child_dict:
                continue
            cc = morph.pos_dict[idx][2:5]
            pc = morph.pos_dict[pidx][2:5]
            for cidx in morph.child_dict[idx]:
                xc = morph.pos_dict[cidx][2:5]
                cur.append(cc)
                par.append(pc)
                chi.append(xc)
        if not cur:
            return np.zeros((0,), dtype=np.float64)
        return included_angles_from_coords(
            np.array(cur),
            np.array(par),
            np.array(chi),
            spacing=spacing,
        )


class MorphCurvature:
    def __init__(self, morph: Morphology, neurite_type: str = "all", spacing: tuple[float, float, float] | None = None):
        self.morph = morph
        self.neurite_type = neurite_type
        self.spacing = np.array(spacing, dtype=np.float64) if spacing is not None else None
        self.paths = self.morph.get_all_paths()

    def estimate_coplanarity(self, discard_multifurcate: bool = True, ignore_thresh: float = 0.05) -> dict[int, float]:
        npt = 4
        out: dict[int, float] = {}
        mf = self.morph.multifurcation | self.morph.bifurcation
        for tip, path in self.paths.items():
            coords = np.array([self.morph.pos_dict[idx][2:5] for idx in path], dtype=np.float64)
            mflags = [idx in mf for idx in path]
            if self.neurite_type != "all":
                nflags = [self.morph.pos_dict[idx][1] in NEURITE_TYPES[self.neurite_type] for idx in path]
            if len(path) < npt:
                continue
            pd1 = coords[1:] - coords[:-1]
            if self.spacing is not None:
                pd1 = pd1 * self.spacing.reshape(1, -1)
            pd1 = pd1 / (np.linalg.norm(pd1, axis=1, keepdims=True) + 1e-7)

            for i in range(len(path) - npt - 1):
                if discard_multifurcate and sum(mflags[i : i + npt]) > 0:
                    continue
                if self.neurite_type != "all" and sum(nflags[i : i + npt]) > 0:
                    continue
                cur_pd = pd1[i : i + npt - 1]
                nv1 = np.cross(cur_pd[0], cur_pd[1])
                nv2 = np.cross(cur_pd[1], cur_pd[2])
                n1 = np.linalg.norm(nv1)
                n2 = np.linalg.norm(nv2)
                if n1 < ignore_thresh or n2 < ignore_thresh:
                    continue
                cos_ang = float(np.clip(nv1.dot(nv2) / (n1 * n2), -1.0, 1.0))
                ang = float(np.arccos(cos_ang))
                out[path[i + 1]] = min(ang, float(np.pi - ang))
        return out

    def estimate_angular_dependence(self, discard_multifurcate: bool = True) -> dict[int, tuple[float, float]]:
        npt = 4
        out: dict[int, tuple[float, float]] = {}
        mf = self.morph.multifurcation | self.morph.bifurcation
        for tip, path in self.paths.items():
            coords = np.array([self.morph.pos_dict[idx][2:5] for idx in path], dtype=np.float64)
            mflags = [idx in mf for idx in path] if discard_multifurcate else [False] * len(path)
            if self.neurite_type != "all":
                nflags = [self.morph.pos_dict[idx][1] in NEURITE_TYPES[self.neurite_type] for idx in path]
            if len(path) < npt:
                continue
            pd1 = coords[1:] - coords[:-1]
            pd1 = pd1 / (np.linalg.norm(pd1, axis=1, keepdims=True) + 1e-7)
            for i in range(len(path) - npt - 1):
                if discard_multifurcate and sum(mflags[i : i + npt]) > 0:
                    continue
                if self.neurite_type != "all" and sum(nflags[i : i + npt]) > 0:
                    continue
                cur = pd1[i : i + npt - 1]
                a1 = float(np.arccos(np.clip((-cur[0]).dot(cur[1]), -1.0, 1.0)))
                a2 = float(np.arccos(np.clip((-cur[1]).dot(cur[2]), -1.0, 1.0)))
                out[path[i + 1]] = (a1, a2)
        return out
