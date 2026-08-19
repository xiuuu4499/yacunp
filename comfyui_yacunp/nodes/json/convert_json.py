"""Convert JSON node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs import errors, json_codec

ROOT_TYPES = ["any", "list", "dictionary", "string", "int", "float", "boolean"]

_CHECKS = {
    "list": (list, "list"),
    "dictionary": (dict, "dictionary"),
    "string": (str, "string"),
    "boolean": (bool, "boolean"),
}


def _actual_name(value) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "dictionary"
    if isinstance(value, list):
        return "list"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    return type(value).__name__


def convert_json(text: str, root_type: str):
    value = json_codec.decode(text)
    if root_type == "any":
        return value
    if root_type == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise errors.json_root_mismatch("int", _actual_name(value))
        return value
    if root_type == "float":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise errors.json_root_mismatch("float", _actual_name(value))
        return float(value)
    expected_cls, name = _CHECKS[root_type]
    if not isinstance(value, expected_cls) or (
        name != "boolean" and isinstance(value, bool)
    ):
        raise errors.json_root_mismatch(name, _actual_name(value))
    return value


class YacunpConvertJSON(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_ConvertJSON",
            display_name="Convert JSON",
            category="YACUNP/JSON",
            description="Parse a JSON string into a nested Python value, validating "
            "the top-level type against the selected root type.",
            inputs=[
                io.String.Input("json", multiline=True, default=""),
                io.Combo.Input("root_type", options=ROOT_TYPES),
            ],
            outputs=[io.AnyType.Output("value")],
        )

    @classmethod
    def execute(cls, json, root_type) -> io.NodeOutput:
        return io.NodeOutput(convert_json(str(json), root_type))
