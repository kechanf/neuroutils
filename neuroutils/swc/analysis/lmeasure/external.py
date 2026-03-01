"""External Vaa3D global-feature wrappers."""

from __future__ import annotations

import csv
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from neuroutils.config import get_vaa3d_path

FEAT_NAMES22 = [
    "Nodes",
    "SomaSurface",
    "Stems",
    "Bifurcations",
    "Branches",
    "Tips",
    "OverallWidth",
    "OverallHeight",
    "OverallDepth",
    "AverageDiameter",
    "Length",
    "Surface",
    "Volume",
    "MaxEuclideanDistance",
    "MaxPathDistance",
    "MaxBranchOrder",
    "AverageContraction",
    "AverageFragmentation",
    "AverageParent-daughterRatio",
    "AverageBifurcationAngleLocal",
    "AverageBifurcationAngleRemote",
    "HausdorffDimension",
]

FEAT_NAME_DICT = {
    "N_node": "Nodes",
    "Soma_surface": "SomaSurface",
    "N_stem": "Stems",
    "Number of Bifurcatons": "Bifurcations",
    "Number of Branches": "Branches",
    "Number of Tips": "Tips",
    "Overall Width": "OverallWidth",
    "Overall Height": "OverallHeight",
    "Overall Depth": "OverallDepth",
    "Average Diameter": "AverageDiameter",
    "Total Length": "Length",
    "Total Surface": "Surface",
    "Total Volume": "Volume",
    "Max Euclidean Distance": "MaxEuclideanDistance",
    "Max Path Distance": "MaxPathDistance",
    "Max Branch Order": "MaxBranchOrder",
    "Average Contraction": "AverageContraction",
    "Average Fragmentation": "AverageFragmentation",
    "Average Parent-daughter Ratio": "AverageParent-daughterRatio",
    "Average Bifurcation Angle Local": "AverageBifurcationAngleLocal",
    "Average Bifurcation Angle Remote": "AverageBifurcationAngleRemote",
    "Hausdorff Dimension": "HausdorffDimension",
}


def parse_vaa3d_global_feature_output(text: str) -> dict[str, float]:
    """Parse `global_neuron_feature` stdout into canonical feature dict."""
    raw: dict[str, float] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        key = k.strip()
        val = v.strip()
        if not key or not val:
            continue
        try:
            fval = float(val)
        except ValueError:
            continue
        raw[key] = fval

    out: dict[str, float] = {}
    for src, dst in FEAT_NAME_DICT.items():
        if src not in raw:
            raise ValueError(f"Missing required key '{src}' in Vaa3D output")
        out[dst] = raw[src]
    return out


def calc_global_features_external(
    swc_file: str | Path,
    *,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    timeout: int = 60,
    use_xvfb: bool = False,
) -> dict[str, float]:
    """Run Vaa3D `global_neuron_feature` and parse 22 canonical features."""
    swc = str(swc_file)
    vb = vaa3d_bin or get_vaa3d_path("features", version=vaa3d_version)
    cmd = [vb, "-x", "global_neuron_feature", "-f", "compute_feature", "-i", swc]
    if use_xvfb:
        if sys.platform.startswith("win"):
            raise ValueError("xvfb is not supported on Windows")
        cmd = ["xvfb-run", "-a", "-s", "-screen 0 640x480x16", *cmd]
    p = subprocess.run(cmd, shell=False, text=True, capture_output=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"Vaa3D failed for {swc}: {p.stderr.strip()}")
    return parse_vaa3d_global_feature_output(p.stdout)




def calc_global_features_from_folder(
    swc_dir: str | Path,
    *,
    outfile: str | Path | None = None,
    robust: bool = True,
    nworkers: int = 4,
    timeout: int = 60,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    use_xvfb: bool = False,
) -> list[dict[str, float | str]]:
    """Batch-run global features for all `.swc` in folder."""
    files = sorted(Path(swc_dir).glob("*.swc"))
    rows: list[dict[str, float | str]] = []

    def _run_one(p: Path) -> dict[str, float | str]:
        feat = calc_global_features_external(
            p,
            vaa3d_bin=vaa3d_bin,
            vaa3d_version=vaa3d_version,
            timeout=timeout,
            use_xvfb=use_xvfb,
        )
        return {"id": p.stem, **feat}

    with ThreadPoolExecutor(max_workers=max(1, nworkers)) as ex:
        futs = {ex.submit(_run_one, p): p for p in files}
        for fut in as_completed(futs):
            p = futs[fut]
            try:
                rows.append(fut.result())
            except Exception:
                if robust:
                    continue
                raise RuntimeError(f"Failed on {p}") from None

    rows.sort(key=lambda x: str(x["id"]))
    if outfile is not None:
        outp = Path(outfile)
        outp.parent.mkdir(parents=True, exist_ok=True)
        with outp.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=["id", *FEAT_NAMES22])
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
    return rows
