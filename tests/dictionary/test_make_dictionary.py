"""Test for the Make Dictionary node."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.libs import errors
from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpKVPair
from yacunp.comfyui_yacunp.nodes.dictionary.make_dictionary import YacunpMakeDictionary


def _pair(key, value="v"):
    return YacunpKVPair(key=key, declared_type="STRING", value=value)


def test_execute_combines_pairs_in_order():
    slots = {"pair_0": _pair("a"), "pair_1": _pair("b")}
    result = YacunpMakeDictionary.execute(pairs=slots)
    dictionary = result.args[0]
    assert isinstance(dictionary, YacunpDictionary)
    assert list(dictionary.items.keys()) == ["a", "b"]


def test_execute_tolerates_list_slot_and_none():
    slots = {"pair_0": [_pair("a"), _pair("b")], "pair_1": None, "pair_2": _pair("c")}
    result = YacunpMakeDictionary.execute(pairs=slots)
    assert list(result.args[0].items.keys()) == ["a", "b", "c"]


def test_execute_duplicate_key_raises():
    slots = {"pair_0": _pair("a"), "pair_1": _pair("a")}
    with pytest.raises(errors.YacunpError):
        YacunpMakeDictionary.execute(pairs=slots)


def test_execute_rejects_non_kvpair():
    with pytest.raises(errors.YacunpError):
        YacunpMakeDictionary.execute(pairs={"pair_0": "not a pair"})
