"""Manifest helpers."""

from __future__ import annotations

from pathlib import Path


def build_manifest(files: list[Path]) -> list[dict[str, str]]:
    """Build plain manifest records from file list."""
    return [{"path": str(f)} for f in files]
