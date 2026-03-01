# Roadmap

Last updated: 2026-03-01

## Completed

- [x] Package skeleton and subpackage hierarchy
- [x] Canonical SWC IO, validation, sorting, pruning, transforms, analysis base
- [x] Vaa3D path resolution model (two env roots, internal function-level routing)
- [x] Tracing command builders and batch/report workflows
- [x] Soma segmentation base workflows and smart-region strategy
- [x] Quality report workflow (single file + directory batch)
- [x] Metadata table loading and consistency report workflow
- [x] Evaluation workflows:
  - topology pair/directory report
  - Sholl profile and directory comparison
  - global-feature extraction wrapper
- [x] Unit test coverage for migrated bottom-layer and new workflows
- [x] Documentation split:
  - user docs: `docs/user/*`
  - dev docs: `docs/dev/*`

## Current TODO (near-term)

- [ ] Continue mid-layer migration from `reference_libs`:
  - metadata converters/mappers for production manifests
  - morphology/topology summary workflows unification
- [ ] Unify report schemas across quality/topology/features/sholl
- [ ] Add CLI subcommands for new workflow reports
- [ ] Add end-to-end smoke tests on real `examples` data (without git tracking examples)
- [ ] Remove or merge duplicate functionality branches, keep canonical implementation only

## Stabilization TODO (pre-1.0)

- [ ] Freeze public API list and mark internal modules
- [ ] Publish compatibility policy (what is stable vs experimental)
- [ ] Strengthen regression tests for external tool integration (Vaa3D-x / Vaa3D-3)
- [ ] Finalize PyPI-facing user docs and release notes templates
