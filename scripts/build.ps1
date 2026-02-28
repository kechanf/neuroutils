#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"

python -m build

Write-Host "Build complete under dist/."
