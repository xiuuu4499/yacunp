"""Make Advanced LLM Arguments node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs.custom_types import DictionaryType
from ...libs.local_llm import args
from .make_basic_llm_arguments import build_inputs


class YacunpMakeAdvancedLLMArguments(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_MakeAdvancedLLMArguments",
            display_name="Make Advanced LLM Arguments (YACUNP)",
            category="YACUNP/Local LLM",
            description="Build a dictionary of the less common LLM knobs: top_k / "
            "min_p sampling, repetition/presence/frequency penalties, batch and "
            "thread counts, FlashAttention, the multimodal image token budget, and "
            "a stop sequence. Combine it with Basic arguments (Combine "
            "Dictionaries) or use it on its own.",
            inputs=build_inputs(args.ADVANCED_ARG_SPECS),
            outputs=[DictionaryType.Output("arguments")],
        )

    @classmethod
    def execute(cls, **values) -> io.NodeOutput:
        return io.NodeOutput(args.build_arguments(args.ADVANCED_ARG_SPECS, values))
