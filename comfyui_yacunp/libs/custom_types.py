"""Custom ComfyUI types and payload dataclasses for YACUNP.

The ``io.Custom`` handles below register the two opaque wire types used by the
Dictionary category, while the dataclasses are the plain-Python payloads that
travel across node connections (and that the tests exercise directly).
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

from comfy_api.latest import io

# Custom wire types. The UPPER_SNAKE strings are the stable io_type ids.
KVPairType = io.Custom("YACUNP_KVPAIR")
DictionaryType = io.Custom("YACUNP_DICTIONARY")
LLMModelType = io.Custom("YACUNP_LLM_MODEL")


@dataclass
class YacunpKVPair:
    """A single key/value pair that remembers the declared ComfyUI type."""

    key: str
    declared_type: str
    value: Any


@dataclass
class YacunpDictionary:
    """An ordered collection of :class:`YacunpKVPair` keyed by pair key."""

    items: OrderedDict[str, YacunpKVPair] = field(default_factory=OrderedDict)


@dataclass
class YacunpLLMModel:
    """A handle to a loaded local LLM, passed between Local LLM nodes.

    ``handle`` is a live backend object (e.g. a ``llama_cpp.Llama`` instance or
    an LM Studio client descriptor) and is deliberately never serialized.
    """

    backend: str
    name: str
    handle: Any = None
    config: dict[str, Any] = field(default_factory=dict)
    multimodal: bool = False
