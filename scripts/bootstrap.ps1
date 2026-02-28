#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
python -m pip install -e .[dev]
pre-commit install

Write-Host "Bootstrap complete."
