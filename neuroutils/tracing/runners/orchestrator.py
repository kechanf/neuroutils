"""Tracing orchestration helpers.

This module provides middle-layer tracing workflows built on top of the
low-level command builders in ``neuroutils.tracing.vaa3d``.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired

from neuroutils.tracing.runners.base import TraceJob, run_trace_job
from neuroutils.tracing.vaa3d import (
    build_tracer_command,
    get_tracer_output_candidates,
    list_available_tracers,
    list_installed_tracers,
)


@dataclass(frozen=True, slots=True)
class TraceRunResult:
    """Execution result for one `(tracer, image)` pair."""

    tracer: str
    image_file: str
    output_swc: str
    status: str
    command: list[str] | None = None
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def _normalize_output_file(target_output: Path, candidates: list[str]) -> bool:
    """Ensure tracer output is available at `target_output`."""
    if target_output.exists():
        return True
    for candidate in candidates:
        candidate_path = Path(candidate)
        if not candidate_path.exists() or candidate_path == target_output:
            continue
        target_output.parent.mkdir(parents=True, exist_ok=True)
        candidate_path.replace(target_output)
        return True
    return False


def run_tracer_for_image(
    *,
    tracer: str,
    image_file: str | Path,
    output_root: str | Path,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 300,
    skip_existing: bool = True,
) -> TraceRunResult:
    """Run one tracer on one image and normalize output location."""
    image_path = Path(image_file)
    output_dir = Path(output_root) / tracer
    target_output = output_dir / f"{image_path.stem}.swc"
    output_dir.mkdir(parents=True, exist_ok=True)
    if skip_existing and target_output.exists():
        return TraceRunResult(
            tracer=tracer,
            image_file=str(image_path),
            output_swc=str(target_output),
            status="skipped",
        )

    try:
        command = build_tracer_command(
            tracer,
            vaa3d_bin=vaa3d_bin,
            vaa3d_version=vaa3d_version,
            image_file=str(image_path),
            output_swc=str(target_output),
        )
    except Exception as exc:
        return TraceRunResult(
            tracer=tracer,
            image_file=str(image_path),
            output_swc=str(target_output),
            status="build_error",
            error=str(exc),
        )

    candidates = get_tracer_output_candidates(tracer, str(image_path), str(target_output))
    try:
        completed = run_trace_job(TraceJob(command=command, output_swc=target_output), timeout=timeout)
        output_ok = _normalize_output_file(target_output, candidates)
        if output_ok:
            return TraceRunResult(
                tracer=tracer,
                image_file=str(image_path),
                output_swc=str(target_output),
                status="ok",
                command=command,
                returncode=completed.returncode,
                stdout=completed.stdout or "",
                stderr=completed.stderr or "",
            )
        return TraceRunResult(
            tracer=tracer,
            image_file=str(image_path),
            output_swc=str(target_output),
            status="no_output",
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            error="Tracer finished without generating SWC output",
        )
    except TimeoutExpired as exc:
        return TraceRunResult(
            tracer=tracer,
            image_file=str(image_path),
            output_swc=str(target_output),
            status="timeout",
            command=command,
            error=str(exc),
        )
    except CalledProcessError as exc:
        output_ok = _normalize_output_file(target_output, candidates)
        status = "ok" if output_ok else "failed"
        return TraceRunResult(
            tracer=tracer,
            image_file=str(image_path),
            output_swc=str(target_output),
            status=status,
            command=command,
            returncode=exc.returncode,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            error="" if output_ok else "Command failed",
        )


def run_tracers_for_image(
    *,
    image_file: str | Path,
    output_root: str | Path,
    tracers: list[str] | tuple[str, ...] | None = None,
    only_installed: bool = True,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 300,
    skip_existing: bool = True,
) -> list[TraceRunResult]:
    """Run a tracer set for a single image."""
    selected_tracers = list(tracers) if tracers is not None else list_available_tracers()
    if only_installed:
        installed = set(list_installed_tracers())
        selected_tracers = [t for t in selected_tracers if t in installed]

    return [
        run_tracer_for_image(
            tracer=tracer,
            image_file=image_file,
            output_root=output_root,
            vaa3d_bin=vaa3d_bin,
            vaa3d_version=vaa3d_version,
            timeout=timeout,
            skip_existing=skip_existing,
        )
        for tracer in selected_tracers
    ]


def run_tracer_batch_for_dir(
    *,
    tracer: str,
    image_dir: str | Path,
    output_root: str | Path,
    image_suffix: str = ".tif",
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 300,
    skip_existing: bool = True,
    max_workers: int = 1,
) -> list[TraceRunResult]:
    """Run one tracer on all images in a directory."""
    images = sorted(Path(image_dir).glob(f"*{image_suffix}"))
    if max_workers <= 1:
        return [
            run_tracer_for_image(
                tracer=tracer,
                image_file=img,
                output_root=output_root,
                vaa3d_bin=vaa3d_bin,
                vaa3d_version=vaa3d_version,
                timeout=timeout,
                skip_existing=skip_existing,
            )
            for img in images
        ]

    futures = []
    results: list[TraceRunResult] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for img in images:
            futures.append(
                executor.submit(
                    run_tracer_for_image,
                    tracer=tracer,
                    image_file=img,
                    output_root=output_root,
                    vaa3d_bin=vaa3d_bin,
                    vaa3d_version=vaa3d_version,
                    timeout=timeout,
                    skip_existing=skip_existing,
                )
            )
        for fut in as_completed(futures):
            results.append(fut.result())
    results.sort(key=lambda r: r.image_file)
    return results


def run_tracers_for_directory(
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
) -> dict[str, list[TraceRunResult]]:
    """Run multiple tracers on all images in a directory.

    Returns a tracer-keyed result dictionary.
    """
    selected_tracers = list(tracers) if tracers is not None else list_available_tracers()
    if only_installed:
        installed = set(list_installed_tracers())
        selected_tracers = [t for t in selected_tracers if t in installed]

    out: dict[str, list[TraceRunResult]] = {}
    for tracer in selected_tracers:
        out[tracer] = run_tracer_batch_for_dir(
            tracer=tracer,
            image_dir=image_dir,
            output_root=output_root,
            image_suffix=image_suffix,
            vaa3d_bin=vaa3d_bin,
            vaa3d_version=vaa3d_version,
            timeout=timeout,
            skip_existing=skip_existing,
            max_workers=max_workers,
        )
    return out
