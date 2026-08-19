"""Test for the Make JSON node."""

from __future__ import annotations

import json
from collections import OrderedDict

from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpKVPair
from yacunp.comfyui_yacunp.nodes.json.make_json import YacunpMakeJSON


def test_execute_preserves_list_root():
    result = YacunpMakeJSON.execute(value=[1, "two", None, True])
    assert json.loads(result.args[0]) == [1, "two", None, True]


def test_execute_preserves_dictionary_root():
    result = YacunpMakeJSON.execute(value={"a": 1})
    assert json.loads(result.args[0]) == {"a": 1}


def test_execute_encodes_primitive_and_escapes_strings():
    result = YacunpMakeJSON.execute(value='say "hello"')
    assert result.args[0] == '"say \\"hello\\""'


def test_execute_encodes_null_root():
    result = YacunpMakeJSON.execute(value=None)
    assert result.args[0] == "null"


def test_execute_serializes_kvpair():
    result = YacunpMakeJSON.execute(value=YacunpKVPair("k", "INT", 5))
    assert json.loads(result.args[0]) == {"key": "k", "type": "INT", "value": 5}


def test_execute_pretty_output():
    result = YacunpMakeJSON.execute(value={"a": 1})
    assert "\n" in result.args[0]


def test_execute_serializes_dictionary_payload():
    dictionary = YacunpDictionary(
        items=OrderedDict([("answer", YacunpKVPair("answer", "INT", 42))])
    )
    result = YacunpMakeJSON.execute(value=dictionary)
    assert json.loads(result.args[0]) == {"answer": 42}


def test_schema_has_one_value_input():
    inputs = YacunpMakeJSON.define_schema().inputs
    assert len(inputs) == 1
    assert inputs[0].id == "value"
    assert "template" not in inputs[0].kwargs
