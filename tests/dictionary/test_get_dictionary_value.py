"""Test for the Get Dictionary Value node."""

from __future__ import annotations

from collections import OrderedDict

import pytest
from yacunp.comfyui_yacunp.libs import errors
from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpKVPair
from yacunp.comfyui_yacunp.nodes.dictionary.get_dictionary_value import YacunpGetDictionaryValue


def _dictionary():
    items = OrderedDict()
    items["name"] = YacunpKVPair("name", "STRING", "Ada")
    items["age"] = YacunpKVPair("age", "INT", 36)
    return YacunpDictionary(items=items)


def test_execute_returns_value():
    result = YacunpGetDictionaryValue.execute(
        dictionary=_dictionary(), type="STRING", key="name"
    )
    assert result.args[0] == "Ada"


def test_execute_missing_key_raises():
    with pytest.raises(errors.YacunpError):
        YacunpGetDictionaryValue.execute(
            dictionary=_dictionary(), type="STRING", key="missing"
        )


def test_execute_type_mismatch_raises():
    with pytest.raises(errors.YacunpError):
        YacunpGetDictionaryValue.execute(
            dictionary=_dictionary(), type="INT", key="name"
        )
