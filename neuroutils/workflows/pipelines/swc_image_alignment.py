"""SWC-image pair alignment workflows."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.io.images import load_image
from neuroutils.io.swc import read_swc, write_swc
from neuroutils.transforms.coordinates import AutoYFlipResult, auto_flip_nodes_y_by_intensity


def _load_image_array(path: str | Path) -> np.ndarray:
    arr = np.asarray(load_image(path))
    if arr.ndim == 4:
        return arr[0]
    return arr


def auto_flip_swc_y_for_image_pair(
    swc_path: str | Path,
    image_path: str | Path,
    *,
    output_swc_path: str | Path | None = None,
    min_improvement: float = 0.0,
    overwrite: bool = False,
) -> AutoYFlipResult:
    """Auto-flip SWC along Y when flipped nodes have higher mean voxel intensity.

    If ``overwrite`` is False and ``output_swc_path`` is None, output path defaults to
    ``<swc_stem>_autoflipy.swc`` beside the input SWC.
    """
    swc_in = Path(swc_path)
    img = _load_image_array(image_path)
    nodes = read_swc(swc_in)

    result = auto_flip_nodes_y_by_intensity(img, nodes, min_improvement=min_improvement)

    if output_swc_path is not None:
        swc_out = Path(output_swc_path)
    elif overwrite:
        swc_out = swc_in
    else:
        swc_out = swc_in.with_name(f"{swc_in.stem}_autoflipy.swc")

    write_swc(swc_out, result.nodes)
    return result
