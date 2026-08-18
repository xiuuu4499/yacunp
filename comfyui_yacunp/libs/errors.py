"""Typed runtime errors for the YACUNP node pack.

All node/runtime failures are raised as :class:`YacunpError` so that callers
(and tests) can distinguish expected, user-facing validation problems from
unexpected bugs. The helper functions build consistently worded messages.
"""

from __future__ import annotations


class YacunpError(Exception):
    """Base error for all YACUNP runtime/validation failures."""


def type_mismatch(declared: str, requested: str) -> YacunpError:
    return YacunpError(
        f"Type mismatch: value is declared as '{declared}' "
        f"but '{requested}' was requested."
    )


def unknown_type(type_id: str) -> YacunpError:
    return YacunpError(f"Unknown type id: '{type_id}'.")


def duplicate_key(key: str) -> YacunpError:
    return YacunpError(f"Duplicate key in dictionary: '{key}'.")


def missing_key(key: str) -> YacunpError:
    return YacunpError(f"Key not found in dictionary: '{key}'.")


def invalid_json(detail: str) -> YacunpError:
    return YacunpError(f"Invalid JSON: {detail}")


def json_root_mismatch(expected: str, actual: str) -> YacunpError:
    return YacunpError(
        f"JSON root type mismatch: expected '{expected}' but decoded a '{actual}'."
    )
