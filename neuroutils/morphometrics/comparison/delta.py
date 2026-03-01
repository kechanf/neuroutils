"""Feature comparison."""

from __future__ import annotations


def feature_delta(reference: dict[str, float], target: dict[str, float]) -> dict[str, float]:
    """Compute target-reference per common key."""
    keys = set(reference).intersection(target)
    return {k: target[k] - reference[k] for k in sorted(keys)}
