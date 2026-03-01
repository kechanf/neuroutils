# neuroutils

Neuron morphology toolkit covering IO, validation, transforms, morphometrics, topology scoring, workflows, and visualization.

## Installation

```bash
python -m pip install -e .[dev]
```

## Main capabilities

- SWC/ESWC/marker/image IO
- SWC validation, reindexing, pruning, standardization
- Morphometric features and topology scoring
- Segmentation utilities (soma centroid/bbox, thresholding)
- Visualization (MIP projection, mask overlay, SWC/marker rendering, QC strip, canvas grid)
- Pipeline and evaluation workflows
- CLI: `neuroutils process|features|compare`

## Quick usage

```python
from neuroutils.io import read_swc
from neuroutils.swc import assert_valid_swc
from neuroutils.morphometrics import global_feature_dict
from neuroutils.topology import composite_topology_score

nodes = read_swc("example.swc")
assert_valid_swc(nodes)
features = global_feature_dict(nodes)
print(features)
```

```python
from neuroutils.visualization import Panel, render_grid

panel = Panel(image=volume_3d, projection="xy", swc_nodes=nodes, mask=seg_mask, title="XY View")
render_grid([panel], ncols=1, output_path="viz.png")
```

## CLI

```bash
neuroutils process in.swc out.swc
neuroutils features in.swc
neuroutils compare gt.swc pred.swc
```

## Visualization guide

See [docs/VISUALIZATION_README.md](docs/VISUALIZATION_README.md).

## Full API reference

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for full function/module documentation text.
