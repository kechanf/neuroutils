from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.swc.base import find_soma_index, find_soma_node_id, index_map
from neuroutils.swc.ops import (
    filter_neurite_types,
    flip_nodes_axis,
    get_soma_line_fast,
    get_specific_neurite,
    load_spacings_csv,
    prune,
    reroot_forest_by_soma_ids,
    rm_disconnected,
    scale_swc,
    shift_swc,
    tree_to_voxels,
)
from neuroutils.swc.pruning import (
    crop_sphere_from_soma,
    crop_tree_by_bbox,
    prune_subtrees,
    trim_swc,
)


def test_base_soma_and_index_map() -> None:
    nodes = [SWCNode(1, 1, 0, 0, 0, 1, -1), SWCNode(2, 3, 1, 0, 0, 1, 1)]
    assert index_map(nodes) == {1: 0, 2: 1}
    assert find_soma_node_id(nodes) == 1
    assert find_soma_index(nodes) == 0


def test_load_spacings_and_filter_flip(tmp_path: Path) -> None:
    p = tmp_path / "spacings.csv"
    p.write_text("brain,x,y,z\n100,1.0,2.0,3.0\n", encoding="utf-8")
    spacing = load_spacings_csv(p)
    assert spacing[100] == (1.0, 2.0, 3.0)

    nodes = [SWCNode(1, 2, 2, 3, 4, 1, -1), SWCNode(2, 3, 5, 6, 7, 1, 1)]
    assert len(filter_neurite_types(nodes, 2)) == 1
    assert len(get_specific_neurite(nodes, "axon")) == 1
    fx = flip_nodes_axis(nodes, axis="y", dim=10.0)
    assert fx[0].y == 7.0


def test_get_soma_line_fast(tmp_path: Path) -> None:
    swc = tmp_path / "a.swc"
    swc.write_text("# c\n1 1 0 0 0 1 -1\n2 3 1 0 0 1 1\n", encoding="utf-8")
    line = get_soma_line_fast(swc)
    assert line is not None and line.endswith("-1")


def test_tree_to_voxels_and_pruning() -> None:
    nodes = [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(2, 3, 3, 0, 0, 1, 1),
        SWCNode(3, 3, 4, 0, 0, 1, 2),
    ]
    vox = tree_to_voxels(nodes, shape_zyx=(5, 5, 5))
    assert vox.shape[1] == 3
    assert np.any(np.all(vox == np.array([1.0, 0.0, 0.0]), axis=1))

    pruned = prune_subtrees(nodes, {2})
    assert [n.node_id for n in pruned] == [1]
    trimmed = trim_swc(nodes, shape_zyx=(5, 5, 5))
    assert len(trimmed) == 3

    shifted = shift_swc(nodes, sx=1.0, sy=2.0, sz=3.0)
    assert shifted[0].x == -1.0
    assert shifted[0].y == -2.0
    assert shifted[0].z == -3.0
    scaled = scale_swc(nodes, (2.0, 1.0, 1.0))
    assert scaled[1].x == 6.0
    connected = rm_disconnected(nodes, anchor=1)
    assert len(connected) == len(nodes)
    kept = prune(nodes, {1, 3})
    assert [n.node_id for n in kept] == [1, 3]
    assert kept[1].parent_id == 1


def test_crop_tree_by_bbox_and_sphere() -> None:
    nodes = [
        SWCNode(1, 1, 0, 0, 0, 1, -1),
        SWCNode(2, 3, 1, 0, 0, 1, 1),
        SWCNode(3, 3, 4, 0, 0, 1, 2),
    ]
    bbox = ((0.0, -1.0, -1.0), (1.0, 1.0, 2.0))
    cropped = crop_tree_by_bbox(nodes, bbox, keep_candidate_points=False)
    assert [n.node_id for n in cropped] == [1, 2]

    sphere = crop_sphere_from_soma(nodes, radius=2.1)
    assert [n.node_id for n in sphere] == [1, 2]


def test_reroot_forest_by_soma_ids_manual_and_auto() -> None:
    nodes = [
        SWCNode(1, 3, 0, 0, 0, 1, -1),
        SWCNode(2, 3, 1, 0, 0, 1, 1),
        SWCNode(3, 3, 2, 0, 0, 1, 2),
        SWCNode(4, 3, 10, 0, 0, 1, -1),
        SWCNode(5, 3, 11, 0, 0, 1, 4),
        SWCNode(6, 3, 10, 1, 0, 1, 4),
        SWCNode(7, 3, 10, -1, 0, 1, 4),
    ]
    out, somas = reroot_forest_by_soma_ids(nodes, soma_node_ids={3})
    by_id = {n.node_id: n for n in out}
    assert sorted(somas) == [3, 4]
    assert by_id[3].parent_id == -1
    assert by_id[2].parent_id == 3
    assert by_id[1].parent_id == 2
    assert by_id[4].parent_id == -1
    assert by_id[3].node_type == 1
    assert by_id[4].node_type == 1
