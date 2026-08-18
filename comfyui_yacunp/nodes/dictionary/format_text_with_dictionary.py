"""Format Text With Dictionary node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs import type_registry
from ...libs.custom_types import DictionaryType


def format_text(dictionary, text: str, prefix: str, suffix: str) -> str:
    result = text
    for key, pair in dictionary.items.items():
        placeholder = f"{prefix}{key}{suffix}"
        replacement = type_registry.to_text(pair.declared_type, pair.value)
        result = result.replace(placeholder, replacement)
    return result


class YacunpFormatTextWithDictionary(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_FormatTextWithDictionary",
            display_name="Format Text With Dictionary (YACUNP)",
            category="YACUNP/Dictionary",
            description="Replace {key} placeholders in a text template with the "
            "string form of each dictionary value.",
            inputs=[
                DictionaryType.Input("dictionary"),
                io.String.Input("text", multiline=True, default=""),
                io.String.Input("placeholder_prefix", default="{"),
                io.String.Input("placeholder_suffix", default="}"),
            ],
            outputs=[io.String.Output("text")],
        )

    @classmethod
    def execute(
        cls, dictionary, text, placeholder_prefix, placeholder_suffix
    ) -> io.NodeOutput:
        return io.NodeOutput(
            format_text(dictionary, str(text), placeholder_prefix, placeholder_suffix)
        )
