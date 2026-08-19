"""LLM argument definitions and dictionary conversion helpers.

Each argument spec carries a long, human-readable description so the node
tooltips can teach users what a parameter actually does. The Basic node exposes
the parameters people tune most often; the Advanced node adds the finer knobs.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

from ..custom_types import YacunpDictionary, YacunpKVPair

# Each spec: name, type id, default, io kwargs (min/max/step), description.
BASIC_ARG_SPECS: list[dict[str, Any]] = [
    {
        "name": "max_tokens",
        "type": "INT",
        "default": 512,
        "io": {"min": 1, "max": 1_000_000, "step": 1},
        "description": (
            "Maximum number of NEW tokens the model may generate in its reply. "
            "This does not include the prompt. Higher values allow longer answers "
            "but take more time and memory."
        ),
    },
    {
        "name": "temperature",
        "type": "FLOAT",
        "default": 0.7,
        "io": {"min": 0.0, "max": 4.0, "step": 0.01},
        "description": (
            "Sampling randomness. 0.0 is deterministic/greedy (always the most "
            "likely token); 0.7-0.9 is a good creative default; above ~1.2 output "
            "becomes increasingly random and can lose coherence."
        ),
    },
    {
        "name": "top_p",
        "type": "FLOAT",
        "default": 0.95,
        "io": {"min": 0.0, "max": 1.0, "step": 0.01},
        "description": (
            "Nucleus sampling: only consider the smallest set of tokens whose "
            "probabilities sum to this fraction. 1.0 disables it; 0.9-0.95 trims "
            "the unlikely tail while keeping variety. Usually tuned instead of "
            "temperature, not alongside it."
        ),
    },
    {
        "name": "seed",
        "type": "INT",
        "default": 0,
        "io": {
            "min": 0,
            "max": 2**63 - 1,
            "step": 1,
            "control_after_generate": False,
        },
        "description": (
            "Random seed for sampling. Reuse the same seed with identical inputs "
            "to reproduce a result. Backends commonly treat 0 as 'pick a fresh "
            "random seed each run'."
        ),
    },
    {
        "name": "n_ctx",
        "type": "INT",
        "default": 4096,
        "io": {"min": 0, "max": 1_000_000, "step": 256},
        "description": (
            "Context window size in tokens (prompt + generation combined). Must "
            "fit the model and your VRAM/RAM. LOAD-TIME setting: it is applied "
            "when the model is loaded, not per generation. 0 uses the model "
            "default."
        ),
    },
    {
        "name": "n_gpu_layers",
        "type": "INT",
        "default": -1,
        "io": {"min": -1, "max": 1000, "step": 1},
        "description": (
            "How many transformer layers to offload to the GPU (llama.cpp). -1 "
            "offloads as many as possible, 0 runs entirely on CPU. LOAD-TIME "
            "setting."
        ),
    },
]

ADVANCED_ARG_SPECS: list[dict[str, Any]] = [
    {
        "name": "top_k",
        "type": "INT",
        "default": 40,
        "io": {"min": 0, "max": 1000, "step": 1},
        "description": (
            "Restrict sampling to the K most likely tokens at each step. 0 "
            "disables it. Lower values (20-40) make output more focused; higher "
            "values allow more diversity."
        ),
    },
    {
        "name": "min_p",
        "type": "FLOAT",
        "default": 0.05,
        "io": {"min": 0.0, "max": 1.0, "step": 0.01},
        "description": (
            "Minimum-probability cutoff relative to the most likely token; tokens "
            "below this share are discarded. A robust alternative to top_p. 0.0 "
            "disables it."
        ),
    },
    {
        "name": "repeat_penalty",
        "type": "FLOAT",
        "default": 1.1,
        "io": {"min": 0.0, "max": 4.0, "step": 0.01},
        "description": (
            "Penalizes tokens that already appeared, discouraging loops and "
            "verbatim repetition. 1.0 is off; 1.1-1.3 is typical. Too high can "
            "hurt fluency."
        ),
    },
    {
        "name": "presence_penalty",
        "type": "FLOAT",
        "default": 0.0,
        "io": {"min": -2.0, "max": 2.0, "step": 0.01},
        "description": (
            "Flat penalty applied to any token that has appeared at least once, "
            "nudging the model toward new topics. 0.0 disables it."
        ),
    },
    {
        "name": "frequency_penalty",
        "type": "FLOAT",
        "default": 0.0,
        "io": {"min": -2.0, "max": 2.0, "step": 0.01},
        "description": (
            "Penalty scaled by how often a token has already appeared, reducing "
            "repetition proportionally. 0.0 disables it."
        ),
    },
    {
        "name": "n_batch",
        "type": "INT",
        "default": 512,
        "io": {"min": 1, "max": 100_000, "step": 1},
        "description": (
            "Prompt-processing batch size (llama.cpp). Larger values speed up "
            "prompt ingestion at the cost of memory. LOAD-TIME setting."
        ),
    },
    {
        "name": "n_threads",
        "type": "INT",
        "default": 0,
        "io": {"min": 0, "max": 4096, "step": 1},
        "description": (
            "CPU threads used for inference. 0 lets the backend choose based on "
            "your CPU. LOAD-TIME setting."
        ),
    },
    {
        "name": "flash_attn",
        "type": "BOOLEAN",
        "default": False,
        "io": {},
        "description": (
            "Enable FlashAttention kernels when the build supports them, reducing "
            "memory use for long contexts. LOAD-TIME setting; ignored if "
            "unsupported."
        ),
    },
    {
        "name": "image_max_tokens",
        "type": "INT",
        "default": 4096,
        "io": {"min": 0, "max": 100_000, "step": 64},
        "description": (
            "Maximum tokens budgeted for encoding each input image on multimodal "
            "(mmproj) models. Higher preserves more visual detail but consumes "
            "more context. LOAD-TIME setting."
        ),
    },
    {
        "name": "stop_sequence",
        "type": "STRING",
        "default": "",
        "io": {},
        "description": (
            "Optional stop sequence. Generation halts when this exact text is "
            "produced. Leave empty for none."
        ),
    },
]


def _coerce(type_id: str, value: Any) -> Any:
    if type_id == "INT":
        return int(value)
    if type_id == "FLOAT":
        return float(value)
    if type_id == "BOOLEAN":
        return bool(value)
    if type_id == "STRING":
        return "" if value is None else str(value)
    return value


def build_arguments(specs: list[dict[str, Any]], values: dict[str, Any]) -> YacunpDictionary:
    """Build a :class:`YacunpDictionary` from arg specs and supplied values."""
    items: OrderedDict[str, YacunpKVPair] = OrderedDict()
    for spec in specs:
        name = spec["name"]
        type_id = spec["type"]
        raw = values.get(name, spec["default"])
        items[name] = YacunpKVPair(
            key=name, declared_type=type_id, value=_coerce(type_id, raw)
        )
    return YacunpDictionary(items=items)


def _infer_type(value: Any) -> str:
    if isinstance(value, bool):
        return "BOOLEAN"
    if isinstance(value, int):
        return "INT"
    if isinstance(value, float):
        return "FLOAT"
    if isinstance(value, str):
        return "STRING"
    if isinstance(value, list):
        return "ARRAY"
    if isinstance(value, dict):
        return "DICT"
    return "ANY"


def plain_to_dictionary(mapping: dict[str, Any]) -> YacunpDictionary:
    """Wrap a plain mapping into a :class:`YacunpDictionary`, inferring types."""
    items: OrderedDict[str, YacunpKVPair] = OrderedDict()
    for key, value in mapping.items():
        items[str(key)] = YacunpKVPair(
            key=str(key), declared_type=_infer_type(value), value=value
        )
    return YacunpDictionary(items=items)


def dictionary_to_plain(dictionary: YacunpDictionary | None) -> dict[str, Any]:
    """Flatten a :class:`YacunpDictionary` into ``{key: value}``."""
    if dictionary is None:
        return {}
    return {key: pair.value for key, pair in dictionary.items.items()}
