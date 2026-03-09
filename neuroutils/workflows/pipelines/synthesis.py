"""SWC synthesis pipeline workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from neuroutils.io.swc import read_swc, write_swc
from neuroutils.swc.synthesis import (
    break_fragment_attach,
    graft_branch_segment,
    graft_full_tree,
    local_spur,
    small_cluster_attach,
)


@dataclass(frozen=True, slots=True)
class SynthesisStepResult:
    """One applied synthesis step summary."""

    name: str
    affected_count: int
    total_nodes_after: int


def _normalize_step(step: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    if "name" not in step:
        raise ValueError("Each strategy step must contain key: name")
    name = str(step["name"]).strip()
    params_raw = step.get("params", {})
    if params_raw is None:
        params_raw = {}
    if not isinstance(params_raw, Mapping):
        raise ValueError("step['params'] must be a mapping when provided")
    params = dict(params_raw)
    for k, v in step.items():
        if k in {"name", "params"}:
            continue
        params[k] = v
    return name, params


def _pick_donor_nodes(
    donor_pool: list[list],
    *,
    params: dict[str, Any],
    rng: np.random.Generator,
) -> list:
    if not donor_pool:
        raise ValueError("Graft strategy requires donor_swc_paths")
    donor_index = params.pop("donor_index", None)
    if donor_index is None:
        idx = int(rng.integers(0, len(donor_pool)))
    else:
        idx = int(donor_index)
        if idx < 0 or idx >= len(donor_pool):
            raise ValueError(f"donor_index out of range: {idx}")
    return donor_pool[idx]


def synthesize_swc_with_strategies(
    input_swc: str | Path,
    output_swc: str | Path,
    *,
    strategies: list[Mapping[str, Any]],
    donor_swc_paths: list[str | Path] | None = None,
    seed: int | None = None,
) -> list[SynthesisStepResult]:
    """Serially apply specified synthesis strategies on one target SWC.

    Supported strategy names:
    - ``full_tree_graft``
    - ``branch_segment_graft``
    - ``local_spur``
    - ``small_cluster_attach``
    - ``break_fragment_attach``
    """
    if not strategies:
        raise ValueError("strategies must not be empty")

    rng = np.random.default_rng(seed)
    nodes = read_swc(input_swc)
    donor_pool = [read_swc(p) for p in (donor_swc_paths or [])]
    logs: list[SynthesisStepResult] = []

    for raw_step in strategies:
        name, params = _normalize_step(raw_step)
        if name == "full_tree_graft":
            donor_nodes = _pick_donor_nodes(donor_pool, params=params, rng=rng)
            res = graft_full_tree(nodes, donor_nodes, rng=rng, **params)
            nodes = res.nodes
            affected = len(res.grafted_node_ids)
        elif name == "branch_segment_graft":
            donor_nodes = _pick_donor_nodes(donor_pool, params=params, rng=rng)
            res = graft_branch_segment(nodes, donor_nodes, rng=rng, **params)
            nodes = res.nodes
            affected = len(res.grafted_node_ids)
        elif name == "local_spur":
            res = local_spur(nodes, rng=rng, **params)
            nodes = res.nodes
            affected = len(res.affected_node_ids)
        elif name == "small_cluster_attach":
            res = small_cluster_attach(nodes, rng=rng, **params)
            nodes = res.nodes
            affected = len(res.affected_node_ids)
        elif name == "break_fragment_attach":
            res = break_fragment_attach(nodes, rng=rng, **params)
            nodes = res.nodes
            affected = len(res.affected_node_ids)
        else:
            raise ValueError(f"Unsupported synthesis strategy: {name}")
        logs.append(
            SynthesisStepResult(
                name=name,
                affected_count=int(affected),
                total_nodes_after=len(nodes),
            )
        )

    output_path = Path(output_swc)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "synthetic by neuroutils",
        f"source={Path(input_swc).name}",
        f"steps={[x.name for x in logs]}",
        f"seed={seed}",
    ]
    write_swc(output_path, nodes, header=header)
    return logs
