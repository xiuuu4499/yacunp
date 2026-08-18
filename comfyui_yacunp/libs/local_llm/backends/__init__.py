"""Backend dispatch for local LLM inference.

Each backend module exposes ``load(resolved, load_args)``,
``generate(model, system, prompt, images, gen_args)`` and ``unload(model)``.
Backends import their heavy dependencies lazily so importing this package never
requires ``llama_cpp`` or network access.
"""

from __future__ import annotations

from ... import errors

_BACKENDS = {"llama_cpp", "lmstudio"}


def get_backend(backend_id: str):
    if backend_id == "llama_cpp":
        from . import llama_cpp

        return llama_cpp
    if backend_id == "lmstudio":
        from . import lmstudio

        return lmstudio
    raise errors.YacunpError(
        f"Unknown LLM backend '{backend_id}'. Supported: {sorted(_BACKENDS)}."
    )
