"""Morphology processing pipeline."""

from __future__ import annotations

from pathlib import Path

from neuroutils.io.swc import read_swc, write_swc
from neuroutils.swc import assert_valid_swc, estimate_missing_radii, reindex_swc
from neuroutils.transforms import standardize_swc


def process_swc_file(input_swc: str | Path, output_swc: str | Path) -> None:
    """Process one SWC file through baseline pipeline."""
    nodes = read_swc(input_swc)
    assert_valid_swc(nodes)
    nodes = estimate_missing_radii(nodes)
    nodes = reindex_swc(nodes)
    nodes = standardize_swc(nodes)
    write_swc(output_swc, nodes, header=["processed by neuroutils"])
