"""Tests for the Set Dictionary Value node."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.libs import errors
from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpKVPair
from yacunp.comfyui_yacunp.nodes.dictionary.set_dictionary_value import (
    YacunpSetDictionaryValue,
    set_value,
)


def _pair(key, value="v"):
    return YacunpKVPair(key=key, declared_type="STRING", value=value)


def _dict(*pairs):
    return YacunpDictionary(items={p.key: p for p in pairs})


def test_set_value_inserts_new_key():
    result = set_value(_dict(_pair("a")), _pair("b", "x"))
    assert list(result.items.keys()) == ["a", "b"]
    assert result.items["b"].value == "x"


def test_set_value_replace_overwrites():
    result = set_value(_dict(_pair("a", "old")), _pair("a", "new"), on_conflict="replace")
    assert result.items["a"].value == "new"


def test_set_value_throw_error_on_conflict():
    with pytest.raises(errors.YacunpError):
        set_value(_dict(_pair("a")), _pair("a"), on_conflict="throw_error")


def test_set_value_does_not_mutate_input():
    original = _dict(_pair("a", "old"))
    set_value(original, _pair("a", "new"))
    assert original.items["a"].value == "old"


def test_execute_returns_dictionary():
    result = YacunpSetDictionaryValue.execute(
        dictionary=_dict(_pair("a")), pair=_pair("b"), on_conflict="replace"
    )
    assert isinstance(result.args[0], YacunpDictionary)
