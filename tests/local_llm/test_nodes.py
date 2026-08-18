"""Execution tests for Local LLM nodes using fake backends."""

from __future__ import annotations

from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpLLMModel
from yacunp.comfyui_yacunp.libs.local_llm import args, backends, config
from yacunp.comfyui_yacunp.libs.local_llm.backends import lmstudio
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
