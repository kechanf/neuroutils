"""Simple line plotting helpers."""

from __future__ import annotations

from pathlib import Path


def plot_lines(
    datas: list[list[float] | tuple[float, ...]],
    legends: list[str],
    *,
    fmts: list[str] | None = None,
    figname: str | Path = "fig.png",
    linewidth: float = 1.0,
    grid: bool = True,
    xlabel: str = "X-axis",
    ylabel: str = "Y-axis",
) -> None:
    """Plot multiple lines and save figure."""
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise RuntimeError("plot_lines requires matplotlib") from exc

    plt.figure()
    if fmts is None:
        fmts = ["-"] * len(datas)
    for y, leg, fmt in zip(datas, legends, fmts):
        plt.plot(y, fmt, linewidth=linewidth, label=leg)
    plt.grid(grid)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if legends:
        plt.legend()
    out = Path(figname)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
