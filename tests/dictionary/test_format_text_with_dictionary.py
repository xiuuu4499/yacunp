"""Test for the Format Text With Dictionary node."""

from __future__ import annotations

from collections import OrderedDict

from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpKVPair
from yacunp.comfyui_yacunp.nodes.dictionary.format_text_with_dictionary import (
    YacunpFormatTextWithDictionary,
)


def _dictionary():
    items = OrderedDict()
    items["name"] = YacunpKVPair("name", "STRING", "Ada")
    items["age"] = YacunpKVPair("age", "INT", 36)
    return YacunpDictionary(items=items)


def test_execute_replaces_placeholders():
    result = YacunpFormatTextWithDictionary.execute(
        dictionary=_dictionary(),
        text="{name} is {age}",
        placeholder_prefix="{",
        placeholder_suffix="}",
    )
    assert result.args[0] == "Ada is 36"


def test_execute_custom_delimiters():
    result = YacunpFormatTextWithDictionary.execute(
        dictionary=_dictionary(),
        text="Hello %%name%%",
        placeholder_prefix="%%",
        placeholder_suffix="%%",
    )
    assert result.args[0] == "Hello Ada"


def test_execute_unknown_placeholder_left_intact():
    result = YacunpFormatTextWithDictionary.execute(
        dictionary=_dictionary(),
        text="{missing}",
        placeholder_prefix="{",
        placeholder_suffix="}",
    )
    assert result.args[0] == "{missing}"
