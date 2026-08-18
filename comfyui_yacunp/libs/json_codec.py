"""JSON encode/decode built on top of :mod:`type_registry`.

Encoding accepts arbitrary Python values (including :class:`YacunpKVPair` /
:class:`YacunpDictionary` payloads and tensor-backed values) and turns them into
a pretty-printed or single-line JSON string. Decoding parses JSON text back into
plain nested Python structures.
"""

from __future__ import annotations

import json
from typing import Any

from . import errors, type_registry

PRETTY = "pretty"
SINGLE_LINE = "single_line"
STYLES = (PRETTY, SINGLE_LINE)


def to_jsonable(value: Any) -> Any:
    """Convert an arbitrary value into a JSON-safe structure via the registry."""
    return type_registry.object_to_jsonable(value)


def encode(value: Any, style: str = PRETTY) -> str:
    """Encode ``value`` as a JSON string.

    ``style`` is either ``"pretty"`` (2-space indented) or ``"single_line"``.
    Output is always properly escaped by :func:`json.dumps`.
    """
    jsonable = to_jsonable(value)
    if style == PRETTY:
        return json.dumps(jsonable, ensure_ascii=False, indent=2, sort_keys=False)
    if style == SINGLE_LINE:
        return json.dumps(
            jsonable, ensure_ascii=False, separators=(", ", ": "), sort_keys=False
        )
    raise errors.YacunpError(
        f"Unknown JSON style '{style}'. Expected one of {', '.join(STYLES)}."
    )


def decode(text: str) -> Any:
    """Parse JSON ``text`` into nested Python data, raising ``YacunpError``."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise errors.invalid_json(str(exc)) from exc
