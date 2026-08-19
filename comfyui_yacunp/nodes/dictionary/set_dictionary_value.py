"""Set Dictionary Value node."""

from __future__ import annotations

from collections import OrderedDict

from comfy_api.latest import io

from ...libs import errors
from ...libs.custom_types import (
    DictionaryType,
    KVPairType,
    YacunpDictionary,
    YacunpKVPair,
)

ON_CONFLICT_MODES = ["replace", "throw_error"]


def set_value(
    dictionary: YacunpDictionary,
    pair: YacunpKVPair,
    on_conflict: str = "replace",
) -> YacunpDictionary:
    if not isinstance(pair, YacunpKVPair):
        raise errors.YacunpError("Set Dictionary Value expects a YACUNP_KVPAIR value.")
    items: OrderedDict[str, YacunpKVPair] = OrderedDict(dictionary.items)
    if pair.key in items and on_conflict == "throw_error":
        raise errors.duplicate_key(pair.key)
    items[pair.key] = pair
    return YacunpDictionary(items=items)


class YacunpSetDictionaryValue(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_SetDictionaryValue",
            display_name="Set Dictionary Value",
            category="YACUNP/Dictionary",
            description="Insert or update a key/value pair in a dictionary. "
            "Returns a new dictionary; the input is left unchanged. "
            "When the key already exists, 'replace' overwrites it while "
            "'throw_error' raises an error.",
            inputs=[
                DictionaryType.Input("dictionary"),
                KVPairType.Input("pair"),
                io.Combo.Input("on_conflict", options=ON_CONFLICT_MODES),
            ],
            outputs=[DictionaryType.Output("dictionary")],
        )

    @classmethod
    def execute(cls, dictionary, pair, on_conflict) -> io.NodeOutput:
        return io.NodeOutput(set_value(dictionary, pair, on_conflict))
