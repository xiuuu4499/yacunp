"""Generate Text node (backend-agnostic)."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs.custom_types import DictionaryType, LLMModelType
from ...libs.local_llm import args, backends, config
from ...libs.local_llm import images as images_util


def generate(model, prompt, system_prompt, arguments, image=None, image2=None) -> tuple:
    _load_args, gen_args = config.split_args(args.dictionary_to_plain(arguments))
    urls = []
    if image is not None or image2 is not None:
        urls = images_util.tensors_to_data_urls(image, image2)
    backend = backends.get_backend(model.backend)
    text, info = backend.generate(
        model, str(system_prompt or ""), str(prompt or ""), urls, gen_args
    )
    return text, args.plain_to_dictionary(info)


class YacunpGenerateText(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_GenerateText",
            display_name="Generate Text (YACUNP)",
            category="YACUNP/Local LLM",
            description="Run text generation on a loaded local model (llama.cpp or "
            "LM Studio). Takes the model, the prompt, an optional system prompt, an "
            "optional arguments dictionary (generation-time keys are used), and "
            "optional images for multimodal models. Outputs the generated text and "
            "an info dictionary with diagnostics such as token counts.",
            inputs=[
                LLMModelType.Input("model"),
                io.String.Input("prompt", multiline=True, default=""),
                io.String.Input(
                    "system_prompt", multiline=True, default="", optional=True
                ),
                DictionaryType.Input("arguments", optional=True),
                io.Image.Input("image", optional=True),
                io.Image.Input("image2", optional=True),
            ],
            outputs=[
                io.String.Output("text"),
                DictionaryType.Output("info"),
            ],
        )

    @classmethod
    def execute(
        cls, model, prompt, system_prompt="", arguments=None, image=None, image2=None
    ) -> io.NodeOutput:
        text, info = generate(model, prompt, system_prompt, arguments, image, image2)
        return io.NodeOutput(text, info)
