from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.validation.swc import (
    DuplicateNodesChecker,
    MultiSomaChecker,
    SWCChecker,
    TripletSomaChecker,
)


def test_swc_checker_passes_simple_tree() -> None:
    nodes = [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(2, 2, 1, 0, 0, 1, 1),
        SWCNode(3, 2, 2, 0, 0, 1, 2),
    ]
    out = SWCChecker().run(nodes)
    assert out.passed is True


def test_swc_checker_finds_errors() -> None:
    nodes = [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(2, 2, 0, 0, 0, 1, 0),
    ]
    out = SWCChecker().run(nodes)
    assert out.checks["ParentZeroIndex"] is False
    assert out.checks["DuplicateNodes"] is False


def test_legacy_checker_classes() -> None:
    nodes = [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(2, 3, 0, -1, 0, 1, 1),
        SWCNode(3, 3, 0, 1, 0, 1, 1),
    ]
    assert MultiSomaChecker()(nodes) is True
    assert DuplicateNodesChecker()(nodes) is True
    assert TripletSomaChecker()(nodes) is True
