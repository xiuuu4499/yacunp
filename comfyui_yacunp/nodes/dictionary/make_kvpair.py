"""Make KV Pair node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs import type_registry
from ...libs.custom_types import KVPairType, YacunpKVPair


class YacunpMakeKVPair(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        options = []
        for type_id in type_registry.type_ids():
            spec = type_registry.spec(type_id)
            socket_options = {
                "optional": True,
                "tooltip": "Connected values take precedence over the literal text.",
            }
            if spec.has_widget:
                socket_options["force_input"] = True
            options.append(
                io.DynamicCombo.Option(
                    type_id,
                    [
                        spec.io_factory("value", **socket_options),
                        io.String.Input(
                            "literal",
                            default="",
                            multiline=True,
                            socketless=True,
                            tooltip=(
                                "Fallback value when no value is connected. Use JSON "
                                "syntax except for STRING."
                            ),
                        ),
                    ],
                )
            )
        return io.Schema(
            node_id="YACUNP_MakeKVPair",
            display_name="Make KV Pair",
            category="YACUNP/Dictionary",
            description="Build a typed key/value pair from a connected value or "
            "a text literal converted to the selected type.",
            inputs=[
                io.String.Input("key", default="", force_input=True),
                io.DynamicCombo.Input("type", options=options),
            ],
            outputs=[KVPairType.Output("kvpair")],
        )

    @classmethod
    def execute(cls, key, type) -> io.NodeOutput:
        declared_type = type["type"]
        if "value" in type:
            value = type["value"]
        else:
            value = type_registry.from_text(declared_type, type.get("literal", ""))
        pair = YacunpKVPair(key=str(key), declared_type=declared_type, value=value)
        return io.NodeOutput(pair)
