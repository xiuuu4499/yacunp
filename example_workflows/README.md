# YACUNP example workflows

Sample workflows that exercise the YACUNP nodes end to end. They are saved in
the **regular ComfyUI canvas (workflow) format**, so you can open them on the
canvas and edit them. Load one in ComfyUI (drag the file onto the canvas, or use
*Workflow → Open*), then press *Queue*.

> These graphs run real local models. Nothing is downloaded for you.

## Prerequisites

- **llama.cpp workflows (01, 03):** install `llama-cpp-python` in your ComfyUI
  environment, and copy `comfyui_yacunp/local_models.example.json` to
  `comfyui_yacunp/local_models.json`, editing the paths to point at GGUF files
  you already have. The examples reference the model key
  `"Qwen2.5 7B Instruct (GGUF, text only)"`; rename it or change the `model`
  widget to match your config.
- **LM Studio workflow (02):** start the LM Studio local server (default
  `http://localhost:1234/v1`) with a **vision-capable** model loaded, and place
  an image named `example.png` in your ComfyUI `input/` folder (or pick another
  in the *Load Image* node).
- **JSON workflow (04):** no model or extra dependency required.

Saved files (text and JSON) are written to your ComfyUI `output/` directory by
ComfyUI’s built-in *Save Text* nodes.

## The workflows

| File | Exercises |
|---|---|
| `01_llamacpp_generate_and_save.json` | Basic + Advanced arguments → Combine Dictionaries → Load Model (llama.cpp) → System Prompt Presets → Generate Text → built-in Save Text (.txt) + Make JSON metadata → built-in Save Text (.json) → Unload Model. |
| `02_lmstudio_vision_describe.json` | Load Image → Load Model (LM Studio) → Describe-Image preset → Generate Text with an image (multimodal) → built-in Save Text → Unload Model. |
| `03_dictionary_prompt_builder.json` | Make KV Pair, Make Dictionary, Set Dictionary Value, Get Dictionary Keys / Value, Read KV Pair, Format Text With Dictionary → build a prompt → Generate Text → built-in Save Text, plus a JSON debug dump. |
| `04_json_argument_inspector.json` | Make JSON, Format JSON (pretty + single line), Convert JSON round-trip on a combined argument dictionary → built-in Save Text (.json). |

## Notes

- Workflow 03 feeds the *Make KV Pair* `key` inputs from core **Primitive
  String** nodes (the `key` input is connection-only). If your ComfyUI build
  names that node differently, swap in any node that outputs a `STRING`.
- Some YACUNP inputs are **dynamic** (the Make KV Pair *type* selector, and the
  auto-growing pair/dictionary slots on Make Dictionary and Combine
  Dictionaries). Make JSON accepts one value; pass a list when an array root
  is desired. If your ComfyUI frontend version renders dynamic inputs
  differently, re-touch the affected node on the canvas and re-save.
- The *Unload Model* nodes take an optional `signal` input wired to the generated
  text purely to force them to run **after** generation.
