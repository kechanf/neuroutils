"""Command-line interface."""

from __future__ import annotations

import argparse

from neuroutils.api import compare, features, process


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(prog="neuroutils")
    sub = parser.add_subparsers(dest="command", required=True)

    p_proc = sub.add_parser("process")
    p_proc.add_argument("input_swc")
    p_proc.add_argument("output_swc")

    p_feat = sub.add_parser("features")
    p_feat.add_argument("swc_file")

    p_cmp = sub.add_parser("compare")
    p_cmp.add_argument("gt_swc")
    p_cmp.add_argument("pred_swc")
    return parser


def main() -> None:
    """Run CLI main."""
    args = build_parser().parse_args()
    if args.command == "process":
        process(args.input_swc, args.output_swc)
        print(f"processed: {args.output_swc}")
    elif args.command == "features":
        print(features(args.swc_file))
    elif args.command == "compare":
        print(compare(args.gt_swc, args.pred_swc))
