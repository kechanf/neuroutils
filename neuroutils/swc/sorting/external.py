"""External Vaa3D-based SWC preprocessing helpers."""

from __future__ import annotations

from pathlib import Path

from neuroutils.utils.subprocess import run_checked


def resample_swc_external(
    swc_in: str | Path,
    swc_out: str | Path,
    *,
    step: float = 2.0,
    vaa3d_bin: str = "vaa3d",
    timeout: int = 300,
) -> None:
    """Run Vaa3D ``resample_swc`` plugin."""
    cmd = [
        vaa3d_bin,
        "-x",
        "resample_swc",
        "-f",
        "resample_swc",
        "-i",
        str(swc_in),
        "-o",
        str(swc_out),
        "-p",
        str(step),
    ]
    run_checked(cmd, timeout=timeout)


def sort_swc_external(
    swc_in: str | Path,
    swc_out: str | Path,
    *,
    vaa3d_bin: str = "vaa3d",
    timeout: int = 300,
) -> None:
    """Run Vaa3D ``sort_swc`` plugin."""
    cmd = [
        vaa3d_bin,
        "-x",
        "sort_neuron_swc",
        "-f",
        "sort_swc",
        "-i",
        str(swc_in),
        "-o",
        str(swc_out),
    ]
    run_checked(cmd, timeout=timeout)


def resample_sort_swc_external(
    swc_in: str | Path,
    swc_out: str | Path,
    *,
    step: float = 2.0,
    vaa3d_bin: str = "vaa3d",
    timeout: int = 300,
) -> None:
    """Resample then sort SWC via Vaa3D plugins."""
    tmp = Path(swc_out).with_suffix(".resampled.tmp.swc")
    resample_swc_external(swc_in, tmp, step=step, vaa3d_bin=vaa3d_bin, timeout=timeout)
    sort_swc_external(tmp, swc_out, vaa3d_bin=vaa3d_bin, timeout=timeout)
    if tmp.exists():
        tmp.unlink()


def resample_sort_swc(
    swc_in: str | Path,
    swc_out: str | Path,
    *,
    step: float = 2.0,
    vaa3d_bin: str = "vaa3d",
    timeout: int = 300,
) -> None:
    """Compatibility alias for external resample+sort pipeline."""
    resample_sort_swc_external(swc_in, swc_out, step=step, vaa3d_bin=vaa3d_bin, timeout=timeout)
