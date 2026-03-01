"""Subprocess wrappers."""

from __future__ import annotations

from subprocess import CompletedProcess, run


def run_checked(cmd: list[str], timeout: int = 300) -> CompletedProcess[str]:
    """Run command and raise on non-zero status."""
    return run(cmd, check=True, text=True, capture_output=True, timeout=timeout)
