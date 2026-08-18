"""In-process resource cache for loaded LLM handles.

Both loader nodes register their model objects here so that the Unload
Model node can explicitly invalidate the entry instead of relying on
object mutation (``handle = None``) that would be missed when ComfyUI
replays a cached output from a previous queue run.

Usage pattern
-------------
Load node (execute)::

    from . import resource_cache
    model = backend.load(...)
    resource_cache.put(cache_key, model)

Load node (is_changed)::

    from . import resource_cache
    return float("nan") if not resource_cache.is_live(cache_key) else cache_key

Unload node (execute)::

    from . import resource_cache
    if model.cache_key:
        resource_cache.invalidate(model.cache_key)
"""

from __future__ import annotations

from typing import Any

_cache: dict[str, Any] = {}


def put(key: str, model: Any) -> Any:
    """Register *model* under *key* and return it."""
    _cache[key] = model
    return model


def get(key: str) -> Any | None:
    """Return the cached model for *key*, or ``None`` if absent."""
    return _cache.get(key)


def is_live(key: str) -> bool:
    """Return ``True`` if *key* maps to a model with a non-``None`` handle."""
    model = _cache.get(key)
    return model is not None and getattr(model, "handle", None) is not None


def invalidate(key: str) -> None:
    """Remove *key* from the cache (no-op if absent)."""
    _cache.pop(key, None)
