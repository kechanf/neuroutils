"""Image statistics and projection helpers."""

from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np


def mip(image: np.ndarray, *, axis: int = 0, mode: str = "max") -> np.ndarray:
    """Maximum/minimum intensity projection."""
    m = mode.lower()
    if m == "max":
        return np.max(image, axis=axis)
    if m == "min":
        return np.min(image, axis=axis)
    raise ValueError("mode must be 'max' or 'min'")


def get_mip_image(image: np.ndarray, axis: int = 0, mode: str = "MAX") -> np.ndarray:
    """Compatibility wrapper for ``mip``."""
    return mip(image, axis=axis, mode=mode.lower())


def crop_nonzero_mask(mask: np.ndarray, *, pad: int = 0) -> tuple[np.ndarray, tuple[int, int, int, int, int, int]]:
    """Crop 3D mask around non-zero region; return cropped mask and z/y/x bounds."""
    arr = np.asarray(mask)
    if arr.ndim != 3:
        raise ValueError("crop_nonzero_mask expects 3D array in (z,y,x)")
    nz = np.argwhere(arr != 0)
    if nz.size == 0:
        return arr[0:0, 0:0, 0:0], (0, 0, 0, 0, 0, 0)

    zmin, ymin, xmin = nz.min(axis=0)
    zmax, ymax, xmax = nz.max(axis=0)
    sz, sy, sx = arr.shape
    zs = max(0, int(zmin) - pad)
    ze = min(sz, int(zmax) + pad + 1)
    ys = max(0, int(ymin) - pad)
    ye = min(sy, int(ymax) + pad + 1)
    xs = max(0, int(xmin) - pad)
    xe = min(sx, int(xmax) + pad + 1)
    return arr[zs:ze, ys:ye, xs:xe], (zs, ze, ys, ye, xs, xe)


