"""Batch tracing helpers."""

from __future__ import annotations

from pathlib import Path

from neuroutils.tracing.runners.base import TraceJob
from neuroutils.tracing.vaa3d import build_tracer_command


def build_trace_jobs_for_dir(
    image_dir: str | Path,
    output_dir: str | Path,
    *,
    tracer: str,
    vaa3d_bin: str,
    image_suffix: str = ".tif",
    skip_existing: bool = True,
) -> list[TraceJob]:
    """Build TraceJob list for one tracer over one directory."""
    in_dir = Path(image_dir)
    out_dir = Path(output_dir) / tracer
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs: list[TraceJob] = []
    for img in sorted(in_dir.glob(f"*{image_suffix}")):
        out = out_dir / f"{img.stem}.swc"
        if skip_existing and out.exists():
            continue
        cmd = build_tracer_command(
            tracer,
            vaa3d_bin=vaa3d_bin,
            image_file=str(img),
            output_swc=str(out),
        )
        jobs.append(TraceJob(command=cmd, output_swc=out))
    return jobs
