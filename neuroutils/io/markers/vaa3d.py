"""Vaa3D marker/ANO helpers."""

from __future__ import annotations

from pathlib import Path

from neuroutils.io.swc import read_swc


def write_vaa3d_markers(
    path: str | Path,
    markers_xyz: list[tuple[float, float, float]],
    *,
    radius: float = 0.0,
    shape: int = 0,
    name: str = "",
    comment: str = "",
    color_rgb: tuple[int, int, int] = (0, 0, 255),
) -> None:
    """Write Vaa3D marker CSV."""
    r, g, b = color_rgb
    lines = ["##x,y,z,radius,shape,name,comment,color_r,color_g,color_b"]
    for x, y, z in markers_xyz:
        lines.append(
            f"{x:.3f},{y:.3f},{z:.3f},{radius:.3f},{shape:d},{name},{comment},{r:d},{g:d},{b:d}"
        )
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_ano_for_swc(swc_path: str | Path, *, outdir: str | Path | None = None) -> tuple[Path, Path]:
    """Generate paired APO/ANO files for an SWC (soma-only marker in APO)."""
    swc = Path(swc_path)
    target_dir = Path(outdir) if outdir is not None else swc.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    apo = target_dir / f"{swc.stem}.apo"
    ano = target_dir / f"{swc.stem}.ano"

    nodes = read_swc(swc)
    lines = [
        "##n,orderinfo,name,comment,z,x,y,pixmax,intensity,sdev,volsize,mass,,,,color_r,color_g,color_b"
    ]
    for n in nodes:
        if n.parent_id == -1:
            lines.append(
                f"{n.node_id},,,,{n.z:.3f},{n.x:.3f},{n.y:.3f},0.000,0.000,0.000,314.159,0.000,,,,0,255,255"
            )
    apo.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ano.write_text(f"APOFILE={apo.name}\nSWCFILE={swc.name}\n", encoding="utf-8")
    return apo, ano
