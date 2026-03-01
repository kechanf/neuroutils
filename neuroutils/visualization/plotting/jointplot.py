"""Seaborn joint-plot helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def sns_jointplot(
    data: Any,
    x: str,
    y: str,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    hue: str,
    out_fig: str | Path,
    *,
    markersize: int = 10,
    hue_order: list[str] | None = None,
) -> None:
    """Create seaborn jointplot and save figure."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except Exception as exc:
        raise RuntimeError("sns_jointplot requires seaborn and matplotlib") from exc

    g = sns.jointplot(
        data=data,
        x=x,
        y=y,
        hue=hue,
        hue_order=hue_order,
        s=markersize,
        marginal_kws={"common_norm": False},
    )
    g.ax_joint.set_xlim(*xlim)
    g.ax_joint.set_ylim(*ylim)
    out = Path(out_fig)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
