# pylib-main Migration Status

Last updated: 2026-03-01

## Scope
- Source reference: `reference_libs/pylib-main` (excluding `examples/` and `test/`).
- Target package: `neuroutils`.
- Goal: function-complete migration with engineering cleanup (modular layout, clearer dependencies, tests).

## Completion Summary
- Name-level migration coverage: complete.
- Automated scan result: `MISSING 0` for all `def`/`class` names from source scope.
- Unit test baseline: all tests in `tests/unit` pass.

## Implemented Compatibility Layers
- SWC ops aliases:
  - `parse_swc`, `load_spacings`, `get_child_dict`, `get_index_dict`, `prune`,
    `get_specific_neurite`, `flip_swc`, `get_soma_from_swc`, `resample_sort_swc`,
    `crop_spheric_from_soma`.
- Anatomy aliases:
  - `ccf2stereotactic_mask_res25`, `resample`, `get_center`,
    `get_salient_regions_mask671`.
- IO and utility aliases:
  - `save_markers`, `generate_ano_file`, `get_tera_res_path`,
    `get_file_prefix`, `get_file_extension`,
    `calc_included_angles_from_vectors`, `calc_included_angles_from_coords`,
    `moranI_score`, `min_distances_between_two_sets`.
- Quality/validation compatibility:
  - `remove_duplicate_nodes` file API.
  - Legacy checker classes (`MultiSomaChecker`, `TypeErrorChecker`, etc.) in validation.
- Tracing compatibility:
  - `BaseTracer`, `TracingRunner`, `RegMST`.
- Imaging migration:
  - `montage_images_for_folder`, `extend_skel_to_boundary`, `get_longest_skeleton`.
- L-measure external wrappers:
  - `calc_global_features`, plus `_create_temp_copy` and `_wrapper`.

## Current Test Baseline
- Command: `python -m pytest -q tests/unit`
- Status: pass.
- Notes:
  - Non-blocking warnings from third-party dependencies (`paramiko`, `jupyter_client`).
  - Plot tests now force non-interactive backend (`Agg`) to avoid hangs.

## Known Differences vs historical scripts
- Some legacy APIs are wrapped over cleaner internals and may not preserve incidental side-effects from old scripts.
- External-tool behavior (`vaa3d`, optional dependencies) is preserved at interface level; runtime output still depends on local installed toolchain versions.

## Recommended Next Phase
- Add end-to-end smoke workflows using real sample data in `examples/`.
- Freeze public API list for `1.0.0` and trim internal compatibility aliases that are not needed for your downstream pipelines.
