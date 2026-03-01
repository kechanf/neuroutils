"""Vaa3D tracer registry and command builders.

Naming conventions in this module:
- Public list-style APIs use `list_*`.
- Public path collection APIs use `get_*`.
- Public command builders use `build_*`.
Legacy names are kept as thin aliases.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from dataclasses import dataclass

from neuroutils.config import get_vaa3d_path, get_vaa3d_paths

@dataclass(frozen=True, slots=True)
class TracerSpec:
    """Static definition for one Vaa3D tracer entry."""

    plugin: str
    function: str
    default_params: tuple[str, ...] = ()
    output_suffix: str | None = None


TRACER_SPECS: dict[str, TracerSpec] = {
    "APP1": TracerSpec("vn2", "app1", ("NULL", "0", "40", "1"), "_app1.swc"),
    "APP2": TracerSpec("vn2", "app2", ("NULL", "0", "10", "1", "1", "0", "0", "5", "0", "0", "0"), "_app2.swc"),
    "APP2_NEW1": TracerSpec("vn2", "app2", ("NULL", "0", "AUTO", "1", "1", "1", "1", "5", "0", "0", "0"), "_app2new1.swc"),
    "APP2_NEW2": TracerSpec("vn2", "app2", ("NULL", "0", "AUTO", "1", "1", "0", "1", "5", "0", "0", "0"), "_app2new2.swc"),
    "APP2_NEW3": TracerSpec("vn2", "app2", ("NULL", "0", "10", "1", "1", "1", "1", "5", "0", "0", "0"), "_app2new3.swc"),
    "MOST": TracerSpec("MOST", "MOST_trace", ("1", "40"), "_MOST.swc"),
    "NEUTUBE": TracerSpec("neuTube", "neutube_trace", ("1", "1"), "_neutube.swc"),
    "SNAKE": TracerSpec("snake", "snake_trace", ("1",), "_snake.swc"),
    "SimpleTracing1": TracerSpec("SimpleTracing", "tracing", (), "_simple.swc"),
    "SimpleTracing2": TracerSpec("SimpleTracing", "ray_shooting", (), "_Rayshooting.swc"),
    "SimpleTracing3": TracerSpec("SimpleTracing", "dfs", (), "_Rollerball.swc"),
    "TreMap": TracerSpec("TReMap", "trace_mip", ("0", "1", "10", "0", "1", "0", "5"), "_TreMap.swc"),
    "MST": TracerSpec("MST_tracing", "trace_mst", ("1", "5"), "_MST_Tracing.swc"),
    "NeuroGPSTree": TracerSpec("NeuroGPSTree", "tracing_func", ("1", "1", "1", "10"), "_NeuroGPSTree.swc"),
    "NeuroGPSTree2": TracerSpec("NeuroGPSTree", "tracing_func", ("0.5", "0.5", "1", "15", "10", "150"), "_NeuroGPSTree.swc"),
    "FMST": TracerSpec("fastmarching_spanningtree", "tracing_func", (), "_fastmarching_spanningtree.swc"),
    "MeanShift": TracerSpec("BJUT_meanshift", "meanshift", (), "_meanshift.swc"),
    "CWlab11": TracerSpec("CWlab_method1_version1", "tracing_func", ("1",), "_Cwlab_ver1.swc"),
    "LCM_boost": TracerSpec("LCM_boost", "LCM_boost", (), "_LCMboost.swc"),
    "LCM_boost_2": TracerSpec("LCM_boost", "LCM_boost_2", (), "_LCMboost_2.swc"),
    "LCM_boost_3": TracerSpec("LCM_boost", "LCM_boost_3", (), "_LCMboost_3.swc"),
    "NeuroStalker": TracerSpec("NeuroStalker", "tracing_func", ("1", "1", "1", "5", "5", "30"), "_NeuroStalker.swc"),
    "nctuTW": TracerSpec("nctuTW", "tracing_func", ("NULL",), "_nctuTW.swc"),
    "tips_GD": TracerSpec("tips_GD", "tracing_func", (), "_nctuTW_GD.swc"),
    "SimpleAxisAnalyzer": TracerSpec("SimpleAxisAnalyzer", "medial_axis_analysis", (), "_axis_analyzer.swc"),
    "NeuronChaser": TracerSpec("NeuronChaser", "nc_func", ("1", "10", "0.6", "15", "60", "30", "5", "1", "0"), "_NeuronChaser.swc"),
    "NeuronChaser2": TracerSpec("NeuronChaser", "nc_func", ("1", "10", "0.7", "20", "60", "10", "5", "1", "0"), "_NeuronChaser.swc"),
    "smartTracing": TracerSpec("smartTrace", "smartTrace", (), "_smartTracing.swc"),
    "neutu_autotrace": TracerSpec("neutu_autotrace", "tracing", (), "_neutu_autotrace.swc"),
    "Advantra": TracerSpec("Advantra", "advantra_func", ("10", "0.3", "0.6", "15", "60", "30", "5", "1"), "_Advantra.swc"),
    "Advantra2": TracerSpec("Advantra", "advantra_func", ("10", "0.5", "0.7", "20", "60", "30", "5", "1"), "_Advantra.swc"),
    "EnsembleNeuronTracer": TracerSpec("EnsembleNeuronTracerBasic", "tracing_func", (), "_EnsembleNeuronTracerBasic.swc"),
    "EnsembleNeuronTracerV2n": TracerSpec("EnsembleNeuronTracerV2n", "tracing_func", (), "_EnsembleNeuronTracerV2n.swc"),
    "EnsembleNeuronTracerV2s": TracerSpec("EnsembleNeuronTracerV2s", "tracing_func", (), "_EnsembleNeuronTracerV2s.swc"),
    "threeDTraceSWC": TracerSpec("aVaaTrace3D", "func1", ("20", "2", "2.5"), "_pyzh.swc"),
    "threeDTraceSWC2": TracerSpec("aVaaTrace3D", "func1", ("50", "5", "2.5"), "_pyzh.swc"),
}

# Derived from reference_libs/neuroutils_old/tracing/big_neuron_tracers.py
# for tracers with explicit version binding in legacy scripts.
TRACER_DEFAULT_VERSION: dict[str, str] = {
    "APP1": "x",
    "APP2": "x",
    "APP2_NEW1": "x",
    "APP2_NEW2": "x",
    "APP2_NEW3": "x",
    "Advantra": "x",
    "Advantra2": "x",
    "TreMap": "x",
    "MOST": "3",
    "NEUTUBE": "3",
    "MST": "3",
    "NeuroGPSTree": "3",
    "NeuroGPSTree2": "3",
    "FMST": "3",
    "CWlab11": "3",
}


def list_available_tracers() -> list[str]:
    """Return all tracer names declared in this registry."""
    return sorted(TRACER_SPECS.keys())


def _is_windows_platform() -> bool:
    return sys.platform.startswith("win")


def _get_plugin_search_roots(vaa3d_executable: str) -> tuple[Path, ...]:
    executable_path = Path(vaa3d_executable)
    if executable_path.is_dir():
        vaa3d_root = executable_path
    else:
        vaa3d_root = executable_path.parent
    return (vaa3d_root / "plugins", vaa3d_root)


PLUGIN_DLL_ALIASES: dict[str, tuple[str, ...]] = {
    "MOST": ("mostVesselTracer", "MOST"),
    "MST_tracing": ("neurontracing_mst", "MST_tracing"),
    "TReMap": ("neurontracing_mip", "TReMap"),
    "vn2": ("vn2",),
    "neuTube": ("neutube", "neuTube"),
    "BJUT_meanshift": ("meanshift", "BJUT_meanshift"),
    "CWlab_method1_version1": ("CWlab_method1_version1",),
}


def _score_plugin_stem(stem: str, tokens: tuple[str, ...]) -> int:
    stem_lower = stem.lower()
    for idx, t in enumerate(tokens):
        token_lower = t.lower()
        if stem_lower == token_lower:
            return 1000 - idx
    for idx, t in enumerate(tokens):
        token_lower = t.lower()
        if token_lower in stem_lower:
            return 100 - idx
    return -1


@lru_cache(maxsize=512)
def _resolve_windows_plugin_argument(vaa3d_executable: str, plugin_name: str) -> str:
    """Resolve plugin argument to a concrete DLL path on Windows."""
    roots = _get_plugin_search_roots(vaa3d_executable)
    tokens = (plugin_name, *PLUGIN_DLL_ALIASES.get(plugin_name, ()))
    best_score = -1
    best_path: Path | None = None
    for root in roots:
        if not root.exists():
            continue
        for dll in root.rglob("*.dll"):
            score = _score_plugin_stem(dll.stem, tokens)
            if score > best_score:
                best_score = score
                best_path = dll
    return str(best_path) if best_path is not None else plugin_name


def resolve_tracer_plugin_arg(vaa3d_bin: str, plugin: str) -> str:
    """Resolve tracer plugin selector for the current platform.

    On Windows, returns a concrete `.dll` path when found.
    On non-Windows platforms, returns plugin name unchanged.
    """
    if _is_windows_platform():
        return _resolve_windows_plugin_argument(vaa3d_bin, plugin)
    return plugin


def _is_resolved_plugin_dll(plugin_argument: str) -> bool:
    plugin_path = Path(plugin_argument)
    return plugin_path.suffix.lower() == ".dll" and plugin_path.exists()


def _auto_pick_vaa3d_bin_for_tracer(spec: TracerSpec) -> str:
    """Pick x/3 executable by plugin availability on Windows."""
    x_bin, three_bin = get_vaa3d_paths()
    x_plugin = resolve_tracer_plugin_arg(x_bin, spec.plugin)
    three_plugin = resolve_tracer_plugin_arg(three_bin, spec.plugin)
    x_ok = _is_resolved_plugin_dll(x_plugin)
    three_ok = _is_resolved_plugin_dll(three_plugin)
    if x_ok and not three_ok:
        return x_bin
    if three_ok and not x_ok:
        return three_bin
    # Keep legacy preference (x first) when both/none are available.
    return x_bin


def get_tracer_output_candidates(tracer: str, image_file: str, output_swc: str | None = None) -> list[str]:
    """Return ordered candidate output paths for a tracer run."""
    if tracer not in TRACER_SPECS:
        raise ValueError(f"Unsupported tracer: {tracer}")
    spec = TRACER_SPECS[tracer]
    candidates: list[str] = []
    if output_swc:
        candidates.append(str(Path(output_swc)))
    if spec.output_suffix:
        candidates.append(str(Path(f"{image_file}{spec.output_suffix}")))
    if tracer == "MeanShift":
        candidates.append(str(Path(f"{image_file}_init_meanshift.swc")))
    # De-duplicate while keeping order.
    seen: set[str] = set()
    unique_candidates: list[str] = []
    for candidate in candidates:
        resolved_candidate = str(Path(candidate))
        if resolved_candidate in seen:
            continue
        seen.add(resolved_candidate)
        unique_candidates.append(resolved_candidate)
    return unique_candidates


def list_installed_tracers() -> list[str]:
    """Return tracers that can resolve plugin binaries in current environment."""
    installed: list[str] = []
    for tracer in list_available_tracers():
        spec = TRACER_SPECS[tracer]
        ver = TRACER_DEFAULT_VERSION.get(tracer)
        if _is_windows_platform():
            if ver is None:
                vaa3d_executable = _auto_pick_vaa3d_bin_for_tracer(spec)
            else:
                vaa3d_executable = get_vaa3d_path("tracing", version=ver)
            plugin_argument = resolve_tracer_plugin_arg(vaa3d_executable, spec.plugin)
            if _is_resolved_plugin_dll(plugin_argument):
                installed.append(tracer)
            continue
        installed.append(tracer)
    return installed


def build_tracer_command(
    tracer: str,
    *,
    vaa3d_bin: str | None = None,
    vaa3d_version: str | None = None,
    image_file: str,
    output_swc: str | None = None,
    params: tuple[str, ...] | list[str] | None = None,
) -> list[str]:
    """Build Vaa3D CLI command for one tracer execution."""
    if tracer not in TRACER_SPECS:
        raise ValueError(f"Unsupported tracer: {tracer}")
    spec = TRACER_SPECS[tracer]
    parameters = tuple(params) if params is not None else spec.default_params
    inferred_version = vaa3d_version or TRACER_DEFAULT_VERSION.get(tracer)
    if vaa3d_bin is not None:
        vaa3d_executable = vaa3d_bin
    elif inferred_version is not None:
        vaa3d_executable = get_vaa3d_path("tracing", version=inferred_version)
    elif _is_windows_platform():
        vaa3d_executable = _auto_pick_vaa3d_bin_for_tracer(spec)
    else:
        vaa3d_executable = get_vaa3d_path("tracing", version=None)
    plugin_argument = resolve_tracer_plugin_arg(vaa3d_executable, spec.plugin)
    if _is_windows_platform():
        executable_path = Path(vaa3d_executable)
        # Fail fast only when local Vaa3D install is explicit and plugin lookup failed.
        if executable_path.exists() and not _is_resolved_plugin_dll(plugin_argument):
            raise ValueError(f"Plugin '{spec.plugin}' is not available under Vaa3D: {vaa3d_executable}")
    flag_prefix = "/" if _is_windows_platform() else "-"

    cmd = [vaa3d_executable, f"{flag_prefix}x", plugin_argument, f"{flag_prefix}f", spec.function, f"{flag_prefix}i", image_file]
    if output_swc is not None:
        cmd.extend([f"{flag_prefix}o", output_swc])
    if parameters:
        cmd.extend([f"{flag_prefix}p", *parameters])
    return cmd


def available_tracers() -> list[str]:
    """Backward-compatible alias of :func:`list_available_tracers`."""
    return list_available_tracers()


def installed_tracers() -> list[str]:
    """Backward-compatible alias of :func:`list_installed_tracers`."""
    return list_installed_tracers()


def tracer_output_candidates(tracer: str, image_file: str, output_swc: str | None = None) -> list[str]:
    """Backward-compatible alias of :func:`get_tracer_output_candidates`."""
    return get_tracer_output_candidates(tracer, image_file, output_swc)
