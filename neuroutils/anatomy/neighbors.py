"""Regional-neighbor and region-mask utilities."""

from __future__ import annotations

from collections import defaultdict

import numpy as np


def _ball_offsets(radius: int) -> np.ndarray:
    r = int(radius)
    if r < 1:
        return np.array([[0, 0, 0]], dtype=np.int32)
    off = []
    for dz in range(-r, r + 1):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dz * dz + dy * dy + dx * dx <= r * r:
                    off.append((dz, dy, dx))
    return np.array(off, dtype=np.int32)


def get_regional_neighbors(mask: np.ndarray, *, radius: int = 5, exclude_zero: bool = True) -> dict[int, list[int]]:
    """Find neighboring region ids for each label using spherical neighborhood."""
    arr = np.asarray(mask)
    if arr.ndim == 4:
        arr = arr[0]
    if arr.ndim != 3:
        raise ValueError("mask must be 3D or 4D (c,z,y,x)")

    values = np.unique(arr)
    if exclude_zero:
        values = values[values != 0]
    offsets = _ball_offsets(radius)
    zdim, ydim, xdim = arr.shape
    rn: dict[int, list[int]] = {}
    for v in values.tolist():
        coords = np.argwhere(arr == v)
        neigh: set[int] = set()
        for dz, dy, dx in offsets.tolist():
            nz = coords[:, 0] + dz
            ny = coords[:, 1] + dy
            nx = coords[:, 2] + dx
            m = (nz >= 0) & (nz < zdim) & (ny >= 0) & (ny < ydim) & (nx >= 0) & (nx < xdim)
            if not np.any(m):
                continue
            labels = np.unique(arr[nz[m], ny[m], nx[m]])
            for lv in labels.tolist():
                if lv != v and (not exclude_zero or lv != 0):
                    neigh.add(int(lv))
        rn[int(v)] = sorted(neigh)
    return rn


def get_regional_neighbors_cuda(mask: np.ndarray, *, radius: int = 5, exclude_zero: bool = True) -> dict[int, list[int]]:
    """CUDA accelerated regional neighbors (requires torch)."""
    try:
        import torch
        import torch.nn.functional as F
    except Exception as exc:
        raise RuntimeError("get_regional_neighbors_cuda requires torch") from exc

    arr = np.asarray(mask)
    if arr.ndim == 4:
        arr = arr[0]
    if arr.ndim != 3:
        raise ValueError("mask must be 3D or 4D (c,z,y,x)")
    values = np.unique(arr)
    if exclude_zero:
        values = values[values != 0]

    tmask = torch.from_numpy(arr.astype(np.int64)).cuda()
    ball = _ball_offsets(radius)
    ksz = 2 * radius + 1
    kernel = torch.zeros((1, 1, ksz, ksz, ksz), dtype=torch.float32, device=tmask.device)
    for dz, dy, dx in ball.tolist():
        kernel[0, 0, dz + radius, dy + radius, dx + radius] = 1.0

    rn: dict[int, list[int]] = {}
    for v in values.tolist():
        m = (tmask == int(v)).float().unsqueeze(0).unsqueeze(0)
        dil = (F.conv3d(m, kernel, stride=1, padding=radius) > 0)[0, 0]
        labels = torch.unique(tmask[dil]).cpu().numpy().tolist()
        neigh = [int(x) for x in labels if x != int(v) and (not exclude_zero or int(x) != 0)]
        rn[int(v)] = sorted(set(neigh))
    return rn


def generate_mask314(mask: np.ndarray, region_map: dict[int, int], *, ventricles: set[int] | None = None) -> np.ndarray:
    """Map original region IDs to compressed region IDs."""
    arr = np.asarray(mask).copy()
    if arr.ndim == 4:
        arr = arr[0]
    if arr.ndim != 3:
        raise ValueError("mask must be 3D or 4D (c,z,y,x)")
    vents = ventricles or set()
    out = arr.astype(np.int64, copy=True)
    for reg in np.unique(arr).tolist():
        if reg == 0:
            continue
        m = arr == reg
        if int(reg) in vents:
            out[m] = 999999
        elif int(reg) in region_map:
            out[m] = int(region_map[int(reg)])
    return out


def get_salient_regions_mask(
    mask: np.ndarray,
    *,
    all_regions: set[int],
    ventricles: set[int],
    fiber_tracts: set[int],
) -> np.ndarray:
    """Binary mask removing ventricles and fiber-tract labels."""
    arr = np.asarray(mask)
    if arr.ndim == 4:
        arr = arr[0]
    if arr.ndim != 3:
        raise ValueError("mask must be 3D or 4D (c,z,y,x)")
    remove = set(ventricles).union(fiber_tracts)
    allowed = set(all_regions) - remove
    out = np.isin(arr, list(allowed)).astype(np.uint8)
    return out


def get_salient_regions_mask671(
    mask: np.ndarray,
    *,
    all_regions: set[int],
    ventricles: set[int],
    fiber_tracts: set[int],
) -> np.ndarray:
    """Compatibility alias for salient-region masking."""
    return get_salient_regions_mask(
        mask,
        all_regions=all_regions,
        ventricles=ventricles,
        fiber_tracts=fiber_tracts,
    )
