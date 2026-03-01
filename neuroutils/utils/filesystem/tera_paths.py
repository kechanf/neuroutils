"""TeraFly resolution directory helpers."""

from __future__ import annotations

from pathlib import Path


def get_tera_res_paths(
    tera_dir: str | Path,
    *,
    res_ids: int | tuple[int, ...] | None = None,
    bracket_escape: bool = True,
) -> str | list[str]:
    """Return selected ``RES(...)`` paths sorted by numeric resolution."""
    root = Path(tera_dir)
    res_dirs = [p for p in root.glob("RES*") if p.is_dir()]
    if not res_dirs:
        raise FileNotFoundError(f"No RES* directories found in: {root}")

    def _res_key(p: Path) -> int:
        name = p.name
        body = name[4:-1] if name.endswith(")") else name[4:]
        return int(body.split("x")[0])

    ordered = sorted(res_dirs, key=_res_key)

    def _fmt(p: Path) -> str:
        s = str(p)
        if bracket_escape:
            s = s.replace("(", r"\(").replace(")", r"\)")
        return s

    if res_ids is None:
        return [_fmt(p) for p in ordered]
    if isinstance(res_ids, int):
        return _fmt(ordered[res_ids])
    return [_fmt(ordered[i]) for i in res_ids]

