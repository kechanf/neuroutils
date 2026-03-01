"""Vaa3D command builders."""

from __future__ import annotations


def app2_command(vaa3d_bin: str, image_file: str, output_swc: str) -> list[str]:
    """Build APP2 command."""
    return [
        vaa3d_bin,
        "-x",
        "vn2",
        "-f",
        "app2",
        "-i",
        image_file,
        "-o",
        output_swc,
    ]
