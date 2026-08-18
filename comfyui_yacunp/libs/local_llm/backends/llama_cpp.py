"""llama.cpp (GGUF) backend -- local only, no downloads.

All heavy imports (``llama_cpp``, ``torch``) happen inside functions so this
module imports cleanly in environments without them. Models are referenced by an
absolute filesystem path; nothing here ever downloads a model.
"""

from __future__ import annotations

import os
from typing import Any

from ... import errors
from ...custom_types import YacunpLLMModel
from .. import config


def _require_llama():
    try:
        from llama_cpp import Llama
    except Exception as exc:  # pragma: no cover - depends on optional install
        raise errors.YacunpError(
            "The llama.cpp backend requires 'llama-cpp-python'. Install it into "
            "your ComfyUI environment (pip install llama-cpp-python), using a "
            "vision-capable build if you need multimodal models."
        ) from exc
    return Llama


def _resolve_path(path: str | None, kind: str) -> str:
    if not path:
        raise errors.YacunpError(f"Model entry is missing a '{kind}' path.")
    if not os.path.isabs(path):
        # Resolve ComfyUI-relative paths when running inside ComfyUI.
        try:
            import folder_paths  # type: ignore

            base = getattr(folder_paths, "models_dir", None) or getattr(
                folder_paths, "base_path", ""
            )
            candidate = os.path.join(base, path) if base else path
        except Exception:
            candidate = path
    else:
        candidate = path
    if not os.path.isfile(candidate):
        raise errors.YacunpError(
            f"Local model file not found ({kind}): '{candidate}'. "
            "No automatic download is performed -- place the file locally and "
            "point local_models.json at it."
        )
    return candidate


def load(resolved: config.ResolvedModel, load_args: dict[str, Any]) -> YacunpLLMModel:
    Llama = _require_llama()
    model_path = _resolve_path(resolved.path, "path")

    kwargs: dict[str, Any] = {"model_path": model_path, "verbose": False}
    if load_args.get("n_ctx"):
        kwargs["n_ctx"] = int(load_args["n_ctx"])
    if "n_gpu_layers" in load_args:
        kwargs["n_gpu_layers"] = int(load_args["n_gpu_layers"])
    if load_args.get("n_batch"):
        kwargs["n_batch"] = int(load_args["n_batch"])
    if load_args.get("n_threads"):
        kwargs["n_threads"] = int(load_args["n_threads"])
    if load_args.get("flash_attn"):
        kwargs["flash_attn"] = bool(load_args["flash_attn"])

    chat_handler = None
    if resolved.multimodal and resolved.mmproj:
        mmproj_path = _resolve_path(resolved.mmproj, "mmproj")
        chat_handler = _build_chat_handler(mmproj_path, load_args, resolved.chat_handler)
        kwargs["chat_handler"] = chat_handler

    handle = Llama(**kwargs)
    meta = {"path": model_path}
    try:
        meta["n_ctx"] = int(handle.n_ctx())
    except Exception:  # pragma: no cover - backend detail
        pass
    return YacunpLLMModel(
        backend="llama_cpp",
        name=resolved.key,
        handle=handle,
        config={**meta, "mmproj": resolved.mmproj if resolved.multimodal else None},
        multimodal=bool(resolved.multimodal and resolved.mmproj),
    )


_MULTIMODAL_CHAT_HANDLERS = ("Qwen3VLChatHandler", "Qwen25VLChatHandler", "Llava15ChatHandler")


def _build_chat_handler(mmproj_path: str, load_args: dict[str, Any], handler_name: str | None = None):  # pragma: no cover
    from llama_cpp import llama_chat_format

    if handler_name:
        handler_cls = getattr(llama_chat_format, handler_name, None)
        if handler_cls is None:
            raise errors.YacunpError(
                f"Chat handler '{handler_name}' is not available in this llama-cpp-python build. "
                f"Known handlers in this build: "
                + ", ".join(
                    n for n in _MULTIMODAL_CHAT_HANDLERS if getattr(llama_chat_format, n, None) is not None
                )
                + ". Install a compatible vision-capable build or correct 'chat_handler' in your catalog."
            )
    else:
        raise errors.YacunpError(
            "Multimodal llama.cpp models require a 'chat_handler' field in the catalog entry. "
            f"Set it to one of: {', '.join(_MULTIMODAL_CHAT_HANDLERS)} (whichever matches your model architecture)."
        )
    kwargs: dict[str, Any] = {"clip_model_path": mmproj_path, "verbose": False}
    if load_args.get("image_max_tokens"):
        kwargs["image_max_tokens"] = int(load_args["image_max_tokens"])
    return handler_cls(**kwargs)


def _build_messages(system: str, prompt: str, images: list[str]):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    if images:
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for url in images:
            content.append({"type": "image_url", "image_url": {"url": url}})
        messages.append({"role": "user", "content": content})
    else:
        messages.append({"role": "user", "content": prompt})
    return messages


def generate(
    model: YacunpLLMModel,
    system: str,
    prompt: str,
    images: list[str],
    gen_args: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    if model.handle is None:
        raise errors.YacunpError("The llama.cpp model is not loaded.")
    if images and not model.multimodal:
        raise errors.YacunpError(
            f"Model '{model.name}' has no mmproj/vision support but images were "
            "provided. Configure it as multimodal or remove the image input."
        )

    call: dict[str, Any] = {"messages": _build_messages(system, prompt, images)}
    if gen_args.get("max_tokens"):
        call["max_tokens"] = int(gen_args["max_tokens"])
    if "temperature" in gen_args:
        call["temperature"] = float(gen_args["temperature"])
    if "top_p" in gen_args:
        call["top_p"] = float(gen_args["top_p"])
    if "top_k" in gen_args:
        call["top_k"] = int(gen_args["top_k"])
    if "min_p" in gen_args:
        call["min_p"] = float(gen_args["min_p"])
    if "repeat_penalty" in gen_args:
        call["repeat_penalty"] = float(gen_args["repeat_penalty"])
    if "presence_penalty" in gen_args:
        call["presence_penalty"] = float(gen_args["presence_penalty"])
    if "frequency_penalty" in gen_args:
        call["frequency_penalty"] = float(gen_args["frequency_penalty"])
    if gen_args.get("seed") not in (None, 0):
        call["seed"] = int(gen_args["seed"])
    if gen_args.get("stop"):
        call["stop"] = [str(gen_args["stop"])]

    result = model.handle.create_chat_completion(**call)
    choice = (result.get("choices") or [{}])[0]
    text = (choice.get("message") or {}).get("content") or ""
    info = {
        "backend": "llama_cpp",
        "model": model.name,
        "finish_reason": choice.get("finish_reason"),
    }
    usage = result.get("usage") or {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        if key in usage:
            info[key] = usage[key]
    return text, info


def unload(model: YacunpLLMModel) -> None:
    handle = model.handle
    model.handle = None
    if handle is not None:
        close = getattr(handle, "close", None)
        if callable(close):
            try:
                close()
            except Exception:  # pragma: no cover - backend detail
                pass
    del handle
