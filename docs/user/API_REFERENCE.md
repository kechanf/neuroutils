# API Reference

This document summarizes the current public capabilities of `neuroutils` and is suitable as source text for package documentation.

## 1. Core Models and Errors

### `neuroutils.core.types`

- `SWCNode(node_id, node_type, x, y, z, radius, parent_id)`
  - Canonical SWC node model.
- `Marker(x, y, z, radius=1.0)`
  - Generic 3D marker.
- `ensure_unique_node_ids(nodes) -> bool`
  - Returns whether SWC node IDs are unique.

### `neuroutils.core.exceptions`

- `NeuroUtilsError`
  - Base package exception.
- `SWCFormatError`
  - Raised for malformed SWC parsing input.
- `ValidationError`
  - Raised for validation failures.

## 2. IO

### `neuroutils.io.swc`

- `read_swc(path) -> list[SWCNode]`
  - Parse SWC file into typed nodes.
- `write_swc(path, nodes, header=None) -> None`
  - Write typed nodes to SWC file.

### `neuroutils.io.eswc`

- `eswc_to_swc_lines(eswc_text) -> list[str]`
  - Convert ESWC textual content to SWC 7-column lines.
- `convert_eswc_to_swc(eswc_path, swc_path) -> None`
  - Convert ESWC file to SWC file.

### `neuroutils.io.markers`

- `read_markers(path) -> list[Marker]`
  - Read CSV marker list (`x,y,z[,radius]`).
- `write_markers(path, markers) -> None`
  - Write marker CSV.

### `neuroutils.io.images`

- `load_npy_image(path) -> np.ndarray`
  - Load `.npy` image/volume.
- `save_npy_image(path, image) -> None`
  - Save image/volume as `.npy`.

## 3. Validation

### `neuroutils.validation.swc`

- `validate_swc(nodes) -> None`
  - Validates SWC consistency:
  - Non-empty input
  - Unique node IDs
  - Exactly one root (`parent_id == -1`)
  - Existing parent references
  - Non-negative radii

### `neuroutils.validation.segmentation`

- `validate_binary_mask(mask) -> None`
  - Ensures mask contains only 0/1.

### `neuroutils.validation.metadata`

- `require_keys(record, keys) -> None`
  - Ensures all required metadata keys exist.

## 4. SWC Toolkit

### `neuroutils.swc.base`

- `node_map(nodes) -> dict[int, SWCNode]`
- `children_map(nodes) -> dict[int, list[int]]`
- `find_root_ids(nodes) -> list[int]`
- `bfs_order(nodes, root_id) -> list[int]`

### `neuroutils.swc.validation`

- `assert_valid_swc(nodes) -> list[SWCNode]`
  - Validate and return nodes for pipeline chaining.

### `neuroutils.swc.sorting`

- `reindex_swc(nodes) -> list[SWCNode]`
  - Reindex nodes to contiguous IDs using BFS from root.

### `neuroutils.swc.pruning`

- `prune_short_leaf_branches(nodes, min_branch_length) -> list[SWCNode]`
  - Prune terminal leaf edges shorter than threshold.

### `neuroutils.swc.radius`

- `estimate_missing_radii(nodes, default_radius=1.0) -> list[SWCNode]`
  - Fill non-positive radii using neighborhood interpolation.

### `neuroutils.swc.convert`

- `convert_eswc_file(eswc_file, swc_file) -> None`
- `normalize_and_rewrite_swc(swc_file) -> None`

### `neuroutils.swc.analysis.connectivity`

- `ConnectivityMetrics`
  - `node_count, edge_count, root_count, branch_point_count, leaf_count`
- `compute_connectivity_metrics(nodes) -> ConnectivityMetrics`

### `neuroutils.swc.analysis.geodesic`

- `GeodesicMetrics`
  - `total_length, max_root_to_leaf_length`
- `compute_geodesic_metrics(nodes) -> GeodesicMetrics`

### `neuroutils.swc.analysis.lmeasure`

