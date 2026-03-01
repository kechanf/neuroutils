# Progress Log

## 2026-03-01

### Major engineering updates

- Completed bottom-layer migration cleanup with canonical snake_case APIs.
- Standardized Vaa3D integration:
  - explicit dual-version handling (`vaa3d-x`, `vaa3d-3`)
  - internal per-function routing policy
  - Windows/Linux path resolution support.
- Added/updated tracing orchestration and reporting workflows.
- Added directory-level quality evaluation and report export.
- Added metadata consistency report workflow for table inputs.
- Added/extended soma workflows:
  - smarter multi-threshold candidate strategy
  - robust thresholding behavior for sparse foreground.
- Extended Sholl workflows:
  - directory comparison with `l1`, `l2`, `bhattacharyya`, `emd`
  - optional CSV/JSON report export.
- Added global-feature CSV comparison workflow with per-feature delta statistics.
- Reorganized docs by audience:
  - `docs/user/*`: usage/API docs
  - `docs/dev/*`: architecture/roadmap/migration/blueprint docs.

### Test status snapshot

- Newly added and updated unit tests for:
  - tracing workflows/reporting
  - soma workflows
  - quality pipeline/reporting
  - metadata consistency
  - topology/sholl/features evaluation workflows.
- Current targeted regression runs in this stage: passed.

### Outstanding work

- Continue mid-layer migration items from `reference_libs`.
- Unify report schema and naming conventions across workflows.
- Build e2e smoke tests using local examples (examples not tracked in git).
