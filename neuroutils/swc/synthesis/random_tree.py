"""Random SWC tree generation utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.core.types import SWCNode
from neuroutils.io.swc import write_swc


def _rng(seed: int | None = None, rng: np.random.Generator | None = None) -> np.random.Generator:
    if rng is not None:
        return rng
    return np.random.default_rng(seed)


def _unit_random_vector(gen: np.random.Generator) -> np.ndarray:
    v = gen.normal(size=3)
    n = float(np.linalg.norm(v))
    if n < 1e-12:
        return np.array([1.0, 0.0, 0.0], dtype=np.float64)
    return v / n


def generate_random_tree_nodes(
    *,
    n_points: int,
    max_size_xyz: tuple[float, float, float] = (100.0, 100.0, 100.0),
    point_distance_range: tuple[float, float] = (1.0, 10.0),
    min_node_distance: float = 1.0,
    radius_range: tuple[float, float] = (0.8, 1.2),
    max_attempts_per_node: int = 500,
    seed: int | None = None,
    rng: np.random.Generator | None = None,
    edge_length_range: tuple[float, float] | None = None,
) -> list[SWCNode]:
    """Generate a random tree under size and spacing constraints.

    Args:
        n_points: Number of nodes in output tree.
        max_size_xyz: Max extent `(sx, sy, sz)` of coordinates.
            Generated coordinates are constrained in `[0, sx] x [0, sy] x [0, sz]`.
        point_distance_range: Parent-child point distance range `(min_len, max_len)`.
        min_node_distance: Minimum Euclidean distance between any two nodes.
        radius_range: Node radius range for random sampling.
        max_attempts_per_node: Retry cap per new node.
    """
    if n_points < 1:
        raise ValueError("n_points must be >= 1")
    sx, sy, sz = (float(max_size_xyz[0]), float(max_size_xyz[1]), float(max_size_xyz[2]))
    if sx <= 0 or sy <= 0 or sz <= 0:
        raise ValueError("max_size_xyz must be all positive")
    active_range = edge_length_range if edge_length_range is not None else point_distance_range
    min_len, max_len = float(active_range[0]), float(active_range[1])
    if min_len <= 0 or max_len <= 0 or min_len > max_len:
        raise ValueError("point_distance_range must satisfy 0 < min <= max")
    if min_node_distance < 0:
        raise ValueError("min_node_distance must be >= 0")
    rmin, rmax = float(radius_range[0]), float(radius_range[1])
    if rmin <= 0 or rmax <= 0 or rmin > rmax:
        raise ValueError("radius_range must satisfy 0 < min <= max")

    gen = _rng(seed=seed, rng=rng)
    center = np.array([sx * 0.5, sy * 0.5, sz * 0.5], dtype=np.float64)
    points = [center]
    parent_ids = [-1]
    radii = [float(gen.uniform(rmin, rmax))]

    for _ in range(1, n_points):
        accepted = False
        for _ in range(max_attempts_per_node):
            pidx = int(gen.integers(0, len(points)))
            parent = points[pidx]
            direction = _unit_random_vector(gen)
            length = float(gen.uniform(min_len, max_len))
            cand = parent + direction * length

            if not (0.0 <= cand[0] <= sx and 0.0 <= cand[1] <= sy and 0.0 <= cand[2] <= sz):
                continue

            if min_node_distance > 0:
                coords = np.asarray(points, dtype=np.float64)
                d2 = np.sum((coords - cand.reshape(1, 3)) ** 2, axis=1)
                if float(np.min(d2)) < (min_node_distance * min_node_distance):
                    continue

            points.append(cand)
            parent_ids.append(pidx + 1)
            radii.append(float(gen.uniform(rmin, rmax)))
            accepted = True
            break

        if not accepted:
            raise RuntimeError(
                "Failed to place a node under current constraints; "
                "relax min_node_distance/edge_length_range or enlarge max_size_xyz."
            )

    nodes: list[SWCNode] = []
    for i, p in enumerate(points, start=1):
        nodes.append(
            SWCNode(
                node_id=i,
                node_type=1 if i == 1 else 3,
                x=float(p[0]),
                y=float(p[1]),
                z=float(p[2]),
                radius=float(radii[i - 1]),
                parent_id=int(parent_ids[i - 1]),
            )
        )
    return nodes


def generate_random_tree_swc(
    output_swc: str | Path,
    *,
    n_points: int,
    max_size_xyz: tuple[float, float, float] = (100.0, 100.0, 100.0),
    point_distance_range: tuple[float, float] = (1.0, 10.0),
    min_node_distance: float = 1.0,
    radius_range: tuple[float, float] = (0.8, 1.2),
    max_attempts_per_node: int = 500,
    seed: int | None = None,
    edge_length_range: tuple[float, float] | None = None,
) -> list[SWCNode]:
    """Generate random tree and save as SWC."""
    nodes = generate_random_tree_nodes(
        n_points=n_points,
        max_size_xyz=max_size_xyz,
        point_distance_range=point_distance_range,
        min_node_distance=min_node_distance,
        radius_range=radius_range,
        max_attempts_per_node=max_attempts_per_node,
        seed=seed,
        edge_length_range=edge_length_range,
    )
    out = Path(output_swc)
    out.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "random_tree_generated_by_neuroutils",
        f"n_points={n_points}",
        f"max_size_xyz={tuple(float(v) for v in max_size_xyz)}",
        f"point_distance_range={tuple(float(v) for v in (edge_length_range if edge_length_range is not None else point_distance_range))}",
        f"min_node_distance={float(min_node_distance)}",
        f"seed={seed}",
    ]
    write_swc(out, nodes, header=header)
    return nodes
