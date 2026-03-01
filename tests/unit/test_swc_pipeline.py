from __future__ import annotations

from pathlib import Path

from neuroutils.io import read_swc, write_swc
from neuroutils.swc import assert_valid_swc, reindex_swc


def test_read_write_and_reindex(tmp_path: Path) -> None:
    swc = tmp_path / "a.swc"
    swc.write_text(
        "\n".join(
            [
                "10 1 0 0 0 1 -1",
                "12 3 1 0 0 1 10",
                "20 3 2 0 0 1 12",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    nodes = read_swc(swc)
    assert_valid_swc(nodes)
    reindexed = reindex_swc(nodes)
    out = tmp_path / "b.swc"
    write_swc(out, reindexed)
    reread = read_swc(out)
    assert [n.node_id for n in reread] == [1, 2, 3]
