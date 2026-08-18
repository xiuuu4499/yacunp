"""Read KV Pair node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs import type_registry
from ...libs.custom_types import KVPairType


class YacunpReadKVPair(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_ReadKVPair",
            display_name="Read KV Pair (YACUNP)",
            category="YACUNP/Dictionary",
            description="Split a key/value pair back into its key and value. "
            "The selected type must match the pair's declared type.",
            inputs=[
                KVPairType.Input("pair"),
                io.Combo.Input("type", options=type_registry.type_ids()),
            ],
            outputs=[
                io.String.Output("key"),
                io.AnyType.Output("value"),
            ],
        )

    @classmethod
    def execute(cls, pair, type) -> io.NodeOutput:
        type_registry.check_type(pair.declared_type, type)
        return io.NodeOutput(pair.key, pair.value)
