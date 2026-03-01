"""Dataset loaders."""

from __future__ import annotations

from pathlib import Path


def list_swc_files(directory: str | Path) -> list[Path]:
    """List SWC/ESWC files in directory recursively."""
    root = Path(directory)
    files = list(root.rglob("*.swc")) + list(root.rglob("*.eswc"))
    return sorted(files)
