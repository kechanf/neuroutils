"""Path metadata helpers."""

from __future__ import annotations

from pathlib import Path


def file_prefix(filepath: str | Path) -> str:
    """Return filename stem."""
    return Path(filepath).stem


def file_extension(filepath: str | Path) -> str:
    """Return filename suffix including leading dot."""
    return Path(filepath).suffix


def get_file_prefix(filepath: str | Path) -> str:
    """Compatibility alias for filename stem."""
    return file_prefix(filepath)


def get_file_extension(filepath: str | Path) -> str:
    """Compatibility alias for filename extension."""
    return file_extension(filepath)
