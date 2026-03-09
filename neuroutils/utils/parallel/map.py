"""Parallel execution helpers."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def thread_map(fn: Callable[[T], R], items: list[T], workers: int = 4) -> list[R]:
    """Thread-based map preserving item order."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fn, items))
