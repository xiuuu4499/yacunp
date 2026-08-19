"""Tests for LLM argument specs and dictionary conversions."""

from __future__ import annotations

from yacunp.comfyui_yacunp.libs.custom_types import YacunpDictionary
from yacunp.comfyui_yacunp.libs.local_llm import args
from yacunp.comfyui_yacunp.nodes.local_llm.make_basic_llm_arguments import (
    YacunpMakeBasicLLMArguments,
)


def test_specs_have_descriptions():
    for spec in args.BASIC_ARG_SPECS + args.ADVANCED_ARG_SPECS:
        assert spec["description"].strip()
        assert spec["type"] in {"INT", "FLOAT", "BOOLEAN", "STRING"}


def test_build_arguments_uses_defaults_and_coerces():
    result = args.build_arguments(args.BASIC_ARG_SPECS, {"max_tokens": "256"})
    assert isinstance(result, YacunpDictionary)
    assert result.items["max_tokens"].value == 256
    assert result.items["max_tokens"].declared_type == "INT"
    # Unspecified value falls back to the spec default (temperature 0.7).
    assert result.items["temperature"].value == 0.7


def test_advanced_arguments_use_stop_sequence():
    result = args.build_arguments(args.ADVANCED_ARG_SPECS, {"stop_sequence": "</end>"})
    assert result.items["stop_sequence"].value == "</end>"
    assert "stop" not in result.items


def test_basic_seed_disables_control_after_generate():
    seed_spec = next(spec for spec in args.BASIC_ARG_SPECS if spec["name"] == "seed")
    assert seed_spec["io"]["control_after_generate"] is False
    assert "control_after_generate" not in {
        spec["name"] for spec in args.BASIC_ARG_SPECS
    }
    seed_input = next(
        slot for slot in YacunpMakeBasicLLMArguments.define_schema().inputs if slot.id == "seed"
    )
    assert seed_input.kwargs["control_after_generate"] is False


def test_plain_to_dictionary_infers_types():
    result = args.plain_to_dictionary(
        {"i": 1, "f": 1.5, "b": True, "s": "x", "l": [1], "d": {}}
    )
    assert result.items["i"].declared_type == "INT"
    assert result.items["f"].declared_type == "FLOAT"
    assert result.items["b"].declared_type == "BOOLEAN"
    assert result.items["s"].declared_type == "STRING"
    assert result.items["l"].declared_type == "ARRAY"
    assert result.items["d"].declared_type == "DICT"


def test_dictionary_to_plain_roundtrip():
    built = args.build_arguments(args.BASIC_ARG_SPECS, {"seed": 5})
    plain = args.dictionary_to_plain(built)
    assert plain["seed"] == 5
    assert "temperature" in plain


def test_dictionary_to_plain_none_is_empty():
    assert args.dictionary_to_plain(None) == {}
