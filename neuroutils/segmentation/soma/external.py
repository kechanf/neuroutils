"""External Vaa3D-based soma detection."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from neuroutils.config import get_vaa3d_path
from neuroutils.io.images import load_image, save_image
from neuroutils.segmentation.soma.workflows import (
    SomaDetectionResult,
    detect_soma_region_from_segmentation,
)
from neuroutils.tracing.vaa3d.tracers import resolve_tracer_plugin_arg
from neuroutils.utils.subprocess import run_checked


def _get_flag_prefix() -> str:
    return "/" if sys.platform.startswith("win") else "-"


def build_gsdt_command(
    *,
    input_image: str | Path,
    output_mask: str | Path,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    params: tuple[str, ...] = ("0", "1", "0", "1.5"),
) -> list[str]:
    """Build Vaa3D GSDT command for soma-region candidate segmentation."""
    vaa3d_executable = vaa3d_bin or get_vaa3d_path("features", version=vaa3d_version)
    flag_prefix = _get_flag_prefix()
    plugin_argument = resolve_tracer_plugin_arg(vaa3d_executable, "gsdt")
    return [
        vaa3d_executable,
        f"{flag_prefix}x",
        plugin_argument,
        f"{flag_prefix}f",
        "gsdt",
        f"{flag_prefix}i",
        str(input_image),
        f"{flag_prefix}o",
        str(output_mask),
        f"{flag_prefix}p",
        *params,
    ]


def detect_soma_region_external_gsdt(
    image_file: str | Path,
    *,
    output_mask_file: str | Path | None = None,
    temp_dir: str | Path | None = None,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 300,
    keep_largest_component: bool = True,
    padding: int = 0,
) -> SomaDetectionResult:
    """Run Vaa3D GSDT and convert output mask into soma detection result."""
    image_path = Path(image_file)
    if output_mask_file is not None:
        output_path = Path(output_mask_file)
    else:
        td = Path(temp_dir) if temp_dir is not None else image_path.parent
        td.mkdir(parents=True, exist_ok=True)
        output_path = td / f"{image_path.stem}.gsdt_mask.tif"

    command = build_gsdt_command(
        input_image=image_path,
        output_mask=output_path,
        vaa3d_bin=vaa3d_bin,
        vaa3d_version=vaa3d_version,
    )
    run_checked(command, timeout=timeout)

    if not output_path.exists():
        raise RuntimeError(f"GSDT output mask not found: {output_path}")
    gsdt_output = load_image(output_path, flip_tif=True)
    segmentation = (np.asarray(gsdt_output) > 0).astype(np.uint8)
    return detect_soma_region_from_segmentation(
        segmentation,
        keep_largest_component=keep_largest_component,
        padding=padding,
    )


def run_gsdt_on_array(
    image: np.ndarray,
    *,
    temp_dir: str | Path,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 300,
    keep_largest_component: bool = True,
    padding: int = 0,
) -> SomaDetectionResult:
    """Convenience wrapper: save ndarray to temp TIFF, run GSDT, parse result."""
    temp_root = Path(temp_dir)
    temp_root.mkdir(parents=True, exist_ok=True)
    in_file = temp_root / "soma_input.tif"
    out_file = temp_root / "soma_output.tif"
    save_image(in_file, np.asarray(image), flip_tif=True)
    return detect_soma_region_external_gsdt(
        in_file,
        output_mask_file=out_file,
        vaa3d_bin=vaa3d_bin,
        vaa3d_version=vaa3d_version,
        timeout=timeout,
        keep_largest_component=keep_largest_component,
        padding=padding,
    )
