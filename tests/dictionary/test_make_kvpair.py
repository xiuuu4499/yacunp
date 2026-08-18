"""Test for the Make KV Pair node."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.libs import errors
from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpKVPair
from yacunp.comfyui_yacunp.nodes.dictionary.make_kvpair import YacunpMakeKVPair


def test_schema_metadata():
    schema = YacunpMakeKVPair.define_schema()
    assert schema.node_id == "YACUNP_MakeKVPair"
    assert schema.category == "YACUNP/Dictionary"


def test_each_type_option_has_optional_socket_and_literal_widget():
    schema = YacunpMakeKVPair.define_schema()
    options = schema.inputs[1].options
    assert options
    for option in options:
        socket, literal = option["inputs"]
        assert socket.id == "value"
        assert socket.optional is True
        assert literal.id == "literal"
        assert literal.socketless is True

    string_socket = next(option for option in options if option["name"] == "STRING")[
        "inputs"
    ][0]
    assert string_socket.force_input is True


def test_execute_builds_kvpair():
    result = YacunpMakeKVPair.execute(key="name", type={"type": "STRING", "value": "Ada"})
    pair = result.args[0]
    assert isinstance(pair, YacunpKVPair)
    assert pair.key == "name"
    assert pair.declared_type == "STRING"
    assert pair.value == "Ada"


@pytest.mark.parametrize(
    ("type_id", "literal", "expected"),
    [
        ("STRING", "Ada", "Ada"),
        ("INT", "42", 42),
        ("FLOAT", "3", 3.0),
        ("BOOLEAN", "true", True),
        ("DICT", '{"answer": 42}', {"answer": 42}),
        ("ARRAY", '[1, "two"]', [1, "two"]),
        ("ANY", '{"nested": [true, null]}', {"nested": [True, None]}),
    ],
)
def test_execute_converts_literal(type_id, literal, expected):
    result = YacunpMakeKVPair.execute(
        key="k", type={"type": type_id, "literal": literal}
    )
    pair = result.args[0]
    assert pair.declared_type == type_id
    assert pair.value == expected


def test_connected_value_takes_precedence_over_literal():
    result = YacunpMakeKVPair.execute(
        key="k", type={"type": "INT", "value": 7, "literal": "not JSON"}
    )
    assert result.args[0].value == 7


def test_execute_converts_kvpair_literal():
    result = YacunpMakeKVPair.execute(
        key="outer",
        type={
            "type": "YACUNP_KVPAIR",
            "literal": '{"key": "inner", "type": "BOOLEAN", "value": true}',
        },
    )
    nested = result.args[0].value
    assert isinstance(nested, YacunpKVPair)
    assert nested.key == "inner"
    assert nested.declared_type == "BOOLEAN"
    assert nested.value is True


def test_execute_converts_dictionary_literal():
    result = YacunpMakeKVPair.execute(
        key="config",
        type={
            "type": "YACUNP_DICTIONARY",
            "literal": (
                '{"count": {"type": "INT", "value": 2}, '
                '"label": "untagged"}'
            ),
        },
    )
    dictionary = result.args[0].value
    assert isinstance(dictionary, YacunpDictionary)
    assert dictionary.items["count"].declared_type == "INT"
    assert dictionary.items["count"].value == 2
    assert dictionary.items["label"].declared_type == "ANY"
    assert dictionary.items["label"].value == "untagged"


@pytest.mark.parametrize(
    ("type_id", "literal", "message"),
    [
        ("INT", "1.5", "must decode to an integer"),
        ("BOOLEAN", '"true"', "must decode to a boolean"),
        ("IMAGE", '"image.png"', "requires a connected value"),
        ("ANY", "not JSON", "Invalid JSON"),
    ],
)
def test_invalid_or_unsupported_literal_raises(type_id, literal, message):
    with pytest.raises(errors.YacunpError, match=message):
        YacunpMakeKVPair.execute(
            key="k", type={"type": type_id, "literal": literal}
        )
