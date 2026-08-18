"""Registration-level tests: every node imports and is well-formed."""

from __future__ import annotations

import pytest
from yacunp.comfyui_yacunp.registration import all_nodes

EXPECTED_NODE_IDS = {
    "YACUNP_MakeKVPair",
    "YACUNP_ReadKVPair",
    "YACUNP_MakeDictionary",
    "YACUNP_GetDictionaryValue",
    "YACUNP_GetDictionaryKeys",
    "YACUNP_FormatTextWithDictionary",
    "YACUNP_SetDictionaryValue",
    "YACUNP_CombineDictionaries",
    "YACUNP_MakeJSON",
    "YACUNP_ConvertJSON",
    "YACUNP_FormatJSON",
    "YACUNP_MakeBasicLLMArguments",
    "YACUNP_MakeAdvancedLLMArguments",
    "YACUNP_LoadModelLlamaCpp",
    "YACUNP_LoadModelLMStudio",
    "YACUNP_SystemPromptPresets",
    "YACUNP_GenerateText",
    "YACUNP_UnloadModel",
}


def test_all_nodes_present():
    assert len(all_nodes()) == len(EXPECTED_NODE_IDS)


def test_node_ids_unique_and_expected():
    ids = [node.define_schema().node_id for node in all_nodes()]
    assert len(ids) == len(set(ids))
    assert set(ids) == EXPECTED_NODE_IDS


@pytest.mark.parametrize("node", all_nodes())
def test_schema_valid(node):
    schema = node.define_schema()
    assert schema.node_id
    assert schema.display_name.endswith("(YACUNP)")
    assert schema.category.startswith("YACUNP/")
    assert schema.outputs


@pytest.mark.parametrize("node", all_nodes())
def test_category_prefixes(node):
    category = node.define_schema().category
    assert category in ("YACUNP/Dictionary", "YACUNP/JSON", "YACUNP/Local LLM")
