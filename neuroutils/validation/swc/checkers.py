"""SWC quality checkers."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby
from pathlib import Path

from neuroutils.core.types import SWCNode
from neuroutils.io.swc import read_swc
from neuroutils.swc.base import children_map


class AbstractErrorChecker:
    """Legacy checker base class."""

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug


class MultiSomaChecker(AbstractErrorChecker):
    def __call__(self, nodes: list[SWCNode]) -> bool:
        return check_multi_soma(nodes)


class NoSomaChecker(AbstractErrorChecker):
    def __call__(self, nodes: list[SWCNode]) -> bool:
        return check_no_soma(nodes)


class ParentZeroIndexChecker(AbstractErrorChecker):
    def __call__(self, nodes: list[SWCNode]) -> bool:
        return check_parent_zero_index(nodes)


class MultifurcationChecker(AbstractErrorChecker):
    def __call__(self, nodes: list[SWCNode]) -> bool:
        return check_multifurcation(nodes)


class TypeErrorChecker(AbstractErrorChecker):
    def __init__(self, debug: bool = False, ignore_3_4: bool = True) -> None:
        super().__init__(debug=debug)
        self.ignore_3_4 = ignore_3_4

    def __call__(self, nodes: list[SWCNode]) -> bool:
        return check_type_error(nodes, ignore_3_4=self.ignore_3_4)


class DuplicateNodesChecker(AbstractErrorChecker):
    def __call__(self, nodes: list[SWCNode]) -> bool:
        return check_duplicate_nodes(nodes)


class SingleTreeChecker(AbstractErrorChecker):
    def __call__(self, nodes: list[SWCNode]) -> bool:
        return check_single_tree(nodes)


class TripletSomaChecker(AbstractErrorChecker):
    """Check canonical triplet-soma layout for ids 1/2/3."""

    def __call__(self, nodes: list[SWCNode]) -> bool:
        nmap = {n.node_id: n for n in nodes}
        if not all(k in nmap for k in (1, 2, 3)):
            return False
        n1, n2, n3 = nmap[1], nmap[2], nmap[3]
        if not (n1.parent_id == -1 and n2.parent_id == 1 and n3.parent_id == 1):
            return False
        eps = 1e-5
        return (
            abs(n1.x - n2.x) < eps
            and abs(n1.x - n3.x) < eps
            and abs(n1.z - n2.z) < eps
            and abs(n1.z - n3.z) < eps
            and abs((n1.y - n2.y) - n1.radius) < eps
            and abs((n1.y - n3.y) + n1.radius) < eps
        )


def check_multi_soma(nodes: list[SWCNode]) -> bool:
    return sum(1 for n in nodes if n.parent_id == -1) <= 1


def check_no_soma(nodes: list[SWCNode]) -> bool:
    return any(n.parent_id == -1 for n in nodes)


def check_parent_zero_index(nodes: list[SWCNode]) -> bool:
    return all(n.parent_id != 0 for n in nodes)


def check_multifurcation(nodes: list[SWCNode]) -> bool:
    cmap = children_map(nodes)
    return all(len(ch) <= 2 for ch in cmap.values())


def check_duplicate_nodes(nodes: list[SWCNode]) -> bool:
    coords = {(n.x, n.y, n.z) for n in nodes}
    return len(coords) == len(nodes)


def check_single_tree(nodes: list[SWCNode]) -> bool:
    ids = [n.node_id for n in nodes]
    if len(ids) != len(set(ids)):
        return False
    roots = [n.node_id for n in nodes if n.parent_id == -1]
    if len(roots) != 1:
        return False
    root = roots[0]
    id_set = set(ids)
    for n in nodes:
        if n.node_id == n.parent_id:
            return False
        if n.parent_id != -1 and n.parent_id not in id_set:
            return False
    cmap = children_map(nodes)
    visited: set[int] = set()
    stack = [root]
    while stack:
        head = stack.pop()
        if head in visited:
            continue
        visited.add(head)
        stack.extend(cmap.get(head, []))
    return len(visited) == len(nodes)


def _all_root_to_leaf_paths(nodes: list[SWCNode]) -> list[list[int]]:
    cmap = children_map(nodes)
    roots = [n.node_id for n in nodes if n.parent_id == -1]
    if not roots:
        return []
    out: list[list[int]] = []
    stack: list[tuple[int, list[int]]] = [(roots[0], [roots[0]])]
    while stack:
        nid, path = stack.pop()
        ch = cmap.get(nid, [])
        if not ch:
            out.append(path)
            continue
        for c in ch:
            stack.append((c, path + [c]))
    return out


def check_type_error(nodes: list[SWCNode], *, ignore_3_4: bool = True) -> bool:
    nmap = {n.node_id: n for n in nodes}
    paths = _all_root_to_leaf_paths(nodes)
    for path in paths:
        types = [nmap[nid].node_type for nid in path[1:]]  # ignore soma node
        if not types:
            continue
        if ignore_3_4:
            types = [3 if t == 4 else t for t in types]
        groups = [k for k, _ in groupby(types)]
        num_switch = len(groups) - 1
        if num_switch > 1:
            return False
        if num_switch == 1:
            v1, v2 = groups[0], groups[1]
            if not (v1 == 2 and v2 in (3, 4, 3)):
                return False
    return True


@dataclass(frozen=True, slots=True)
class SWCCheckResult:
    checks: dict[str, bool]

    @property
    def passed(self) -> bool:
        return all(self.checks.values())


class SWCChecker:
    """Run configurable SWC quality checks."""

    ERROR_TYPES = (
        "MultiSoma",
        "NoSoma",
        "ParentZeroIndex",
        "Multifurcation",
        "TypeError",
        "DuplicateNodes",
        "SingleTree",
    )

    def __init__(
        self,
        error_types: tuple[str, ...] | list[str] | None = None,
        *,
        ignore_3_4: bool = False,
    ) -> None:
        self.error_types = tuple(error_types) if error_types is not None else self.ERROR_TYPES
        self.ignore_3_4 = ignore_3_4

    def run(self, swc: str | Path | list[SWCNode]) -> SWCCheckResult:
        if isinstance(swc, (str, Path)):
            nodes = read_swc(swc)
        else:
            nodes = swc

        checks: dict[str, bool] = {}
        for name in self.error_types:
            if name == "MultiSoma":
                checks[name] = check_multi_soma(nodes)
            elif name == "NoSoma":
                checks[name] = check_no_soma(nodes)
            elif name == "ParentZeroIndex":
                checks[name] = check_parent_zero_index(nodes)
            elif name == "Multifurcation":
                checks[name] = check_multifurcation(nodes)
            elif name == "TypeError":
                checks[name] = check_type_error(nodes, ignore_3_4=self.ignore_3_4)
            elif name == "DuplicateNodes":
                checks[name] = check_duplicate_nodes(nodes)
            elif name == "SingleTree":
                checks[name] = check_single_tree(nodes)
            else:
                raise ValueError(f"Unsupported error type: {name}")
        return SWCCheckResult(checks=checks)
