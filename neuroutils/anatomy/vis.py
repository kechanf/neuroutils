"""Anatomy visualization helpers."""

from __future__ import annotations

import numpy as np

from neuroutils.imaging.preprocess import get_mip_image


def detect_edges2d(img2d: np.ndarray) -> np.ndarray:
    """Detect 2D edges by non-zero gradient magnitude."""
    img = img2d.astype(float)
    gx, gy = np.gradient(img)
    return (gx * gx + gy * gy) != 0


def detect_edges3d(img3d: np.ndarray) -> np.ndarray:
    """Detect 3D edges by non-zero gradient magnitude."""
    img = img3d.astype(float)
    gx, gy, gz = np.gradient(img)
    return (gx * gx + gy * gy + gz * gz) != 0


def get_section_boundary(mask: np.ndarray, *, axis: int = 0, c: int | None = None, v: int = 255) -> np.ndarray:
    """Return one section boundary map from 3D mask."""
    if c is None:
        c = int(mask.shape[axis] // 2)
    if axis == 0:
        section = mask[c]
    elif axis == 1:
        section = mask[:, c]
    elif axis == 2:
        section = mask[:, :, c]
    else:
        raise ValueError("axis must be one of 0/1/2")
    boundary = detect_edges2d(section)
    return boundary if v == 1 else boundary.astype(np.uint8) * v


def get_brain_outline2d(mask: np.ndarray, *, axis: int = 0, v: int = 255) -> np.ndarray:
    """2D outline from MIP mask."""
    mask2d = get_mip_image((mask > 0), axis=axis, mode="MAX")
    out = detect_edges2d(mask2d)
    return out if v == 1 else out.astype(np.uint8) * v


def get_brain_mask2d(mask: np.ndarray, *, axis: int = 0, v: int = 255) -> np.ndarray:
    """2D binary mask from MIP mask."""
    mask2d = get_mip_image((mask > 0), axis=axis, mode="MAX")
    return mask2d if v == 1 else mask2d.astype(np.uint8) * v


def get_section_boundary_with_outline(
    mask: np.ndarray,
    *,
    axis: int = 0,
    section_x: int | None = None,
    v: int = 255,
    fuse: bool = True,
) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
    """Section regional boundary and global outline."""
    boundary = get_section_boundary(mask, axis=axis, c=section_x, v=v)
    outline = get_brain_outline2d(mask, axis=axis, v=v)
    if fuse:
        return np.maximum(boundary, outline)
    return boundary, outline
