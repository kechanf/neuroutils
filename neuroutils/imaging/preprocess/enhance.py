"""Image enhancement helpers."""

from __future__ import annotations

import numpy as np

from neuroutils.imaging.preprocess.basic import min_max_normalize


def gamma_correction(
    image: np.ndarray,
    gamma: float,
    *,
    trunc_thresh: float = 0.0,
    normalize: bool = True,
    epsilon: float = 1e-7,
) -> np.ndarray:
    """Gamma correction with optional truncation and normalization."""
    img = np.asarray(image, dtype=np.float32)
    if trunc_thresh > 0:
        img = np.maximum(img, trunc_thresh)
    if normalize:
        img = min_max_normalize(img)
    return np.power(img + epsilon, gamma)


def do_gamma(
    img: np.ndarray,
    gamma: float,
    trunc_thresh: float = 0.0,
    normalize: bool = True,
    epsilon: float = 1e-7,
) -> np.ndarray:
    """Compatibility wrapper for gamma correction."""
    return gamma_correction(
        img,
        gamma=gamma,
        trunc_thresh=trunc_thresh,
        normalize=normalize,
        epsilon=epsilon,
    )


def clahe_enhance(
    image: np.ndarray,
    *,
    kernel_size: int | tuple[int, ...] = 8,
    clip_limit: float = 0.01,
    nbins: int = 256,
    normalize: bool = True,
) -> np.ndarray:
    """Contrast-limited adaptive histogram equalization."""
    try:
        from skimage.exposure import equalize_adapthist
    except ImportError as exc:
        raise RuntimeError("CLAHE requires scikit-image. Install with: pip install scikit-image") from exc
    img = np.asarray(image, dtype=np.float32)
    if normalize:
        img = min_max_normalize(img)
    return np.asarray(
        equalize_adapthist(img, kernel_size=kernel_size, clip_limit=clip_limit, nbins=nbins),
        dtype=np.float32,
    )


def do_CLAHE(
    img: np.ndarray,
    kernel_size: int | tuple[int, ...],
    clip_limit: float = 0.01,
    nbins: int = 256,
    normalize: bool = True,
    epsilon: float = 1e-7,
) -> np.ndarray:
    """Compatibility wrapper for CLAHE."""
    _ = epsilon
    return clahe_enhance(
        img,
        kernel_size=kernel_size,
        clip_limit=clip_limit,
        nbins=nbins,
        normalize=normalize,
    )
