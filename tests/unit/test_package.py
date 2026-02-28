"""Tests for package metadata and import behavior."""

import neuroutils


def test_package_importable() -> None:
    assert neuroutils is not None


def test_version_present() -> None:
    assert isinstance(neuroutils.__version__, str)
    assert neuroutils.__version__