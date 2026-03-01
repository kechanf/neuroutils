from __future__ import annotations

from pathlib import Path

import pytest

from neuroutils.io.images import load_image, load_v3dpbd


def test_load_v3dpbd_invalid_header(tmp_path: Path) -> None:
    p = tmp_path / "x.v3dpbd"
    p.write_bytes(b"not_a_valid_header")
    with pytest.raises(ValueError):
        load_v3dpbd(p)


def test_load_image_dispatch_v3dpbd(tmp_path: Path) -> None:
    p = tmp_path / "x.v3dpbd"
    p.write_bytes(b"not_a_valid_header")
    with pytest.raises(ValueError):
        load_image(p)
