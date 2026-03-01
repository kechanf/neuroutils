from __future__ import annotations

import sys
from pathlib import Path

from neuroutils.tracing import available_tracers, build_trace_jobs_for_dir, build_tracer_command
from neuroutils.tracing.vaa3d.tracers import resolve_tracer_plugin_arg


def test_build_tracer_command() -> None:
    cmd = build_tracer_command(
        "APP2",
        vaa3d_bin="vaa3d",
        image_file="a.tif",
        output_swc="a.swc",
    )
    assert cmd[0] == "vaa3d"
    if sys.platform.startswith("win"):
        assert "/x" in cmd and "/f" in cmd and "/i" in cmd
    else:
        assert "-x" in cmd and "-f" in cmd and "-i" in cmd
    assert "APP2" in available_tracers()


def test_build_tracer_command_reads_env(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("NEUROUTILS_VAA3D_X", "vaa3d-x")
    cmd = build_tracer_command("APP2", image_file="a.tif", output_swc="a.swc")
    assert cmd[0] == "vaa3d-x"


def test_build_tracer_command_override_version(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("NEUROUTILS_VAA3D_X", "vaa3d-x")
    monkeypatch.setenv("NEUROUTILS_VAA3D_3", "vaa3d-3")
    cmd = build_tracer_command("APP2", image_file="a.tif", output_swc="a.swc", vaa3d_version="3")
    assert cmd[0] == "vaa3d-3"


def test_build_tracer_command_tracer_level_default_version(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("NEUROUTILS_VAA3D_X", "vaa3d-x")
    monkeypatch.setenv("NEUROUTILS_VAA3D_3", "vaa3d-3")
    cmd_app2 = build_tracer_command("APP2", image_file="a.tif", output_swc="a.swc")
    cmd_most = build_tracer_command("MOST", image_file="a.tif", output_swc="a.swc")
    assert cmd_app2[0] == "vaa3d-x"
    assert cmd_most[0] == "vaa3d-3"


def test_build_trace_jobs_for_dir(tmp_path: Path) -> None:
    (tmp_path / "img1.tif").write_text("x", encoding="utf-8")
    (tmp_path / "img2.tif").write_text("x", encoding="utf-8")
    jobs = build_trace_jobs_for_dir(
        tmp_path,
        tmp_path / "out",
        tracer="APP2",
        vaa3d_bin="vaa3d",
        image_suffix=".tif",
        skip_existing=False,
    )
    assert len(jobs) == 2
    assert all(str(j.output_swc).endswith(".swc") for j in jobs)


def test_resolve_tracer_plugin_arg_windows_falls_back_when_not_found(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(sys, "platform", "win32")
    vb = tmp_path / "vaa3d-x.exe"
    vb.write_text("", encoding="utf-8")
    out = resolve_tracer_plugin_arg(str(vb), "vn2")
    assert out == "vn2"


def test_resolve_tracer_plugin_arg_windows_finds_dll(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(sys, "platform", "win32")
    root = tmp_path / "vaa3d"
    plug_dir = root / "plugins" / "neuron_tracing" / "Vaa3D_Neuron2"
    plug_dir.mkdir(parents=True)
    vb = root / "vaa3d-x.exe"
    vb.write_text("", encoding="utf-8")
    dll = plug_dir / "vn2.dll"
    dll.write_text("", encoding="utf-8")
    out = resolve_tracer_plugin_arg(str(vb), "vn2")
    assert out.endswith("vn2.dll")
