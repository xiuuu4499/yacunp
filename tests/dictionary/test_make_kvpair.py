"""Test for the Make KV Pair node."""

from __future__ import annotations

from yacunp.comfyui_yacunp.libs.custom_types import YacunpKVPair
from yacunp.comfyui_yacunp.nodes.dictionary.make_kvpair import YacunpMakeKVPair


def test_schema_metadata():
    schema = YacunpMakeKVPair.define_schema()
    assert schema.node_id == "YACUNP_MakeKVPair"
    assert schema.category == "YACUNP/Dictionary"


def test_execute_builds_kvpair():
    result = YacunpMakeKVPair.execute(key="name", type={"type": "STRING", "value": "Ada"})
    pair = result.args[0]
    assert isinstance(pair, YacunpKVPair)
    assert pair.key == "name"
    assert pair.declared_type == "STRING"
    assert pair.value == "Ada"


def test_execute_without_value():
    result = YacunpMakeKVPair.execute(key="k", type={"type": "IMAGE"})
    pair = result.args[0]
    assert pair.declared_type == "IMAGE"
    assert pair.value is None
