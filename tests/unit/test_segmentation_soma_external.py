from __future__ import annotations

from pathlib import Path

import numpy as np

import neuroutils.segmentation.soma.external as ext


def test_build_gsdt_command_basic(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(ext, "get_vaa3d_path", lambda *args, **kwargs: "vaa3d")
    monkeypatch.setattr(ext, "resolve_tracer_plugin_arg", lambda vb, p: p)
    cmd = ext.build_gsdt_command(input_image="a.tif", output_mask="b.tif")
    assert cmd[0] == "vaa3d"
    assert any(token in cmd for token in ("-x", "/x"))
    assert "gsdt" in cmd


def test_detect_soma_region_external_gsdt_mocked(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    image = tmp_path / "in.tif"
    out = tmp_path / "out.tif"
    image.write_text("x", encoding="utf-8")

    monkeypatch.setattr(ext, "build_gsdt_command", lambda **kwargs: ["vaa3d", "-x", "gsdt"])  # type: ignore[arg-type]

    def _fake_run_checked(cmd, timeout=300):  # type: ignore[no-untyped-def]
        out.write_text("mask", encoding="utf-8")
        return None

    def _fake_load_image(path, flip_tif=True):  # type: ignore[no-untyped-def]
        mask = np.zeros((3, 4, 4), dtype=np.uint8)
        mask[1, 1:3, 1:3] = 255
        return mask

    monkeypatch.setattr(ext, "run_checked", _fake_run_checked)
    monkeypatch.setattr(ext, "load_image", _fake_load_image)

    res = ext.detect_soma_region_external_gsdt(image, output_mask_file=out)
    assert res.voxel_count == 4
    assert res.bbox_zyxzyx == (1, 1, 1, 2, 1, 2)
