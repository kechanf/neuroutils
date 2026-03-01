from __future__ import annotations

from pathlib import Path

from neuroutils.io.markers import generate_ano_file, generate_ano_for_swc, save_markers, write_vaa3d_markers


def test_write_vaa3d_markers(tmp_path: Path) -> None:
    p = tmp_path / "markers.marker"
    write_vaa3d_markers(p, [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)])
    text = p.read_text(encoding="utf-8")
    assert text.startswith("##x,y,z")
    assert "1.000,2.000,3.000" in text


def test_generate_ano_for_swc(tmp_path: Path) -> None:
    swc = tmp_path / "a.swc"
    swc.write_text("1 1 1 2 3 1 -1\n2 3 2 3 4 1 1\n", encoding="utf-8")
    apo, ano = generate_ano_for_swc(swc, outdir=tmp_path)
    assert apo.exists() and ano.exists()
    ano_text = ano.read_text(encoding="utf-8")
    assert "APOFILE=a.apo" in ano_text
    assert "SWCFILE=a.swc" in ano_text
    apo2, ano2 = generate_ano_file(swc, outdir=tmp_path)
    assert apo2 == apo and ano2 == ano


def test_save_markers_alias(tmp_path: Path) -> None:
    p = tmp_path / "m.marker"
    save_markers(p, [(1.0, 2.0, 3.0)])
    assert p.exists()
