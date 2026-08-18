"""Test for the Format JSON node."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.libs import errors, json_codec
from yacunp.comfyui_yacunp.nodes.json.format_json import YacunpFormatJSON


def test_execute_single_line():
    result = YacunpFormatJSON.execute(
        json='{\n  "a": 1\n}', format=json_codec.SINGLE_LINE
    )
    assert result.args[0] == '{"a": 1}'


def test_execute_pretty():
    result = YacunpFormatJSON.execute(json='{"a":1}', format=json_codec.PRETTY)
    assert "\n" in result.args[0]


def test_execute_invalid_json_raises():
    with pytest.raises(errors.YacunpError):
        YacunpFormatJSON.execute(json="{bad}", format=json_codec.PRETTY)
