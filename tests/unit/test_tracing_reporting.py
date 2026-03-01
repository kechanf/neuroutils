from __future__ import annotations

import json
from pathlib import Path

from neuroutils.tracing.runners.orchestrator import TraceRunResult
from neuroutils.tracing.runners.reporting import (
    flatten_trace_results,
    summarize_trace_results,
    write_trace_report_csv,
    write_trace_report_json,
)


def _sample_results(tmp_path: Path) -> dict[str, list[TraceRunResult]]:
    return {
        "APP2": [
            TraceRunResult(
                tracer="APP2",
                image_file="a.tif",
                output_swc=str(tmp_path / "APP2" / "a.swc"),
                status="ok",
            ),
            TraceRunResult(
                tracer="APP2",
                image_file="b.tif",
                output_swc=str(tmp_path / "APP2" / "b.swc"),
                status="timeout",
                error="timeout",
            ),
        ],
        "MOST": [
            TraceRunResult(
                tracer="MOST",
                image_file="a.tif",
                output_swc=str(tmp_path / "MOST" / "a.swc"),
                status="build_error",
                error="missing plugin",
            )
        ],
    }


def test_summary_and_flatten(tmp_path: Path) -> None:
    rows = flatten_trace_results(_sample_results(tmp_path))
    assert len(rows) == 3
    summary = summarize_trace_results(rows)
    assert summary["total"] == 3
    assert summary["ok"] == 1
    assert summary["timeout"] == 1
    assert summary["build_error"] == 1


def test_write_reports(tmp_path: Path) -> None:
    data = _sample_results(tmp_path)
    json_out = tmp_path / "report.json"
    csv_out = tmp_path / "report.csv"
    write_trace_report_json(data, json_out)
    write_trace_report_csv(data, csv_out)
    assert json_out.exists()
    assert csv_out.exists()
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert "summary" in payload and "results" in payload
