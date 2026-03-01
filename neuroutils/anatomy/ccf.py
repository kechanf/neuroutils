"""CCF coordinate conversion helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.io.images import load_image, save_image

RX_CCF25, RY_CCF25, RZ_CCF25 = 216, 18, 228
ROTATE_Z_DEG = 5.0
SCALE_Y = 0.9434


def matrix_from_axis_angle(a: tuple[float, float, float, float] | list[float] | np.ndarray) -> np.ndarray:
    """Compute rotation matrix from axis-angle (Rodrigues formula)."""
    ux, uy, uz, theta = map(float, a)
    c = float(np.cos(theta))
    s = float(np.sin(theta))
    ci = 1.0 - c
    return np.array(
        [
            [ci * ux * ux + c, ci * ux * uy - uz * s, ci * ux * uz + uy * s],
            [ci * uy * ux + uz * s, ci * uy * uy + c, ci * uy * uz - ux * s],
            [ci * uz * ux - uy * s, ci * uz * uy + ux * s, ci * uz * uz + c],
        ],
        dtype=np.float64,
    )


def ccf_to_stereotactic_mask_res25(
    mask: str | Path | np.ndarray,
    *,
    stereo_file: str | Path | None = None,
    rotate_z_deg: float = ROTATE_Z_DEG,
    scale_y: float = SCALE_Y,
) -> np.ndarray:
    """Convert CCF mask to stereotactic space by Z-rotation and Y scaling."""
    if isinstance(mask, (str, Path)):
        arr = np.asarray(load_image(mask, flip_tif=False))
    else:
        arr = np.asarray(mask)
    if arr.ndim != 3:
        raise ValueError("mask must be a 3D array")

    try:
        from scipy.ndimage import rotate, zoom
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("ccf_to_stereotactic_mask_res25 requires scipy") from exc

    rot = rotate(arr, angle=rotate_z_deg, axes=(2, 1), reshape=False, order=0, mode="constant", cval=0.0)
    out = zoom(rot, zoom=(1.0, scale_y, 1.0), order=0, mode="constant", cval=0.0)
    out = out.astype(arr.dtype, copy=False)
    if stereo_file is not None:
        save_image(stereo_file, out, flip_tif=False)
    return out


def resample(image: np.ndarray, transform: np.ndarray) -> np.ndarray:
    """Apply affine transform to a 3D image with nearest-neighbor sampling."""
    try:
        from scipy.ndimage import affine_transform
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("resample requires scipy") from exc
    arr = np.asarray(image)
    if arr.ndim != 3:
        raise ValueError("image must be a 3D array")
    m = np.asarray(transform, dtype=np.float64)
    if m.shape != (4, 4):
        raise ValueError("transform must be shape (4,4)")
    center = get_center(arr)
    offset = center - m[:3, :3] @ center - m[:3, 3]
    out = affine_transform(arr, matrix=m[:3, :3], offset=offset, order=0, mode="constant", cval=0.0)
    return out.astype(arr.dtype, copy=False)


def get_center(img: np.ndarray, w: int | None = None, h: int | None = None, d: int | None = None) -> np.ndarray:
    """Return center coordinate in xyz order."""
    arr = np.asarray(img)
    if w is None or h is None or d is None:
        d0, h0, w0 = arr.shape
        return np.array([w0 / 2.0, h0 / 2.0, d0 / 2.0], dtype=np.float64)
    return np.array([float(w) / 2.0, float(h) / 2.0, float(d) / 2.0], dtype=np.float64)


def ccf2stereotactic_mask_res25(mask_file: str | Path, stereo_file: str | Path | None = None) -> np.ndarray:
    """Compatibility alias for CCF->stereotactic conversion."""
    return ccf_to_stereotactic_mask_res25(mask_file, stereo_file=stereo_file)
