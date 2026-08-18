"""Load Model (LM Studio) node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs import errors
from ...libs.custom_types import DictionaryType, LLMModelType
from ...libs.local_llm import args, backends, config


def load_model(base_url: str, model: str, multimodal: bool, override_args: dict) -> tuple:
    backend = backends.get_backend("lmstudio")
    base = str(base_url or "").rstrip("/")
    model_id = str(model or "").strip()
    if not model_id:
        available = backend.list_models(base)
        if not available:
            raise errors.YacunpError(
                "LM Studio returned no models. Load a model in LM Studio first."
            )
        model_id = available[0]
    llm = backend.load_direct(base, model_id, bool(multimodal))
    resolved = args.plain_to_dictionary(config.merge_args({}, override_args))
    return llm, resolved


class YacunpLoadModelLMStudio(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        base_url = config.lmstudio_base_url(config.load_catalog())
        return io.Schema(
            node_id="YACUNP_LoadModelLMStudio",
            display_name="Load Model (LM Studio) (YACUNP)",
            category="YACUNP/Local LLM",
            description="Point at a running LM Studio server (OpenAI-compatible "
            "local API) and select a model it already exposes. No downloads are "
            "performed. Outputs a model handle and the resolved argument dictionary "
            "for Generate Text.",
            inputs=[
                io.String.Input(
                    "base_url",
                    default=base_url,
                    tooltip="LM Studio API base URL, e.g. http://localhost:1234/v1.",
                ),
                io.String.Input(
                    "model",
                    default="",
                    tooltip="Model id as shown by LM Studio (GET /v1/models). Leave "
                    "blank to use the first available model.",
                ),
                io.Boolean.Input(
                    "multimodal",
                    default=False,
                    tooltip="Enable if the selected model accepts image input.",
                ),
                DictionaryType.Input("arguments", optional=True),
            ],
            outputs=[
                LLMModelType.Output("model"),
                DictionaryType.Output("resolved_arguments"),
            ],
        )

    @classmethod
    def execute(cls, base_url, model, multimodal=False, arguments=None) -> io.NodeOutput:
        override = args.dictionary_to_plain(arguments)
        llm, resolved = load_model(base_url, model, multimodal, override)
        return io.NodeOutput(llm, resolved)
