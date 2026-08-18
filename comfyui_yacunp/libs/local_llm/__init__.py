"""Local LLM support library.

Pure-Python, ComfyUI-independent helpers for the ``YACUNP/Local LLM`` node
category: model catalog parsing, argument definitions, system-prompt presets,
and lazily-imported backends. Nothing here imports heavy runtime dependencies
(``llama_cpp``, ``torch``) at module load, so the whole package is importable
and unit-testable without a ComfyUI install.
"""

from __future__ import annotations
