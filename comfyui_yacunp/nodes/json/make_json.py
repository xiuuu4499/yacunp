"""Make JSON node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs import json_codec


def make_json(slots) -> str:
    values = [value for value in slots.values() if value is not None]
    return json_codec.encode(values, style=json_codec.PRETTY)


class YacunpMakeJSON(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_MakeJSON",
            display_name="Make JSON (YACUNP)",
            category="YACUNP/JSON",
            description="Encode any connected values into a pretty-printed JSON "
            "array. KV pairs and dictionaries are serialized structurally.",
            inputs=[
                io.Autogrow.Input(
                    "values",
                    template=io.Autogrow.TemplatePrefix(
                        input=io.AnyType.Input("value"),
                        prefix="value_",
                        min=1,
                        max=32,
                    ),
                )
            ],
            outputs=[io.String.Output("json")],
        )

    @classmethod
    def execute(cls, values) -> io.NodeOutput:
        return io.NodeOutput(make_json(values))
