"""Runtime settings."""

from __future__ import annotations

import os


def get_vaa3d_path(default: str = "vaa3d") -> str:
    """Resolve Vaa3D executable path from environment."""
    return os.environ.get("VAA3D_BIN", default)
