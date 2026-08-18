"""Test for the Get Dictionary Keys node."""

from __future__ import annotations

from collections import OrderedDict

from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpKVPair
from yacunp.comfyui_yacunp.nodes.dictionary.get_dictionary_keys import YacunpGetDictionaryKeys


def test_execute_returns_ordered_keys():
    items = OrderedDict()
    items["first"] = YacunpKVPair("first", "STRING", "1")
    items["second"] = YacunpKVPair("second", "STRING", "2")
    result = YacunpGetDictionaryKeys.execute(dictionary=YacunpDictionary(items=items))
    assert result.args[0] == ["first", "second"]


def test_execute_empty_dictionary():
    result = YacunpGetDictionaryKeys.execute(dictionary=YacunpDictionary())
    assert result.args[0] == []
