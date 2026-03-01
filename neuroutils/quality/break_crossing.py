"""Break and crossing detection on morphology trees."""

from __future__ import annotations

import numpy as np

from neuroutils.morph_topo import Morphology
from neuroutils.utils.math import included_angles_from_vectors


def find_point_by_distance(
    pt: np.ndarray,
    anchor_idx: int,
    is_parent: bool,
    morph: Morphology,
    dist: float,
    return_center_point: bool = True,
    epsilon: float = 1e-7,
    spacing: tuple[float, float, float] = (1.0, 1.0, 1.0),
    stop_by_branch: bool = True,
    only_tgt_pt: bool = True,
) -> np.ndarray | tuple[np.ndarray, list[np.ndarray]]:
    """Trace along parent/child chain and return point around target geodesic distance."""
    d = 0.0
    ci = np.array(pt, dtype=np.float64)
    pts = [ci]
    s = np.array(spacing, dtype=np.float64)
    cc = ci
    while d < dist:
        if anchor_idx not in morph.pos_dict:
            break
        cc = np.array(morph.pos_dict[anchor_idx][2:5], dtype=np.float64)
        d0 = float(np.linalg.norm((ci - cc) * s))
        d += d0
        if d < dist:
            ci = cc
            pts.append(cc)
            if is_parent:
                anchor_idx = morph.pos_dict[anchor_idx][6]
                if stop_by_branch and len(morph.child_dict.get(anchor_idx, [])) > 1:
                    break
            else:
                ch = morph.child_dict.get(anchor_idx, [])
                if (not ch) or (stop_by_branch and len(ch) > 1):
                    break
                anchor_idx = ch[0]

    dd = d - dist
    if dd < 0:
        pt_a = cc
    else:
        dcur = float(np.linalg.norm((cc - ci) * s))
        pt_a = ci + (cc - ci) * (dcur - dd) / (dcur + epsilon)
        pts.append(pt_a)
    if return_center_point:
        pt_a = np.mean(np.array(pts), axis=0)
    if only_tgt_pt:
        return pt_a
    return pt_a, pts


class BreakFinder:
    def __init__(
        self,
        morph: Morphology,
        *,
        soma_radius: float = 30.0,
        dist_thresh: float = 4.0,
        line_length: float = 5.0,
        angle_thresh: float = 90.0,
        spacing: tuple[float, float, float] = (1.0, 1.0, 1.0),
    ):
        self.morph = morph
        self.soma_radius = soma_radius
        self.dist_thresh = dist_thresh
        self.line_length = line_length
        self.angle_thresh = angle_thresh
        self.spacing = np.array(spacing, dtype=np.float64)

    def find_break_pairs(self) -> dict[tuple[int, int], tuple[float, float]]:
        tips = list(self.morph.tips)
        soma = np.array(self.morph.pos_dict[self.morph.idx_soma][2:5], dtype=np.float64)
        tip_list = []
        for tip in tips:
            c = np.array(self.morph.pos_dict[tip][2:5], dtype=np.float64)
            if np.linalg.norm((soma - c) * self.spacing) >= self.soma_radius:
                tip_list.append(tip)

        out: dict[tuple[int, int], tuple[float, float]] = {}
        for i, t1 in enumerate(tip_list):
            c1 = np.array(self.morph.pos_dict[t1][2:5], dtype=np.float64)
            for t2 in tip_list[i + 1 :]:
                c2 = np.array(self.morph.pos_dict[t2][2:5], dtype=np.float64)
                dist = float(np.linalg.norm((c1 - c2) * self.spacing))
                if dist > self.dist_thresh:
                    continue
                p1 = self.morph.pos_dict[t1][6]
                p2 = self.morph.pos_dict[t2][6]
                pt1 = find_point_by_distance(c1, p1, True, self.morph, self.line_length, return_center_point=False)
                pt2 = find_point_by_distance(c2, p2, True, self.morph, self.line_length, return_center_point=False)
                v1 = np.asarray(pt1) - c1
                v2 = np.asarray(pt2) - c2
                ang = float(included_angles_from_vectors(v1, v2)[0])
                if ang > self.angle_thresh:
                    out[(t1, t2)] = (ang, dist)
        return out


class CrossingFinder:
    def __init__(
        self,
        morph: Morphology,
        *,
        soma_radius: float = 30.0,
        dist_thresh: float = 3.0,
        spacing: tuple[float, float, float] = (1.0, 1.0, 1.0),
        epsilon: float = 1e-7,
    ):
        self.morph = morph
        self.soma_radius = soma_radius
        self.dist_thresh = dist_thresh
        self.spacing = np.array(spacing, dtype=np.float64)
        self.epsilon = epsilon

    def find_crossing_pairs(self) -> tuple[list[int], list[tuple[int, int, float]]]:
        pairs: list[tuple[int, int, float]] = []
        points: list[int] = []
        m = self.morph
        soma = np.array(m.pos_dict[m.idx_soma][2:5], dtype=np.float64)
        used: set[int] = set()
        pset: set[int] = set()

        for tid in m.tips:
            idx = tid
            pre_tip = None
            cur_tip = None
            while idx != m.idx_soma and idx != -1:
                ch = m.child_dict.get(idx, [])
                if len(ch) >= 2:
                    pre_tip = cur_tip
                    cur_tip = idx
                    if pre_tip is not None:
                        if pre_tip in used:
                            break
                        used.add(pre_tip)
                        c0 = np.array(m.pos_dict[cur_tip][2:5], dtype=np.float64)
                        c1 = np.array(m.pos_dict[pre_tip][2:5], dtype=np.float64)
                        if np.linalg.norm((c0 - soma) * self.spacing) > self.soma_radius:
                            dist = float(np.linalg.norm((c0 - c1) * self.spacing))
                            ct = (c0 + c1) / 2.0
                            if np.linalg.norm(ct - soma) > self.epsilon and dist < self.dist_thresh:
                                pairs.append((pre_tip, cur_tip, dist))
                                pset.add(pre_tip)
                                pset.add(cur_tip)
                idx = m.pos_dict[idx][6]

        for idx, ch in m.child_dict.items():
            if len(ch) > 2 and idx not in pset:
                c = np.array(m.pos_dict[idx][2:5], dtype=np.float64)
                if np.linalg.norm((c - soma) * self.spacing) > self.soma_radius:
                    points.append(idx)
                    pset.add(idx)
        return points, pairs
