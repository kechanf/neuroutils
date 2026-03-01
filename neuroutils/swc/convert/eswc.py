"""SWC conversion wrappers."""

from __future__ import annotations

from pathlib import Path

from neuroutils.io.eswc import convert_eswc_to_swc
from neuroutils.io.swc import read_swc, write_swc


def convert_eswc_file(eswc_file: str | Path, swc_file: str | Path) -> None:
    """Convert one ESWC file to SWC."""
    convert_eswc_to_swc(eswc_file, swc_file)


def normalize_and_rewrite_swc(swc_file: str | Path) -> None:
    """Read and rewrite SWC using canonical formatting."""
    nodes = read_swc(swc_file)
    write_swc(swc_file, nodes)
