"""Get Dictionary Keys node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs.custom_types import DictionaryType


class YacunpGetDictionaryKeys(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_GetDictionaryKeys",
            display_name="Get Dictionary Keys",
            category="YACUNP/Dictionary",
            description="Output the ordered list of keys in a dictionary.",
            inputs=[DictionaryType.Input("dictionary")],
            outputs=[io.String.Output("keys", is_output_list=True)],
        )

    @classmethod
    def execute(cls, dictionary) -> io.NodeOutput:
        return io.NodeOutput(list(dictionary.items.keys()))
