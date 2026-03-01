from __future__ import annotations

from pathlib import Path

import neuroutils.swc.sorting.external as ext


def test_resample_sort_external_builds_calls(tmp_path: Path, monkeypatch) -> None:
    calls: list[list[str]] = []

    def _fake_run_checked(cmd: list[str], timeout: int = 300):  # type: ignore[no-untyped-def]
        calls.append(cmd)
        class _Dummy:
            returncode = 0
        return _Dummy()

    monkeypatch.setattr(ext, "run_checked", _fake_run_checked)

    swc_in = tmp_path / "in.swc"
    swc_out = tmp_path / "out.swc"
    swc_in.write_text("1 1 0 0 0 1 -1\n", encoding="utf-8")

    ext.resample_swc_external(swc_in, swc_out, step=2.0, vaa3d_bin="vaa3d")
    ext.sort_swc_external(swc_in, swc_out, vaa3d_bin="vaa3d")

    assert len(calls) == 2
    assert calls[0][0] == "vaa3d"
    assert "resample_swc" in calls[0]
    assert "sort_swc" in calls[1]