def histogram_equalize(image: np.ndarray, *, number_bins: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """Histogram equalization using CDF remapping."""
    arr = np.asarray(image)
    hist, bins = np.histogram(arr.flatten(), number_bins, density=True)
    cdf = hist.cumsum()
    cdf = (number_bins - 1) * cdf / cdf[-1]
    out = np.interp(arr.flatten(), bins[:-1], cdf).reshape(arr.shape)
    return out, cdf


def image_histeq(image: np.ndarray, number_bins: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """Compatibility wrapper for histogram equalization."""
    return histogram_equalize(image, number_bins=number_bins)


def montage_images_for_folder(img_dir: str | Path, sw: int, sh: int, prefix: str = "") -> list[Path]:
    """Compose PNG montages for images in folder using PIL."""
    try:
        from PIL import Image
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("montage_images_for_folder requires Pillow") from exc

    root = Path(img_dir)
    imgs = sorted(root.glob("*.png"))
    if sw <= 0 or sh <= 0:
        raise ValueError("sw and sh must be > 0")
    chunk = sw * sh
    outputs: list[Path] = []
    for i in range(0, len(imgs), chunk):
        subset = imgs[i : i + chunk]
        if not subset:
            continue
        opened = [Image.open(p).convert("RGB") for p in subset]
        w = max(im.width for im in opened)
        h = max(im.height for im in opened)
        canvas = Image.new("RGB", (w * sw, h * sh), (0, 0, 0))
        for j, im in enumerate(opened):
            row, col = divmod(j, sw)
            canvas.paste(im, (col * w, row * h))
            im.close()
        out = root / f"montage_{prefix}_{i:04d}.png"
        canvas.save(out)
        outputs.append(out)
    return outputs


def extend_skel_to_boundary(boundaries: np.ndarray, pcoords: np.ndarray, is_start: bool = True) -> np.ndarray:
    """Extend skeleton path to nearest boundary endpoint by direction."""
    b = np.asarray(boundaries, dtype=np.int32)
    p = np.asarray(pcoords, dtype=np.int32)
    if b.ndim != 2 or p.ndim != 2 or b.shape[1] != p.shape[1]:
        raise ValueError("boundaries and pcoords must be (N,D)/(M,D) with same D")
    if p.shape[0] < 2 or b.shape[0] == 0:
        return p
    if is_start:
        pt = p[0]
        anchor = p[min(5, p.shape[0] - 1)]
    else:
        pt = p[-1]
        anchor = p[max(0, p.shape[0] - 1 - min(5, p.shape[0] - 1))]
    direction = (pt - anchor).astype(np.float64)
    n = np.linalg.norm(direction)
    if n == 0:
        return p
    direction /= n
    vb = (b - pt).astype(np.float64)
    vb_norm = np.linalg.norm(vb, axis=1, keepdims=True)
    vb_norm[vb_norm == 0] = 1.0
    vb /= vb_norm
    scores = vb @ direction
    target = b[int(np.argmax(scores))]
    dist = int(np.max(np.abs(target - pt)))
    if dist <= 0:
        return p
    line = np.array(
        [
            np.round(pt + (target - pt) * (k / dist)).astype(np.int32)
            for k in range(1, dist + 1)
        ],
        dtype=np.int32,
    )
    return np.vstack((line[::-1], p)) if is_start else np.vstack((p, line))


def get_longest_skeleton(
    mask: np.ndarray,
    is_3D: bool = True,
    extend_to_boundary: bool = True,
    smoothing: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract one approximate longest skeleton path from binary mask."""
    arr = np.asarray(mask) > 0
    if arr.ndim not in (2, 3):
        raise ValueError("mask must be 2D or 3D")
    if arr.ndim == 2:
        is_3D = False
    try:
        from scipy import ndimage as ndi
        from skimage.morphology import skeletonize, skeletonize_3d
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("get_longest_skeleton requires scipy and scikit-image") from exc

    if smoothing:
        arr = ndi.binary_closing(arr, structure=np.ones((3,) * arr.ndim, dtype=bool))
    skel = skeletonize_3d(arr) if is_3D else skeletonize(arr)
    coords = np.argwhere(skel > 0).astype(np.int32)
    out = np.zeros_like(arr, dtype=np.uint8)
    if coords.shape[0] == 0:
        return out, coords

    coord_to_idx = {tuple(c.tolist()): i for i, c in enumerate(coords)}
    neigh_offsets = np.array(
        [o for o in np.ndindex(*(3,) * arr.ndim) if o != (1,) * arr.ndim], dtype=np.int32
    ) - 1
    adj: list[list[int]] = [[] for _ in range(coords.shape[0])]
    for i, c in enumerate(coords):
        for o in neigh_offsets:
            nb = tuple((c + o).tolist())
            j = coord_to_idx.get(nb)
            if j is not None:
                adj[i].append(j)

    deg = np.array([len(v) for v in adj], dtype=np.int32)
    endpoints = np.where(deg <= 1)[0]
    if endpoints.size < 2:
        endpoints = np.array([0, int(np.argmax(np.sum((coords - coords[0]) ** 2, axis=1)))], dtype=np.int32)
    start = int(endpoints[0])
    q: deque[int] = deque([start])
    prev = [-1] * coords.shape[0]
    seen = {start}
    while q:
        cur = q.popleft()
        for nxt in adj[cur]:
            if nxt in seen:
                continue
            seen.add(nxt)
            prev[nxt] = cur
            q.append(nxt)
    end = int(max(seen, key=lambda i: np.sum((coords[i] - coords[start]) ** 2)))
    path_idx: list[int] = []
    cur = end
    while cur != -1:
        path_idx.append(cur)
        cur = prev[cur]
    path = coords[path_idx[::-1]]

    if extend_to_boundary:
        edges = arr & (~ndi.binary_erosion(arr))
        bcoords = np.argwhere(edges).astype(np.int32)
        path = extend_skel_to_boundary(bcoords, path, is_start=True)
        path = extend_skel_to_boundary(bcoords, path, is_start=False)

    out[tuple(path.T)] = 1
    return out.astype(np.uint8), path
