#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"

ruff check .
mypy neuroutils
pytest
python -m build

Write-Host "All checks passed."
