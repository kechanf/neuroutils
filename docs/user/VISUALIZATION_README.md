# Visualization Usage

`neuroutils.visualization` is split into decoupled modules:

- `base`: array normalization
- `plotting`: 3D->2D projection
- `segmentation`: mask overlay
- `swc`: SWC/marker rendering
- `canvas`: multi-panel rendering
- `gallery`: layout composition
- `qc`: QC strip generation

## 1. Project volume

```python
from neuroutils.visualization import project_volume

xy = project_volume(volume, projection="xy")
xz = project_volume(volume, projection="xz")
```

## 2. Overlay segmentation

```python
from neuroutils.visualization import overlay_mask

overlay = overlay_mask(xy, mask_xy, color=(255, 0, 0), alpha=0.4)
```

## 3. Draw SWC and markers

```python
from neuroutils.visualization import draw_swc, draw_markers

img1 = draw_swc(xy, swc_nodes, projection="xy")
img2 = draw_markers(img1, markers, projection="xy")
```

## 4. Render panel grid

```python
from neuroutils.visualization import Panel, render_grid

panels = [
    Panel(image=volume, mask=mask, swc_nodes=swc_nodes, projection="xy", title="XY"),
    Panel(image=volume, mask=mask, swc_nodes=swc_nodes, projection="xz", title="XZ"),
]
render_grid(panels, ncols=2, output_path="result.png")
```

## 5. Build QC strip

```python
from neuroutils.visualization import make_qc_strip

qc = make_qc_strip(raw_image=xy, seg_overlay=overlay, swc_overlay=img2)
```
