"""Legacy-style tracing runner classes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from neuroutils.tracing.runners import TraceJob, build_trace_jobs_for_dir, run_trace_job
from neuroutils.tracing.vaa3d import build_tracer_command


@dataclass
class BaseTracer:
    """Compatibility tracer wrapper with callable interface."""

    tracer: str
    vaa3d_path: str = "vaa3d"
    timeout: int = 300

    def __call__(self, infile: str | Path, outfile: str | Path) -> None:
        cmd = build_tracer_command(
            self.tracer,
            vaa3d_bin=self.vaa3d_path,
            image_file=str(infile),
            output_swc=str(outfile),
        )
        run_trace_job(TraceJob(command=cmd, output_swc=outfile), timeout=self.timeout)


class RegMST(BaseTracer):
    def __init__(self, vaa3d_path: str = "vaa3d", p0: int = 21, p1: int = 200, timeout: int = 300) -> None:
        super().__init__(tracer="RegMST", vaa3d_path=vaa3d_path, timeout=timeout)
        self.p0 = p0
        self.p1 = p1

    def __call__(self, infile: str | Path, outfile: str | Path) -> None:
        cmd = build_tracer_command(
            "RegMST",
            vaa3d_bin=self.vaa3d_path,
            image_file=str(infile),
            output_swc=str(outfile),
            params=(str(self.p0), str(self.p1)),
        )
        run_trace_job(TraceJob(command=cmd, output_swc=outfile), timeout=self.timeout)


class TracingRunner:
    """Batch helper that mirrors legacy run_tracers API shape."""

    def __init__(self, vaa3d_path: str = "vaa3d", tracers: list[str] | None = None) -> None:
        self.vaa3d_path = vaa3d_path
        self.tracers = list(tracers or [])

    def run_in_tracer(
        self,
        imgdir: str | Path,
        outdir: str | Path,
        *,
        file_ext: str = ".tif",
        skip_existing: bool = True,
    ) -> list[TraceJob]:
        jobs: list[TraceJob] = []
        for tracer in self.tracers:
            jobs.extend(
                build_trace_jobs_for_dir(
                    imgdir,
                    outdir,
                    tracer=tracer,
                    vaa3d_bin=self.vaa3d_path,
                    image_suffix=file_ext,
                    skip_existing=skip_existing,
                )
            )
        return jobs
