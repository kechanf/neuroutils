"""Metadata mapping helpers."""

from __future__ import annotations


def invert_mapping(mapping: dict[str, str]) -> dict[str, str]:
    """Invert one-to-one string mapping."""
    return {v: k for k, v in mapping.items()}
