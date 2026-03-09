"""High-level one-call visualization helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.core.types import Marker, SWCNode
from neuroutils.io.images import load_image, save_image
from neuroutils.io.markers import read_markers
from neuroutils.io.swc import read_swc
from neuroutils.visualization.base import normalize_to_uint8
from neuroutils.visualization.plotting import project_volume
from neuroutils.visualization.segmentation import overlay_mask
from neuroutils.visualization.swc import draw_markers, draw_swc


def _coerce_image(data: np.ndarray | str | Path, *, flip_tif: bool) -> np.ndarray:
    if isinstance(data, (str, Path)):
        return np.asarray(load_image(data, flip_tif=flip_tif))
    return np.asarray(data)


def _coerce_mask(data: np.ndarray | str | Path | None, *, flip_tif: bool) -> np.ndarray | None:
    if data is None:
        return None
    if isinstance(data, (str, Path)):
        return np.asarray(load_image(data, flip_tif=flip_tif))
    return np.asarray(data)


def _coerce_swc(data: list[SWCNode] | str | Path | None) -> list[SWCNode]:
    if data is None:
        return []
    if isinstance(data, (str, Path)):
        return read_swc(data)
    return list(data)


def _coerce_markers(data: list[Marker] | str | Path | None) -> list[Marker]:
    if data is None:
        return []
    if isinstance(data, (str, Path)):
        return read_markers(data)
    return list(data)


def quick_plot(
    image: np.ndarray | str | Path,
    *,
    mask: np.ndarray | str | Path | None = None,
    swc: list[SWCNode] | str | Path | None = None,
    markers: list[Marker] | str | Path | None = None,
    projection: str = "xy",
    flip_tif: bool = True,
    mask_color: tuple[int, int, int] = (255, 0, 0),
    mask_alpha: float = 0.35,
    swc_line_color: tuple[int, int, int] = (255, 0, 0),
    swc_soma_color: tuple[int, int, int] = (0, 0, 255),
    marker_color: tuple[int, int, int] = (0, 255, 0),
    normalize_mip: bool = True,
    save_path: str | Path | None = None,
) -> np.ndarray:
    """Build one visualization image from image/mask/swc/marker inputs.

    The function accepts either already-loaded arrays/objects or file paths.
    """
    img = _coerce_image(image, flip_tif=flip_tif)
    base = project_volume(img, projection=projection)
    if normalize_mip:
        base = normalize_to_uint8(np.asarray(base))
    out = base

    mask_arr = _coerce_mask(mask, flip_tif=flip_tif)
    if mask_arr is not None:
        mask2d = project_volume(mask_arr, projection=projection) > 0 if mask_arr.ndim == 3 else mask_arr > 0
        out = overlay_mask(out, mask2d, color=mask_color, alpha=mask_alpha)

    swc_nodes = _coerce_swc(swc)
    if swc_nodes:
        out = draw_swc(
            out,
            swc_nodes,
            projection=projection,
            line_color=swc_line_color,
            soma_color=swc_soma_color,
        )

    marker_objs = _coerce_markers(markers)
    if marker_objs:
        out = draw_markers(out, marker_objs, projection=projection, color=marker_color)

    if save_path is not None:
        save_image(save_path, out, flip_tif=False)
    return out
