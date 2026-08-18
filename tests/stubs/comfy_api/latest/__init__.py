"""Permissive stand-in for ``comfy_api.latest``.

Provides just enough of the V3 ``io`` surface (plus ``ComfyExtension``/``ui``)
for the YACUNP node modules to import and for ``define_schema()`` to run. Every
input/output factory is a no-op that records its arguments; unknown type names
are generated on demand so the registry can reference any ComfyUI type.
"""

from __future__ import annotations

from typing import Any


class _Slot:
    """Records an input/output slot definition."""

    def __init__(self, slot_id: Any = None, **kwargs: Any) -> None:
        self.id = slot_id
        self.kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"Slot(id={self.id!r})"


class _IOType:
    """A generic ComfyUI type exposing ``Input``/``Output`` factories."""

    def __init__(self, name: str) -> None:
        self._name = name

    def Input(self, slot_id: Any = None, **kwargs: Any) -> _Slot:
        return _Slot(slot_id, **kwargs)

    def Output(self, slot_id: Any = None, **kwargs: Any) -> _Slot:
        return _Slot(slot_id, **kwargs)


def _custom(type_string: str) -> _IOType:
    return _IOType(type_string)


class _DynamicCombo:
    Type = dict

    @staticmethod
    def Input(slot_id: Any = None, options: Any = None, **kwargs: Any) -> _Slot:
        return _Slot(slot_id, options=options, **kwargs)

    @staticmethod
    def Option(name: str, inputs: Any) -> dict:
        return {"name": name, "inputs": inputs}


class _Autogrow:
    Type = dict

    @staticmethod
    def Input(slot_id: Any = None, template: Any = None, **kwargs: Any) -> _Slot:
        return _Slot(slot_id, template=template, **kwargs)

    @staticmethod
    def TemplatePrefix(
        input: Any = None, prefix: str = "", min: int = 1, max: int = 10, **kwargs: Any
    ) -> dict:
        return {"input": input, "prefix": prefix, "min": min, "max": max}

    @staticmethod
    def TemplateNames(
        input: Any = None, names: Any = None, min: int = 1, **kwargs: Any
    ) -> dict:
        return {"input": input, "names": names, "min": min}


class _MultiType:
    @staticmethod
    def Input(slot_id: Any = None, types: Any = None, **kwargs: Any) -> _Slot:
        return _Slot(slot_id, types=types, **kwargs)


class Schema:
    def __init__(
        self,
        node_id: str = None,
        display_name: str = None,
        category: str = None,
        description: str = None,
        inputs: Any = None,
        outputs: Any = None,
        hidden: Any = None,
        **kwargs: Any,
    ) -> None:
        self.node_id = node_id
        self.display_name = display_name
        self.category = category
        self.description = description
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.hidden = hidden or []
        for key, value in kwargs.items():
            setattr(self, key, value)


class NodeOutput:
    def __init__(
        self,
        *args: Any,
        ui: Any = None,
        block_execution: Any = None,
        expand: Any = None,
        **kwargs: Any,
    ) -> None:
        self.args = args
        self.ui = ui
        self.block_execution = block_execution
        self.expand = expand
        self.kwargs = kwargs

    def __iter__(self):
        return iter(self.args)

    def __getitem__(self, index: int) -> Any:
        return self.args[index]

    def __len__(self) -> int:
        return len(self.args)


class ComfyNode:
    """Base class for V3 nodes (no behaviour needed for tests)."""


class _IONamespace:
    Schema = Schema
    NodeOutput = NodeOutput
    ComfyNode = ComfyNode
    Custom = staticmethod(_custom)
    DynamicCombo = _DynamicCombo
    Autogrow = _Autogrow
    MultiType = _MultiType
    String = _IOType("STRING")
    Int = _IOType("INT")
    Float = _IOType("FLOAT")
    Boolean = _IOType("BOOLEAN")
    Combo = _IOType("COMBO")
    AnyType = _IOType("ANY")

    def __getattr__(self, name: str) -> _IOType:
        generated = _IOType(name.upper())
        setattr(self, name, generated)
        return generated


io = _IONamespace()


class ComfyExtension:
    async def get_node_list(self) -> list:  # pragma: no cover - overridden
        return []

    async def on_load(self) -> None:  # pragma: no cover - overridden
        return None


class _UINamespace:
    def __getattr__(self, name: str) -> Any:
        def _factory(*args: Any, **kwargs: Any) -> dict:
            return {"ui": name, "args": args, "kwargs": kwargs}

        return _factory


ui = _UINamespace()
