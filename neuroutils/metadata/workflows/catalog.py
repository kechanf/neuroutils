"""Metadata middle-layer workflows."""

from __future__ import annotations

import csv
import re
from pathlib import Path


def extract_neuron_id_from_filename(filename: str) -> int:
    """Extract the first numeric token from filename/path as neuron ID."""
    name = Path(filename).stem
    matches = re.findall(r"\d+", name)
    if not matches:
        raise ValueError(f"No numeric neuron id found in: {filename}")
    return int(matches[0])


def _load_table_records(table_file: str | Path) -> list[dict[str, str]]:
    path = Path(table_file)
    if path.suffix.lower() in {".csv", ".tsv"}:
        delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        with path.open("r", encoding="utf-8-sig", newline="") as fp:
            reader = csv.DictReader(fp, delimiter=delimiter)
            return [{str(k): str(v) for k, v in row.items()} for row in reader]
    if path.suffix.lower() in {".xlsx", ".xls"}:
        try:
            import pandas as pd
        except Exception as exc:  # pragma: no cover - guarded by runtime dependency
            raise ValueError("Reading Excel metadata requires pandas/openpyxl installed") from exc
        df = pd.read_excel(path)
        return [
            {str(k): str(v) for k, v in row.items()}
            for row in df.to_dict(orient="records")
        ]
    raise ValueError(f"Unsupported metadata table format: {path.suffix}")


def load_metadata_table_records(table_file: str | Path) -> list[dict[str, str]]:
    """Public wrapper to load metadata table rows as string dictionaries."""
    return _load_table_records(table_file)


def split_metadata_table_by_neuron_id(
    table_file: str | Path,
    output_dir: str | Path,
    *,
    id_columns: tuple[str, ...] = ("cell_id", "Cell ID"),
) -> list[Path]:
    """Split metadata table into one record CSV per neuron ID."""
    records = _load_table_records(table_file)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    def _pick_id(record: dict[str, str]) -> int:
        for col in id_columns:
            if col in record and str(record[col]).strip():
                return int(float(str(record[col]).strip()))
        raise ValueError(f"Cannot find neuron id from columns: {id_columns}")

    out_files: list[Path] = []
    for record in records:
        neuron_id = _pick_id(record)
        out_file = out_dir / f"{neuron_id}.csv"
        with out_file.open("w", encoding="utf-8", newline="") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(record.keys()))
            writer.writeheader()
            writer.writerow(record)
        out_files.append(out_file)
    return out_files


def load_neuron_metadata_record(
    neuron_id: int,
    *,
    table_file: str | Path,
    cache_dir: str | Path | None = None,
    id_columns: tuple[str, ...] = ("cell_id", "Cell ID"),
    use_cache: bool = True,
) -> dict[str, str]:
    """Load one neuron metadata record from table, with optional cache."""
    if cache_dir is not None:
        cached = Path(cache_dir) / f"{int(neuron_id)}.csv"
        if use_cache and cached.exists():
            with cached.open("r", encoding="utf-8-sig", newline="") as fp:
                rows = list(csv.DictReader(fp))
                if rows:
                    return {str(k): str(v) for k, v in rows[0].items()}

    records = _load_table_records(table_file)
    match: dict[str, str] | None = None
    for record in records:
        for col in id_columns:
            if col not in record:
                continue
            try:
                rid = int(float(str(record[col]).strip()))
            except Exception:
                continue
            if rid == int(neuron_id):
                match = record
                break
        if match is not None:
            break
    if match is None:
        raise ValueError(f"Neuron id not found: {neuron_id}")

    if cache_dir is not None and use_cache:
        out_dir = Path(cache_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{int(neuron_id)}.csv"
        with out_file.open("w", encoding="utf-8", newline="") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(match.keys()))
            writer.writeheader()
            writer.writerow(match)
    return match


def map_neuron_id(
    neuron_id: int,
    mapping_records: list[dict[str, str]],
    *,
    old_column: str = "old_id",
    new_column: str = "new_id",
    old_to_new: bool = False,
) -> int | None:
    """Map neuron id by provided mapping records."""
    src = old_column if old_to_new else new_column
    dst = new_column if old_to_new else old_column
    for record in mapping_records:
        if src not in record or dst not in record:
            continue
        try:
            rid = int(float(str(record[src]).strip()))
        except Exception:
            continue
        if rid == int(neuron_id):
            try:
                return int(float(str(record[dst]).strip()))
            except Exception:
                return None
    return None


def tile_id_from_record(
    record: dict[str, str],
    *,
    candidate_columns: tuple[str, ...] = ("document_name", "PTRS(B)", "PTRSB"),
) -> str | None:
    """Extract tile/document id from one metadata record."""
    for col in candidate_columns:
        if col in record and str(record[col]).strip():
            return str(record[col]).strip()
    return None


def xy_z_resolution_from_record(
    record: dict[str, str],
    *,
    xy_columns: tuple[str, ...] = ("xy_resolution", "xy拍摄分辨率(*10e-3μm/px)"),
    z_columns: tuple[str, ...] = ("z_resolution", "z拍摄分辨率(*10e-3μm/px)"),
) -> tuple[float, float]:
    """Extract `(xy_resolution, z_resolution)` from metadata record."""
    xy_val: float | None = None
    z_val: float | None = None
    for col in xy_columns:
        if col in record and str(record[col]).strip():
            xy_val = float(record[col])
            break
    for col in z_columns:
        if col in record and str(record[col]).strip():
            z_val = float(record[col])
            break
    if xy_val is None or z_val is None:
        raise ValueError("Cannot find xy/z resolution in record")
    return xy_val, z_val


def v3dpbd_relative_path_from_cell_id(cell_id: int, *, min_digits: int = 5) -> str:
    """Build hierarchical V3DPBD relative path by numeric cell id."""
    if cell_id <= 0:
        raise ValueError("cell_id must be positive")
    thousand_start = (cell_id // 1000) * 1000
    thousand_end = thousand_start + 999
    hundred_start = thousand_start + ((cell_id % 1000) // 100) * 100
    hundred_end = hundred_start + 99
    thousand_range = f"{thousand_start:0>{min_digits}d}_{thousand_end:0>{min_digits}d}"
    hundred_range = f"{hundred_start:0>{min_digits}d}_{hundred_end:0>{min_digits}d}"
    file_name = f"{cell_id:0>{min_digits}d}.v3dpbd"
    return str(Path(thousand_range) / hundred_range / file_name)


def rebuild_metadata_cache(
    table_file: str | Path,
    cache_dir: str | Path,
    *,
    id_columns: tuple[str, ...] = ("cell_id", "Cell ID"),
) -> int:
    """Rebuild cache directory and return number of generated cache files."""
    out_dir = Path(cache_dir)
    if out_dir.exists():
        for f in out_dir.glob("*.csv"):
            f.unlink()
    out_files = split_metadata_table_by_neuron_id(table_file, out_dir, id_columns=id_columns)
    return len(out_files)
