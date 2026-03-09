from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from neuroutils.segmentation import (
    export_rotational_mips_for_2p5d_annotation,
    polygon_json_to_mask2d,
    restore_3d_mask_from_2p5d_annotation_folder,
    rotate_volume_to_mips,
)


def test_rotate_volume_to_mips_shapes() -> None:
    vol = np.zeros((8, 16, 16), dtype=np.uint8)
    vol[:, 6:10, 6:10] = 1
    mips = rotate_volume_to_mips(vol, rotate_times=6, axes_rot=(1, 2), mip_axis=1)
    assert len(mips) == 6
    assert all(m.shape == (8, 16) for m in mips)


def test_polygon_json_to_mask2d(tmp_path: Path) -> None:
    js = tmp_path / "a.json"
    data = {
        "imageHeight": 20,
        "imageWidth": 30,
        "shapes": [
            {"points": [[5, 5], [20, 5], [20, 15], [5, 15]]},
        ],
    }
    js.write_text(json.dumps(data), encoding="utf-8")
    mask = polygon_json_to_mask2d(js)
    assert mask is not None
    assert mask.shape == (20, 30)
    assert int(mask.sum()) > 0


def test_export_and_restore_annotation_roundtrip(tmp_path: Path) -> None:
    pytest.importorskip("scipy")
    vol = np.zeros((16, 32, 32), dtype=np.uint8)
    vol[4:12, 10:22, 11:23] = 200
    img_file = tmp_path / "vol.npy"
    np.save(img_file, vol)

    ann_dir = tmp_path / "ann"
    cfg = export_rotational_mips_for_2p5d_annotation(
        img_file,
        ann_dir,
        rotate_times=6,
        axes_rot=(1, 2),
        mip_axis=1,
    )
    assert (ann_dir / "rotation_mip_config.json").exists()
    assert len(cfg["entries"]) == 6

    # Simulate annotator: create full-foreground polygon on each MIP.
    for entry in cfg["entries"]:
        mip_path = ann_dir / entry["mip_file"]
        assert mip_path.exists()
        h, w = np.load(img_file).shape[0], np.load(img_file).shape[2]
        poly = {
            "imageHeight": int(h),
            "imageWidth": int(w),
            "shapes": [{"points": [[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]]}],
        }
        (ann_dir / entry["label_file"]).write_text(json.dumps(poly), encoding="utf-8")

    out_mask_file = tmp_path / "mask.tif"
    mask = restore_3d_mask_from_2p5d_annotation_folder(ann_dir, output_mask_file=out_mask_file)
    assert mask.shape == vol.shape
    assert out_mask_file.exists()
