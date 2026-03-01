from __future__ import annotations

from pathlib import Path

import neuroutils.tracing.runners.orchestrator as orch


class _DummyCompleted:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_run_tracer_for_image_ok_with_target_output(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    image = tmp_path / "a.tif"
    image.write_text("x", encoding="utf-8")

    def _fake_build(*_args, **kwargs):  # type: ignore[no-untyped-def]
        return ["vaa3d", "-x", "vn2"]

    def _fake_candidates(*_args, **kwargs):  # type: ignore[no-untyped-def]
        return [str(tmp_path / "out" / "APP2" / "a.swc")]

    def _fake_run(job, timeout=300):  # type: ignore[no-untyped-def]
        Path(job.output_swc).parent.mkdir(parents=True, exist_ok=True)
        Path(job.output_swc).write_text("swc", encoding="utf-8")
        return _DummyCompleted(returncode=0)

    monkeypatch.setattr(orch, "build_tracer_command", _fake_build)
    monkeypatch.setattr(orch, "get_tracer_output_candidates", _fake_candidates)
    monkeypatch.setattr(orch, "run_trace_job", _fake_run)

    result = orch.run_tracer_for_image(tracer="APP2", image_file=image, output_root=tmp_path / "out")
    assert result.status == "ok"
    assert Path(result.output_swc).exists()


def test_run_tracer_for_image_moves_candidate_output(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    image = tmp_path / "b.tif"
    image.write_text("x", encoding="utf-8")
    candidate = tmp_path / "b.tif_app2.swc"

    def _fake_build(*_args, **kwargs):  # type: ignore[no-untyped-def]
        return ["vaa3d", "-x", "vn2"]

    def _fake_candidates(*_args, **kwargs):  # type: ignore[no-untyped-def]
        target = tmp_path / "out" / "APP2" / "b.swc"
        return [str(target), str(candidate)]

    def _fake_run(_job, timeout=300):  # type: ignore[no-untyped-def]
        candidate.write_text("swc", encoding="utf-8")
        return _DummyCompleted(returncode=0)

    monkeypatch.setattr(orch, "build_tracer_command", _fake_build)
    monkeypatch.setattr(orch, "get_tracer_output_candidates", _fake_candidates)
    monkeypatch.setattr(orch, "run_trace_job", _fake_run)

    result = orch.run_tracer_for_image(tracer="APP2", image_file=image, output_root=tmp_path / "out")
    assert result.status == "ok"
    assert Path(result.output_swc).exists()
    assert not candidate.exists()


def test_run_tracers_for_image_only_installed_filter(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    image = tmp_path / "c.tif"
    image.write_text("x", encoding="utf-8")

    monkeypatch.setattr(orch, "list_available_tracers", lambda: ["APP2", "MOST", "MST"])
    monkeypatch.setattr(orch, "list_installed_tracers", lambda: ["APP2", "MST"])

    def _fake_run_one(**kwargs):  # type: ignore[no-untyped-def]
        tracer = kwargs["tracer"]
        return orch.TraceRunResult(
            tracer=tracer,
            image_file=str(image),
            output_swc=str(tmp_path / "out" / tracer / "c.swc"),
            status="ok",
        )

    monkeypatch.setattr(orch, "run_tracer_for_image", _fake_run_one)
    results = orch.run_tracers_for_image(image_file=image, output_root=tmp_path / "out", only_installed=True)
    assert [r.tracer for r in results] == ["APP2", "MST"]


def test_run_tracers_for_directory_dispatch(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    (img_dir / "a.tif").write_text("x", encoding="utf-8")
    (img_dir / "b.tif").write_text("x", encoding="utf-8")

    monkeypatch.setattr(orch, "list_available_tracers", lambda: ["APP2", "MOST"])
    monkeypatch.setattr(orch, "list_installed_tracers", lambda: ["APP2"])

    def _fake_batch(**kwargs):  # type: ignore[no-untyped-def]
        tracer = kwargs["tracer"]
        return [
            orch.TraceRunResult(
                tracer=tracer,
                image_file=str(img_dir / "a.tif"),
                output_swc=str(tmp_path / "out" / tracer / "a.swc"),
                status="ok",
            )
        ]

    monkeypatch.setattr(orch, "run_tracer_batch_for_dir", _fake_batch)
    out = orch.run_tracers_for_directory(image_dir=img_dir, output_root=tmp_path / "out", only_installed=True)
    assert sorted(out.keys()) == ["APP2"]
    assert out["APP2"][0].status == "ok"
