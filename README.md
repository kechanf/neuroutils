# neuroutils

Toolkit scaffold for neuron morphology processing, validation, analysis, and visualization.

The repository is now prepared for real feature implementation with packaging, CI, release automation, quality gates, and collaboration templates.

## Project status

- Functional algorithms: not implemented yet.
- Engineering foundation: ready.

## Quick start

```bash
python -m pip install -e .[dev]
pre-commit install
pytest
```

Or on PowerShell:

```powershell
./scripts/bootstrap.ps1
./scripts/check.ps1
```

## Repository structure

- `neuroutils/`: package source
- `tests/`: unit and smoke tests
- `docs/`: architecture and roadmap notes
- `scripts/`: local developer helper scripts
- `.github/workflows/`: CI and release automation

## Tooling

- Packaging: `setuptools` via `pyproject.toml`
- Lint: `ruff`
- Type checking: `mypy`
- Testing: `pytest`
- Hooks: `pre-commit`
- CI: GitHub Actions matrix (`3.10/3.11/3.12`)
- Publish: GitHub tag-based PyPI trusted publishing (`v*` tags)

## Release flow

1. Update version in `pyproject.toml` and `CHANGELOG.md`.
2. Commit and tag: `git tag vX.Y.Z`.
3. Push commits and tag.
4. GitHub Action publishes to PyPI (after PyPI trusted publisher is configured).

## Notes

- Replace placeholder repository URLs in `pyproject.toml` with your actual GitHub namespace.
- Ensure repository ownership is correct to avoid Git safe-directory warnings.

## License

MIT License. See `LICENSE`.
