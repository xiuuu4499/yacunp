"""Tests for the JSON codec."""

from __future__ import annotations

from collections import OrderedDict

import pytest
from yacunp.comfyui_yacunp.libs import errors, json_codec
from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpKVPair


def test_encode_pretty_multiline():
    out = json_codec.encode({"a": 1}, style=json_codec.PRETTY)
    assert "\n" in out
    assert out.startswith("{")


def test_encode_single_line():
    out = json_codec.encode({"a": 1, "b": 2}, style=json_codec.SINGLE_LINE)
    assert "\n" not in out
    assert out == '{"a": 1, "b": 2}'


def test_encode_escapes_special_characters():
    out = json_codec.encode('quote " and newline \n', style=json_codec.SINGLE_LINE)
    assert '\\"' in out
    assert "\\n" in out


def test_encode_kvpair_structurally():
    pair = YacunpKVPair(key="k", declared_type="INT", value=3)
    out = json_codec.encode(pair, style=json_codec.SINGLE_LINE)
    assert out == '{"key": "k", "type": "INT", "value": 3}'


def test_encode_dictionary_structurally():
    items = OrderedDict()
    items["name"] = YacunpKVPair("name", "STRING", "Ada")
    items["age"] = YacunpKVPair("age", "INT", 36)
    dictionary = YacunpDictionary(items=items)
    out = json_codec.encode(dictionary, style=json_codec.SINGLE_LINE)
    assert out == '{"name": "Ada", "age": 36}'


def test_decode_roundtrip():
    value = json_codec.decode('{"x": [1, 2, 3]}')
    assert value == {"x": [1, 2, 3]}


def test_decode_invalid_raises():
    with pytest.raises(errors.YacunpError):
        json_codec.decode("{not json}")


def test_encode_unknown_style_raises():
    with pytest.raises(errors.YacunpError):
        json_codec.encode({}, style="bogus")
