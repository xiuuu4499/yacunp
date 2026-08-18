"""Tests for the Combine Dictionaries node."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.libs import errors
from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpKVPair
from yacunp.comfyui_yacunp.nodes.dictionary.combine_dictionaries import (
    YacunpCombineDictionaries,
    combine_dictionaries,
)


def _pair(key, value="v", declared_type="STRING"):
    return YacunpKVPair(key=key, declared_type=declared_type, value=value)


def _dict(*pairs):
    return YacunpDictionary(items={p.key: p for p in pairs})


def test_combine_disjoint_keeps_order():
    result = combine_dictionaries([_dict(_pair("a")), _dict(_pair("b"))])
    assert list(result.items.keys()) == ["a", "b"]


def test_throw_error_on_collision():
    with pytest.raises(errors.YacunpError):
        combine_dictionaries([_dict(_pair("a", "1")), _dict(_pair("a", "2"))])


def test_keep_first():
    result = combine_dictionaries(
        [_dict(_pair("a", "1")), _dict(_pair("a", "2"))], mode="keep_first"
    )
    assert result.items["a"].value == "1"


def test_keep_last():
    result = combine_dictionaries(
        [_dict(_pair("a", "1")), _dict(_pair("a", "2"))], mode="keep_last"
    )
    assert result.items["a"].value == "2"


def test_concatenate_joins_text_with_separator():
    result = combine_dictionaries(
        [_dict(_pair("a", "1")), _dict(_pair("a", "2"))],
        mode="concatenate",
        separator="-",
    )
    assert result.items["a"].value == "1-2"
    assert result.items["a"].declared_type == "STRING"


def test_list_combine_values_collects_all():
    result = combine_dictionaries(
        [_dict(_pair("a", "1")), _dict(_pair("a", "2")), _dict(_pair("a", "3"))],
        mode="list_combine_values",
    )
    assert result.items["a"].value == ["1", "2", "3"]
    assert result.items["a"].declared_type == "ARRAY"


def test_execute_uses_slot_mapping():
    slots = {"dict_0": _dict(_pair("a")), "dict_1": _dict(_pair("b"))}
    result = YacunpCombineDictionaries.execute(
        dictionaries=slots, collision_mode="throw_error", separator=" "
    )
    assert list(result.args[0].items.keys()) == ["a", "b"]


def test_execute_rejects_non_dictionary():
    with pytest.raises(errors.YacunpError):
        YacunpCombineDictionaries.execute(
            dictionaries={"dict_0": "nope"}, collision_mode="throw_error", separator=" "
        )
