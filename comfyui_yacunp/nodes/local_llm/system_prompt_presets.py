"""System Prompt Presets node."""

from __future__ import annotations

from comfy_api.latest import io

from ...libs.local_llm import presets


def resolve_system_prompt(preset: str, extra_instructions: str, custom_override: str) -> str:
    override = (custom_override or "").strip()
    text = override if override else presets.get(preset)
    extra = (extra_instructions or "").strip()
    if extra:
        text = f"{text}\n\n{extra}"
    return text


class YacunpSystemPromptPresets(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="YACUNP_SystemPromptPresets",
            display_name="System Prompt Presets (YACUNP)",
            category="YACUNP/Local LLM",
            description="Pick a ready-made system prompt grouped by purpose "
            "(long-form text, image prompt, video prompt, prompt adjustment, "
            "analysis). Optionally append extra instructions, or replace the preset "
            "entirely with a custom override. Add your own presets via "
            "system_prompts.json.",
            inputs=[
                io.Combo.Input("preset", options=presets.options()),
                io.String.Input(
                    "extra_instructions",
                    multiline=True,
                    default="",
                    tooltip="Optional text appended after the preset, e.g. "
                    "task-specific guidance or constraints.",
                ),
                io.String.Input(
                    "custom_override",
                    multiline=True,
                    default="",
                    tooltip="If non-empty, this text replaces the preset entirely.",
                ),
            ],
            outputs=[io.String.Output("system_prompt")],
        )

    @classmethod
    def execute(cls, preset, extra_instructions="", custom_override="") -> io.NodeOutput:
        return io.NodeOutput(
            resolve_system_prompt(str(preset), extra_instructions, custom_override)
        )
