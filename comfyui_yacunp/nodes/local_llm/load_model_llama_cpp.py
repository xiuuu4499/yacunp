"""Load Model (llama.cpp) node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs.custom_types import DictionaryType, LLMModelType
from ...libs.local_llm import args, backends, config


def _model_options():
    keys = config.model_keys(config.load_catalog(), backend="llama_cpp")
    return keys or ["(add llama_cpp models to local_models.json)"]


def load_model(model_key: str, override_args: dict) -> tuple:
    catalog = config.load_catalog()
    resolved = config.resolve(catalog, model_key)
    merged = config.merge_args(resolved.defaults, override_args)
    load_args, _gen_args = config.split_args(merged)
    backend = backends.get_backend("llama_cpp")
    llm = backend.load(resolved, load_args)
    resolved_plain = dict(merged)
    if llm.config.get("n_ctx"):
        resolved_plain["n_ctx"] = llm.config["n_ctx"]
    return llm, args.plain_to_dictionary(resolved_plain)


class YacunpLoadModelLlamaCpp(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_LoadModelLlamaCpp",
            display_name="Load Model (llama.cpp) (YACUNP)",
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
    def execute(cls, model, arguments=None) -> io.NodeOutput:
        override = args.dictionary_to_plain(arguments)
        llm, resolved = load_model(str(model), override)
        return io.NodeOutput(llm, resolved)
