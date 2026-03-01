from __future__ import annotations

import json
import pickle
from pathlib import Path

from neuroutils.anatomy import get_struct_from_id_path, parse_ana_tree, parse_id_map, parse_regions316


def test_parse_anatomy_and_id_map(tmp_path: Path) -> None:
    tree = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ]
    tfile = tmp_path / "tree.json"
    tfile.write_text(json.dumps(tree), encoding="utf-8")
    mfile = tmp_path / "map.pkl"
    with mfile.open("wb") as fp:
        pickle.dump({1: 10, 2: 20}, fp)

    out = parse_ana_tree(tfile, mfile, keyname="id")
    assert out[1]["mapped_id"] == 10
    idmap = parse_id_map(mfile)
    assert idmap[2] == 20
    path_structs = get_struct_from_id_path([2, 3, 1], out)
    assert [s["id"] for s in path_structs] == [2, 1]


def test_parse_regions316(tmp_path: Path) -> None:
    f = tmp_path / "regions.csv"
    f.write_text("id\n1\n2,abc\n300\n", encoding="utf-8")
    out = parse_regions316(f)
    assert {1, 2, 300}.issubset(out)
