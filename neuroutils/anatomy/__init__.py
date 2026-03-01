"""Anatomy exports."""

from neuroutils.anatomy.ccf import (
    ccf_to_stereotactic_mask_res25,
    ccf2stereotactic_mask_res25,
    get_center,
    matrix_from_axis_angle,
    resample,
)
from neuroutils.anatomy.core import get_struct_from_id_path, parse_ana_tree, parse_id_map, parse_regions316
from neuroutils.anatomy.neighbors import (
    generate_mask314,
    get_regional_neighbors,
    get_regional_neighbors_cuda,
    get_salient_regions_mask,
    get_salient_regions_mask671,
)
from neuroutils.anatomy.region_size import compute_region_voxel_stats
from neuroutils.anatomy.vis import (
    detect_edges2d,
    detect_edges3d,
    get_brain_mask2d,
    get_brain_outline2d,
    get_section_boundary,
    get_section_boundary_with_outline,
)

__all__ = [
    "ccf_to_stereotactic_mask_res25",
    "ccf2stereotactic_mask_res25",
    "get_center",
    "detect_edges2d",
    "detect_edges3d",
    "generate_mask314",
    "get_brain_mask2d",
    "get_brain_outline2d",
    "get_regional_neighbors",
    "get_regional_neighbors_cuda",
    "get_salient_regions_mask",
    "get_salient_regions_mask671",
    "get_section_boundary",
    "get_section_boundary_with_outline",
    "get_struct_from_id_path",
    "compute_region_voxel_stats",
    "matrix_from_axis_angle",
    "resample",
    "parse_ana_tree",
    "parse_id_map",
    "parse_regions316",
]
