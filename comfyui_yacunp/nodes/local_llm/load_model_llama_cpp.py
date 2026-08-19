"""Load Model (llama.cpp) node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs.custom_types import DictionaryType, LLMModelType
from ...libs.local_llm import args, backends, config, resource_cache


def _model_options():
    keys = config.model_keys(config.load_catalog(), backend="llama_cpp")
    return keys or ["(add llama_cpp models to local_models.json)"]


def load_model(model_key: str, override_args: dict) -> tuple:
    cache_key = f"llama_cpp:{model_key}"
    catalog = config.load_catalog()
    resolved = config.resolve(catalog, model_key)
    merged = config.merge_args(resolved.defaults, override_args)

    cached = resource_cache.get(cache_key)
    if cached is not None and cached.handle is not None:
        resolved_plain = dict(merged)
        if cached.config.get("n_ctx"):
            resolved_plain["n_ctx"] = cached.config["n_ctx"]
        return cached, args.plain_to_dictionary(resolved_plain)

    load_args, _gen_args = config.split_args(merged)
    backend = backends.get_backend("llama_cpp")
    llm = backend.load(resolved, load_args)
    llm.cache_key = cache_key
    resource_cache.put(cache_key, llm)
    resolved_plain = dict(merged)
    if llm.config.get("n_ctx"):
        resolved_plain["n_ctx"] = llm.config["n_ctx"]
    return llm, args.plain_to_dictionary(resolved_plain)


class YacunpLoadModelLlamaCpp(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_LoadModelLlamaCpp",
            display_name="Load Model (llama.cpp)",
            category="YACUNP/Local LLM",
            description="Load a local GGUF model with llama.cpp. Models are defined "
            "in local_models.json (no downloads are ever performed). Optional "
            "arguments override the config defaults for load-time settings such as "
            "n_ctx and n_gpu_layers. Outputs the live model plus the fully resolved "
            "argument dictionary to pass on to Generate Text.",
            inputs=[
                io.Combo.Input("model", options=_model_options()),
                DictionaryType.Input("arguments", optional=True),
            ],
            outputs=[
                LLMModelType.Output("model"),
                DictionaryType.Output("resolved_arguments"),
            ],
        )

    @classmethod
    def is_changed(cls, model, arguments=None) -> float | str:
        cache_key = f"llama_cpp:{model}"
        return cache_key if resource_cache.is_live(cache_key) else float("nan")

    @classmethod
    def execute(cls, model, arguments=None) -> io.NodeOutput:
        override = args.dictionary_to_plain(arguments)
        llm, resolved = load_model(str(model), override)
        return io.NodeOutput(llm, resolved)
