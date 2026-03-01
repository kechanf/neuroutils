from __future__ import annotations

from pathlib import Path

from neuroutils.swc.analysis.lmeasure.external import (
    FEAT_NAME_DICT,
    calc_global_features_external,
    calc_global_features_from_folder,
    parse_vaa3d_global_feature_output,
)


def test_parse_vaa3d_global_feature_output() -> None:
    text = "\n".join([f"{k}: 1" for k in FEAT_NAME_DICT.keys()])
    out = parse_vaa3d_global_feature_output(text)
    assert len(out) == 22
    assert out["Nodes"] == 1.0


def test_calc_global_features_from_folder_mocked(tmp_path: Path, monkeypatch) -> None:
    for name in ("a.swc", "b.swc"):
        (tmp_path / name).write_text("1 1 0 0 0 1 -1\n", encoding="utf-8")

    def _fake_calc(*args, **kwargs):  # type: ignore[no-untyped-def]
        return {v: 1.0 for v in FEAT_NAME_DICT.values()}

    import neuroutils.swc.analysis.lmeasure.external as ext

    monkeypatch.setattr(ext, "calc_global_features_external", _fake_calc)
    rows = calc_global_features_from_folder(tmp_path, nworkers=2, robust=True)
    assert len(rows) == 2
    assert rows[0]["Nodes"] == 1.0


def test_calc_global_features_external_uses_list_command(monkeypatch, tmp_path: Path) -> None:
    swc = tmp_path / "a.swc"
    swc.write_text("1 1 0 0 0 1 -1\n", encoding="utf-8")
    captured: dict[str, object] = {}

    class _DummyProc:
        returncode = 0
        stdout = "\n".join([f"{k}: 1" for k in FEAT_NAME_DICT.keys()])
        stderr = ""

    def _fake_run(cmd, shell, text, capture_output, timeout):  # type: ignore[no-untyped-def]
        captured["cmd"] = cmd
        captured["shell"] = shell
        return _DummyProc()

    monkeypatch.setattr("neuroutils.swc.analysis.lmeasure.external.subprocess.run", _fake_run)
    out = calc_global_features_external(swc, vaa3d_bin="vaa3d")
    assert out["Nodes"] == 1.0
    assert isinstance(captured["cmd"], list)
    assert captured["shell"] is False


def test_calc_global_features_external_xvfb_forbidden_on_windows(monkeypatch, tmp_path: Path) -> None:
    swc = tmp_path / "a.swc"
    swc.write_text("1 1 0 0 0 1 -1\n", encoding="utf-8")
    monkeypatch.setattr("neuroutils.swc.analysis.lmeasure.external.sys.platform", "win32")
    try:
        calc_global_features_external(swc, vaa3d_bin="vaa3d", use_xvfb=True)
    except ValueError:
        return
    raise AssertionError("Expected ValueError for xvfb on Windows")
