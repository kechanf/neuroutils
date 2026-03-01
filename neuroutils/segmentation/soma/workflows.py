"""Middle-layer soma detection workflows."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

from neuroutils.segmentation.soma.detection import largest_component_bbox, mask_centroid


@dataclass(frozen=True, slots=True)
class SomaDetectionResult:
    """Structured soma-region detection output."""

    centroid_zyx: tuple[float, float, float]
    bbox_zyxzyx: tuple[int, int, int, int, int, int]
    voxel_count: int
    soma_mask: np.ndarray


def _iter_neighbors_6(z: int, y: int, x: int, shape: tuple[int, int, int]):
    zmax, ymax, xmax = shape
    if z > 0:
        yield z - 1, y, x
    if z + 1 < zmax:
        yield z + 1, y, x
    if y > 0:
        yield z, y - 1, x
    if y + 1 < ymax:
        yield z, y + 1, x
    if x > 0:
        yield z, y, x - 1
    if x + 1 < xmax:
        yield z, y, x + 1


def _largest_component_mask(binary_mask: np.ndarray) -> np.ndarray:
    """Extract largest 3D connected component (6-connectivity)."""
    if binary_mask.ndim != 3:
        raise ValueError("Expected a 3D mask in z,y,x order")
    mask = (binary_mask > 0).astype(np.uint8)
    if mask.sum() == 0:
        return mask

    visited = np.zeros_like(mask, dtype=bool)
    best_component: list[tuple[int, int, int]] = []
    shape = mask.shape
    for seed in np.argwhere(mask > 0):
        z0, y0, x0 = int(seed[0]), int(seed[1]), int(seed[2])
        if visited[z0, y0, x0]:
            continue
        q: deque[tuple[int, int, int]] = deque([(z0, y0, x0)])
        visited[z0, y0, x0] = True
        current: list[tuple[int, int, int]] = []
        while q:
            z, y, x = q.popleft()
            current.append((z, y, x))
            for nz, ny, nx in _iter_neighbors_6(z, y, x, shape):
                if visited[nz, ny, nx] or mask[nz, ny, nx] == 0:
                    continue
                visited[nz, ny, nx] = True
                q.append((nz, ny, nx))
        if len(current) > len(best_component):
            best_component = current

    out = np.zeros_like(mask, dtype=np.uint8)
    for z, y, x in best_component:
        out[z, y, x] = 1
    return out


def _expand_bbox(
    bbox: tuple[int, int, int, int, int, int],
    shape: tuple[int, int, int],
    padding: int,
) -> tuple[int, int, int, int, int, int]:
    zmin, zmax, ymin, ymax, xmin, xmax = bbox
    if padding <= 0:
        return bbox
    zz, yy, xx = shape
    return (
        max(0, zmin - padding),
        min(zz - 1, zmax + padding),
        max(0, ymin - padding),
        min(yy - 1, ymax + padding),
        max(0, xmin - padding),
        min(xx - 1, xmax + padding),
    )


def _connected_components_masks(binary_mask: np.ndarray) -> list[np.ndarray]:
    """Return all connected-component masks (6-connectivity)."""
    if binary_mask.ndim != 3:
        raise ValueError("Expected a 3D mask in z,y,x order")
    mask = (binary_mask > 0).astype(np.uint8)
    if mask.sum() == 0:
        return []
    visited = np.zeros_like(mask, dtype=bool)
    components: list[np.ndarray] = []
    shape = mask.shape
    for seed in np.argwhere(mask > 0):
        z0, y0, x0 = int(seed[0]), int(seed[1]), int(seed[2])
        if visited[z0, y0, x0]:
            continue
        q: deque[tuple[int, int, int]] = deque([(z0, y0, x0)])
        visited[z0, y0, x0] = True
        coords: list[tuple[int, int, int]] = []
        while q:
            z, y, x = q.popleft()
            coords.append((z, y, x))
            for nz, ny, nx in _iter_neighbors_6(z, y, x, shape):
                if visited[nz, ny, nx] or mask[nz, ny, nx] == 0:
                    continue
                visited[nz, ny, nx] = True
                q.append((nz, ny, nx))
        comp = np.zeros_like(mask, dtype=np.uint8)
        for z, y, x in coords:
            comp[z, y, x] = 1
        components.append(comp)
    return components


def detect_soma_region_from_segmentation(
    segmentation_mask: np.ndarray,
    *,
    keep_largest_component: bool = True,
    padding: int = 0,
) -> SomaDetectionResult:
    """Detect soma region from binary/label segmentation mask."""
    base_mask = (segmentation_mask > 0).astype(np.uint8)
    soma_mask = _largest_component_mask(base_mask) if keep_largest_component else base_mask
    bbox = largest_component_bbox(soma_mask)
    bbox = _expand_bbox(bbox, soma_mask.shape, padding)
    centroid = mask_centroid(soma_mask)
    return SomaDetectionResult(
        centroid_zyx=centroid,
        bbox_zyxzyx=bbox,
        voxel_count=int(soma_mask.sum()),
        soma_mask=soma_mask,
    )


def detect_soma_region_from_image(
    image: np.ndarray,
    *,
    threshold: float | None = None,
    percentile: float = 99.5,
    keep_largest_component: bool = True,
    padding: int = 0,
) -> SomaDetectionResult:
    """Simple intensity-threshold soma detection workflow.

    This is a lightweight middle-layer fallback when Vaa3D gsdt-based soma
    detection is not used.
    """
    if image.ndim != 3:
        raise ValueError("Expected a 3D image in z,y,x order")
    if threshold is None:
        foreground = image[image > 0]
        source = foreground if foreground.size > 0 else image
        threshold = float(np.percentile(source, percentile))
    segmentation = (image >= threshold).astype(np.uint8)
    return detect_soma_region_from_segmentation(
        segmentation,
        keep_largest_component=keep_largest_component,
        padding=padding,
    )


def detect_soma_region_smart(
    image: np.ndarray,
    *,
    percentiles: tuple[float, ...] = (99.9, 99.7, 99.5, 99.0),
    min_voxel_count: int = 8,
    padding: int = 0,
) -> SomaDetectionResult:
    """Multi-threshold soma detection with component scoring.

    Strategy:
    - Generate candidate masks from multiple intensity percentiles.
    - Enumerate connected components in each candidate mask.
    - Score each component by `voxel_count * mean_intensity`.
    - Pick the highest-scoring component.
    """
    if image.ndim != 3:
        raise ValueError("Expected a 3D image in z,y,x order")
    foreground = image[image > 0]
    source = foreground if foreground.size > 0 else image
    best_score = -1.0
    best_mask: np.ndarray | None = None
    threshold_candidates = [float(np.percentile(source, pct)) for pct in percentiles]
    if foreground.size > 0:
        threshold_candidates.append(float(foreground.min()))
    for thr in sorted(set(threshold_candidates), reverse=True):
        binary = (image >= thr).astype(np.uint8)
        for comp in _connected_components_masks(binary):
            vox = int(comp.sum())
            if vox < min_voxel_count:
                continue
            mean_intensity = float(image[comp > 0].mean()) if vox > 0 else 0.0
            score = float(vox) * mean_intensity
            if score > best_score:
                best_score = score
                best_mask = comp

    if best_mask is None:
        return detect_soma_region_from_image(
            image,
            threshold=None,
            percentile=percentiles[-1],
            keep_largest_component=True,
            padding=padding,
        )
    return detect_soma_region_from_segmentation(
        best_mask,
        keep_largest_component=False,
        padding=padding,
    )
