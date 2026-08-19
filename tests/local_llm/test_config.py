"""Tests for the local LLM model catalog."""

from __future__ import annotations

import json

import pytest
from yacunp.comfyui_yacunp.libs import errors
from yacunp.comfyui_yacunp.libs.local_llm import config


def _write(tmp_path, data):
    path = tmp_path / "local_models.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_load_catalog_missing_returns_empty(tmp_path):
    catalog = config.load_catalog(str(tmp_path / "nope.json"))
    assert catalog == {"models": {}, "lmstudio": {}}


def test_example_file_is_loadable_and_has_models():
    catalog = config.load_catalog(config.EXAMPLE_PATH)
    assert config.model_keys(catalog, backend="llama_cpp")
    assert config.model_keys(catalog, backend="lmstudio")


def test_model_keys_filters_by_backend(tmp_path):
    path = _write(
        tmp_path,
        {
            "models": {
                "a": {"backend": "llama_cpp", "path": "/m/a.gguf"},
                "b": {"backend": "lmstudio", "path": "b"},
            }
        },
    )
    catalog = config.load_catalog(path)
    assert config.model_keys(catalog, backend="llama_cpp") == ["a"]
    assert config.model_keys(catalog, backend="lmstudio") == ["b"]
    assert set(config.model_keys(catalog)) == {"a", "b"}


def test_resolve_reads_fields(tmp_path):
    path = _write(
        tmp_path,
        {
            "models": {
                "vl": {
                    "backend": "llama_cpp",
                    "path": "/m/vl.gguf",
                    "mmproj": "/m/vl-mmproj.gguf",
                    "multimodal": True,
                    "defaults": {"n_ctx": 8192, "temperature": 0.5},
                    "base_url": "http://x",
                }
            }
        },
    )
    resolved = config.resolve(config.load_catalog(path), "vl")
    assert resolved.backend == "llama_cpp"
    assert resolved.mmproj == "/m/vl-mmproj.gguf"
    assert resolved.multimodal is True
    assert resolved.chat_handler is None
    assert resolved.defaults["n_ctx"] == 8192
    assert resolved.extra["base_url"] == "http://x"


def test_resolve_reads_chat_handler(tmp_path):
    path = _write(
        tmp_path,
        {
            "models": {
                "vl": {
                    "backend": "llama_cpp",
                    "path": "/m/vl.gguf",
                    "mmproj": "/m/vl-mmproj.gguf",
                    "multimodal": True,
                    "chat_handler": "Qwen25VLChatHandler",
                    "defaults": {},
                }
            }
        },
    )
    resolved = config.resolve(config.load_catalog(path), "vl")
    assert resolved.chat_handler == "Qwen25VLChatHandler"


def test_resolve_unknown_raises(tmp_path):
    catalog = config.load_catalog(_write(tmp_path, {"models": {}}))
    with pytest.raises(errors.YacunpError):
        config.resolve(catalog, "missing")


def test_merge_args_override_wins():
    merged = config.merge_args({"a": 1, "b": 2}, {"b": 3, "c": None})
    assert merged == {"a": 1, "b": 3}


def test_split_args_partitions_load_and_gen():
    load_args, gen_args = config.split_args(
        {
            "n_ctx": 4096,
            "n_gpu_layers": -1,
            "temperature": 0.7,
            "max_tokens": 128,
            "stop_sequence": "</end>",
        }
    )
    assert load_args == {"n_ctx": 4096, "n_gpu_layers": -1}
    assert gen_args == {
        "temperature": 0.7,
        "max_tokens": 128,
        "stop_sequence": "</end>",
    }


def test_lmstudio_base_url_prefers_override(tmp_path):
    catalog = config.load_catalog(
        _write(tmp_path, {"lmstudio": {"base_url": "http://cfg:1/v1/"}})
    )
    assert config.lmstudio_base_url(catalog) == "http://cfg:1/v1"
    assert config.lmstudio_base_url(catalog, "http://over:2/v1/") == "http://over:2/v1"


def test_lmstudio_catalog_defaults_returns_matching_entry(tmp_path):
    catalog = config.load_catalog(
        _write(
            tmp_path,
            {
                "models": {
                    "My LM Studio model": {
                        "backend": "lmstudio",
                        "base_url": "http://localhost:1234/v1",
                        "path": "my-model",
                        "multimodal": False,
                        "defaults": {"temperature": 0.7, "max_tokens": 512},
                    }
                }
            },
        )
    )
    defaults = config.lmstudio_catalog_defaults(
        catalog, "http://localhost:1234/v1", "my-model"
    )
    assert defaults == {"temperature": 0.7, "max_tokens": 512}


def test_lmstudio_catalog_defaults_returns_empty_on_no_match(tmp_path):
    catalog = config.load_catalog(
        _write(
            tmp_path,
            {
                "models": {
                    "My LM Studio model": {
                        "backend": "lmstudio",
                        "base_url": "http://localhost:1234/v1",
                        "path": "my-model",
                        "defaults": {"temperature": 0.7},
                    }
                }
            },
        )
    )
    assert config.lmstudio_catalog_defaults(catalog, "http://localhost:1234/v1", "other") == {}
    assert config.lmstudio_catalog_defaults(catalog, "http://other:1/v1", "my-model") == {}
