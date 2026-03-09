from __future__ import annotations

from pathlib import Path

import pytest

from neuroutils.io.swc import read_swc
from neuroutils.workflows.pipelines import synthesize_swc_with_strategies


def _write_swc(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_synthesize_swc_with_strategies_serial(tmp_path: Path) -> None:
    target = tmp_path / "target.swc"
    donor = tmp_path / "donor.swc"
    out = tmp_path / "out.swc"
    _write_swc(
        target,
        [
            "1 1 0 0 0 1 -1",
            "2 3 1 0 0 1 1",
            "3 3 2 0 0 1 2",
        ],
    )
    _write_swc(
        donor,
        [
            "10 1 10 0 0 1 -1",
            "11 3 11 0 0 1 10",
            "12 3 12 0 0 1 11",
        ],
    )
    logs = synthesize_swc_with_strategies(
        target,
        out,
        strategies=[
            {"name": "local_spur", "params": {"spur_count": 1, "spur_len_range": (2, 2)}},
            {"name": "small_cluster_attach", "cluster_size": 3, "cluster_radius": 2.0},
            {"name": "branch_segment_graft", "max_hops": 2, "donor_index": 0},
        ],
        donor_swc_paths=[donor],
        seed=42,
    )
    assert out.exists()
    out_nodes = read_swc(out)
    assert len(logs) == 3
    assert [x.name for x in logs] == ["local_spur", "small_cluster_attach", "branch_segment_graft"]
    assert len(out_nodes) > 3
    assert logs[-1].total_nodes_after == len(out_nodes)


def test_synthesize_graft_requires_donor(tmp_path: Path) -> None:
    target = tmp_path / "target.swc"
    out = tmp_path / "out.swc"
    _write_swc(
        target,
        [
            "1 1 0 0 0 1 -1",
            "2 3 1 0 0 1 1",
        ],
    )
    with pytest.raises(ValueError):
        synthesize_swc_with_strategies(
            target,
            out,
            strategies=[{"name": "full_tree_graft"}],
            donor_swc_paths=None,
            seed=0,
        )
