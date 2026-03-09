from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.visualization import quick_plot


def test_quick_plot_path_inputs(tmp_path: Path) -> None:
    img = np.zeros((4, 16, 16), dtype=np.uint8)
    img[:, 5:12, 4:10] = 100
    mask = np.zeros((4, 16, 16), dtype=np.uint8)
    mask[:, 7:10, 6:9] = 1

    image_file = tmp_path / "img.npy"
    mask_file = tmp_path / "mask.npy"
    swc_file = tmp_path / "n.swc"
    marker_file = tmp_path / "m.csv"
    out_file = tmp_path / "vis.npy"

    np.save(image_file, img)
    np.save(mask_file, mask)
    swc_file.write_text(
        "1 1 6 6 1 2 -1\n2 3 10 10 2 1 1\n",
        encoding="utf-8",
    )
    marker_file.write_text(
        "x,y,z,radius\n8,9,2,2\n",
        encoding="utf-8",
    )

    rendered = quick_plot(
        image_file,
        mask=mask_file,
        swc=swc_file,
        markers=marker_file,
        projection="xy",
        save_path=out_file,
    )
    assert rendered.shape == (16, 16, 3)
    assert rendered.dtype == np.uint8
    assert out_file.exists()

