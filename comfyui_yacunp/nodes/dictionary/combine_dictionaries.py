"""Combine Dictionaries node."""

from __future__ import annotations

from collections import OrderedDict

from comfy_api.latest import io

from ...libs import errors, type_registry
from ...libs.custom_types import (
    DictionaryType,
    YacunpDictionary,
    YacunpKVPair,
)

COLLISION_MODES = [
    "throw_error",
    "keep_first",
    "keep_last",
    "concatenate",
    "list_combine_values",
]


def _iter_dictionaries(slots):
    """Yield every :class:`YacunpDictionary` from an Autogrow slot mapping."""
    for value in slots.values():
        if value is None:
            continue
        if isinstance(value, YacunpDictionary):
            yield value
        elif isinstance(value, (list, tuple)):
            for item in value:
                if not isinstance(item, YacunpDictionary):
                    raise errors.YacunpError(
                        "Combine Dictionaries inputs must be YACUNP_DICTIONARY values."
                    )
                yield item
        else:
            raise errors.YacunpError(
                "Combine Dictionaries inputs must be YACUNP_DICTIONARY values."
            )


def _merge_pair(existing, incoming, mode, separator):
    if mode == "throw_error":
        raise errors.duplicate_key(existing.key)
    if mode == "keep_first":
        return existing
    if mode == "keep_last":
        return incoming
    if mode == "concatenate":
        left = type_registry.to_text(existing.declared_type, existing.value)
        right = type_registry.to_text(incoming.declared_type, incoming.value)
        return YacunpKVPair(
            key=existing.key,
            declared_type="STRING",
            value=f"{left}{separator}{right}",
        )
    if mode == "list_combine_values":
        if existing.declared_type == "ARRAY" and isinstance(existing.value, list):
            combined = list(existing.value)
        else:
            combined = [existing.value]
        combined.append(incoming.value)
        return YacunpKVPair(key=existing.key, declared_type="ARRAY", value=combined)
    raise errors.YacunpError(f"Unknown collision mode: '{mode}'.")


def combine_dictionaries(dictionaries, mode="throw_error", separator=""):
    result: OrderedDict[str, YacunpKVPair] = OrderedDict()
    for dictionary in dictionaries:
        for key, pair in dictionary.items.items():
            if key not in result:
                result[key] = pair
            else:
                result[key] = _merge_pair(result[key], pair, mode, separator)
    return YacunpDictionary(items=result)


class YacunpCombineDictionaries(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_CombineDictionaries",
            display_name="Combine Dictionaries",
            category="YACUNP/Dictionary",
            description="Merge two or more dictionaries into one. The collision "
            "mode decides what happens when a key appears more than once: "
            "'throw_error' raises, 'keep_first'/'keep_last' pick one value, "
            "'concatenate' joins the values as text with the separator, and "
            "'list_combine_values' collects the values into a list.",
            inputs=[
                io.Autogrow.Input(
                    "dictionaries",
                    template=io.Autogrow.TemplatePrefix(
                        input=DictionaryType.Input("dictionary"),
                        prefix="dict_",
                        min=2,
                        max=32,
                    ),
                ),
                io.Combo.Input("collision_mode", options=COLLISION_MODES),
                io.String.Input("separator", default=" "),
            ],
            outputs=[DictionaryType.Output("dictionary")],
        )

    @classmethod
    def execute(cls, dictionaries, collision_mode, separator) -> io.NodeOutput:
        merged = combine_dictionaries(
            _iter_dictionaries(dictionaries),
            mode=collision_mode,
            separator=str(separator),
        )
        return io.NodeOutput(merged)
