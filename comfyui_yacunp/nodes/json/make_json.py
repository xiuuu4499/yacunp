"""Make JSON node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs import json_codec


def make_json(value) -> str:
    """Encode one workflow value while preserving its JSON root type."""
    return json_codec.encode(value, style=json_codec.PRETTY)


class YacunpMakeJSON(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_MakeJSON",
            display_name="Make JSON",
            category="YACUNP/JSON",
            description="Encode one connected value as pretty-printed JSON while "
            "preserving its root type. KV pairs and dictionaries are serialized "
            "structurally.",
            inputs=[io.AnyType.Input("value")],
            outputs=[io.String.Output("json")],
        )

    @classmethod
    def execute(cls, value) -> io.NodeOutput:
        return io.NodeOutput(make_json(value))
