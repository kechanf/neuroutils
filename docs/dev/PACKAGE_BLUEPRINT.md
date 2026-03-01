# Package Blueprint

This blueprint is derived from a full scan of function/class definitions under:

- `reference_libs/neuroutils_old`
- `reference_libs/simple_swc_tool`

## Functional domains covered

- SWC/ESWC IO and conversion
- Morphology analysis (connectivity, geodesic, L-Measure, Sholl, keypoints)
- Topology scoring metrics (graph/junction/path/pixel)
- Soma detection and segmentation helpers
- Tracing runners (Vaa3D and related wrappers)
- Imaging IO/preprocess/nnUNet integration points
- Metadata mapping/tile/neuron utilities
- Visualization (canvas/plot/qc/gallery/swc overlays)
- Workflow orchestration and evaluation pipelines
- Shared utils and plugin extension points

The package hierarchy has been pre-created as empty packages to support staged code migration.
