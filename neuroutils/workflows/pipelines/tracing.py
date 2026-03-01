"""Tracing pipeline workflows."""

from __future__ import annotations

from pathlib import Path

from neuroutils.tracing import (
    flatten_trace_results,
    run_tracers_for_directory,
    summarize_trace_results,
    write_trace_report_csv,
    write_trace_report_json,
)


def run_tracing_directory_with_reports(
    *,
    image_dir: str | Path,
    output_root: str | Path,
    tracers: list[str] | tuple[str, ...] | None = None,
    only_installed: bool = True,
    image_suffix: str = ".tif",
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 300,
    skip_existing: bool = True,
    max_workers: int = 1,
    report_dir: str | Path | None = None,
    report_prefix: str = "tracing_report",
) -> dict[str, object]:
    """Run multi-tracer directory tracing and write summary reports."""
    results_by_tracer = run_tracers_for_directory(
        image_dir=image_dir,
        output_root=output_root,
        tracers=tracers,
        only_installed=only_installed,
        image_suffix=image_suffix,
        vaa3d_bin=vaa3d_bin,
        vaa3d_version=vaa3d_version,
        timeout=timeout,
        skip_existing=skip_existing,
        max_workers=max_workers,
    )
    rows = flatten_trace_results(results_by_tracer)
    summary = summarize_trace_results(rows)

    if report_dir is None:
        report_root = Path(output_root)
    else:
        report_root = Path(report_dir)
    report_root.mkdir(parents=True, exist_ok=True)
    json_path = report_root / f"{report_prefix}.json"
    csv_path = report_root / f"{report_prefix}.csv"
    write_trace_report_json(results_by_tracer, json_path)
    write_trace_report_csv(results_by_tracer, csv_path)

    return {
        "summary": summary,
        "json_report": str(json_path),
        "csv_report": str(csv_path),
        "results_by_tracer": results_by_tracer,
    }