- `LMeasureLike`
  - `node_count, branch_count, tip_count, total_length, max_path_length`
- `compute_lmeasure_like(nodes) -> LMeasureLike`

### `neuroutils.swc.analysis.keypoints`

- `KeypointMetrics`
  - `roots, bifurcations, leaves`
- `compute_keypoint_metrics(nodes) -> KeypointMetrics`

### `neuroutils.swc.analysis.sholl`

- `ShollResult`
  - `radii, intersections`
- `sholl_intersections(nodes, step=10.0) -> ShollResult`
- `bhattacharyya_distance(counts_a, counts_b, eps=1e-12) -> float`
- `earth_movers_distance(counts_a, counts_b) -> float`

### `neuroutils.swc.analysis.topology`

- `TopologySummary`
  - `roots, bifurcations, leaves, edge_count`
- `summarize_topology(nodes) -> TopologySummary`

## 5. Transforms

### `neuroutils.transforms.coordinates`

- `shift_nodes(nodes, dx=0.0, dy=0.0, dz=0.0) -> list[SWCNode]`

### `neuroutils.transforms.geometry`

- `scale_nodes(nodes, sx=1.0, sy=1.0, sz=1.0) -> list[SWCNode]`

### `neuroutils.transforms.normalization`

- `center_at_root(nodes) -> list[SWCNode]`

### `neuroutils.transforms.resampling`

- `resample_edges(nodes, step) -> list[SWCNode]`

### `neuroutils.transforms.standardization`

- `standardize_swc(nodes) -> list[SWCNode]`

## 6. Morphometrics

### `neuroutils.morphometrics.global_features`

- `global_feature_dict(nodes) -> dict[str, float]`

### `neuroutils.morphometrics.local_features`

- `edge_lengths(nodes) -> list[float]`

### `neuroutils.morphometrics.comparison`

- `feature_delta(reference, target) -> dict[str, float]`

## 7. Matching and Topology Scoring

### `neuroutils.matching.points`

- `match_by_nearest(gt, pred, max_dist=5.0) -> list[(gt_id, pred_id)]`

### `neuroutils.matching.topology`

- `topology_similarity(gt, pred) -> float`

### `neuroutils.topology.metrics`

- `opt_g_score(gt, pred) -> float`
- `opt_j_score(gt, pred) -> float`
- `opt_p_score(gt, pred) -> float`
- `corr_comp_qual_score(gt, pred, max_dist=3.0) -> float`

### `neuroutils.topology.scoring`

- `composite_topology_score(gt, pred) -> dict[str, float]`
  - Returns `opt_g`, `opt_j`, `opt_p`, `ccq`, `total`.

## 8. Segmentation

### `neuroutils.segmentation.soma`

- `mask_centroid(mask) -> (z, y, x)`
- `largest_component_bbox(mask) -> (zmin, zmax, ymin, ymax, xmin, xmax)`

### `neuroutils.segmentation.postprocess`

- `threshold_mask(image, threshold) -> np.ndarray`

## 9. Visualization

### `neuroutils.visualization.base`

- `normalize_to_uint8(arr) -> np.ndarray`
- `to_rgb(gray_or_rgb) -> np.ndarray`

### `neuroutils.visualization.plotting`

- `project_volume(volume, projection="xy") -> np.ndarray`

### `neuroutils.visualization.segmentation`

- `overlay_mask(image, mask, color=(255, 0, 0), alpha=0.35) -> np.ndarray`

### `neuroutils.visualization.swc`

- `draw_swc(image, nodes, projection="xy", line_color=(255,0,0), soma_color=(0,0,255)) -> np.ndarray`
- `draw_markers(image, markers, projection="xy", color=(0,255,0)) -> np.ndarray`

### `neuroutils.visualization.gallery`

- `side_by_side(images, padding=8) -> np.ndarray`

### `neuroutils.visualization.qc`

