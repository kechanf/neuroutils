"""QC strip creation."""

from __future__ import annotations

import numpy as np

from neuroutils.visualization.gallery import side_by_side


def make_qc_strip(
    raw_image: np.ndarray,
    seg_overlay: np.ndarray | None = None,
    swc_overlay: np.ndarray | None = None,
) -> np.ndarray:
    """Create a horizontal QC strip."""
    panels = [raw_image]
    if seg_overlay is not None:
        panels.append(seg_overlay)
    if swc_overlay is not None:
        panels.append(swc_overlay)
    return side_by_side(panels)
