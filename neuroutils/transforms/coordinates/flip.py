"""Coordinate flip utilities for SWC nodes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from neuroutils.core.types import SWCNode


@dataclass(frozen=True, slots=True)
class AutoYFlipResult:
    """Decision payload for automatic SWC Y-axis flipping."""

    nodes: list[SWCNode]
    flipped: bool
    original_mean_intensity: float
    flipped_mean_intensity: float
    sampled_points: int


def flip_nodes_y(nodes: list[SWCNode], image_height: int) -> list[SWCNode]:
    """Flip SWC nodes along image Y axis.

    Uses pixel-center convention: y' = (image_height - 1) - y.
    """
    if image_height <= 0:
        raise ValueError("image_height must be positive")
    max_y = float(image_height - 1)
    return [
        SWCNode(
            node_id=n.node_id,
            node_type=n.node_type,
            x=n.x,
            y=max_y - n.y,
            z=n.z,
            radius=n.radius,
            parent_id=n.parent_id,
        )
        for n in nodes
    ]


def mean_intensity_at_nodes(image: np.ndarray, nodes: list[SWCNode]) -> tuple[float, int]:
    """Sample nearest-neighbor intensities at SWC nodes and return mean,count.

    Supported image layouts:
    - 2D: (y, x)
    - 3D: (z, y, x)
    """
    if image.ndim not in (2, 3):
        raise ValueError("image must be 2D (y,x) or 3D (z,y,x)")

    samples: list[float] = []
    if image.ndim == 2:
        height, width = image.shape
        for n in nodes:
            x = int(round(n.x))
            y = int(round(n.y))
            if 0 <= x < width and 0 <= y < height:
                samples.append(float(image[y, x]))
    else:
        depth, height, width = image.shape
        for n in nodes:
            x = int(round(n.x))
            y = int(round(n.y))
            z = int(round(n.z))
            if 0 <= x < width and 0 <= y < height and 0 <= z < depth:
                samples.append(float(image[z, y, x]))

    if not samples:
        return float("-inf"), 0
    return float(np.mean(samples)), len(samples)


def auto_flip_nodes_y_by_intensity(
    image: np.ndarray,
    nodes: list[SWCNode],
    *,
    min_improvement: float = 0.0,
) -> AutoYFlipResult:
    """Flip SWC on Y axis only when flipped nodes have higher mean voxel intensity."""
    if image.ndim not in (2, 3):
        raise ValueError("image must be 2D (y,x) or 3D (z,y,x)")
    height = int(image.shape[-2])
    original_mean, original_count = mean_intensity_at_nodes(image, nodes)
    flipped_nodes = flip_nodes_y(nodes, image_height=height)
    flipped_mean, flipped_count = mean_intensity_at_nodes(image, flipped_nodes)

    sampled_points = min(original_count, flipped_count)
    should_flip = (flipped_mean - original_mean) > min_improvement
    chosen_nodes = flipped_nodes if should_flip else nodes
    return AutoYFlipResult(
        nodes=chosen_nodes,
        flipped=should_flip,
        original_mean_intensity=original_mean,
        flipped_mean_intensity=flipped_mean,
        sampled_points=sampled_points,
    )
