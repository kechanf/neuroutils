"""Metadata record converters."""

from __future__ import annotations


def to_str_dict(record: dict[str, object]) -> dict[str, str]:
    """Convert arbitrary record to string dictionary."""
    return {k: str(v) for k, v in record.items()}
