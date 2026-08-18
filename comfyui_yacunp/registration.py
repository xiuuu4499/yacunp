"""Central registration: collect every node class from the category packages.

Each category package exposes a ``NODES`` list; :func:`all_nodes` concatenates
them into the flat list consumed by the V3 ``ComfyExtension``.
"""

from __future__ import annotations

from .nodes.dictionary import NODES as DICTIONARY_NODES
from .nodes.io import NODES as IO_NODES
from .nodes.json import NODES as JSON_NODES
from .nodes.local_llm import NODES as LOCAL_LLM_NODES

_CATEGORY_NODES = [
    DICTIONARY_NODES,
    JSON_NODES,
    LOCAL_LLM_NODES,
    IO_NODES,
]


def all_nodes() -> list:
    """Return every registered node class across all categories."""
    nodes: list = []
    for group in _CATEGORY_NODES:
        nodes.extend(group)
    return nodes
