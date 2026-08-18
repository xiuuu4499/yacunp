"""Tests for system prompt presets."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.libs import errors
from yacunp.comfyui_yacunp.libs.local_llm import presets
from yacunp.comfyui_yacunp.nodes.local_llm.system_prompt_presets import (
    resolve_system_prompt,
)


def test_options_are_category_scoped():
    options = presets.options()
    assert options
    assert all(presets.SEPARATOR in option for option in options)


def test_get_resolves_option():
    option = presets.options()[0]
    assert presets.get(option).strip()


def test_get_unknown_raises():
    with pytest.raises(errors.YacunpError):
        presets.get("Nope :: Missing")


def test_resolve_appends_extra_instructions():
    option = presets.options()[0]
    base = presets.get(option)
    combined = resolve_system_prompt(option, "Be terse.", "")
    assert combined.startswith(base)
    assert combined.endswith("Be terse.")


def test_custom_override_replaces_preset():
    option = presets.options()[0]
    result = resolve_system_prompt(option, "", "Only this.")
    assert result == "Only this."
