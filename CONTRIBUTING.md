# Contributing to neuroutils

## Setup

```bash
python -m pip install -e .[dev]
pre-commit install
```

## Development checks

Run all checks before committing:

```bash
ruff check .
ruff format .
mypy neuroutils
pytest
```

## Branch and commit

- Create a feature branch from `main`.
- Keep commits focused and small.
- Use clear commit messages.

## Pull request expectations

- Include a short summary of motivation and behavior changes.
- Add or update tests for behavior changes.
- Ensure local checks pass.