- `make_qc_strip(raw_image, seg_overlay=None, swc_overlay=None) -> np.ndarray`

### `neuroutils.visualization.canvas`

- `Panel(image, projection="xy", title=None, mask=None, swc_nodes=[], markers=[])`
- `Panel.render() -> np.ndarray`
- `render_grid(panels, ncols=2, figsize=(12.0, 8.0), output_path=None) -> None`

## 10. Workflows and Public API

### `neuroutils.workflows.pipelines`

- `process_swc_file(input_swc, output_swc) -> None`
  - Baseline flow: validate -> estimate radii -> reindex -> standardize -> save.

### `neuroutils.workflows.evaluation`

- `evaluate_pair(gt_swc, pred_swc) -> dict[str, float]`
- `compare_global_feature_csvs(csv_a, csv_b, features=None, csv_outfile=None, json_outfile=None) -> dict`
  - Returns `summary` and `per_feature` delta statistics over shared IDs.
- `sholl_profile_for_swc(swc_file, step=10.0) -> dict`
- `sholl_profiles_for_directory(swc_dir, suffix=".swc", step=10.0, outfile=None) -> list[dict]`
- `compare_sholl_directories(gt_dir, pred_dir, suffix=".swc", step=10.0, csv_outfile=None, json_outfile=None) -> list[dict]`
  - Returns per-file `l1`, `l2`, `bhattacharyya`, `emd`, `num_radii`.

### `neuroutils.api`

- `process(input_swc, output_swc) -> None`
- `features(swc_file) -> dict[str, float]`
- `compare(gt_swc, pred_swc) -> dict[str, float]`

## 11. CLI

### `neuroutils.cli`

- `neuroutils process <input_swc> <output_swc>`
- `neuroutils features <swc_file>`
- `neuroutils compare <gt_swc> <pred_swc>`

## 12. Utilities

### `neuroutils.utils.filesystem`

- `ensure_dir(path) -> Path`

### `neuroutils.utils.math`

- `euclidean_3d(a, b) -> float`

### `neuroutils.utils.parallel`

- `thread_map(fn, items, workers=4) -> list`

### `neuroutils.utils.subprocess`

- `run_checked(cmd, timeout=300) -> CompletedProcess[str]`

## 13. Tracing Integration Boundaries

### `neuroutils.tracing.vaa3d`

- `build_app2_command(vaa3d_bin, image_file, output_swc, *, vaa3d_version=None) -> list[str]`
- `app2_command(vaa3d_bin, image_file, output_swc, *, vaa3d_version=None) -> list[str]`
  - Backward-compatible alias of APP2 command builder.
- `list_available_tracers() -> list[str]`
- `list_installed_tracers() -> list[str]`
  - On Windows, includes tracers whose plugin `.dll` can be resolved.
- `build_tracer_command(tracer, *, vaa3d_bin=None, vaa3d_version=None, image_file, output_swc=None, params=None) -> list[str]`
- `get_tracer_output_candidates(tracer, image_file, output_swc=None) -> list[str]`
  - Candidate output files considering Vaa3D auto-naming behavior.
- Backward-compatible aliases:
  - `available_tracers()`, `installed_tracers()`, `tracer_output_candidates()`

### `neuroutils.tracing.gcut`

- `gcut_command(python_bin, script_file, swc_file) -> list[str]`

### `neuroutils.tracing.runners`

- `TraceJob(command, output_swc)`
- `run_trace_job(job, timeout=300) -> CompletedProcess[str]`

## 14. Vaa3D Config Resolution

### `neuroutils.config`

- `get_vaa3d_path(task=None, version=None, default="vaa3d") -> str`
  - Resolves executable from env vars and OS-aware defaults.
- `get_vaa3d_paths(default="vaa3d") -> tuple[str, str]`
  - Returns `(vaa3d_x, vaa3d_3)`.
- `resolve_vaa3d_executable(path_or_cmd, default="vaa3d", platform=None) -> str`
  - Accepts executable path, directory path, or command name.
