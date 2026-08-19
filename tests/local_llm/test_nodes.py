"""Execution tests for Local LLM nodes using fake backends."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.libs import errors
from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpLLMModel
from yacunp.comfyui_yacunp.libs.local_llm import args, backends, config
from yacunp.comfyui_yacunp.libs.local_llm.backends import llama_cpp, lmstudio
from yacunp.comfyui_yacunp.nodes.local_llm import (
    generate_text,
    load_model_llama_cpp,
    load_model_lmstudio,
    unload_model,
)


class _FakeGenerateBackend:
    def __init__(self):
        self.calls = []

    def generate(self, model, system, prompt, images, gen_args):
        self.calls.append((system, prompt, images, gen_args))
        return "hello world", {"backend": "fake", "completion_tokens": 2}


def test_generate_text_dispatches_and_returns_info(monkeypatch):
    fake = _FakeGenerateBackend()
    monkeypatch.setattr(backends, "get_backend", lambda backend_id: fake)
    model = YacunpLLMModel(backend="llama_cpp", name="m", handle=object())
    arguments = args.build_arguments(args.BASIC_ARG_SPECS, {"temperature": 0.3})

    result = generate_text.YacunpGenerateText.execute(
        model=model, prompt="hi", system_prompt="sys", arguments=arguments
    )

    assert result.args[0] == "hello world"
    info = result.args[1]
    assert isinstance(info, YacunpDictionary)
    assert info.items["backend"].value == "fake"
    system, prompt, images, gen_args = fake.calls[0]
    assert (system, prompt, images) == ("sys", "hi", [])
    assert gen_args["temperature"] == 0.3
    assert "n_ctx" not in gen_args  # load-time keys are filtered out


def test_llama_backend_translates_stop_sequence_to_stop():
    calls = []

    class _FakeHandle:
        def create_chat_completion(self, **payload):
            calls.append(payload)
            return {"choices": [{"message": {"content": "done"}}]}

    model = YacunpLLMModel(backend="llama_cpp", name="m", handle=_FakeHandle())
    llama_cpp.generate(
        model=model,
        system="",
        prompt="hi",
        images=[],
        gen_args={"stop_sequence": "</end>"},
    )

    assert calls[0]["stop"] == ["</end>"]
    assert "stop_sequence" not in calls[0]


def test_lmstudio_backend_translates_stop_sequence_to_stop(monkeypatch):
    requests = []

    def fake_request(url, payload=None, timeout=120.0):
        requests.append((url, payload))
        return {"choices": [{"message": {"content": "done"}}]}

    monkeypatch.setattr(lmstudio, "_request", fake_request)
    model = YacunpLLMModel(
        backend="lmstudio",
        name="m",
        handle={"base_url": "http://host:1/v1", "model": "m"},
    )
    lmstudio.generate(
        model=model,
        system="",
        prompt="hi",
        images=[],
        gen_args={"stop_sequence": "</end>"},
    )

    assert requests[0][1]["stop"] == ["</end>"]
    assert "stop_sequence" not in requests[0][1]


def test_load_model_llama_cpp_splits_load_args(monkeypatch):
    catalog = {
        "models": {
            "m": {
                "backend": "llama_cpp",
                "path": "/x.gguf",
                "defaults": {"n_ctx": 4096, "temperature": 0.5},
            }
        },
        "lmstudio": {},
    }
    monkeypatch.setattr(config, "load_catalog", lambda path=None: catalog)
    captured = {}

    class _FakeLoader:
        def load(self, resolved, load_args):
            captured["load_args"] = load_args
            return YacunpLLMModel(
                backend="llama_cpp", name=resolved.key, handle=object(),
                config={"n_ctx": 4096},
            )

    monkeypatch.setattr(backends, "get_backend", lambda backend_id: _FakeLoader())

    result = load_model_llama_cpp.YacunpLoadModelLlamaCpp.execute(model="m")
    llm, resolved_dict = result.args
    assert llm.name == "m"
    assert captured["load_args"] == {"n_ctx": 4096}
    assert resolved_dict.items["temperature"].value == 0.5
    assert resolved_dict.items["n_ctx"].value == 4096


def test_unload_frees_model(monkeypatch):
    calls = []

    class _FakeUnload:
        def unload(self, model):
            calls.append(model)

    monkeypatch.setattr(backends, "get_backend", lambda backend_id: _FakeUnload())
    model = YacunpLLMModel(backend="llama_cpp", name="m", handle=object())

    result = unload_model.YacunpUnloadModel.execute(model=model)
    info = result.args[0]
    assert info.items["unloaded"].value is True
    assert info.items["model"].value == "m"
    assert calls == [model]


def test_unload_without_model_still_cleans():
    result = unload_model.YacunpUnloadModel.execute(model=None)
    assert result.args[0].items["unloaded"].value is False


def test_lmstudio_load_direct_no_network(monkeypatch):
    monkeypatch.setattr(lmstudio, "ensure_model_loaded", lambda base_url, model_id: None)
    monkeypatch.setattr(backends, "get_backend", lambda backend_id: lmstudio)
    result = load_model_lmstudio.YacunpLoadModelLMStudio.execute(
        base_url="http://host:1/v1", model="my-model", multimodal=True
    )
    llm, _resolved = result.args
    assert llm.backend == "lmstudio"
    assert llm.name == "my-model"
    assert llm.multimodal is True


def test_lmstudio_load_applies_catalog_defaults(monkeypatch):
    catalog = {
        "models": {
            "My LM Studio model": {
                "backend": "lmstudio",
                "base_url": "http://localhost:1234/v1",
                "path": "qwen2.5-7b-instruct",
                "multimodal": False,
                "defaults": {"temperature": 0.7, "top_p": 0.95, "max_tokens": 1024},
            }
        },
        "lmstudio": {},
    }
    monkeypatch.setattr(config, "load_catalog", lambda path=None: catalog)
    monkeypatch.setattr(lmstudio, "ensure_model_loaded", lambda base_url, model_id: None)
    monkeypatch.setattr(backends, "get_backend", lambda backend_id: lmstudio)
    result = load_model_lmstudio.YacunpLoadModelLMStudio.execute(
        base_url="http://localhost:1234/v1",
        model="qwen2.5-7b-instruct",
        multimodal=False,
    )
    _llm, resolved = result.args
    assert resolved.items["temperature"].value == 0.7
    assert resolved.items["top_p"].value == 0.95
    assert resolved.items["max_tokens"].value == 1024


# --- ensure_model_loaded / _native_base unit tests ---

def test_native_base_strips_v1_suffix():
    assert lmstudio._native_base("http://localhost:1234/v1") == "http://localhost:1234/api/v1"
    assert lmstudio._native_base("http://localhost:1234/v1/") == "http://localhost:1234/api/v1"
    assert lmstudio._native_base("http://localhost:1234") == "http://localhost:1234/api/v1"


def test_ensure_model_loaded_already_active(monkeypatch):
    """Model with a loaded instance: no load request is issued."""
    api_response = {
        "data": [{"id": "my-model", "loaded_instances": [{"instance_id": "x"}]}]
    }
    requests = []

    def fake_request(url, payload=None, timeout=120.0):
        requests.append((url, payload))
        return api_response

    monkeypatch.setattr(lmstudio, "_request", fake_request)
    lmstudio.ensure_model_loaded("http://localhost:1234/v1", "my-model")
    assert len(requests) == 1  # only GET /api/v1/models, no POST


def test_ensure_model_loaded_triggers_load(monkeypatch):
    """Model present but not loaded: a POST to load is issued and validated."""
    list_response = {"data": [{"id": "my-model", "loaded_instances": []}]}
    load_response = {"data": {"loaded_instances": [{"instance_id": "y"}]}}
    responses = [list_response, load_response]

    def fake_request(url, payload=None, timeout=120.0):
        return responses.pop(0)

    monkeypatch.setattr(lmstudio, "_request", fake_request)
    lmstudio.ensure_model_loaded("http://localhost:1234/v1", "my-model")


def test_ensure_model_loaded_raises_if_load_fails(monkeypatch):
    """Load response with no loaded_instances raises a clear error."""
    list_response = {"data": [{"id": "my-model", "loaded_instances": []}]}
    load_response = {"data": {}, "error": {"message": "out of memory"}}
    responses = [list_response, load_response]

    def fake_request(url, payload=None, timeout=120.0):
        return responses.pop(0)

    monkeypatch.setattr(lmstudio, "_request", fake_request)
    with pytest.raises(errors.YacunpError, match="out of memory"):
        lmstudio.ensure_model_loaded("http://localhost:1234/v1", "my-model")


def test_ensure_model_loaded_raises_if_not_in_catalog(monkeypatch):
    """Model not in native API response: clear error is raised."""
    monkeypatch.setattr(lmstudio, "_request", lambda url, payload=None, timeout=120.0: {"data": []})
    with pytest.raises(errors.YacunpError, match="not available"):
        lmstudio.ensure_model_loaded("http://localhost:1234/v1", "missing-model")


# --- resource cache tests ---

from yacunp.comfyui_yacunp.libs.local_llm import resource_cache  # noqa: E402


@pytest.fixture(autouse=False)
def _clear_cache():
    """Isolate tests by clearing the resource cache before and after each test."""
    resource_cache._cache.clear()
    yield
    resource_cache._cache.clear()


def test_llama_cpp_load_registers_in_resource_cache(monkeypatch, _clear_cache):
    catalog = {
        "models": {
            "m": {
                "backend": "llama_cpp",
                "path": "/x.gguf",
                "defaults": {"n_ctx": 4096, "temperature": 0.5},
            }
        },
        "lmstudio": {},
    }
    monkeypatch.setattr(config, "load_catalog", lambda path=None: catalog)

    class _FakeLoader:
        def load(self, resolved, load_args):
            return YacunpLLMModel(
                backend="llama_cpp", name=resolved.key, handle=object(),
                config={"n_ctx": 4096},
            )

    monkeypatch.setattr(backends, "get_backend", lambda backend_id: _FakeLoader())

    result = load_model_llama_cpp.YacunpLoadModelLlamaCpp.execute(model="m")
    llm, _ = result.args
    assert resource_cache.is_live("llama_cpp:m")
    assert resource_cache.get("llama_cpp:m") is llm
    assert llm.cache_key == "llama_cpp:m"


def test_unload_invalidates_resource_cache(monkeypatch, _clear_cache):
    model = YacunpLLMModel(
        backend="llama_cpp", name="m", handle=object(), cache_key="llama_cpp:m"
    )
    resource_cache.put("llama_cpp:m", model)
    assert resource_cache.is_live("llama_cpp:m")

    monkeypatch.setattr(backends, "get_backend", lambda backend_id: type("B", (), {"unload": lambda self, m: None})())
    unload_model.YacunpUnloadModel.execute(model=model)

    assert not resource_cache.is_live("llama_cpp:m")
    assert resource_cache.get("llama_cpp:m") is None


def test_llama_cpp_is_changed_returns_nan_when_not_live(_clear_cache):
    result = load_model_llama_cpp.YacunpLoadModelLlamaCpp.is_changed(model="m")
    import math
    assert math.isnan(result)


def test_llama_cpp_is_changed_returns_stable_key_when_live(_clear_cache):
    model = YacunpLLMModel(backend="llama_cpp", name="m", handle=object())
    resource_cache.put("llama_cpp:m", model)
    result = load_model_llama_cpp.YacunpLoadModelLlamaCpp.is_changed(model="m")
    assert result == "llama_cpp:m"


def test_lmstudio_load_registers_in_resource_cache(monkeypatch, _clear_cache):
    monkeypatch.setattr(lmstudio, "ensure_model_loaded", lambda base_url, model_id: None)
    monkeypatch.setattr(backends, "get_backend", lambda backend_id: lmstudio)
    result = load_model_lmstudio.YacunpLoadModelLMStudio.execute(
        base_url="http://host:1/v1", model="my-model", multimodal=False
    )
    llm, _ = result.args
    cache_key = "lmstudio:http://host:1/v1:my-model"
    assert resource_cache.is_live(cache_key)
    assert resource_cache.get(cache_key) is llm
    assert llm.cache_key == cache_key


def test_lmstudio_is_changed_returns_nan_for_blank_model(_clear_cache):
    import math
    result = load_model_lmstudio.YacunpLoadModelLMStudio.is_changed(
        base_url="http://host:1/v1", model=""
    )
    assert math.isnan(result)


def test_lmstudio_is_changed_returns_stable_key_when_live(_clear_cache):
    model = YacunpLLMModel(backend="lmstudio", name="my-model", handle={"x": 1})
    cache_key = "lmstudio:http://host:1/v1:my-model"
    resource_cache.put(cache_key, model)
    result = load_model_lmstudio.YacunpLoadModelLMStudio.is_changed(
        base_url="http://host:1/v1", model="my-model"
    )
    assert result == cache_key


def test_llama_cpp_reuses_cached_handle(monkeypatch, _clear_cache):
    """Second execute() call returns the same live handle from cache, not a new load."""
    catalog = {
        "models": {
            "m": {"backend": "llama_cpp", "path": "/x.gguf", "defaults": {"n_ctx": 2048}}
        },
        "lmstudio": {},
    }
    monkeypatch.setattr(config, "load_catalog", lambda path=None: catalog)
    load_calls = []

    class _FakeLoader:
        def load(self, resolved, load_args):
            load_calls.append(1)
            return YacunpLLMModel(
                backend="llama_cpp", name=resolved.key, handle=object(),
                config={"n_ctx": 2048},
            )

    monkeypatch.setattr(backends, "get_backend", lambda backend_id: _FakeLoader())

    r1 = load_model_llama_cpp.YacunpLoadModelLlamaCpp.execute(model="m")
    r2 = load_model_llama_cpp.YacunpLoadModelLlamaCpp.execute(model="m")
    assert r1.args[0] is r2.args[0]
    assert len(load_calls) == 1
