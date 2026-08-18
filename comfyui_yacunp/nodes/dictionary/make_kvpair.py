"""Make KV Pair node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs import type_registry
from ...libs.custom_types import KVPairType, YacunpKVPair


class YacunpMakeKVPair(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        options = [
            io.DynamicCombo.Option(type_id, [type_registry.spec(type_id).io_factory("value")])
            for type_id in type_registry.type_ids()
        ]
        return io.Schema(
            node_id="YACUNP_MakeKVPair",
            display_name="Make KV Pair (YACUNP)",
            category="YACUNP/Dictionary",
            description="Build a typed key/value pair. The value slot changes to "
            "match the selected type.",
            inputs=[
                io.String.Input("key", default="", force_input=True),
                io.DynamicCombo.Input("type", options=options),
            ],
            outputs=[KVPairType.Output("kvpair")],
        )

    @classmethod
    def execute(cls, key, type) -> io.NodeOutput:
        declared_type = type["type"]
        value = type.get("value")
        pair = YacunpKVPair(key=str(key), declared_type=declared_type, value=value)
        return io.NodeOutput(pair)
