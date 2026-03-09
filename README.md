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
- SWC synthesis operators: tree/branch graft, local spur, cluster noise, break-fragment
- Random SWC tree generation with node-count / size / distance constraints
- SWC external preprocessing via Vaa3D (`resample_swc`, `sort_swc`, `resample_sort_swc`)
- Morphometric features and topology scoring
- SWC geometry stats: node count + xyz extent (width/height/depth)
- Segmentation utilities (soma centroid/bbox, thresholding)
- Visualization (MIP projection, mask overlay, SWC/marker rendering, QC strip, canvas grid)
- Generic directory batch workflows (file processing + metrics CSV/summary)
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

## Generic Batch Workflows

```python
from pathlib import Path
from neuroutils.workflows import process_directory_files, compute_directory_metrics
from neuroutils.swc.sorting.external import resample_sort_swc_external

# 1) Generic file processing over one directory
def resample_10um(src: Path, dst: Path):
    resample_sort_swc_external(src, dst, step=10.0)
    return {"step_um": 10.0}

rows = process_directory_files(
    input_dir="examples/origin_swc",
    output_dir="examples/origin_swc/resampled_10um",
    processor=resample_10um,
    pattern="*.swc",
    n_jobs=1,  # Windows-safe default for restricted environments
)
print(len(rows))

# 2) Generic metric aggregation (detail.csv + summary.csv)
report = compute_directory_metrics(
    input_dir="examples/origin_swc/resampled_10um",
    metric_fn=lambda p: {"size_bytes": p.stat().st_size},
    output_csv="tmp/size_detail.csv",
    pattern="*.swc",
    n_jobs=1,
)
print(report["summary"], report["summary_csv"])
```

## Connectivity Check

```python
from pathlib import Path
from neuroutils.validation.swc.checkers import SWCChecker

checker = SWCChecker(error_types=["SingleTree"])
for swc in Path("examples/origin_swc/resampled_10um").glob("*.swc"):
    ok = checker.run(swc).checks["SingleTree"]
    if not ok:
        swc.unlink()  # remove disconnected/non-single-tree files
```

## SWC Synthesis

```python
from neuroutils.swc import (
    graft_branch_segment,
    graft_full_tree,
    local_spur,
    small_cluster_attach,
    break_fragment_attach,
)

# low-level operators (in-memory)
nodes1 = local_spur(nodes, spur_count=8, spur_len_range=(1, 3)).nodes
nodes2 = small_cluster_attach(nodes, cluster_size=10, cluster_radius=4.0).nodes
nodes3 = break_fragment_attach(nodes, break_ratio=0.12, reconnect_prob=0.5).nodes
```

```python
from neuroutils.workflows import synthesize_swc_with_strategies

# middle-level serial synthesis on one target SWC
logs = synthesize_swc_with_strategies(
    input_swc="target.swc",
    output_swc="target_synth.swc",
    strategies=[
        {"name": "branch_segment_graft", "params": {"max_hops": 10}},
        {"name": "local_spur", "params": {"spur_count": 8, "spur_len_range": (1, 3)}},
        {"name": "small_cluster_attach", "params": {"cluster_size": 10, "cluster_radius": 4.0}},
        {"name": "break_fragment_attach", "params": {"break_ratio": 0.12, "offset": (2.0, 8.0)}},
    ],
    donor_swc_paths=["donor_a.swc", "donor_b.swc"],
    seed=42,
)
print(logs)
```

## Random Tree Generation

```python
from neuroutils.swc import generate_random_tree_swc

generate_random_tree_swc(
    "random_tree.swc",
    n_points=200,
    max_size_xyz=(300, 300, 120),
    point_distance_range=(1.0, 10.0),  # default
    min_node_distance=1.0,
    seed=42,
)
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

## Core usage guide

See [docs/user/CORE_USAGE.md](docs/user/CORE_USAGE.md) for step-by-step feature workflows (including 2.5D rotational annotation).
