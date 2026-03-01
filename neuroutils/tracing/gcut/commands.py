"""GCut command builders."""

from __future__ import annotations


def gcut_command(python_bin: str, script_file: str, swc_file: str) -> list[str]:
    """Build GCut python command."""
    return [python_bin, script_file, "--swc", swc_file]
