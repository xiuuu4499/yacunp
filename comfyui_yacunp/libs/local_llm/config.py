"""Local model catalog: parse ``local_models.json`` and resolve entries.

The catalog is user-supplied and never contains download instructions -- every
model is referenced by an absolute (or ComfyUI-relative) filesystem path or, for
LM Studio, by the identifier the server already exposes. If the real
``local_models.json`` is missing we transparently fall back to the committed
``local_models.example.json`` so the nodes still load with usable examples.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from .. import errors

# Package root: comfyui_yacunp/ (three levels up from this file:
# libs/local_llm/config.py -> libs/local_llm -> libs -> comfyui_yacunp).
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_FILENAME = "local_models.json"
EXAMPLE_FILENAME = "local_models.example.json"
CONFIG_PATH = os.path.join(_PACKAGE_ROOT, CONFIG_FILENAME)
EXAMPLE_PATH = os.path.join(_PACKAGE_ROOT, EXAMPLE_FILENAME)

# Which argument keys apply when the model is constructed vs. per generation.
LOAD_KEYS = frozenset(
    {"n_ctx", "n_gpu_layers", "n_batch", "n_threads", "flash_attn", "image_max_tokens"}
)
GEN_KEYS = frozenset(
    {
        "max_tokens",
        "temperature",
        "top_p",
        "top_k",
        "min_p",
        "seed",
        "repeat_penalty",
        "presence_penalty",
        "frequency_penalty",
        "stop",
    }
)


@dataclass
class ResolvedModel:
    key: str
    backend: str
    path: str | None
    mmproj: str | None
    multimodal: bool
    defaults: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


def config_source() -> str:
    """Return the path the catalog is (or would be) loaded from."""
    return CONFIG_PATH if os.path.isfile(CONFIG_PATH) else EXAMPLE_PATH


def load_catalog(path: str | None = None) -> dict[str, Any]:
    """Load and parse the catalog, falling back to the example file.

    A missing or empty catalog returns an empty structure rather than raising,
    so schema definition (which runs at import/registration time) never breaks.
    """
    target = path or config_source()
    if not target or not os.path.isfile(target):
        return {"models": {}, "lmstudio": {}}
    try:
        with open(target, encoding="utf-8") as handle:
            data = json.load(handle) or {}
    except (OSError, ValueError) as exc:
        raise errors.YacunpError(f"Could not read '{target}': {exc}") from None
    if not isinstance(data, dict):
        raise errors.YacunpError(f"'{target}' must contain a JSON object.")
    data.setdefault("models", {})
    data.setdefault("lmstudio", {})
    return data


def model_keys(catalog: dict[str, Any], backend: str | None = None) -> list[str]:
    """Return catalog model keys, optionally filtered by backend id."""
    models = catalog.get("models") or {}
    keys = []
    for key, entry in models.items():
        if backend is None or (entry or {}).get("backend") == backend:
            keys.append(key)
    return keys


def resolve(catalog: dict[str, Any], key: str) -> ResolvedModel:
    models = catalog.get("models") or {}
    entry = models.get(key)
    if not entry:
        raise errors.YacunpError(
            f"Model '{key}' is not defined in {CONFIG_FILENAME}. "
            f"Add it there (see {EXAMPLE_FILENAME})."
        )
    known = {"backend", "path", "mmproj", "multimodal", "defaults"}
    return ResolvedModel(
        key=key,
        backend=str(entry.get("backend") or "llama_cpp"),
        path=entry.get("path"),
        mmproj=entry.get("mmproj"),
        multimodal=bool(entry.get("multimodal", False)),
        defaults=dict(entry.get("defaults") or {}),
        extra={k: v for k, v in entry.items() if k not in known},
    )


def lmstudio_base_url(catalog: dict[str, Any], override: str | None = None) -> str:
    if override:
        return override.rstrip("/")
    section = catalog.get("lmstudio") or {}
    return str(section.get("base_url") or "http://localhost:1234/v1").rstrip("/")


def merge_args(defaults: dict[str, Any], override: dict[str, Any] | None) -> dict[str, Any]:
    """Overlay ``override`` on top of ``defaults`` (override wins)."""
    merged = dict(defaults or {})
    if override:
        for key, value in override.items():
            if value is not None:
                merged[key] = value
    return merged


def split_args(args: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Partition an argument mapping into (load-time, generation-time) dicts."""
    load_args = {k: v for k, v in args.items() if k in LOAD_KEYS}
    gen_args = {k: v for k, v in args.items() if k in GEN_KEYS}
    return load_args, gen_args
