"""Runtime settings."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

TASK_DEFAULT_VERSION: dict[str, str] = {
    "tracing": "x",
    "sorting": "x",
    "features": "x",
}


def _read_windows_env_from_registry(name: str) -> str:
    """Read system environment variable value from Windows registry."""
    if not sys.platform.startswith("win"):
        return ""
    try:
        import winreg  # type: ignore[import-not-found]
    except Exception:
        return ""

    key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(hive, key_path) as key:
                val, _ = winreg.QueryValueEx(key, name)
                if str(val).strip():
                    return str(val).strip()
        except Exception:
            continue
    return ""


def _read_env_with_registry_fallback(name: str, default: str = "") -> str:
    """Read env var from process env, then Windows registry fallback."""
    val = os.environ.get(name, "").strip()
    if val:
        return val
    reg = _read_windows_env_from_registry(name)
    if reg:
        return reg
    return default


def _get_executable_name_candidates(platform: str) -> tuple[str, ...]:
    """Return candidate Vaa3D executable names for one platform."""
    if platform.startswith("win"):
        return ("vaa3d_msvc.exe", "vaa3d.exe", "vaa3d-x.exe", "vaa3d_msvc", "vaa3d")
    return ("Vaa3D-x", "vaa3d", "vaa3d-x", "start_vaa3d.sh")


def _normalize_vaa3d_version(version: str | None) -> str | None:
    """Normalize version alias to canonical `x` or `3`."""
    if version is None:
        return None
    vv = version.strip().lower()
    if vv in {"x", "vaa3d-x", "vaa3dx"}:
        return "x"
    if vv in {"3", "vaa3d-3", "vaa3d3"}:
        return "3"
    return None


def _get_configured_version_path(version: str, default: str) -> str:
    """Get configured Vaa3D path for version `x` or `3`."""
    if version == "x":
        return _read_env_with_registry_fallback("NEUROUTILS_VAA3D_X", "")
    if version == "3":
        return _read_env_with_registry_fallback("NEUROUTILS_VAA3D_3", "")
    return default


def resolve_vaa3d_executable(path_or_cmd: str, default: str = "vaa3d", platform: str | None = None) -> str:
    """Resolve executable path from command/file/directory input.

    - If input is an existing executable file, return it.
    - If input is an existing directory, probe common executable names.
    - If input is a bare command, return resolved `PATH` entry when found.
    - Otherwise, return input as-is.
    """
    raw = (path_or_cmd or "").strip()
    if not raw:
        raw = default

    path_obj = Path(raw).expanduser()
    if path_obj.is_file():
        return str(path_obj)
    if path_obj.is_dir():
        plat = platform or sys.platform
        for name in _get_executable_name_candidates(plat):
            cand = path_obj / name
            if cand.is_file():
                return str(cand)
        return str(path_obj)

    hit = shutil.which(raw)
    if hit:
        return hit
    return raw


def get_vaa3d_path(task: str | None = None, version: str | None = None, default: str = "vaa3d") -> str:
    """Resolve Vaa3D executable path from environment.

    Priority:
    1) explicit function arg `version` (x|3)
    2) internal task default version mapping (tracing->x, sorting->3, features->3)
    3) global version paths:
       - NEUROUTILS_VAA3D_X / NEUROUTILS_VAA3D_3
    4) legacy generic vars:
       - NEUROUTILS_VAA3D_PRIMARY
       - VAA3D_BIN
    5) fallback default argument.
    """
    vv = _normalize_vaa3d_version(version)
    if vv is None:
        vv = TASK_DEFAULT_VERSION.get((task or "").lower(), "x")

    raw = _get_configured_version_path(vv, default="")
    if not raw:
        alt = "3" if vv == "x" else "x"
        raw = _get_configured_version_path(alt, default="")
    if not raw:
        raw = _read_env_with_registry_fallback(
            "NEUROUTILS_VAA3D_PRIMARY",
            _read_env_with_registry_fallback("VAA3D_BIN", default),
        )
    return resolve_vaa3d_executable(raw, default=default)


def get_vaa3d_paths(default: str = "vaa3d") -> tuple[str, str]:
    """Resolve two-version Vaa3D paths (x, 3) from environment.

    - x: NEUROUTILS_VAA3D_X -> NEUROUTILS_VAA3D_PRIMARY -> VAA3D_BIN -> default
    - 3: NEUROUTILS_VAA3D_3 -> NEUROUTILS_VAA3D_SECONDARY -> x
    """
    x_raw = _read_env_with_registry_fallback(
        "NEUROUTILS_VAA3D_X",
        _read_env_with_registry_fallback(
            "NEUROUTILS_VAA3D_PRIMARY",
            _read_env_with_registry_fallback("VAA3D_BIN", default),
        ),
    )
    x_path = resolve_vaa3d_executable(x_raw, default=default)
    three_raw = _read_env_with_registry_fallback(
        "NEUROUTILS_VAA3D_3",
        _read_env_with_registry_fallback("NEUROUTILS_VAA3D_SECONDARY", x_path),
    )
    three_path = resolve_vaa3d_executable(three_raw, default=x_path)
    return x_path, three_path


# Internal backwards-compatible aliases for older tests/imports.
_get_env = _read_env_with_registry_fallback
_exe_candidates = _get_executable_name_candidates
_norm_version = _normalize_vaa3d_version
_base_version_path = _get_configured_version_path
