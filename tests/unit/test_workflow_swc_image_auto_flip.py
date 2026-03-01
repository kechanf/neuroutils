from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.io.swc import read_swc
from neuroutils.workflows.pipelines import auto_flip_swc_y_for_image_pair


def test_auto_flip_swc_y_for_image_pair_writes_new_file(tmp_path: Path) -> None:
    img = np.zeros((1, 10, 10), dtype=np.uint8)
    img[0, 8, 4] = 200
    img[0, 1, 4] = 50
    img_path = tmp_path / "img.npy"
    np.save(img_path, img)

    swc_path = tmp_path / "trace.swc"
    swc_path.write_text("1 1 4 1 0 1 -1\n", encoding="utf-8")

    result = auto_flip_swc_y_for_image_pair(swc_path, img_path)
    out_path = tmp_path / "trace_autoflipy.swc"

    assert result.flipped is True
    assert out_path.exists()
    out_nodes = read_swc(out_path)
    assert out_nodes[0].y == 8.0
