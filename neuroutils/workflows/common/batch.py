"""Generic directory-level batch helpers for processing and metrics."""

from __future__ import annotations

import csv
import math
import statistics
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from joblib import Parallel, delayed
from tqdm.auto import tqdm

FileProcessor = Callable[[Path, Path], dict[str, Any] | None]
MetricComputer = Callable[[Path], dict[str, Any]]


@contextmanager
def _tqdm_joblib(total: int, desc: str):
    """Patch joblib callback so tqdm progress updates with each finished task."""
    from joblib import parallel

    bar = tqdm(total=total, desc=desc, unit="file")
    original = parallel.BatchCompletionCallBack

    class _TqdmBatchCompletionCallback(original):  # type: ignore[misc]
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            bar.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    parallel.BatchCompletionCallBack = _TqdmBatchCompletionCallback  # type: ignore[assignment]
    try:
        yield bar
    finally:
        parallel.BatchCompletionCallBack = original  # type: ignore[assignment]
        bar.close()


def _list_files(input_dir: Path, pattern: str) -> list[Path]:
    return sorted([p for p in input_dir.rglob(pattern) if p.is_file()])


def process_directory_files(
    input_dir: str | Path,
    output_dir: str | Path,
    processor: FileProcessor,
    *,
    pattern: str = "*",
    n_jobs: int = -1,
    backend: str = "loky",
    show_progress: bool = True,
    skip_existing: bool = False,
) -> list[dict[str, Any]]:
    """Run one file-processing function over a directory in parallel.

    Parameters
    ----------
    input_dir:
        Input root directory.
    output_dir:
        Output root directory. Relative structure is preserved.
    processor:
        Callable with signature ``processor(input_path, output_path)``.
    pattern:
        Glob pattern, e.g. ``*.swc`` or ``*.tif``.
    skip_existing:
        If true, existing output files are skipped.
    """
    in_root = Path(input_dir)
    out_root = Path(output_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    files = _list_files(in_root, pattern)

    def _one(in_path: Path) -> dict[str, Any]:
        rel = in_path.relative_to(in_root)
        out_path = out_root / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if skip_existing and out_path.exists():
            return {"file": str(in_path), "output": str(out_path), "status": "skipped"}
        extra = processor(in_path, out_path) or {}
        return {
            "file": str(in_path),
            "output": str(out_path),
            "status": "ok",
            **extra,
        }

    if not files:
        return []

    if show_progress:
        with _tqdm_joblib(total=len(files), desc="process_directory_files"):
            rows = Parallel(n_jobs=n_jobs, backend=backend)(delayed(_one)(p) for p in files)
    else:
        rows = Parallel(n_jobs=n_jobs, backend=backend)(delayed(_one)(p) for p in files)
    return rows


def _to_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        val = float(value)
        if math.isfinite(val):
            return val
        return None
    return None


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = sorted({k for row in rows for k in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _summarize_numeric_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    by_col: dict[str, list[float]] = {}
    for row in rows:
        for k, v in row.items():
            fv = _to_float(v)
            if fv is not None:
                by_col.setdefault(k, []).append(fv)
    summary: dict[str, float] = {"n_files": float(len(rows))}
    for k, vals in sorted(by_col.items()):
        if not vals:
            continue
        summary[f"{k}_mean"] = float(statistics.fmean(vals))
        summary[f"{k}_std"] = float(statistics.pstdev(vals)) if len(vals) > 1 else 0.0
        summary[f"{k}_min"] = float(min(vals))
        summary[f"{k}_max"] = float(max(vals))
    return summary


def compute_directory_metrics(
    input_dir: str | Path,
    metric_fn: MetricComputer,
    *,
    output_csv: str | Path,
    pattern: str = "*",
    summary_csv: str | Path | None = None,
    n_jobs: int = -1,
    backend: str = "loky",
    show_progress: bool = True,
) -> dict[str, Any]:
    """Compute per-file metrics in parallel and save detail/summary CSVs."""
    in_root = Path(input_dir)
    detail_path = Path(output_csv)
    summary_path = Path(summary_csv) if summary_csv is not None else detail_path.with_name(
        f"{detail_path.stem}_summary.csv"
    )
    files = _list_files(in_root, pattern)

    def _one(in_path: Path) -> dict[str, Any]:
        out = {"file": str(in_path)}
        out.update(metric_fn(in_path))
        return out

    if not files:
        _write_csv([], detail_path)
        _write_csv([{"n_files": 0.0}], summary_path)
        return {
            "rows": [],
            "summary": {"n_files": 0.0},
            "detail_csv": str(detail_path),
            "summary_csv": str(summary_path),
        }

    if show_progress:
        with _tqdm_joblib(total=len(files), desc="compute_directory_metrics"):
            rows = Parallel(n_jobs=n_jobs, backend=backend)(delayed(_one)(p) for p in files)
    else:
        rows = Parallel(n_jobs=n_jobs, backend=backend)(delayed(_one)(p) for p in files)

    summary = _summarize_numeric_metrics(rows)
    _write_csv(rows, detail_path)
    _write_csv([summary], summary_path)
    return {
        "rows": rows,
        "summary": summary,
        "detail_csv": str(detail_path),
        "summary_csv": str(summary_path),
    }

