"""Format JSON node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs import json_codec

FORMATS = [json_codec.SINGLE_LINE, json_codec.PRETTY]


def format_json(text: str, style: str) -> str:
    return json_codec.encode(json_codec.decode(text), style=style)


class YacunpFormatJSON(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_FormatJSON",
            display_name="Format JSON",
            category="YACUNP/JSON",
            description="Re-serialize a JSON string as either a single line or "
            "pretty-printed text.",
            inputs=[
                io.String.Input("json", multiline=True, default=""),
                io.Combo.Input("format", options=FORMATS),
            ],
            outputs=[io.String.Output("json")],
        )

    @classmethod
    def execute(cls, json, format) -> io.NodeOutput:
        return io.NodeOutput(format_json(str(json), format))
