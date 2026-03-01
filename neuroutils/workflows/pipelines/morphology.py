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


def process_swc_directory(
    input_dir: str | Path,
    output_dir: str | Path,
    *,
    suffix: str = ".swc",
    skip_existing: bool = True,
    robust: bool = True,
) -> list[Path]:
    """Process all SWCs in a directory with the baseline morphology pipeline."""
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for src in sorted(in_dir.glob(f"*{suffix}")):
        dst = out_dir / src.name
        if skip_existing and dst.exists():
            outputs.append(dst)
            continue
        try:
            process_swc_file(src, dst)
            outputs.append(dst)
        except Exception:
            if robust:
                continue
            raise
    return outputs
