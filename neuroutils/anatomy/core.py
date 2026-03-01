"""Anatomy metadata parsing utilities."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any


def parse_ana_tree(
    tree_file: str | Path,
    map_file: str | Path | None = None,
    *,
    keyname: str = "id",
) -> dict[int, dict[str, Any]]:
    """Parse anatomy tree JSON and optional id-map into dict indexed by ``keyname``."""
    records = json.loads(Path(tree_file).read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Anatomy tree JSON must be a list of records")

    id_map: dict[int, int] | None = None
    if map_file is not None:
        with Path(map_file).open("rb") as fp:
            id_map = pickle.load(fp)

    out: dict[int, dict[str, Any]] = {}
    for item in records:
        if keyname not in item:
            continue
        cur = dict(item)
        if id_map is not None and "id" in cur:
            iid = int(cur["id"])
            if iid in id_map:
                cur["mapped_id"] = int(id_map[iid])
        out[int(cur[keyname])] = cur
    return out


def parse_regions316(regions_file: str | Path) -> set[int]:
    """Parse region id list text/csv file."""
    text = Path(regions_file).read_text(encoding="utf-8")
    out: set[int] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.replace("\t", ",").split(",")]
        for p in parts:
            if p and (p.lstrip("-").isdigit()):
                out.add(int(p))
                break
    return out


def parse_id_map(map_file: str | Path) -> dict[int, int]:
    """Parse pickled id mapping."""
    with Path(map_file).open("rb") as fp:
        data = pickle.load(fp)
    if not isinstance(data, dict):
        raise ValueError("id map must be a dict")
    return {int(k): int(v) for k, v in data.items()}


def get_struct_from_id_path(id_path: list[int], bstructs: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """Resolve region structs by path ids."""
    out: list[dict[str, Any]] = []
    for rid in id_path:
        if rid in bstructs:
            out.append(bstructs[rid])
    return out
