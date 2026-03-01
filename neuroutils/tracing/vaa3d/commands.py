"""Vaa3D command builders."""

from __future__ import annotations

import sys

from neuroutils.config import get_vaa3d_path
from neuroutils.tracing.vaa3d.tracers import resolve_tracer_plugin_arg


def app2_command(
    vaa3d_bin: str | None,
    image_file: str,
    output_swc: str,
    *,
    vaa3d_version: str | None = None,
) -> list[str]:
    """Build an APP2 Vaa3D CLI command.

    This low-level helper is intentionally small and deterministic.
    For multi-tracer dispatch, use `build_tracer_command`.
    """
    vaa3d_executable = vaa3d_bin or get_vaa3d_path("tracing", version=vaa3d_version)
    flag_prefix = "/" if sys.platform.startswith("win") else "-"
    plugin_argument = resolve_tracer_plugin_arg(vaa3d_executable, "vn2")
    return [
        vaa3d_executable,
        f"{flag_prefix}x",
        plugin_argument,
        f"{flag_prefix}f",
        "app2",
        f"{flag_prefix}i",
        image_file,
        f"{flag_prefix}o",
        output_swc,
    ]


def build_app2_command(
    vaa3d_bin: str | None,
    image_file: str,
    output_swc: str,
    *,
    vaa3d_version: str | None = None,
) -> list[str]:
    """Preferred name for APP2 command builder."""
    return app2_command(vaa3d_bin, image_file, output_swc, vaa3d_version=vaa3d_version)
