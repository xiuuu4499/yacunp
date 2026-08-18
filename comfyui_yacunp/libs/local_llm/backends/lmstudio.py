"""LM Studio backend via its OpenAI-compatible local HTTP API.

Uses only the Python standard library (``urllib``) so no extra dependency is
required. LM Studio must already be running locally with the target model loaded
or available; this backend never downloads anything.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from ... import errors
from ...custom_types import YacunpLLMModel
from .. import config


def _request(url: str, payload: dict[str, Any] | None = None, timeout: float = 120.0):
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise errors.YacunpError(
            f"Could not reach LM Studio at '{url}'. Is the local server running? "
            f"({exc})"
        ) from None


def list_models(base_url: str) -> list[str]:
    result = _request(f"{base_url}/models")
    return [entry.get("id") for entry in (result.get("data") or []) if entry.get("id")]


def load(resolved: config.ResolvedModel, load_args: dict[str, Any]) -> YacunpLLMModel:
    base_url = str(resolved.extra.get("base_url") or "http://localhost:1234/v1").rstrip("/")
    model_id = resolved.path or resolved.key
    return YacunpLLMModel(
        backend="lmstudio",
        name=model_id,
        handle={"base_url": base_url, "model": model_id},
        config={"base_url": base_url, "model": model_id},
        multimodal=bool(resolved.multimodal),
    )


def load_direct(base_url: str, model_id: str, multimodal: bool) -> YacunpLLMModel:
    base_url = base_url.rstrip("/")
    return YacunpLLMModel(
        backend="lmstudio",
        name=model_id,
        handle={"base_url": base_url, "model": model_id},
        config={"base_url": base_url, "model": model_id},
        multimodal=multimodal,
    )


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
        raise errors.YacunpError("The LM Studio model is not loaded.")
    if images and not model.multimodal:
        raise errors.YacunpError(
            f"Model '{model.name}' is not configured for image input."
        )
    handle = model.handle
    base_url = handle.get("base_url", "http://localhost:1234/v1")
    payload: dict[str, Any] = {
        "model": handle.get("model", model.name),
        "messages": _build_messages(system, prompt, images),
    }
    if gen_args.get("max_tokens"):
        payload["max_tokens"] = int(gen_args["max_tokens"])
    if "temperature" in gen_args:
        payload["temperature"] = float(gen_args["temperature"])
    if "top_p" in gen_args:
        payload["top_p"] = float(gen_args["top_p"])
    if "presence_penalty" in gen_args:
        payload["presence_penalty"] = float(gen_args["presence_penalty"])
    if "frequency_penalty" in gen_args:
        payload["frequency_penalty"] = float(gen_args["frequency_penalty"])
    if gen_args.get("seed") not in (None, 0):
        payload["seed"] = int(gen_args["seed"])
    if gen_args.get("stop"):
        payload["stop"] = [str(gen_args["stop"])]

    result = _request(f"{base_url}/chat/completions", payload)
    choice = (result.get("choices") or [{}])[0]
    text = (choice.get("message") or {}).get("content") or ""
    info = {
        "backend": "lmstudio",
        "model": payload["model"],
        "finish_reason": choice.get("finish_reason"),
    }
    usage = result.get("usage") or {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        if key in usage:
            info[key] = usage[key]
    return text, info


def unload(model: YacunpLLMModel) -> None:
    # LM Studio owns the model lifecycle; just drop our lightweight handle.
    model.handle = None
