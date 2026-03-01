from __future__ import annotations

from pathlib import Path

import numpy as np

from neuroutils.projection import Projection, preprocess_projections


def test_projection_matrix_basic(tmp_path: Path) -> None:
    atlas = np.zeros((4, 4, 4), dtype=np.int64)
    atlas[:, :, :] = 1
    atlas[:, 2:, 2:] = 2

    swc = tmp_path / "axon.swc"
    swc.write_text(
        "1 1 25 25 25 1 -1\n"
        "2 2 50 50 50 1 1\n"
        "3 2 75 75 50 1 2\n",
        encoding="utf-8",
    )

    proj = Projection(atlas, use_two_hemispheres=False, resample_scale=1.0, atlas_voxel_um=25.0)
    res = proj.calc_proj_matrix([swc])
    assert res.matrix.shape[0] == 1
    assert len(res.region_ids) >= 1

    res2 = preprocess_projections(res, min_proj=0, log=True)
    assert res2.matrix.shape[0] == 1
