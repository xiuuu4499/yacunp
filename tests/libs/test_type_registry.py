"""Tests for the shared type registry."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.libs import errors, type_registry
from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary, YacunpKVPair


def test_type_ids_include_core_types():
    ids = type_registry.type_ids()
    for expected in ("ANY", "STRING", "INT", "FLOAT", "BOOLEAN", "IMAGE"):
        assert expected in ids
    assert ids[0] == "ANY"  # ANY is first for UX


def test_has_widget_only_for_scalars():
    for scalar in ("STRING", "INT", "FLOAT", "BOOLEAN"):
        assert type_registry.spec(scalar).has_widget is True
    for non_scalar in ("ANY", "IMAGE", "DICT", "YACUNP_KVPAIR"):
        assert type_registry.spec(non_scalar).has_widget is False


def test_io_factory_uses_slot_id():
    slot = type_registry.spec("STRING").io_factory("value")
    assert slot.id == "value"


def test_io_factory_passes_input_options():
    slot = type_registry.spec("STRING").io_factory(
        "value", optional=True, force_input=True
    )
    assert slot.optional is True
    assert slot.force_input is True


@pytest.mark.parametrize(
    ("type_id", "value", "expected"),
    [
        ("STRING", "hi", "hi"),
        ("INT", 5, 5),
        ("FLOAT", 1.5, 1.5),
        ("BOOLEAN", True, True),
    ],
)
def test_scalar_jsonable_roundtrip(type_id, value, expected):
    spec = type_registry.spec(type_id)
    jsonable = spec.to_jsonable(value)
    assert jsonable == expected
    assert spec.from_jsonable(jsonable) == expected


def test_int_jsonable_coerces_numeric_string():
    assert type_registry.to_jsonable("INT", "7") == 7


def test_to_text_variants():
    assert type_registry.to_text("STRING", "abc") == "abc"
    assert type_registry.to_text("INT", 3) == "3"
    assert type_registry.to_text("BOOLEAN", False) == "false"
    assert type_registry.to_text("BOOLEAN", True) == "true"


def test_opaque_type_descriptor():
    class FakeTensor:
        shape = (1, 512, 512, 3)
        dtype = "float32"

    descriptor = type_registry.to_jsonable("IMAGE", FakeTensor())
    assert descriptor == {
        "__type__": "IMAGE",
        "shape": [1, 512, 512, 3],
        "dtype": "float32",
    }
    text = type_registry.to_text("IMAGE", FakeTensor())
    assert "IMAGE(shape=" in text


def test_kvpair_jsonable_and_roundtrip():
    pair = YacunpKVPair(key="name", declared_type="STRING", value="Ada")
    jsonable = type_registry.to_jsonable("YACUNP_KVPAIR", pair)
    assert jsonable == {"key": "name", "type": "STRING", "value": "Ada"}
    restored = type_registry.from_jsonable("YACUNP_KVPAIR", jsonable)
    assert isinstance(restored, YacunpKVPair)
    assert restored.key == "name"
    assert restored.declared_type == "STRING"
    assert restored.value == "Ada"


def test_check_type_ok_and_any():
    type_registry.check_type("STRING", "STRING")
    type_registry.check_type("STRING", "ANY")
    type_registry.check_type("ANY", "IMAGE")


def test_check_type_mismatch_raises():
    with pytest.raises(errors.YacunpError):
        type_registry.check_type("STRING", "INT")


def test_unknown_type_raises():
    with pytest.raises(errors.YacunpError):
        type_registry.spec("NOT_A_TYPE")


def test_from_text_builds_typed_dictionary():
    value = type_registry.from_text(
        "YACUNP_DICTIONARY",
        '{"count": {"type": "INT", "value": 2}, "name": "Ada"}',
    )
    assert isinstance(value, YacunpDictionary)
    assert value.items["count"].declared_type == "INT"
    assert value.items["count"].value == 2
    assert value.items["name"].declared_type == "ANY"


def test_from_text_rejects_opaque_type():
    with pytest.raises(errors.YacunpError, match="requires a connected value"):
        type_registry.from_text("MODEL", '"model.safetensors"')
