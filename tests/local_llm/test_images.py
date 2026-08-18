"""Tests for IMAGE -> data URL encoding (requires numpy + PIL)."""

from __future__ import annotations

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("PIL")

from yacunp.comfyui_yacunp.libs.local_llm import images as images_util  # noqa: E402


def test_none_inputs_yield_no_urls():
    assert images_util.tensors_to_data_urls(None, None) == []


def test_batch_produces_one_url_per_frame():
    batch = np.zeros((2, 4, 4, 3), dtype="float32")
    urls = images_util.tensors_to_data_urls(batch)
    assert len(urls) == 2
    assert all(url.startswith("data:image/png;base64,") for url in urls)
