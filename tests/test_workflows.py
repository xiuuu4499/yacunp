"""Structural checks for the committed ComfyUI canvas workflows."""

from __future__ import annotations

import json
from pathlib import Path

WORKFLOW_DIR = Path(__file__).parents[1] / "example_workflows"


def test_example_workflows_use_current_node_shapes():
    for path in sorted(WORKFLOW_DIR.glob("*.json")):
        workflow = json.loads(path.read_text(encoding="utf-8"))
        for node in workflow["nodes"]:
            assert node["type"] != "YACUNP_SaveText", path.name
            if node["type"] == "YACUNP_MakeJSON":
                assert [item["name"] for item in node.get("inputs", [])] == ["value"]
            if node["type"] == "SaveText":
                assert node["properties"]["Node name for S&R"] == "SaveText"
                assert node["outputs"][0]["name"] == "text"
