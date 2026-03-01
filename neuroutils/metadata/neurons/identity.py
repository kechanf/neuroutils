"""Neuron metadata helpers."""

from __future__ import annotations


def canonical_neuron_id(raw_id: str) -> str:
    """Normalize neuron identifier."""
    return raw_id.strip().lower().replace(" ", "_")
