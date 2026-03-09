"""Temporary helper: rescale SWC by metadata xy resolution and then resample by Vaa3D.

Rule:
- xy_scale = (xy_resolution / 1000) * 2
- z_scale = 2
- then Vaa3D resample with step=10
"""

from __future__ import annotations

import argparse
from pathlib import Path

from neuroutils.io.swc import read_swc, write_swc
from neuroutils.metadata import (
    extract_neuron_id_from_filename,
    load_neuron_metadata_record,
    xy_z_resolution_from_record,
)
from neuroutils.swc.sorting import resample_swc_external
from neuroutils.transforms import scale_nodes


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rescale SWC from metadata xy_resolution and then resample (step=10) by Vaa3D."
    )
    parser.add_argument("swc_file", help="Input SWC file path")
    parser.add_argument("meta_xlsx", help="Metadata table path (.xlsx/.csv/.tsv)")
    parser.add_argument(
        "--output",
        dest="output_swc",
        default=None,
        help="Output SWC path (default: <input_stem>_metaXYx2_z2_resample10.swc)",
    )
    parser.add_argument(
        "--step",
        type=float,
        default=10.0,
        help="Vaa3D resample step (default: 10.0)",
    )
    parser.add_argument(
        "--vaa3d-version",
        default=None,
        help='Optional Vaa3D version selector ("x" or "3").',
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Vaa3D timeout seconds (default: 600)",
    )
    return parser


def run_once(
    swc_file: str | Path,
    meta_xlsx: str | Path,
    *,
    output_swc: str | Path | None = None,
    step: float = 10.0,
    vaa3d_version: str | None = None,
    timeout: int = 600,
) -> Path:
    src = Path(swc_file)
    meta = Path(meta_xlsx)
    if not src.exists():
        raise FileNotFoundError(f"SWC not found: {src}")
    if not meta.exists():
        raise FileNotFoundError(f"Meta file not found: {meta}")

    out = (
        Path(output_swc)
        if output_swc is not None
        else src.with_name(f"{src.stem}_metaXYx2_z2_resample10.swc")
    )

    neuron_id = extract_neuron_id_from_filename(src.name)
    record = load_neuron_metadata_record(neuron_id, table_file=meta)
    xy_resolution, _ = xy_z_resolution_from_record(record)
    xy_scale = (float(xy_resolution) / 1000.0) * 2.0
    z_scale = 2.0

    nodes = read_swc(src)
    scaled_nodes = scale_nodes(nodes, sx=xy_scale, sy=xy_scale, sz=z_scale)

    temp_scaled = out.with_suffix(".scaled.tmp.swc")
    write_swc(
        temp_scaled,
        scaled_nodes,
        header=[
            "temporary scaled by metadata",
            f"neuron_id={neuron_id}",
            f"xy_resolution={xy_resolution}",
            f"xy_scale={xy_scale}",
            f"z_scale={z_scale}",
        ],
    )

    try:
        resample_swc_external(
            temp_scaled,
            out,
            step=step,
            vaa3d_version=vaa3d_version,
            timeout=timeout,
        )
    finally:
        if temp_scaled.exists():
            temp_scaled.unlink()

    print(f"input: {src}")
    print(f"neuron_id: {neuron_id}")
    print(f"xy_resolution: {xy_resolution}")
    print(f"xy_scale: {xy_scale}")
    print(f"z_scale: {z_scale}")
    print(f"output: {out}")
    return out


def main() -> None:
    args = build_arg_parser().parse_args()
    run_once(
        args.swc_file,
        args.meta_xlsx,
        output_swc=args.output_swc,
        step=args.step,
        vaa3d_version=args.vaa3d_version,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    main()

