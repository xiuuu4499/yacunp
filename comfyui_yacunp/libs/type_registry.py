"""The YACUNP type registry — the single source of truth for every supported
ComfyUI data type.

Each supported type id maps to a :class:`TypeSpec` describing:

* ``io_factory`` — builds the ``io.*.Input`` used as a value slot / DynamicCombo
  sub-input for that type,
* ``has_widget`` — whether values are entered via a manual widget (scalars) or
  only via a connection,
* ``to_jsonable`` / ``from_jsonable`` — canonical JSON-safe conversion and its
  inverse (where meaningful),
* ``to_text`` — canonical string form used by text formatting.

Everything else in the pack (Make KV Pair options, JSON encoding, text
formatting) consumes this registry, so adding a new type only requires editing
this file.

Tensor-backed / opaque types (IMAGE, LATENT, MODEL, ...) cannot be serialized
losslessly; they are represented as a **descriptor** dict of the form
``{"__type__": "IMAGE", "shape": [...], "dtype": "..."}`` (decision D1).
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import errors
from .custom_types import YacunpDictionary, YacunpKVPair

ANY = "ANY"


# --------------------------------------------------------------------------- #
# Descriptor + recursive object conversion helpers
# --------------------------------------------------------------------------- #
def _descriptor(type_id: str, value: Any) -> dict[str, Any]:
    """Build a JSON-safe descriptor for a tensor-backed / opaque value."""
    descriptor: dict[str, Any] = {"__type__": type_id}
    source = value
    if isinstance(value, dict) and "samples" in value:
        source = value["samples"]
    shape = getattr(source, "shape", None)
    if shape is not None:
        try:
            descriptor["shape"] = list(shape)
        except TypeError:
            pass
    dtype = getattr(source, "dtype", None)
    if dtype is not None:
        descriptor["dtype"] = str(dtype)
    return descriptor


def object_to_jsonable(value: Any) -> Any:
    """Recursively convert an arbitrary Python value to a JSON-safe form.

    Used both for the ``ANY`` type and by :mod:`json_codec` when encoding values
    whose declared type is not known ahead of time.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, YacunpKVPair):
        return {
            "key": value.key,
            "type": value.declared_type,
            "value": to_jsonable(value.declared_type, value.value),
        }
    if isinstance(value, YacunpDictionary):
        return {
            key: to_jsonable(pair.declared_type, pair.value)
            for key, pair in value.items.items()
        }
    if isinstance(value, dict):
        return {str(key): object_to_jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [object_to_jsonable(item) for item in value]
    # Tensor-backed / opaque object: fall back to a descriptor.
    return _descriptor("OBJECT", value)


def _opaque_to_text(type_id: str) -> Callable[[Any], str]:
    def to_text(value: Any) -> str:
        descriptor = _descriptor(type_id, value)
        if "shape" in descriptor:
            return f"{type_id}(shape={descriptor['shape']})"
        return f"<{type_id}>"

    return to_text


# --------------------------------------------------------------------------- #
# io_factory builders (lazily import comfy_api so pure-logic imports are cheap)
# --------------------------------------------------------------------------- #
def _widget_factory(io_attr: str, **defaults: Any) -> Callable[..., Any]:
    def factory(input_id: str, **kwargs: Any) -> Any:
        from comfy_api.latest import io

        return getattr(io, io_attr).Input(input_id, **(defaults | kwargs))

    return factory


def _connection_factory(io_attr: str) -> Callable[..., Any]:
    def factory(input_id: str, **kwargs: Any) -> Any:
        from comfy_api.latest import io

        return getattr(io, io_attr).Input(input_id, **kwargs)

    return factory


def _custom_factory(type_string: str) -> Callable[..., Any]:
    def factory(input_id: str, **kwargs: Any) -> Any:
        from comfy_api.latest import io

        return io.Custom(type_string).Input(input_id, **kwargs)

    return factory


def _any_factory() -> Callable[..., Any]:
    def factory(input_id: str, **kwargs: Any) -> Any:
        from comfy_api.latest import io

        return io.AnyType.Input(input_id, **kwargs)

    return factory


# --------------------------------------------------------------------------- #
# TypeSpec
# --------------------------------------------------------------------------- #
@dataclass
class TypeSpec:
    """Describes how one ComfyUI type is entered, connected and serialized."""

    id: str
    has_widget: bool
    _io_factory: Callable[..., Any]
    _to_jsonable: Callable[[Any], Any]
    _from_jsonable: Callable[[Any], Any]
    _to_text: Callable[[Any], str]

    def io_factory(self, input_id: str = "value", **kwargs: Any) -> Any:
        return self._io_factory(input_id, **kwargs)

    def to_jsonable(self, value: Any) -> Any:
        return self._to_jsonable(value)

    def from_jsonable(self, value: Any) -> Any:
        return self._from_jsonable(value)

    def to_text(self, value: Any) -> str:
        return self._to_text(value)


def _identity(value: Any) -> Any:
    return value


def _to_str(value: Any) -> str:
    return "" if value is None else str(value)


def _bool_text(value: Any) -> str:
    return "true" if value else "false"


def _kvpair_from_jsonable(value: Any) -> Any:
    if isinstance(value, dict) and {"key", "type", "value"} <= set(value):
        declared_type = str(value["type"])
        return YacunpKVPair(
            key=str(value["key"]),
            declared_type=declared_type,
            value=from_jsonable(declared_type, value["value"]),
        )
    return value


# --------------------------------------------------------------------------- #
# Registry construction
# --------------------------------------------------------------------------- #
def _build_registry() -> dict[str, TypeSpec]:
    registry: dict[str, TypeSpec] = {}

    def add(spec: TypeSpec) -> None:
        registry[spec.id] = spec

    # ANY comes first so it is the default option in combos.
    add(
        TypeSpec(
            id=ANY,
            has_widget=False,
            _io_factory=_any_factory(),
            _to_jsonable=object_to_jsonable,
            _from_jsonable=_identity,
            _to_text=_to_str,
        )
    )

    # Scalar widget types.
    add(
        TypeSpec(
            id="STRING",
            has_widget=True,
            _io_factory=_widget_factory("String", default=""),
            _to_jsonable=lambda v: "" if v is None else str(v),
            _from_jsonable=lambda v: "" if v is None else str(v),
            _to_text=_to_str,
        )
    )
    add(
        TypeSpec(
            id="INT",
            has_widget=True,
            _io_factory=_widget_factory("Int", default=0),
            _to_jsonable=lambda v: int(v),
            _from_jsonable=lambda v: int(v),
            _to_text=lambda v: str(int(v)),
        )
    )
    add(
        TypeSpec(
            id="FLOAT",
            has_widget=True,
            _io_factory=_widget_factory("Float", default=0.0),
            _to_jsonable=lambda v: float(v),
            _from_jsonable=lambda v: float(v),
            _to_text=lambda v: repr(float(v)),
        )
    )
    add(
        TypeSpec(
            id="BOOLEAN",
            has_widget=True,
            _io_factory=_widget_factory("Boolean", default=False),
            _to_jsonable=lambda v: bool(v),
            _from_jsonable=lambda v: bool(v),
            _to_text=_bool_text,
        )
    )

    # Container / recursively-serializable types.
    add(
        TypeSpec(
            id="DICT",
            has_widget=False,
            _io_factory=_connection_factory("Dict"),
            _to_jsonable=object_to_jsonable,
            _from_jsonable=lambda v: dict(v) if isinstance(v, dict) else v,
            _to_text=lambda v: _compact_json(object_to_jsonable(v)),
        )
    )
    add(
        TypeSpec(
            id="ARRAY",
            has_widget=False,
            _io_factory=_connection_factory("Array"),
            _to_jsonable=object_to_jsonable,
            _from_jsonable=lambda v: list(v) if isinstance(v, (list, tuple)) else v,
            _to_text=lambda v: _compact_json(object_to_jsonable(v)),
        )
    )
    add(
        TypeSpec(
            id="YACUNP_KVPAIR",
            has_widget=False,
            _io_factory=_custom_factory("YACUNP_KVPAIR"),
            _to_jsonable=object_to_jsonable,
            _from_jsonable=_kvpair_from_jsonable,
            _to_text=lambda v: _compact_json(object_to_jsonable(v)),
        )
    )
    add(
        TypeSpec(
            id="YACUNP_DICTIONARY",
            has_widget=False,
            _io_factory=_custom_factory("YACUNP_DICTIONARY"),
            _to_jsonable=object_to_jsonable,
            _from_jsonable=_identity,
            _to_text=lambda v: _compact_json(object_to_jsonable(v)),
        )
    )

    # Tensor-backed / opaque types -> descriptor dict (decision D1).
    opaque_types = [
        ("IMAGE", "Image"),
        ("MASK", "Mask"),
        ("LATENT", "Latent"),
        ("CONDITIONING", "Conditioning"),
        ("MODEL", "Model"),
        ("CLIP", "Clip"),
        ("VAE", "Vae"),
        ("CONTROL_NET", "ControlNet"),
        ("CLIP_VISION", "ClipVision"),
        ("CLIP_VISION_OUTPUT", "ClipVisionOutput"),
        ("STYLE_MODEL", "StyleModel"),
        ("GLIGEN", "Gligen"),
        ("UPSCALE_MODEL", "UpscaleModel"),
        ("AUDIO", "Audio"),
        ("VIDEO", "Video"),
        ("SIGMAS", "Sigmas"),
        ("NOISE", "Noise"),
        ("SAMPLER", "Sampler"),
        ("GUIDER", "Guider"),
        ("LORA_MODEL", "LoraModel"),
        ("MESH", "Mesh"),
        ("VOXEL", "Voxel"),
        ("SVG", "SVG"),
        ("POINT", "Point"),
        ("BBOX", "BBOX"),
        ("SEGS", "SEGS"),
        ("HOOKS", "Hooks"),
    ]
    for type_id, io_attr in opaque_types:
        add(
            TypeSpec(
                id=type_id,
                has_widget=False,
                _io_factory=_connection_factory(io_attr),
                _to_jsonable=(lambda tid: lambda v: _descriptor(tid, v))(type_id),
                _from_jsonable=_identity,
                _to_text=_opaque_to_text(type_id),
            )
        )

    return registry


def _compact_json(jsonable: Any) -> str:
    import json

    return json.dumps(jsonable, ensure_ascii=False, separators=(",", ":"))


_REGISTRY: dict[str, TypeSpec] = _build_registry()


# --------------------------------------------------------------------------- #
# Public helpers
# --------------------------------------------------------------------------- #
def type_ids() -> list[str]:
    """Return all supported type ids, in registration (UX) order."""
    return list(_REGISTRY.keys())


def spec(type_id: str) -> TypeSpec:
    try:
        return _REGISTRY[type_id]
    except KeyError:
        raise errors.unknown_type(type_id) from None


def check_type(declared: str, requested: str) -> None:
    """Raise :class:`errors.YacunpError` if ``declared`` is incompatible with
    ``requested``. ``ANY`` on either side matches everything."""
    if requested == ANY or declared == ANY or declared == requested:
        return
    raise errors.type_mismatch(declared, requested)


def to_jsonable(type_id: str, value: Any) -> Any:
    return spec(type_id).to_jsonable(value)


def from_jsonable(type_id: str, value: Any) -> Any:
    return spec(type_id).from_jsonable(value)


def _literal_type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "dictionary"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if value is None:
        return "null"
    return type(value).__name__


def _literal_mismatch(type_id: str, expected: str, value: Any) -> errors.YacunpError:
    return errors.YacunpError(
        f"Literal for '{type_id}' must decode to {expected}; "
        f"got {_literal_type_name(value)}."
    )


def _convert_literal_value(type_id: str, value: Any) -> Any:
    """Convert an already-decoded JSON value to a registry runtime value."""
    spec(type_id)
    if type_id == ANY:
        return value
    if type_id == "STRING":
        if not isinstance(value, str):
            raise _literal_mismatch(type_id, "a string", value)
        return value
    if type_id == "INT":
        if isinstance(value, bool) or not isinstance(value, int):
            raise _literal_mismatch(type_id, "an integer", value)
        return value
    if type_id == "FLOAT":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise _literal_mismatch(type_id, "a number", value)
        return float(value)
    if type_id == "BOOLEAN":
        if not isinstance(value, bool):
            raise _literal_mismatch(type_id, "a boolean", value)
        return value
    if type_id == "DICT":
        if not isinstance(value, dict):
            raise _literal_mismatch(type_id, "a JSON object", value)
        return value
    if type_id == "ARRAY":
        if not isinstance(value, list):
            raise _literal_mismatch(type_id, "a JSON array", value)
        return value
    if type_id == "YACUNP_KVPAIR":
        if not isinstance(value, dict) or not {"key", "type", "value"} <= value.keys():
            raise errors.YacunpError(
                "Literal for 'YACUNP_KVPAIR' must be an object containing "
                "'key', 'type', and 'value'."
            )
        declared_type = str(value["type"])
        return YacunpKVPair(
            key=str(value["key"]),
            declared_type=declared_type,
            value=_convert_literal_value(declared_type, value["value"]),
        )
    if type_id == "YACUNP_DICTIONARY":
        if not isinstance(value, dict):
            raise _literal_mismatch(type_id, "a JSON object", value)
        items: OrderedDict[str, YacunpKVPair] = OrderedDict()
        for key, raw_value in value.items():
            if (
                isinstance(raw_value, dict)
                and "type" in raw_value
                and "value" in raw_value
            ):
                declared_type = str(raw_value["type"])
                converted = _convert_literal_value(declared_type, raw_value["value"])
            else:
                declared_type = ANY
                converted = raw_value
            pair_key = str(key)
            items[pair_key] = YacunpKVPair(pair_key, declared_type, converted)
        return YacunpDictionary(items)
    raise errors.YacunpError(
        f"Type '{type_id}' requires a connected value; it cannot be created from text."
    )


def from_text(type_id: str, text: str) -> Any:
    """Parse a Make KV Pair literal for ``type_id``.

    STRING consumes the text verbatim. Other supported literal types use JSON
    syntax so booleans, numbers, arrays, dictionaries, and null are unambiguous.
    Opaque ComfyUI runtime types require a connected value.
    """
    spec(type_id)
    if type_id == "STRING":
        return str(text)

    from . import json_codec

    decoded = json_codec.decode(str(text))
    return _convert_literal_value(type_id, decoded)


def to_text(type_id: str, value: Any) -> str:
    return spec(type_id).to_text(value)
