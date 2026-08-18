"""Save Text node."""

from __future__ import annotations

import os
import re

from comfy_api.latest import io, ui

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize(name: str, fallback: str) -> str:
    cleaned = _SAFE.sub("_", os.path.basename(str(name))).strip("._")
    return cleaned or fallback


def write_text_file(
    directory: str, text, filename_prefix: str = "yacunp", extension: str = "txt"
) -> tuple[str, str]:
    """Write ``text`` to ``directory`` and return ``(path, filename)``.

    The prefix and extension are sanitized to a bare filename to keep writes
    inside ``directory``; an existing name is disambiguated with a counter.
    """
    prefix = _sanitize(filename_prefix, "yacunp")
    ext = _sanitize(extension, "txt").lstrip(".") or "txt"
    os.makedirs(directory, exist_ok=True)
    filename = f"{prefix}.{ext}"
    path = os.path.join(directory, filename)
    counter = 1
    while os.path.exists(path):
        filename = f"{prefix}_{counter:03d}.{ext}"
        path = os.path.join(directory, filename)
        counter += 1
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("" if text is None else str(text))
    return path, filename


class YacunpSaveText(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_SaveText",
            display_name="Save Text (YACUNP)",
            category="YACUNP/IO",
            description="Write a string to a file in the ComfyUI output directory. "
            "Use it to persist generated text (e.g. .txt) or serialized JSON "
            "metadata (e.g. .json). Runs as an output node and outputs the saved "
            "file path.",
            inputs=[
                io.String.Input("text", multiline=True, default=""),
                io.String.Input("filename_prefix", default="yacunp"),
                io.String.Input("extension", default="txt"),
            ],
            outputs=[io.String.Output("path")],
            is_output_node=True,
        )

    @classmethod
    def execute(cls, text, filename_prefix="yacunp", extension="txt") -> io.NodeOutput:
        import folder_paths

        path, _filename = write_text_file(
            folder_paths.get_output_directory(), text, filename_prefix, extension
        )
        return io.NodeOutput(path, ui=ui.PreviewText(path))
