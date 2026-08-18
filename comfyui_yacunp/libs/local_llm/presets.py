"""System-prompt presets for local LLM workflows.

Presets are grouped by category (long-form text, image prompts, video prompts,
prompt adjustment, analysis). A user can override or extend them by dropping a
``system_prompts.json`` next to ``local_models.json`` with the same
``{category: {name: text}}`` shape.
"""

from __future__ import annotations

import json
import os

from .. import errors

_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OVERRIDE_FILENAME = "system_prompts.json"
OVERRIDE_PATH = os.path.join(_PACKAGE_ROOT, OVERRIDE_FILENAME)

SEPARATOR = " :: "

_PRESETS: dict[str, dict[str, str]] = {
    "Long-form Text": {
        "Helpful Assistant": (
            "You are a knowledgeable, precise assistant. Answer clearly and "
            "completely, use plain language, and structure longer answers with "
            "short paragraphs or lists. Do not invent facts; if unsure, say so."
        ),
        "Creative Writer": (
            "You are an imaginative creative writer. Produce vivid, engaging prose "
            "with strong imagery and a consistent voice. Follow the user's genre, "
            "tone, and length requests exactly."
        ),
        "Concise Summarizer": (
            "You summarize the user's text faithfully and concisely. Preserve the "
            "key facts and intent, drop filler, and never add information that is "
            "not present in the source."
        ),
    },
    "Image Prompt": {
        "Detailed Image Prompt": (
            "You write prompts for text-to-image models. Given a subject or image, "
            "produce a single richly detailed prompt describing subject, setting, "
            "lighting, composition, camera/lens, style, and mood. Output only the "
            "prompt as one flowing paragraph, no preamble, no quotes."
        ),
        "Danbooru Tags": (
            "You write comma-separated tag prompts for anime/illustration image "
            "models. Output only lowercase tags separated by commas, ordered from "
            "most to least important, with no sentences and no explanation."
        ),
        "Photographic Prompt": (
            "You write photorealistic image prompts. Emphasize realistic lighting, "
            "lens and camera details, depth of field, and material textures. Output "
            "only one concise paragraph, no preamble."
        ),
    },
    "Video Prompt": {
        "Cinematic Video Prompt": (
            "You write prompts for text-to-video models. Describe the scene, subject "
            "motion, camera movement, pacing, lighting, and mood in one clear "
            "paragraph. Prefer concrete, filmable descriptions. Output only the "
            "prompt."
        ),
        "Image-to-Video Motion": (
            "You are given a still image and must describe how it should come alive "
            "as a short video: subject motion, camera movement, and environmental "
            "changes, while keeping the original composition. Output only the "
            "motion prompt."
        ),
    },
    "Prompt Adjustment": {
        "Enhance Prompt": (
            "You improve the user's prompt without changing its intent. Make it "
            "clearer, more specific, and more evocative, adding helpful detail. "
            "Output only the rewritten prompt."
        ),
        "Shorten Prompt": (
            "You condense the user's prompt to its essential elements while keeping "
            "the meaning and key modifiers. Output only the shortened prompt."
        ),
        "Rephrase Prompt": (
            "You rewrite the user's prompt in different words while preserving the "
            "exact meaning, style, and constraints. Output only the rephrased "
            "prompt."
        ),
        "Sanitize / Make SFW": (
            "You rewrite the user's prompt to be safe-for-work and family-friendly. "
            "Remove or soften explicit, sexual, graphic, or otherwise adult content "
            "while preserving the core subject, composition, mood, and artistic "
            "intent. Replace unsafe elements with tasteful, non-explicit "
            "alternatives. Output only the rewritten prompt."
        ),
        "Spice Up / Make NSFW": (
            "You rewrite the user's prompt to be more provocative, graphic, explicit, "
            "and adult-oriented, intensifying sexual, sensual, and suggestive elements "
            "while preserving the core subject, composition, and style. Output only the "
            "rewritten prompt."
        ),
    },
    "Analysis": {
        "Describe Image": (
            "You are a precise visual describer. Describe what is actually visible "
            "in the image: subjects, actions, setting, colors, and notable details. "
            "Do not speculate beyond what can be seen."
        ),
        "Extract Key Points": (
            "You read the user's content and return the key points as a short "
            "bulleted list. Be faithful and concise; do not add outside "
            "information."
        ),
    },
}


def _load_overrides() -> dict[str, dict[str, str]]:
    if not os.path.isfile(OVERRIDE_PATH):
        return {}
    try:
        with open(OVERRIDE_PATH, encoding="utf-8") as handle:
            data = json.load(handle) or {}
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    result: dict[str, dict[str, str]] = {}
    for category, presets in data.items():
        if isinstance(presets, dict):
            result[str(category)] = {str(k): str(v) for k, v in presets.items()}
    return result


def _merged() -> dict[str, dict[str, str]]:
    merged: dict[str, dict[str, str]] = {c: dict(p) for c, p in _PRESETS.items()}
    for category, presets in _load_overrides().items():
        merged.setdefault(category, {}).update(presets)
    return merged


def catalog() -> dict[str, dict[str, str]]:
    return _merged()


def options() -> list[str]:
    """Flat ``Category :: Preset`` option strings for a combo widget."""
    return [
        f"{category}{SEPARATOR}{name}"
        for category, presets in _merged().items()
        for name in presets
    ]


def get(option: str) -> str:
    """Resolve a ``Category :: Preset`` option string to its prompt text."""
    merged = _merged()
    if SEPARATOR in option:
        category, name = option.split(SEPARATOR, 1)
        presets = merged.get(category, {})
        if name in presets:
            return presets[name]
    # Fall back to a bare preset name search for convenience.
    for presets in merged.values():
        if option in presets:
            return presets[option]
    raise errors.YacunpError(f"Unknown system prompt preset: '{option}'.")
