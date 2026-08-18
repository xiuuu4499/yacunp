"""YACUNP — Yet Another ComfyUI Node Pack.

V3 entry point: expose every registered node through a :class:`ComfyExtension`.
"""

from __future__ import annotations

from comfy_api.latest import ComfyExtension, io
from typing_extensions import override

from .comfyui_yacunp.registration import all_nodes


class YacunpExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return all_nodes()


async def comfy_entrypoint() -> YacunpExtension:
    return YacunpExtension()
