"""Test for the Make JSON node."""

from __future__ import annotations

import json

from yacunp.comfyui_yacunp.libs.custom_types import YacunpKVPair
from yacunp.comfyui_yacunp.nodes.json.make_json import YacunpMakeJSON


def test_execute_encodes_array_of_values():
    slots = {"value_0": 1, "value_1": "two", "value_2": None, "value_3": True}
    result = YacunpMakeJSON.execute(values=slots)
    assert json.loads(result.args[0]) == [1, "two", True]


def test_execute_serializes_kvpair():
    slots = {"value_0": YacunpKVPair("k", "INT", 5)}
    result = YacunpMakeJSON.execute(values=slots)
    assert json.loads(result.args[0]) == [{"key": "k", "type": "INT", "value": 5}]


def test_execute_pretty_output():
    result = YacunpMakeJSON.execute(values={"value_0": {"a": 1}})
    assert "\n" in result.args[0]
