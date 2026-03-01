from __future__ import annotations

from pathlib import Path

import neuroutils.workflows.pipelines.tracing as wtrace
from neuroutils.tracing.runners.orchestrator import TraceRunResult


def test_run_tracing_directory_with_reports(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    image_dir = tmp_path / "images"
    image_dir.mkdir()
    (image_dir / "a.tif").write_text("x", encoding="utf-8")

    fake = {
        "APP2": [
            TraceRunResult(
                tracer="APP2",
                image_file=str(image_dir / "a.tif"),
                output_swc=str(tmp_path / "out" / "APP2" / "a.swc"),
                status="ok",
            )
        ]
    }
    monkeypatch.setattr(wtrace, "run_tracers_for_directory", lambda **kwargs: fake)
    out = wtrace.run_tracing_directory_with_reports(
        image_dir=image_dir,
        output_root=tmp_path / "out",
        report_dir=tmp_path / "reports",
    )
    assert out["summary"]["total"] == 1
    assert Path(out["json_report"]).exists()
    assert Path(out["csv_report"]).exists()
