"""Pickle helpers."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any


def load_pickle(path: str | Path) -> Any:
    """Load pickle object from file."""
    with Path(path).open("rb") as f:
        return pickle.load(f)


def save_pickle(obj: Any, path: str | Path) -> None:
    """Save object to pickle file."""
    with Path(path).open("wb") as f:
        pickle.dump(obj, f)
