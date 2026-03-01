"""Vaa3D tracer registry and command builders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TracerSpec:
    """Specification for one Vaa3D tracer plugin/function."""

    plugin: str
    function: str
    default_params: tuple[str, ...] = ()


TRACER_SPECS: dict[str, TracerSpec] = {
    "APP1": TracerSpec("vn2", "app1", ("NULL", "0", "40", "1")),
    "APP2": TracerSpec("vn2", "app2", ("NULL", "0", "10", "1", "1", "0", "0", "5", "0", "0", "0")),
    "APP2_NEW1": TracerSpec("vn2", "app2", ("NULL", "0", "AUTO", "1", "1", "1", "1", "5", "0", "0", "0")),
    "APP2_NEW2": TracerSpec("vn2", "app2", ("NULL", "0", "AUTO", "1", "1", "0", "1", "5", "0", "0", "0")),
    "APP2_NEW3": TracerSpec("vn2", "app2", ("NULL", "0", "10", "1", "1", "1", "1", "5", "0", "0", "0")),
    "MOST": TracerSpec("MOST", "MOST_trace", ("1", "40")),
    "NEUTUBE": TracerSpec("neuTube", "neutube_trace", ("1", "1")),
    "SNAKE": TracerSpec("snake", "snake_trace", ("1",)),
    "SimpleTracing1": TracerSpec("SimpleTracing", "tracing", ()),
    "SimpleTracing2": TracerSpec("SimpleTracing", "ray_shooting", ()),
    "SimpleTracing3": TracerSpec("SimpleTracing", "dfs", ()),
    "TreMap": TracerSpec("TReMap", "trace_mip", ("0", "1", "10", "0", "1", "0", "5")),
    "MST": TracerSpec("MST_tracing", "trace_mst", ("1", "5")),
    "RegMST": TracerSpec("MST_tracing", "trace_mst", ("21", "200")),
    "NeuroGPSTree": TracerSpec("NeuroGPSTree", "tracing_func", ("1", "1", "1", "10")),
    "NeuroGPSTree2": TracerSpec("NeuroGPSTree", "tracing_func", ("0.5", "0.5", "1", "15", "10", "150")),
    "FMST": TracerSpec("fastmarching_spanningtree", "tracing_func", ()),
    "MeanShift": TracerSpec("BJUT_meanshift", "meanshift", ()),
    "CWlab11": TracerSpec("CWlab_method1_version1", "tracing_func", ("1",)),
    "LCM_boost": TracerSpec("LCM_boost", "LCM_boost", ()),
    "LCM_boost_2": TracerSpec("LCM_boost", "LCM_boost_2", ()),
    "LCM_boost_3": TracerSpec("LCM_boost", "LCM_boost_3", ()),
    "NeuroStalker": TracerSpec("NeuroStalker", "tracing_func", ("1", "1", "1", "5", "5", "30")),
    "nctuTW": TracerSpec("nctuTW", "tracing_func", ("NULL",)),
    "tips_GD": TracerSpec("tips_GD", "tracing_func", ()),
    "SimpleAxisAnalyzer": TracerSpec("SimpleAxisAnalyzer", "medial_axis_analysis", ()),
    "NeuronChaser": TracerSpec("NeuronChaser", "nc_func", ("1", "10", "0.6", "15", "60", "30", "5", "1", "0")),
    "NeuronChaser2": TracerSpec("NeuronChaser", "nc_func", ("1", "10", "0.7", "20", "60", "10", "5", "1", "0")),
    "smartTracing": TracerSpec("smartTrace", "smartTrace", ()),
    "neutu_autotrace": TracerSpec("neutu_autotrace", "tracing", ()),
    "Advantra": TracerSpec("Advantra", "advantra_func", ("10", "0.3", "0.6", "15", "60", "30", "5", "1")),
    "Advantra2": TracerSpec("Advantra", "advantra_func", ("10", "0.5", "0.7", "20", "60", "30", "5", "1")),
    "EnsembleNeuronTracer": TracerSpec("EnsembleNeuronTracerBasic", "tracing_func", ()),
    "EnsembleNeuronTracerV2n": TracerSpec("EnsembleNeuronTracerV2n", "tracing_func", ()),
    "EnsembleNeuronTracerV2s": TracerSpec("EnsembleNeuronTracerV2s", "tracing_func", ()),
    "threeDTraceSWC": TracerSpec("aVaaTrace3D", "func1", ("20", "2", "2.5")),
    "threeDTraceSWC2": TracerSpec("aVaaTrace3D", "func1", ("50", "5", "2.5")),
}


def available_tracers() -> list[str]:
    """Return supported tracer names."""
    return sorted(TRACER_SPECS.keys())


def build_tracer_command(
    tracer: str,
    *,
    vaa3d_bin: str,
    image_file: str,
    output_swc: str | None = None,
    params: tuple[str, ...] | list[str] | None = None,
) -> list[str]:
    """Build Vaa3D command for a tracer by name."""
    if tracer not in TRACER_SPECS:
        raise ValueError(f"Unsupported tracer: {tracer}")
    spec = TRACER_SPECS[tracer]
    p = tuple(params) if params is not None else spec.default_params

    cmd = [vaa3d_bin, "-x", spec.plugin, "-f", spec.function, "-i", image_file]
    if output_swc is not None:
        cmd.extend(["-o", output_swc])
    if p:
        cmd.extend(["-p", *p])
    return cmd
