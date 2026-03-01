from __future__ import annotations

from pathlib import Path

from neuroutils.swc.analysis.lmeasure.external import (
    FEAT_NAME_DICT,
    _create_temp_copy,
    _wrapper,
    calc_global_features,
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


def test_calc_global_features_alias(tmp_path: Path, monkeypatch) -> None:
    swc = tmp_path / "a.swc"
    swc.write_text("1 1 0 0 0 1 -1\n", encoding="utf-8")

    def _fake_calc(*args, **kwargs):  # type: ignore[no-untyped-def]
        return {v: 2.0 for v in FEAT_NAME_DICT.values()}

    import neuroutils.swc.analysis.lmeasure.external as ext

    monkeypatch.setattr(ext, "calc_global_features_external", _fake_calc)
    out = calc_global_features(swc)
    assert out["Nodes"] == 2.0


def test_internal_wrapper_helpers(tmp_path: Path, monkeypatch) -> None:
    swc = tmp_path / "a.swc"
    swc.write_text("1 1 0 0 0 1 -1\n", encoding="utf-8")
    cp = _create_temp_copy(swc)
    assert cp.exists()

    def _fake_calc(*args, **kwargs):  # type: ignore[no-untyped-def]
        return {v: 3.0 for v in FEAT_NAME_DICT.values()}

    import neuroutils.swc.analysis.lmeasure.external as ext

    monkeypatch.setattr(ext, "calc_global_features", _fake_calc)
    out_dict: dict[str, dict[str, float]] = {}
    _wrapper(swc, "id1", out_dict, robust=True)
    assert out_dict["id1"]["Nodes"] == 3.0
