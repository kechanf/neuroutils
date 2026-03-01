"""External Vaa3D-based SWC preprocessing helpers."""

from __future__ import annotations

import sys
from pathlib import Path

from neuroutils.config import get_vaa3d_path
from neuroutils.utils.subprocess import run_checked


def _get_vaa3d_flag_prefix() -> str:
    """Return `/` for Windows Vaa3D CLI and `-` for Linux/macOS."""
    return "/" if sys.platform.startswith("win") else "-"


def resample_swc_external(
    swc_in: str | Path,
    swc_out: str | Path,
    *,
    step: float = 2.0,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 300,
) -> None:
    """Run the Vaa3D `resample_swc` plugin."""
    vaa3d_executable = vaa3d_bin or get_vaa3d_path("sorting", version=vaa3d_version)
    flag_prefix = _get_vaa3d_flag_prefix()
    cmd = [
        vaa3d_executable,
        f"{flag_prefix}x",
        "resample_swc",
        f"{flag_prefix}f",
        "resample_swc",
        f"{flag_prefix}i",
        str(swc_in),
        f"{flag_prefix}o",
        str(swc_out),
        f"{flag_prefix}p",
        str(step),
    ]
    run_checked(cmd, timeout=timeout)


def sort_swc_external(
    swc_in: str | Path,
    swc_out: str | Path,
    *,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 300,
) -> None:
    """Run the Vaa3D `sort_swc` plugin."""
    vaa3d_executable = vaa3d_bin or get_vaa3d_path("sorting", version=vaa3d_version)
    flag_prefix = _get_vaa3d_flag_prefix()
    cmd = [
        vaa3d_executable,
        f"{flag_prefix}x",
        "sort_neuron_swc",
        f"{flag_prefix}f",
        "sort_swc",
        f"{flag_prefix}i",
        str(swc_in),
        f"{flag_prefix}o",
        str(swc_out),
    ]
    run_checked(cmd, timeout=timeout)


def resample_sort_swc_external(
    swc_in: str | Path,
    swc_out: str | Path,
    *,
    step: float = 2.0,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 300,
) -> None:
    """Resample first, then sort SWC with Vaa3D plugins."""
    vaa3d_executable = vaa3d_bin or get_vaa3d_path("sorting", version=vaa3d_version)
    temp_resampled_swc = Path(swc_out).with_suffix(".resampled.tmp.swc")
    resample_swc_external(
        swc_in,
        temp_resampled_swc,
        step=step,
        vaa3d_bin=vaa3d_executable,
        vaa3d_version=vaa3d_version,
        timeout=timeout,
    )
    sort_swc_external(
        temp_resampled_swc,
        swc_out,
        vaa3d_bin=vaa3d_executable,
        vaa3d_version=vaa3d_version,
        timeout=timeout,
    )
    if temp_resampled_swc.exists():
        temp_resampled_swc.unlink()
