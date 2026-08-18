"""Test for the Read KV Pair node."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.libs import errors
from yacunp.comfyui_yacunp.libs.custom_types import YacunpKVPair
from yacunp.comfyui_yacunp.nodes.dictionary.read_kvpair import YacunpReadKVPair


def test_execute_returns_key_and_value():
    pair = YacunpKVPair(key="name", declared_type="STRING", value="Ada")
    result = YacunpReadKVPair.execute(pair=pair, type="STRING")
    assert result.args == ("name", "Ada")


def test_execute_type_mismatch_raises():
    pair = YacunpKVPair(key="name", declared_type="STRING", value="Ada")
    with pytest.raises(errors.YacunpError):
        YacunpReadKVPair.execute(pair=pair, type="INT")


def test_execute_any_matches():
    pair = YacunpKVPair(key="k", declared_type="IMAGE", value=object())
    result = YacunpReadKVPair.execute(pair=pair, type="ANY")
    assert result.args[0] == "k"
