from __future__ import annotations

import neuroutils.config.settings as settings
from neuroutils.config import get_vaa3d_path, get_vaa3d_paths, resolve_vaa3d_executable


def test_get_vaa3d_paths_x_and_3(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "_read_windows_env_from_registry", lambda _name: "")
    monkeypatch.delenv("NEUROUTILS_VAA3D_X", raising=False)
    monkeypatch.delenv("NEUROUTILS_VAA3D_3", raising=False)
    monkeypatch.delenv("NEUROUTILS_VAA3D_PRIMARY", raising=False)
    monkeypatch.delenv("NEUROUTILS_VAA3D_SECONDARY", raising=False)
    monkeypatch.setenv("VAA3D_BIN", "vaa3d-default")
    x, three = get_vaa3d_paths()
    assert x == "vaa3d-default"
    assert three == "vaa3d-default"

    monkeypatch.setenv("NEUROUTILS_VAA3D_X", "vaa3d-x")
    monkeypatch.setenv("NEUROUTILS_VAA3D_3", "vaa3d-3")
    x2, three2 = get_vaa3d_paths()
    assert x2 == "vaa3d-x"
    assert three2 == "vaa3d-3"


def test_get_vaa3d_path_defaults_and_explicit_version(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "_read_windows_env_from_registry", lambda _name: "")
    monkeypatch.setenv("NEUROUTILS_VAA3D_X", "vaa3d-x")
    monkeypatch.setenv("NEUROUTILS_VAA3D_3", "vaa3d-3")
    # internal defaults: tracing->x, sorting->x, features->x
    assert get_vaa3d_path("tracing") == "vaa3d-x"
    assert get_vaa3d_path("sorting") == "vaa3d-x"
    assert get_vaa3d_path("features") == "vaa3d-x"
    assert get_vaa3d_path("unknown") == "vaa3d-x"
    assert get_vaa3d_path("tracing", version="3") == "vaa3d-3"


def test_resolve_vaa3d_executable_from_dir(tmp_path) -> None:
    win_dir = tmp_path / "win"
    win_dir.mkdir()
    win_exe = win_dir / "vaa3d_msvc.exe"
    win_exe.write_text("", encoding="utf-8")
    assert resolve_vaa3d_executable(str(win_dir), platform="win32").endswith("vaa3d_msvc.exe")

    linux_dir = tmp_path / "linux"
    linux_dir.mkdir()
    linux_exe = linux_dir / "Vaa3D-x"
    linux_exe.write_text("", encoding="utf-8")
    assert resolve_vaa3d_executable(str(linux_dir), platform="linux").endswith("Vaa3D-x")


def test_get_vaa3d_paths_reads_registry_fallback(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("NEUROUTILS_VAA3D_X", raising=False)
    monkeypatch.delenv("NEUROUTILS_VAA3D_3", raising=False)

    def _fake_registry(name: str) -> str:
        if name == "NEUROUTILS_VAA3D_X":
            return "reg-x"
        if name == "NEUROUTILS_VAA3D_3":
            return "reg-3"
        return ""

    monkeypatch.setattr(settings, "_read_windows_env_from_registry", _fake_registry)
    x, three = get_vaa3d_paths()
    assert x == "reg-x"
    assert three == "reg-3"
