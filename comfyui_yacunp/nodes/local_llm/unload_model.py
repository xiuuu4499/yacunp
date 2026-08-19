"""Unload Model / VRAM Cleanup node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs.custom_types import DictionaryType, LLMModelType
from ...libs.local_llm import args, backends, resource_cache


def _vram_cleanup() -> dict:
    import gc

    gc.collect()
    info: dict = {"gc_collected": True}
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            info["cuda_cache_cleared"] = True
    except Exception:  # pragma: no cover - torch optional / no CUDA
        pass
    return info


def unload(model=None) -> dict:
    freed = False
    name = None
    if model is not None:
        name = model.name
        if model.cache_key:
            resource_cache.invalidate(model.cache_key)
        backends.get_backend(model.backend).unload(model)
        freed = True
    return {"unloaded": freed, "model": name, **_vram_cleanup()}


class YacunpUnloadModel(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_UnloadModel",
            display_name="Unload Model / VRAM Cleanup",
            category="YACUNP/Local LLM",
            description="Free a loaded model and run a VRAM/RAM cleanup pass "
            "(garbage collection and, if available, CUDA cache clear). Connect the "
            "optional 'signal' input to any upstream output (e.g. the generated "
            "text) to force this to run after generation. Runs as an output node.",
            inputs=[
                LLMModelType.Input("model", optional=True),
                io.AnyType.Input("signal", optional=True),
            ],
            outputs=[DictionaryType.Output("info")],
            is_output_node=True,
        )

    @classmethod
    def execute(cls, model=None, signal=None) -> io.NodeOutput:
        return io.NodeOutput(args.plain_to_dictionary(unload(model)))
