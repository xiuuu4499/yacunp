"""Test for the Convert JSON node."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.libs import errors
from yacunp.comfyui_yacunp.nodes.json.convert_json import YacunpConvertJSON


def test_execute_list_root():
    result = YacunpConvertJSON.execute(json="[1, 2, 3]", root_type="list")
    assert result.args[0] == [1, 2, 3]


def test_execute_dictionary_root():
    result = YacunpConvertJSON.execute(json='{"a": 1}', root_type="dictionary")
    assert result.args[0] == {"a": 1}


def test_execute_any_root():
    result = YacunpConvertJSON.execute(json='"hello"', root_type="any")
    assert result.args[0] == "hello"


def test_execute_root_mismatch_raises():
    with pytest.raises(errors.YacunpError):
        YacunpConvertJSON.execute(json='{"a": 1}', root_type="list")


def test_execute_boolean_not_int():
    with pytest.raises(errors.YacunpError):
        YacunpConvertJSON.execute(json="true", root_type="int")


def test_execute_invalid_json_raises():
    with pytest.raises(errors.YacunpError):
        YacunpConvertJSON.execute(json="{bad}", root_type="any")
