from __future__ import annotations

import numpy as np

from neuroutils.core.types import Marker, SWCNode
from neuroutils.visualization import draw_markers, draw_swc, overlay_mask, project_volume


def test_visualization_primitives() -> None:
    vol = np.zeros((3, 16, 16), dtype=np.uint8)
    vol[:, 5:8, 5:8] = 100
    proj = project_volume(vol, projection="xy")
    assert proj.shape == (16, 16)

    mask = np.zeros((16, 16), dtype=np.uint8)
    mask[6:10, 6:10] = 1
    over = overlay_mask(proj, mask)
    assert over.shape == (16, 16, 3)

    nodes = [
        SWCNode(1, 1, 4, 4, 0, 2, -1),
        SWCNode(2, 3, 12, 12, 0, 1, 1),
    ]
    rendered = draw_swc(over, nodes)
    marked = draw_markers(rendered, [Marker(x=8, y=8, z=0, radius=2)])
    assert marked.shape == (16, 16, 3)
