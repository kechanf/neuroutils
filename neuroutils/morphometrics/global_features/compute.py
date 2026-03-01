"""Global morphometric feature extraction."""

from __future__ import annotations

from neuroutils.core.types import SWCNode
from neuroutils.swc.analysis import compute_lmeasure_like


def global_feature_dict(nodes: list[SWCNode]) -> dict[str, float]:
    """Return a stable global feature dictionary."""
    f = compute_lmeasure_like(nodes)
    return {
        "node_count": float(f.node_count),
        "branch_count": float(f.branch_count),
        "tip_count": float(f.tip_count),
        "total_length": float(f.total_length),
        "max_path_length": float(f.max_path_length),
    }
