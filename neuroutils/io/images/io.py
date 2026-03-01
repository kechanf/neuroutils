"""Image IO helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.io.images.pbd import load_v3dpbd
from neuroutils.io.images.v3draw import load_v3draw, save_v3draw


def load_npy_image(path: str | Path) -> np.ndarray:
    """Load image volume from .npy."""
    return np.load(Path(path))


def save_npy_image(path: str | Path, image: np.ndarray) -> None:
    """Save image volume to .npy."""
    np.save(Path(path), image)


def load_image(path: str | Path, *, flip_tif: bool = True) -> np.ndarray:
    """Load image from .npy/.v3draw/.v3dpbd/.tif/.tiff.

    For TIFF images, ``flip_tif=True`` applies Y-axis flip (axis -2) to
    match common SWC coordinate convention used in Vaa3D workflows.
    """
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".npy":
        return load_npy_image(p)
    if suffix == ".v3draw":
        return load_v3draw(p)
    if suffix == ".v3dpbd":
        return load_v3dpbd(p)
    if suffix in {".tif", ".tiff"}:
        try:
            import tifffile as tiff
        except ImportError as exc:
            raise RuntimeError("Loading TIFF requires tifffile. Install with: pip install tifffile") from exc
        img = np.asarray(tiff.imread(p))
        if flip_tif and img.ndim >= 2:
            img = np.flip(img, axis=-2).copy()
        return img
    raise ValueError(f"Unsupported image format: {suffix}")


def save_image(path: str | Path, image: np.ndarray, *, flip_tif: bool = True) -> None:
    """Save image to .npy/.v3draw/.tif/.tiff."""
    p = Path(path)
    suffix = p.suffix.lower()
    img = np.asarray(image)
    if suffix == ".npy":
        save_npy_image(p, img)
        return
    if suffix == ".v3draw":
        save_v3draw(img, p)
        return
    if suffix in {".tif", ".tiff"}:
        try:
            import tifffile as tiff
        except ImportError as exc:
            raise RuntimeError("Saving TIFF requires tifffile. Install with: pip install tifffile") from exc
        out = np.flip(img, axis=-2).copy() if flip_tif and img.ndim >= 2 else img
        tiff.imwrite(p, out)
        return
    raise ValueError(f"Unsupported image format: {suffix}")
