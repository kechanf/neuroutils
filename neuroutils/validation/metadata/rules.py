"""Metadata validation."""

from __future__ import annotations

from neuroutils.core.exceptions import ValidationError


def require_keys(record: dict[str, object], keys: list[str]) -> None:
    """Validate required keys are present."""
    missing = [k for k in keys if k not in record]
    if missing:
        raise ValidationError(f"Missing metadata keys: {', '.join(missing)}")
