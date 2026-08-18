# YACUNP

**Y**et **A**nother **C**omfy**U**I **N**ode **P**ack — a personal collection of
small, composable utility nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

YACUNP focuses on **data plumbing** inside a workflow: building and reading typed
key/value pairs, assembling them into ordered dictionaries, formatting text from
those values, and converting structured data to and from JSON. Every node is
built on the ComfyUI V3 node API.

## Categories

All nodes appear under the **`YACUNP`** menu, grouped by category:

- **`YACUNP/Dictionary`** — create typed key/value pairs, collect them into
  dictionaries, look values up by key, list keys, and fill text templates from a
  dictionary.
- **`YACUNP/JSON`** — encode workflow values into JSON, parse JSON back into
  nested data, and reformat JSON between compact and pretty layouts.

For the full catalog — every node's purpose, inputs, outputs, error conditions,
and a diagram — see **[NODE_LIST.md](NODE_LIST.md)**.

## Installation

### Option A — ComfyUI-Manager

Search for **YACUNP** in [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)
and install it, then restart ComfyUI.

### Option B — Manual clone

Clone this repository into your ComfyUI `custom_nodes` directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/xiuuu4499/yacunp.git
```

YACUNP requires no dependencies beyond what ComfyUI already ships with, so no
extra `pip install` step is needed. Restart ComfyUI after cloning.

## Requirements

- ComfyUI with V3 node API support (`comfy_api.latest`).
- Python 3.10 or newer.

## Contributing / development

Developer setup, architecture, testing, and release information live in
**[DEVELOPMENT.md](DEVELOPMENT.md)**.

## License

Released under the [MIT License](LICENSE).
