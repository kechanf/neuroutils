from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

from neuroutils.visualization.plotting import plot_lines, sns_jointplot


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


os.environ.setdefault("MPLBACKEND", "Agg")
if _has_module("matplotlib"):
    import matplotlib

    matplotlib.use("Agg", force=True)


@pytest.mark.skipif(not _has_module("matplotlib"), reason="matplotlib not installed")
def test_plot_lines_writes_file(tmp_path: Path) -> None:
    out = tmp_path / "lines.png"
    plot_lines(
        datas=[[1.0, 2.0, 3.0], [3.0, 2.0, 1.0]],
        legends=["up", "down"],
        fmts=["-r", "--b"],
        figname=out,
    )
    assert out.exists()
    assert out.stat().st_size > 0


@pytest.mark.skipif(
    not (_has_module("matplotlib") and _has_module("seaborn") and _has_module("pandas")),
    reason="plot dependencies not installed",
)
def test_sns_jointplot_writes_file(tmp_path: Path) -> None:
    import pandas as pd

    data = pd.DataFrame(
        {
            "x": [0.1, 0.2, 0.3, 0.4],
            "y": [0.2, 0.1, 0.35, 0.5],
            "cls": ["a", "a", "b", "b"],
        }
    )
    out = tmp_path / "joint.png"
    sns_jointplot(
        data=data,
        x="x",
        y="y",
        xlim=(0.0, 0.5),
        ylim=(0.0, 0.6),
        hue="cls",
        out_fig=out,
    )
    assert out.exists()
    assert out.stat().st_size > 0
