"""Make Basic LLM Arguments node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs.custom_types import DictionaryType
from ...libs.local_llm import args

_IO_FACTORIES = {
    "INT": io.Int,
    "FLOAT": io.Float,
    "BOOLEAN": io.Boolean,
    "STRING": io.String,
}


def build_inputs(specs):
    inputs = []
    for spec in specs:
        factory = _IO_FACTORIES[spec["type"]]
        inputs.append(
            factory.Input(
                spec["name"],
                default=spec["default"],
                tooltip=spec["description"],
                **spec["io"],
            )
        )
    return inputs


class YacunpMakeBasicLLMArguments(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_MakeBasicLLMArguments",
            display_name="Make Basic LLM Arguments",
            category="YACUNP/Local LLM",
            description="Build a dictionary of the LLM parameters people tune most "
            "often: generation length, temperature, nucleus sampling, seed, plus "
            "the core load-time context window and GPU-offload settings. Feed the "
            "result to Load Model and/or Generate Text.",
            inputs=build_inputs(args.BASIC_ARG_SPECS),
            outputs=[DictionaryType.Output("arguments")],
        )

    @classmethod
    def execute(cls, **values) -> io.NodeOutput:
        return io.NodeOutput(args.build_arguments(args.BASIC_ARG_SPECS, values))
