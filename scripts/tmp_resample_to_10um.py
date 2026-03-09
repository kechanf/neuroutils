"""Temporary batch script: resample SWC files to 10 um spacing.

Assumption:
- Input SWC coordinates are already in 1 um isotropic units.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from neuroutils.swc.sorting.external import resample_swc_external
from neuroutils.workflows.common import process_directory_files

DEFAULT_INPUT_DIR = Path(r"E:\neuroutils\examples\to_kaifeng")


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Batch resample SWC files to 10 um.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing source .swc files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for output .swc files. Defaults to <input-dir>/resampled_10um.",
    )
    parser.add_argument(
        "--step",
        type=float,
        default=10.0,
        help="Resampling step size in um. Default: 10.0.",
    )
    parser.add_argument(
        "--vaa3d-bin",
        type=str,
        default=None,
        help="Optional Vaa3D executable path. If omitted, environment-based resolution is used.",
    )
    parser.add_argument(
        "--vaa3d-version",
        type=str,
        default=None,
        help="Optional Vaa3D version selector: 'x' or '3'.",
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=-1,
        help="Parallel workers for batch processing. Default: -1.",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="loky",
        choices=["loky", "threading"],
        help="Joblib backend. Default: loky.",
    )
    return parser


def main() -> None:
    args = _build_argparser().parse_args()
    input_dir: Path = args.input_dir
    output_dir: Path = args.output_dir or (input_dir / "resampled_10um")
    step: float = float(args.step)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    swc_files = sorted(input_dir.glob("*.swc"))
    if not swc_files:
        print(f"No SWC files found in: {input_dir}")
        return

    def _processor(swc_path: Path, out_path: Path) -> dict[str, float]:
        resample_swc_external(
            swc_in=swc_path,
            swc_out=out_path,
            step=step,
            vaa3d_bin=args.vaa3d_bin,
            vaa3d_version=args.vaa3d_version,
        )
        return {"step_um": step}

    rows = process_directory_files(
        input_dir=input_dir,
        output_dir=output_dir,
        processor=_processor,
        pattern="*.swc",
        n_jobs=args.n_jobs,
        backend=args.backend,
        show_progress=True,
        skip_existing=False,
    )
    print(f"Done. Resampled {len(rows)} files. Output directory: {output_dir}")


if __name__ == "__main__":
    main()
