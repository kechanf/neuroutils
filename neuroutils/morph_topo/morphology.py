"""Morphology/topology structures adapted from SWC trees."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.swc.ops import NEURITE_TYPES

SWCTuple = tuple[int, int, float, float, float, float, int]


def _to_tuple_tree(tree: list[SWCNode] | list[SWCTuple]) -> list[SWCTuple]:
    if not tree:
        return []
    first = tree[0]
    if isinstance(first, SWCNode):
        return [(n.node_id, n.node_type, n.x, n.y, n.z, n.radius, n.parent_id) for n in tree]  # type: ignore[arg-type]
    return [tuple(x[:7]) for x in tree]  # type: ignore[index]


@dataclass
class TreeInitializeError(RuntimeError):
    args: str


class AbstractTree:
    def __init__(self, tree: list[SWCNode] | list[SWCTuple], p_soma: int = -1):
        self.p_soma = p_soma
        self.tree: list[SWCTuple] = _to_tuple_tree(tree)
        if len(self.tree) == 0:
            raise TreeInitializeError("The tree contains no nodes")

        self.child_dict = self._get_child_dict(self.tree)
        self.index_dict = {leaf[0]: i for i, leaf in enumerate(self.tree)}
        self.pos_dict = {leaf[0]: leaf for leaf in self.tree}
        self.idx_soma = self.find_soma_node(self.tree, p_soma=self.p_soma)
        self.index_soma = self.find_soma_index(self.tree, p_soma=self.p_soma)

    @staticmethod
    def _get_child_dict(tree: list[SWCTuple]) -> dict[int, list[int]]:
        out: dict[int, list[int]] = {}
        for leaf in tree:
            pid = leaf[6]
            out.setdefault(pid, []).append(leaf[0])
        return out

    @staticmethod
    def find_soma_node(tree: list[SWCTuple], p_soma: int = -1) -> int:
        for leaf in tree:
            if leaf[6] == p_soma:
                return leaf[0]
        return -99

    @staticmethod
    def find_soma_index(tree: list[SWCTuple], p_soma: int = -1) -> int:
        for i, leaf in enumerate(tree):
            if leaf[6] == p_soma:
                return i
        return -99

    def get_nodes_by_types(self, neurite_type: str) -> set[int]:
        types = set(NEURITE_TYPES[neurite_type])
        return {node[0] for node in self.tree if node[1] in types}

    def get_volume_size(self) -> tuple[np.ndarray, float]:
        coords = np.array([leaf[2:5] for leaf in self.tree], dtype=np.float64)
        cmin = coords.min(axis=0)
        cmax = coords.max(axis=0)
        span = cmax - cmin
        return span, float(np.prod(span))

    def calc_node_distances(self, spacing: tuple[float, float, float] = (1.0, 1.0, 4.0)) -> tuple[float, float, float, float]:
        c1 = []
        c2 = []
        for idx in self.child_dict:
            if idx == self.p_soma:
                continue
            p = self.pos_dict[idx][2:5]
            for ch in self.child_dict[idx]:
                c1.append(p)
                c2.append(self.pos_dict[ch][2:5])
        if not c1:
            return 0.0, 0.0, 0.0, 0.0
        shift = (np.array(c2) - np.array(c1)) * np.array(spacing).reshape(1, -1)
        d = np.linalg.norm(shift, axis=1)
        return float(d.mean()), float(d.std()), float(d.max()), float(d.min())

    def get_distances_to_soma(self, spacing: tuple[float, float, float] = (1.0, 1.0, 1.0)) -> np.ndarray:
        soma = np.array(self.pos_dict[self.idx_soma][2:5], dtype=np.float64)
        coords = np.array([leaf[2:5] for leaf in self.tree], dtype=np.float64)
        return np.linalg.norm((coords - soma) * np.array(spacing).reshape(1, -1), axis=1)

    def get_critical_points(self) -> None:
        if len(self.tree) == 0:
            self.stems = set()
            self.tips = set()
            self.unifurcation = set()
            self.bifurcation = set()
            self.multifurcation = set()
            return

        self.stems = set(self.child_dict.get(self.idx_soma, []))
        all_nodes = {leaf[0] for leaf in self.tree}
        has_child = set(self.child_dict.keys())
        self.tips = all_nodes - has_child

        uni: list[int] = []
        bi: list[int] = []
        multi: list[int] = []
        for idx, ch in self.child_dict.items():
            if idx in (self.p_soma, self.idx_soma):
                continue
            if len(ch) == 1:
                uni.append(idx)
            elif len(ch) == 2:
                bi.append(idx)
            elif len(ch) > 2:
                multi.append(idx)
        self.unifurcation = set(uni)
        self.bifurcation = set(bi)
        self.multifurcation = set(multi)

    def get_all_paths(self) -> dict[int, list[int]]:
        if not hasattr(self, "tips"):
            self.get_critical_points()
        paths: dict[int, list[int]] = {}
        for tip in self.tips:
            path = [tip]
            leaf = self.pos_dict[tip]
            while leaf[6] in self.pos_dict:
                pid = leaf[6]
                path.append(pid)
                leaf = self.pos_dict[pid]
            paths[tip] = path
        return paths

    def calc_frag_lengths(self) -> tuple[np.ndarray, dict[int, float]]:
        pcoords = []
        for leaf in self.tree:
            if leaf[6] != self.p_soma:
                pcoords.append(self.pos_dict[leaf[6]][2:5])
            else:
                pcoords.append(self.pos_dict[self.idx_soma][2:5])
        coords = np.array([leaf[2:5] for leaf in self.tree], dtype=np.float64)
        pcoords_a = np.array(pcoords, dtype=np.float64)
        lengths = np.linalg.norm(coords - pcoords_a, axis=1)
        d = {idx: float(length) for idx, length in zip([leaf[0] for leaf in self.tree], lengths)}
        return lengths, d

    def calc_total_length(self) -> float:
        lengths, _ = self.calc_frag_lengths()
        return float(lengths.sum())


class Morphology(AbstractTree):
    def __init__(self, tree: list[SWCNode] | list[SWCTuple], p_soma: int = -1):
        super().__init__(tree, p_soma=p_soma)
        self.get_critical_points()

    def get_path_idx_dict(self) -> dict[int, list[int]]:
        path_dict: dict[int, list[int]] = {self.idx_soma: []}

        def dfs(idx: int) -> None:
            if idx not in self.child_dict:
                return
            for cidx in self.child_dict[idx]:
                path_dict[cidx] = path_dict[idx] + [idx]
                dfs(cidx)

        dfs(self.idx_soma)
        return path_dict

    def get_path_len_dict(self, path_dict: dict[int, list[int]], frag_lengths: np.ndarray) -> dict[int, float]:
        out: dict[int, float] = {}
        for idx, pids in path_dict.items():
            indices = [self.index_dict[pid] for pid in pids]
            out[idx] = float(frag_lengths[indices].sum()) if indices else 0.0
        return out

    def calc_seg_path_lengths(self, seg_dict: dict[int, list[int]], frag_lengths_dict: dict[int, float]) -> dict[int, float]:
        out = {self.idx_soma: 0.0}
        for seg_id, seg_nodes in seg_dict.items():
            out[seg_id] = frag_lengths_dict.get(seg_id, 0.0) + sum(
                frag_lengths_dict.get(nid, 0.0) for nid in seg_nodes
            )
        return out

    def convert_to_topology_tree(self, debug: bool = False) -> tuple[list[SWCTuple], dict[int, list[int]]]:
        def update_node(old: SWCTuple, new_parent: int) -> SWCTuple:
            return (old[0], old[1], old[2], old[3], old[4], old[5], new_parent)

        seg_dict: dict[int, list[int]] = {}
        new_tree: list[SWCTuple] = []
        for tip in self.tips:
            seg_dict[tip] = []
            cur = tip
            seg_start = tip
            while True:
                par = self.pos_dict[cur][6]
                if par == -1:
                    break
                if par in self.unifurcation:
                    seg_dict[seg_start].append(par)
                else:
                    new_tree.append(update_node(self.pos_dict[seg_start], par))
                    if par in seg_dict:
                        break
                    seg_dict[par] = []
                    seg_start = par
                cur = par
        for node in self.tree:
            if node[6] == -1:
                new_tree.append(node)
        if debug:
            _ = (len(new_tree), len(self.tree))
        return new_tree, seg_dict


class Topology(AbstractTree):
    def __init__(self, tree: list[SWCNode] | list[SWCTuple], p_soma: int = -1):
        super().__init__(tree, p_soma=p_soma)
        self.get_critical_points()

    def calc_order_dict(self) -> None:
        order: dict[int, int] = {}
        roots = [n[0] for n in self.tree if n[6] == -1]
        for root in roots:
            order[root] = 0
            stack = [root]
            while stack:
                head = stack.pop()
                for ch in self.child_dict.get(head, []):
                    order[ch] = order[head] + 1
                    stack.append(ch)
        self.order_dict = order

    def get_num_branches(self) -> int:
        return max(len(self.tree) - 1, 0)

    def get_topo_width(self) -> int:
        if not hasattr(self, "order_dict"):
            self.calc_order_dict()
        order_freq: dict[int, int] = {}
        split_nodes = self.multifurcation | self.bifurcation
        for idx, order in self.order_dict.items():
            order_freq.setdefault(order, 0)
            if idx == self.p_soma:
                order_freq[order] = 1
            elif idx in split_nodes:
                order_freq[order] += 1
        self.order_freq_dict = order_freq
        self.topo_width = max(order_freq.values()) if order_freq else 0
        return self.topo_width

    def get_topo_depth(self) -> int:
        if not hasattr(self, "order_dict"):
            self.calc_order_dict()
        self.topo_depth = max(self.order_dict.values()) if self.order_dict else 0
        return self.topo_depth
