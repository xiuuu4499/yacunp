"""Get Dictionary Value node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs import errors, type_registry
from ...libs.custom_types import DictionaryType


def get_value(dictionary, key: str, requested_type: str):
    try:
        pair = dictionary.items[key]
    except KeyError:
        raise errors.missing_key(key) from None
    type_registry.check_type(pair.declared_type, requested_type)
    return pair.value


class YacunpGetDictionaryValue(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_GetDictionaryValue",
            display_name="Get Dictionary Value",
            category="YACUNP/Dictionary",
            description="Look up a value by key. Errors if the key is missing or "
            "the stored type does not match the selected type.",
            inputs=[
                DictionaryType.Input("dictionary"),
                io.Combo.Input("type", options=type_registry.type_ids()),
                io.String.Input("key", default=""),
            ],
            outputs=[io.AnyType.Output("value")],
        )

    @classmethod
    def execute(cls, dictionary, type, key) -> io.NodeOutput:
        return io.NodeOutput(get_value(dictionary, str(key), type))
