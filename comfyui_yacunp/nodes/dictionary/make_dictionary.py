"""Make Dictionary node."""

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


def _iter_pairs(slots):
    """Yield every :class:`YacunpKVPair` from the Autogrow slot mapping.

    A slot may carry a single pair, ``None``, or a list of pairs.
    """
    for value in slots.values():
        if value is None:
            continue
        if isinstance(value, YacunpKVPair):
            yield value
        elif isinstance(value, (list, tuple)):
            for item in value:
                if not isinstance(item, YacunpKVPair):
                    raise errors.YacunpError(
                        "Make Dictionary inputs must be YACUNP_KVPAIR values."
                    )
                yield item
        else:
            raise errors.YacunpError(
                "Make Dictionary inputs must be YACUNP_KVPAIR values."
            )


def build_dictionary(slots) -> YacunpDictionary:
    items: OrderedDict[str, YacunpKVPair] = OrderedDict()
    for pair in _iter_pairs(slots):
        if pair.key in items:
            raise errors.duplicate_key(pair.key)
        items[pair.key] = pair
    return YacunpDictionary(items=items)


class YacunpMakeDictionary(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_MakeDictionary",
            display_name="Make Dictionary",
            category="YACUNP/Dictionary",
            description="Combine one or more key/value pairs into a dictionary. "
            "Duplicate keys raise an error.",
            inputs=[
                io.Autogrow.Input(
                    "pairs",
                    template=io.Autogrow.TemplatePrefix(
                        input=KVPairType.Input("pair"),
                        prefix="pair_",
                        min=1,
                        max=32,
                    ),
                )
            ],
            outputs=[DictionaryType.Output("dictionary")],
        )

    @classmethod
    def execute(cls, pairs) -> io.NodeOutput:
        return io.NodeOutput(build_dictionary(pairs))
