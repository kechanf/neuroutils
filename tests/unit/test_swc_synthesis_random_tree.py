from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.io.swc import read_swc
from neuroutils.swc.synthesis import generate_random_tree_nodes, generate_random_tree_swc


def test_generate_random_tree_nodes_constraints() -> None:
    nodes = generate_random_tree_nodes(
        n_points=40,
        max_size_xyz=(60.0, 70.0, 80.0),
        edge_length_range=(2.5, 6.5),
        min_node_distance=1.2,
        seed=123,
    )
    assert len(nodes) == 40
    assert nodes[0].parent_id == -1

    nmap = {n.node_id: n for n in nodes}
    coords = np.array([[n.x, n.y, n.z] for n in nodes], dtype=np.float64)
    assert np.all(coords[:, 0] >= 0.0) and np.all(coords[:, 0] <= 60.0)
    assert np.all(coords[:, 1] >= 0.0) and np.all(coords[:, 1] <= 70.0)
    assert np.all(coords[:, 2] >= 0.0) and np.all(coords[:, 2] <= 80.0)

    for n in nodes[1:]:
        p = nmap[n.parent_id]
        d = float(np.linalg.norm(np.array([n.x - p.x, n.y - p.y, n.z - p.z])))
        assert 2.5 <= d <= 6.5

    for i in range(len(coords)):
        d2 = np.sum((coords[i + 1 :] - coords[i]) ** 2, axis=1) if i + 1 < len(coords) else np.array([])
        if d2.size > 0:
            assert float(np.min(d2)) >= (1.2 * 1.2)


def test_generate_random_tree_swc_write_and_read(tmp_path: Path) -> None:
    out = tmp_path / "rand_tree.swc"
    generate_random_tree_swc(
        out,
        n_points=20,
        max_size_xyz=(30.0, 30.0, 30.0),
        edge_length_range=(2.0, 4.0),
        min_node_distance=0.8,
        seed=7,
    )
    assert out.exists()
    nodes = read_swc(out)
    assert len(nodes) == 20
    assert nodes[0].parent_id == -1
