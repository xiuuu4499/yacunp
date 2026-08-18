"""Shared pytest configuration for the YACUNP test suite.

Installs the local ``comfy_api`` stub (so node modules import without a real
ComfyUI install) and puts the *parent* of the repository on ``sys.path`` so the
whole pack is importable as the ``yacunp`` package.

The implementation directory is named ``comfyui_yacunp``; tests reference it
through the repository package (``yacunp.comfyui_yacunp.*``). The suite runs
with either ``pytest`` or ``python -m pytest`` from the repository root.
"""

from __future__ import annotations

import os
import sys

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_TESTS_DIR)
_REPO_PARENT = os.path.dirname(_REPO_ROOT)
_STUBS_DIR = os.path.join(_TESTS_DIR, "stubs")

for path in (_STUBS_DIR, _REPO_PARENT):
    if path not in sys.path:
        sys.path.insert(0, path)
