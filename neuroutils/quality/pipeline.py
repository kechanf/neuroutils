"""Middle-layer quality workflows for SWC files."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from neuroutils.io.swc import read_swc, write_swc
from neuroutils.quality.correctors import remove_duplicate_parent_coordinate_nodes
from neuroutils.quality.metrics import DistanceEvaluation, DistanceMetrics
from neuroutils.swc import reindex_swc
from neuroutils.transforms import standardize_swc
from neuroutils.validation.swc import SWCChecker


@dataclass(frozen=True, slots=True)
class SWCQualitySummary:
    """Structured quality report for one SWC file."""

    swc_file: str
    checks: dict[str, bool]
    passed: bool
    distance_metrics: DistanceMetrics | None = None


def evaluate_swc_quality(
    swc_file: str | Path,
    *,
    error_types: tuple[str, ...] | list[str] | None = None,
    ignore_3_4: bool = False,
    reference_swc: str | Path | None = None,
    dsa_threshold: float = 2.0,
) -> SWCQualitySummary:
    """Evaluate structural checks and optional distance metrics."""
    checker = SWCChecker(error_types=error_types, ignore_3_4=ignore_3_4)
    check_result = checker.run(swc_file)

    dist_metrics: DistanceMetrics | None = None
    if reference_swc is not None:
        evaluator = DistanceEvaluation(dsa_thr=dsa_threshold)
        dist_metrics = evaluator.run(str(swc_file), str(reference_swc))

    return SWCQualitySummary(
        swc_file=str(swc_file),
        checks=check_result.checks,
        passed=check_result.passed,
        distance_metrics=dist_metrics,
    )


def repair_and_validate_swc(
    swc_in: str | Path,
    swc_out: str | Path | None = None,
    *,
    deduplicate: bool = True,
    reindex: bool = True,
    standardize: bool = True,
    strict: bool = True,
    error_types: tuple[str, ...] | list[str] | None = None,
    ignore_3_4: bool = False,
) -> Path:
    """Apply common SWC quality repairs and validate result."""
    source = Path(swc_in)
    destination = Path(swc_out) if swc_out is not None else source

    nodes = read_swc(source)
    if deduplicate:
        nodes = remove_duplicate_parent_coordinate_nodes(nodes)
    if reindex:
        nodes = reindex_swc(nodes)
    if standardize:
        nodes = standardize_swc(nodes)

    write_swc(destination, nodes, header=["repaired by neuroutils"])
    summary = evaluate_swc_quality(
        destination,
        error_types=error_types,
        ignore_3_4=ignore_3_4,
    )
    if strict and not summary.passed:
        failed = [name for name, ok in summary.checks.items() if not ok]
        raise ValueError(f"SWC quality checks failed after repair: {failed}")
    return destination


def evaluate_swc_quality_directory(
    swc_dir: str | Path,
    *,
    suffix: str = ".swc",
    error_types: tuple[str, ...] | list[str] | None = None,
    ignore_3_4: bool = False,
    reference_dir: str | Path | None = None,
    dsa_threshold: float = 2.0,
    robust: bool = True,
    csv_outfile: str | Path | None = None,
    json_outfile: str | Path | None = None,
) -> dict[str, object]:
    """Evaluate SWC quality for all files in a directory and build report."""
    swc_files = {p.stem: p for p in sorted(Path(swc_dir).glob(f"*{suffix}"))}
    ref_files = (
        {p.stem: p for p in sorted(Path(reference_dir).glob(f"*{suffix}"))}
        if reference_dir is not None
        else {}
    )
    rows: list[dict[str, object]] = []
    failed: list[dict[str, str]] = []
    for stem, swc_path in swc_files.items():
        ref_swc = ref_files.get(stem) if reference_dir is not None else None
        try:
            summary = evaluate_swc_quality(
                swc_path,
                error_types=error_types,
                ignore_3_4=ignore_3_4,
                reference_swc=ref_swc,
                dsa_threshold=dsa_threshold,
            )
            row: dict[str, object] = {
                "id": stem,
                "swc_file": str(swc_path),
                "passed": summary.passed,
            }
            for key, value in summary.checks.items():
                row[f"check_{key}"] = value
            if summary.distance_metrics is not None:
                row["esa_total"] = summary.distance_metrics.esa[2]
                row["dsa_total"] = summary.distance_metrics.dsa[2]
                row["pds_total"] = summary.distance_metrics.pds[2]
            rows.append(row)
        except Exception as exc:
            if not robust:
                raise
            failed.append({"id": stem, "error": str(exc)})

    passed_count = sum(1 for row in rows if bool(row["passed"]))
    report: dict[str, object] = {
        "summary": {
            "num_files": len(swc_files),
            "num_evaluated": len(rows),
            "num_failed": len(failed),
            "num_passed": passed_count,
            "num_not_passed": len(rows) - passed_count,
            "num_reference_only": max(0, len(ref_files) - len(set(swc_files) & set(ref_files)))
            if reference_dir is not None
            else 0,
        },
        "rows": rows,
        "failed": failed,
    }

    if csv_outfile is not None:
        out_csv = Path(csv_outfile)
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames: list[str] = ["id", "swc_file", "passed"]
        check_keys = sorted({k for row in rows for k in row.keys() if k.startswith("check_")})
        metric_keys = ["esa_total", "dsa_total", "pds_total"]
        fieldnames.extend(check_keys)
        fieldnames.extend([k for k in metric_keys if any(k in row for row in rows)])
        with out_csv.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fieldnames})

    if json_outfile is not None:
        out_json = Path(json_outfile)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return report
