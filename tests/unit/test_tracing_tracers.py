from __future__ import annotations

from pathlib import Path

from neuroutils.tracing import BaseTracer, TracingRunner, available_tracers, build_trace_jobs_for_dir, build_tracer_command


def test_build_tracer_command() -> None:
    cmd = build_tracer_command(
        "APP2",
        vaa3d_bin="vaa3d",
        image_file="a.tif",
        output_swc="a.swc",
    )
    assert cmd[0] == "vaa3d"
    assert "-x" in cmd and "-f" in cmd and "-i" in cmd
    assert "APP2" in available_tracers()


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


def test_legacy_wrappers_basic() -> None:
    tr = BaseTracer(tracer="APP2", vaa3d_path="vaa3d")
    assert tr.tracer == "APP2"
    runner = TracingRunner(vaa3d_path="vaa3d", tracers=["APP2"])
    assert runner.tracers == ["APP2"]
