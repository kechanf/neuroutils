"""Panel-grid rendering with optional matplotlib backend."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from neuroutils.core.types import Marker, SWCNode
from neuroutils.visualization.plotting import project_volume
from neuroutils.visualization.segmentation import overlay_mask
from neuroutils.visualization.swc import draw_markers, draw_swc


@dataclass(slots=True)
class Panel:
    """Composable panel containing image + optional overlays."""

    image: np.ndarray
    projection: str = "xy"
    title: str | None = None
    mask: np.ndarray | None = None
    swc_nodes: list[SWCNode] = field(default_factory=list)
    markers: list[Marker] = field(default_factory=list)

    def render(self) -> np.ndarray:
        """Render panel to RGB image."""
        out = project_volume(self.image, projection=self.projection)
        if self.mask is not None:
            out = overlay_mask(out, project_volume(self.mask, projection=self.projection) > 0)
        if self.swc_nodes:
            out = draw_swc(out, self.swc_nodes, projection=self.projection)
        if self.markers:
            out = draw_markers(out, self.markers, projection=self.projection)
        return out


def render_grid(
    panels: list[Panel],
    ncols: int = 2,
    figsize: tuple[float, float] = (12.0, 8.0),
    output_path: str | None = None,
) -> None:
    """Render a panel grid; requires matplotlib only for display/save."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("render_grid requires matplotlib. Install with pip install matplotlib") from exc

    if not panels:
        raise ValueError("panels cannot be empty")
    nrows = (len(panels) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
    axes_flat = np.atleast_1d(axes).ravel()
    for i, ax in enumerate(axes_flat):
        if i >= len(panels):
            ax.axis("off")
            continue
        panel = panels[i]
        ax.imshow(panel.render())
        ax.axis("off")
        if panel.title:
            ax.set_title(panel.title)
    fig.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()
