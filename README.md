# neuroutils

Neuron morphology toolkit covering IO, validation, transforms, morphometrics, topology scoring, workflows, and visualization.

## Installation

```bash
python -m pip install -e .[dev]
```

## Vaa3D Environment Variables

Set only two Vaa3D version paths in your OS environment:

```bash
# explicit version paths
NEUROUTILS_VAA3D_X=/path/to/vaa3d-x
NEUROUTILS_VAA3D_3=/path/to/vaa3d-3
```

Each variable can point to either:
- a Vaa3D executable file (`.../vaa3d_msvc.exe`, `.../Vaa3D-x`)
- or a Vaa3D install directory (neuroutils will auto-detect executable name for Windows/Linux)

Internal default version routing:
- SWC sorting/resample -> `vaa3d-x` (from `neuroutils_old.swc.standardize`)
- global features (`global_neuron_feature`) -> `vaa3d-x` (from `neuroutils_old.swc.analysis.l_measure`)
- tracing -> tracer-level mapping (from `neuroutils_old.tracing.big_neuron_tracers`):
  - defaults to `vaa3d-x`: `APP1`, `APP2`, `APP2_NEW1/2/3`, `Advantra`, `Advantra2`, `TreMap`
  - defaults to `vaa3d-3`: `MOST`, `NEUTUBE`, `MST`, `NeuroGPSTree`, `NeuroGPSTree2`, `FMST`, `CWlab11`
  - tracers without explicit legacy binding fall back to task default (`vaa3d-x`)

You can override per call with function parameter `vaa3d_version="x"` or `"3"` where supported.

### Low-level Tracing API (standardized names)

```python
from neuroutils.tracing import (
    list_available_tracers,
    list_installed_tracers,
    build_tracer_command,
    get_tracer_output_candidates,
)

all_tracers = list_available_tracers()
installed = list_installed_tracers()  # Windows: checks plugin dll resolvability

cmd = build_tracer_command(
    "APP2",
    image_file="examples/image_40009_0000.tif",
    output_swc="tmp/app2.swc",
)

print(cmd)
print(get_tracer_output_candidates("APP2", "examples/image_40009_0000.tif", "tmp/app2.swc"))
```

Backwards-compatible aliases remain available:
- `available_tracers()` -> `list_available_tracers()`
- `installed_tracers()` -> `list_installed_tracers()`
- `tracer_output_candidates()` -> `get_tracer_output_candidates()`

### Batch Tracing With Reports

```python
from neuroutils.workflows import run_tracing_directory_with_reports

result = run_tracing_directory_with_reports(
    image_dir="examples",
    output_root="tmp/trace_out",
    image_suffix=".tif",
    only_installed=True,
    timeout=120,
)
print(result["summary"])
print(result["json_report"], result["csv_report"])
```

### Soma Region From Vaa3D GSDT

```python
from neuroutils.segmentation import detect_soma_region_external_gsdt

soma = detect_soma_region_external_gsdt(
    "examples/image_40009_0000.tif",
    temp_dir="tmp/soma",
)
print(soma.centroid_zyx, soma.bbox_zyxzyx, soma.voxel_count)
```

### Smart Soma Detection (No External Dependency)

```python
from neuroutils.segmentation import detect_soma_region_smart
import numpy as np

image = np.load("example_volume.npy")  # z,y,x
res = detect_soma_region_smart(image)
print(res.centroid_zyx, res.bbox_zyxzyx)
```

### Metadata Consistency Report

```python
from neuroutils.metadata import validate_metadata_table_consistency

report = validate_metadata_table_consistency(
    "metadata.csv",
    json_outfile="tmp/metadata_report.json",
)
print(report["summary"])
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

See [docs/user/VISUALIZATION_README.md](docs/user/VISUALIZATION_README.md).

## Full API reference

See [docs/user/API_REFERENCE.md](docs/user/API_REFERENCE.md) for full function/module documentation text.
