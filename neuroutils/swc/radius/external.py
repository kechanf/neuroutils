"""External Vaa3D-based SWC radius estimation."""

from __future__ import annotations

import sys
from pathlib import Path

from neuroutils.config import get_vaa3d_path
from neuroutils.tracing.vaa3d.tracers import resolve_tracer_plugin_arg
from neuroutils.utils.subprocess import run_checked


def _get_vaa3d_flag_prefix() -> str:
    """Return `/` for Windows Vaa3D CLI and `-` for Linux/macOS."""
    return "/" if sys.platform.startswith("win") else "-"


def estimate_swc_radius_external(
    image_in: str | Path,
    swc_in: str | Path,
    swc_out: str | Path,
    *,
    threshold: float = 10.0,
    radius_from_2d: bool = True,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 300,
) -> None:
    """Run Vaa3D `neuron_radius` to estimate radius for all SWC nodes.

    Parameters
    ----------
    image_in:
        Input image path (typically normalized binary/uint8 volume).
    swc_in:
        Input SWC centerline.
    swc_out:
        Output SWC path with estimated radius.
    threshold:
        Foreground threshold passed to the Vaa3D plugin.
    radius_from_2d:
        Whether to estimate radius from 2D plane (`1`) vs 3D (`0`).
    """
    vaa3d_executable = vaa3d_bin or get_vaa3d_path("features", version=vaa3d_version)
    plugin_argument = resolve_tracer_plugin_arg(vaa3d_executable, "neuron_radius")
    flag_prefix = _get_vaa3d_flag_prefix()
    cmd = [
        vaa3d_executable,
        f"{flag_prefix}x",
        plugin_argument,
        f"{flag_prefix}f",
        "neuron_radius",
        f"{flag_prefix}i",
        str(image_in),
        str(swc_in),
        f"{flag_prefix}o",
        str(swc_out),
        f"{flag_prefix}p",
        str(float(threshold)),
        "1" if radius_from_2d else "0",
    ]
    run_checked(cmd, timeout=timeout)

