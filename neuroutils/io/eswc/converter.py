"""ESWC conversion helpers."""

from __future__ import annotations

from pathlib import Path


def eswc_to_swc_lines(eswc_text: str) -> list[str]:
    """Convert ESWC text to SWC-compatible 7-column lines."""
    out: list[str] = []
    for raw in eswc_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            if line.startswith("#"):
                out.append(line)
            continue
        parts = line.split()
        out.append(" ".join(parts[:7]))
    return out


def convert_eswc_to_swc(eswc_path: str | Path, swc_path: str | Path) -> None:
    """Convert ESWC file to SWC file."""
    eswc_text = Path(eswc_path).read_text(encoding="utf-8")
    swc_lines = eswc_to_swc_lines(eswc_text)
    Path(swc_path).write_text("\n".join(swc_lines) + "\n", encoding="utf-8")
