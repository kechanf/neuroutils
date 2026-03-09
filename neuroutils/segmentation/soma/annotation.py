"""Rotational MIP annotation workflows for 3D soma masks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from neuroutils.imaging.preprocess import to_uint8
from neuroutils.io.images import load_image, save_image


def _require_scipy_rotate():
    try:
        from scipy.ndimage import rotate  # type: ignore
    except Exception as exc:
        raise RuntimeError("Rotational MIP workflows require scipy (scipy.ndimage.rotate)") from exc
    return rotate


def rotate_volume_to_mips(
    volume: np.ndarray,
    *,
    rotate_times: int = 12,
    axes_rot: tuple[int, int] = (1, 2),
    mip_axis: int = 1,
    order: int = 1,
) -> list[np.ndarray]:
    """Rotate a 3D volume around center and produce MIP stack."""
    arr = np.asarray(volume)
    if arr.ndim != 3:
        raise ValueError("volume must be 3D in z,y,x order")
    if rotate_times <= 0:
        raise ValueError("rotate_times must be positive")
    if mip_axis not in (0, 1, 2):
        raise ValueError("mip_axis must be one of 0,1,2")

    rotate = _require_scipy_rotate()
    step = 180.0 / float(rotate_times)
    mips: list[np.ndarray] = []
    for i in range(rotate_times):
        angle = float(i) * step
        rotated = rotate(arr, angle, axes=axes_rot, reshape=False, order=order, mode="constant")
        mips.append(np.max(rotated, axis=mip_axis))
    return mips


def _fill_polygon(mask: np.ndarray, polygon_xy: np.ndarray) -> None:
    """Rasterize one polygon into 2D mask using scanline fill."""
    poly = np.asarray(polygon_xy, dtype=np.float64)
    if poly.ndim != 2 or poly.shape[1] != 2 or len(poly) < 3:
        return

    h, w = mask.shape
    xmin = max(0, int(np.floor(np.min(poly[:, 0]))))
    xmax = min(w - 1, int(np.ceil(np.max(poly[:, 0]))))
    ymin = max(0, int(np.floor(np.min(poly[:, 1]))))
    ymax = min(h - 1, int(np.ceil(np.max(poly[:, 1]))))
    if xmin > xmax or ymin > ymax:
        return

    x = poly[:, 0]
    y = poly[:, 1]
    n = len(poly)
    for yy in range(ymin, ymax + 1):
        yline = yy + 0.5
        xs: list[float] = []
        for i in range(n):
            j = (i + 1) % n
            y0 = y[i]
            y1 = y[j]
            if y0 == y1:
                continue
            low = min(y0, y1)
            high = max(y0, y1)
            if not (low <= yline < high):
                continue
            t = (yline - y0) / (y1 - y0)
            xs.append(x[i] + t * (x[j] - x[i]))
        if not xs:
            continue
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            x0 = max(xmin, int(np.ceil(xs[k])))
            x1 = min(xmax, int(np.floor(xs[k + 1])))
            if x0 <= x1:
                mask[yy, x0 : x1 + 1] = 1


def polygon_json_to_mask2d(label_json: str | Path) -> np.ndarray | None:
    """Convert one LabelMe polygon JSON to binary 2D mask."""
    path = Path(label_json)
    if not path.exists():
        return None
    info = json.loads(path.read_text(encoding="utf-8"))
    h = int(info.get("imageHeight", 0))
    w = int(info.get("imageWidth", 0))
    if h <= 0 or w <= 0:
        raise ValueError(f"Invalid imageHeight/imageWidth in {path}")
    out = np.zeros((h, w), dtype=np.uint8)
    shapes = info.get("shapes", [])
    if not isinstance(shapes, list):
        return out
    for shape in shapes:
        if not isinstance(shape, dict):
            continue
        points = shape.get("points")
        if points is None:
            continue
        poly = np.asarray(points, dtype=np.float64)
        _fill_polygon(out, poly)
    return out


def reconstruct_3d_mask_from_mip_polygons(
    mip_masks: list[np.ndarray | None],
    image_shape_zyx: tuple[int, int, int],
    *,
    rotate_times: int,
    axes_rot: tuple[int, int] = (1, 2),
    mip_axis: int = 1,
    order: int = 1,
    threshold: float = 0.5,
) -> np.ndarray:
    """Reconstruct 3D mask by inverse rotation from 2D MIP polygon masks."""
    if rotate_times <= 0:
        raise ValueError("rotate_times must be positive")
    if len(mip_masks) != rotate_times:
        raise ValueError("len(mip_masks) must equal rotate_times")
    zz, yy, xx = image_shape_zyx
    total = np.ones((zz, yy, xx), dtype=np.uint8)
    used = 0
    rotate = _require_scipy_rotate()
    step = 180.0 / float(rotate_times)
    for i, mm in enumerate(mip_masks):
        if mm is None:
            continue
        mask2d = (np.asarray(mm) > 0).astype(np.uint8)
        col = np.expand_dims(mask2d, axis=mip_axis)
        col = np.repeat(col, (zz, yy, xx)[mip_axis], axis=mip_axis)
        angle = float(i) * step
        back = rotate(col, -angle, axes=axes_rot, reshape=False, order=order, mode="constant")
        back_bin = (back > threshold).astype(np.uint8)
        total = total * back_bin
        used += 1
    if used == 0 or int(total.sum()) == int(total.size):
        return np.zeros((zz, yy, xx), dtype=np.uint8)
    return total


def export_rotational_mips_for_2p5d_annotation(
    image_file: str | Path,
    output_dir: str | Path,
    *,
    rotate_times: int = 12,
    axes_rot: tuple[int, int] = (1, 2),
    mip_axis: int = 1,
    order: int = 1,
    flip_tif: bool = False,
) -> dict[str, Any]:
    """Generate rotational MIPs for 2.5D rotational annotation and save config."""
    src = Path(image_file)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    vol = np.asarray(load_image(src, flip_tif=flip_tif))
    if vol.ndim != 3:
        raise ValueError("image_file must be a 3D volume")
    mips = rotate_volume_to_mips(
        vol,
        rotate_times=rotate_times,
        axes_rot=axes_rot,
        mip_axis=mip_axis,
        order=order,
    )

    step = 180.0 / float(rotate_times)
    entries: list[dict[str, Any]] = []
    for i, mp in enumerate(mips):
        mip_name = f"{src.stem}_mip_axis{mip_axis}_angle{int(round(i * step)):03d}.tif"
        label_name = f"{Path(mip_name).stem}.json"
        save_image(out_dir / mip_name, to_uint8(mp), flip_tif=False)
        entries.append(
            {
                "index": i,
                "angle_deg": float(i) * step,
                "mip_file": mip_name,
                "label_file": label_name,
            }
        )

    cfg = {
        "version": 1,
        "source_image": str(src),
        "image_shape_zyx": [int(x) for x in vol.shape],
        "rotate_times": int(rotate_times),
        "axes_rot": [int(axes_rot[0]), int(axes_rot[1])],
        "mip_axis": int(mip_axis),
        "order": int(order),
        "entries": entries,
    }
    cfg_file = out_dir / "rotation_mip_config.json"
    cfg_file.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return cfg


def restore_3d_mask_from_2p5d_annotation_folder(
    annotation_dir: str | Path,
    *,
    output_mask_file: str | Path | None = None,
    strict: bool = False,
) -> np.ndarray:
    """Restore 3D mask from a 2.5D rotational-annotation folder."""
    ann_dir = Path(annotation_dir)
    cfg_file = ann_dir / "rotation_mip_config.json"
    if not cfg_file.exists():
        raise FileNotFoundError(f"Config not found: {cfg_file}")
    cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
    shape = tuple(int(x) for x in cfg["image_shape_zyx"])
    rotate_times = int(cfg["rotate_times"])
    axes_rot = (int(cfg["axes_rot"][0]), int(cfg["axes_rot"][1]))
    mip_axis = int(cfg["mip_axis"])
    order = int(cfg.get("order", 1))
    entries = list(cfg["entries"])
    if len(entries) != rotate_times:
        raise ValueError("Config entries count does not match rotate_times")

    mip_masks: list[np.ndarray | None] = []
    for it in entries:
        label_file = ann_dir / str(it["label_file"])
        m = polygon_json_to_mask2d(label_file)
        if strict and m is None:
            raise FileNotFoundError(f"Missing label json: {label_file}")
        mip_masks.append(m)

    mask = reconstruct_3d_mask_from_mip_polygons(
        mip_masks,
        shape,  # type: ignore[arg-type]
        rotate_times=rotate_times,
        axes_rot=axes_rot,
        mip_axis=mip_axis,
        order=order,
    )
    if output_mask_file is not None:
        save_image(output_mask_file, (mask > 0).astype(np.uint8) * 255, flip_tif=False)
    return mask


# Backward-compatible aliases (kept for existing call sites).
export_rotational_mips_for_annotation = export_rotational_mips_for_2p5d_annotation
restore_3d_mask_from_annotation_folder = restore_3d_mask_from_2p5d_annotation_folder
