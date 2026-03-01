"""Tracing runner abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess, run


@dataclass(frozen=True, slots=True)
class TraceJob:
    """One tracing execution request."""

    command: list[str]
    output_swc: str | Path


def run_trace_job(job: TraceJob, timeout: int = 300) -> CompletedProcess[str]:
    """Execute tracing command."""
    return run(job.command, check=True, text=True, capture_output=True, timeout=timeout)
