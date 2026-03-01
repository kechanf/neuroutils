"""High-level public API."""

from __future__ import annotations

from pathlib import Path

from neuroutils.io.swc import read_swc
from neuroutils.morphometrics import global_feature_dict
from neuroutils.topology import composite_topology_score
from neuroutils.workflows import process_swc_file


def process(input_swc: str | Path, output_swc: str | Path) -> None:
    """Run baseline morphology pipeline."""
    process_swc_file(input_swc, output_swc)


def features(swc_file: str | Path) -> dict[str, float]:
    """Compute global features."""
    return global_feature_dict(read_swc(swc_file))


def compare(gt_swc: str | Path, pred_swc: str | Path) -> dict[str, float]:
    """Compute topology comparison metrics."""
    return composite_topology_score(read_swc(gt_swc), read_swc(pred_swc))
