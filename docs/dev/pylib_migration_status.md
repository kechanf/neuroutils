# pylib-main Migration Status

Last updated: 2026-03-01

## Scope
- Source reference: `reference_libs/pylib-main` (excluding `examples/` and `test/`).
- Target package: `neuroutils`.
- Goal: function-complete migration with engineering cleanup (modular layout, clearer dependencies, tests).

## Completion Summary
- Core capability migration: complete for bottom-layer modules.
- Engineering cleanup pass completed: compatibility-only duplicate aliases were removed.
- Unit test baseline: all tests in `tests/unit` pass.

## Current Canonical APIs
- SWC: `load_spacings_csv`, `filter_neurite_types`, `flip_nodes_axis`, `prune`, `tree_to_voxels`,
  `crop_sphere_from_soma`, `resample_sort_swc_external`.
- Anatomy: `ccf_to_stereotactic_mask_res25`, `resample`, `get_center`, `get_salient_regions_mask`.
- IO/util/math/spatial: canonical snake_case interfaces only (duplicate compatibility names removed).
- Validation: `SWCChecker` + rule-based checks.
- Tracing: function-based command builders/jobs (`build_tracer_command`, `TraceJob`, `build_trace_jobs_for_dir`).
- Imaging:
  - `montage_images_for_folder`, `extend_skel_to_boundary`, `get_longest_skeleton`.
- L-measure external wrappers:
  - `calc_global_features_external`, `calc_global_features_from_folder`.

## Current Test Baseline
- Command: `python -m pytest -q tests/unit`
- Status: pass.
- Notes:
  - Non-blocking warnings from third-party dependencies (`paramiko`, `jupyter_client`).
  - Plot tests now force non-interactive backend (`Agg`) to avoid hangs.

## Known Differences vs historical scripts
- Compatibility-only alias names from legacy scripts were intentionally removed to reduce duplicate APIs.
- External-tool behavior (`vaa3d`, optional dependencies) is preserved at interface level; runtime output still depends on local installed toolchain versions.

## Recommended Next Phase
- Add end-to-end smoke workflows using real sample data in `examples/`.
- Freeze public API list for `1.0.0` and trim internal compatibility aliases that are not needed for your downstream pipelines.
