"""Reporting helpers for tracing orchestration results."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from neuroutils.tracing.runners.orchestrator import TraceRunResult


def flatten_trace_results(results_by_tracer: dict[str, list[TraceRunResult]]) -> list[TraceRunResult]:
    """Flatten tracer-keyed result dict into one list."""
    rows: list[TraceRunResult] = []
    for tracer in sorted(results_by_tracer.keys()):
        rows.extend(results_by_tracer[tracer])
    return rows


def summarize_trace_results(results: list[TraceRunResult]) -> dict[str, int]:
    """Compute aggregate counts for trace run statuses."""
    summary = {
        "total": len(results),
        "ok": 0,
        "failed": 0,
        "skipped": 0,
        "timeout": 0,
        "build_error": 0,
        "no_output": 0,
    }
    for result in results:
        status = result.status
        if status in summary:
            summary[status] += 1
        elif status != "ok":
            summary["failed"] += 1
        if status not in {"ok", "skipped"}:
            summary["failed"] += 1
    return summary


def write_trace_report_json(
    results_by_tracer: dict[str, list[TraceRunResult]],
    outfile: str | Path,
) -> Path:
    """Write full tracing report as JSON."""
    rows = flatten_trace_results(results_by_tracer)
    summary = summarize_trace_results(rows)
    payload = {
        "summary": summary,
        "results": [
            {
                "tracer": r.tracer,
                "image_file": r.image_file,
                "output_swc": r.output_swc,
                "status": r.status,
                "returncode": r.returncode,
                "command": r.command,
                "error": r.error,
            }
            for r in rows
        ],
    }
    out_path = Path(outfile)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def write_trace_report_csv(
    results_by_tracer: dict[str, list[TraceRunResult]],
    outfile: str | Path,
) -> Path:
    """Write flattened tracing report rows as CSV."""
    out_path = Path(outfile)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = flatten_trace_results(results_by_tracer)
    with out_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=["tracer", "image_file", "output_swc", "status", "returncode", "error"],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "tracer": r.tracer,
                    "image_file": r.image_file,
                    "output_swc": r.output_swc,
                    "status": r.status,
                    "returncode": r.returncode if r.returncode is not None else "",
                    "error": r.error,
                }
            )
    return out_path
