"""Pairwise-distance based crossing candidate detection."""

from __future__ import annotations

import numpy as np

from neuroutils.morph_topo.morphology import Morphology


class PDist:
    """Detect potential crossing pairs by spatial proximity and tree linkage rules."""

    def __init__(self, *, ignore_radius_from_soma: float = 50.0, offspring_thresh: int = 10):
        self.ignore_radius_from_soma = ignore_radius_from_soma
        self.offspring_thresh = offspring_thresh
        self.morph: Morphology | None = None
        self.coords: np.ndarray | None = None
        self.idxs: np.ndarray | None = None

    def set_morph(self, morph: Morphology) -> None:
        self.morph = morph
        self.coords = np.array([node[2:5] for node in morph.tree], dtype=np.float64)
        self.idxs = np.array([node[0] for node in morph.tree], dtype=np.int64)

    def _require(self) -> tuple[Morphology, np.ndarray, np.ndarray]:
        if self.morph is None or self.coords is None or self.idxs is None:
            raise RuntimeError("Call set_morph(...) first")
        return self.morph, self.coords, self.idxs

    def get_soma_nearby_nodes(self) -> tuple[np.ndarray, np.ndarray]:
        morph, coords, idxs = self._require()
        soma = coords[morph.index_soma]
        dists = np.linalg.norm(coords - soma, axis=1)
        near = idxs[dists < self.ignore_radius_from_soma]
        away = idxs[dists >= self.ignore_radius_from_soma]
        return near, away

    def get_linkages_with_thresh(self) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
        morph, _, idxs = self._require()
        parent_dict: dict[int, set[int]] = {}
        for idx in idxs.tolist():
            leaf = morph.pos_dict[idx]
            os_id = 0
            cur_set: list[int] = []
            while os_id < self.offspring_thresh:
                pid = leaf[6]
                if pid not in morph.pos_dict:
                    break
                p_leaf = morph.pos_dict[pid]
                cur_set.append(p_leaf[0])
                leaf = p_leaf
                os_id += 1
            parent_dict[idx] = set(cur_set)

        offspring_dict: dict[int, set[int]] = {}
        for ofs, parents in parent_dict.items():
            for p_idx in parents:
                offspring_dict.setdefault(p_idx, set()).add(ofs)
        return parent_dict, offspring_dict

    def find_crossing_pairs(self, *, crossing_thresh: float = 3.0) -> dict[tuple[int, int], tuple[np.ndarray, np.ndarray]]:
        morph, coords, _ = self._require()
        nodes_away_soma = self.get_soma_nearby_nodes()[1].tolist()
        parent_dict, offspring_dict = self.get_linkages_with_thresh()
        tt = crossing_thresh * 1.5
        crossing_dict: dict[tuple[int, int], tuple[np.ndarray, np.ndarray]] = {}

        for idx in nodes_away_soma:
            cur_pos = coords[morph.index_dict[idx]]
            candidates = set(nodes_away_soma) - parent_dict[idx] - {idx}
            candidates -= offspring_dict.get(idx, set())
            if not candidates:
                continue
            cand_list = sorted(candidates)
            cand_coords = coords[[morph.index_dict[ii] for ii in cand_list]]
            d = np.linalg.norm(cand_coords - cur_pos.reshape(1, -1), axis=1)
            cross_ids = [cand_list[i] for i in np.nonzero(d < crossing_thresh)[0].tolist()]
            cross_coords = [cand_coords[i] for i in np.nonzero(d < crossing_thresh)[0].tolist()]

            # Filter by shared ancestors.
            filt_ids: list[int] = []
            filt_coords: list[np.ndarray] = []
            for iidx, icoord in zip(cross_ids, cross_coords):
                if len(parent_dict[idx].intersection(parent_dict[iidx])) > 0:
                    continue
                filt_ids.append(iidx)
                filt_coords.append(icoord)

            for iidx, icoord in zip(filt_ids, filt_coords):
                has_near_pair = False
                for _, pcs in crossing_dict.items():
                    if (
                        np.linalg.norm(cur_pos - pcs[0]) < tt and np.linalg.norm(icoord - pcs[1]) < tt
                    ) or (
                        np.linalg.norm(cur_pos - pcs[1]) < tt and np.linalg.norm(icoord - pcs[0]) < tt
                    ):
                        has_near_pair = True
                        break
                if not has_near_pair:
                    crossing_dict[(idx, iidx)] = (cur_pos, icoord)
        return crossing_dict
