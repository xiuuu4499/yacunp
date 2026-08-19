# Development guide

Developer documentation for the YACUNP node pack: repository layout, the
architecture that keeps nodes testable, how to add nodes and types, how to run
the checks, and how the CI gate is wired up.

## Repository layout

```
yacunp/
  __init__.py                 # V3 entry: ComfyExtension + comfy_entrypoint
  pyproject.toml              # metadata, [tool.comfy], ruff + pytest config
  requirements.txt            # runtime deps (none beyond ComfyUI)
  requirements-dev.txt        # pytest, ruff
  README.md                   # overview (no node list, no dev info)
  NODE_LIST.md                # node catalog + per-node diagrams
  DEVELOPMENT.md              # this file
  LICENSE
  .github/workflows/test.yml  # PR-gated CI (ruff + pytest)
  comfyui_yacunp/
    __init__.py
    registration.py           # collects NODES from every category package
    local_models.example.json # Local LLM model catalog template (copy to local_models.json)
    libs/                     # reusable, comfy_api-light logic
      custom_types.py         # io.Custom handles + payload dataclasses
      type_registry.py        # single source of truth for all types
      json_codec.py           # JSON encode/decode on top of the registry
      errors.py               # YacunpError + typed error helpers
      local_llm/              # model catalog, arg specs, presets, lazy backends
    nodes/
      dictionary/             # one node per file; __init__ exports NODES
      json/                   # one node per file; __init__ exports NODES
      local_llm/              # one node per file; __init__ exports NODES
  tests/
    conftest.py               # installs the comfy_api stub, sets sys.path
    stubs/comfy_api/          # minimal io surface for imports + schema
    libs/                     # registry + codec unit tests
    dictionary/, json/, local_llm/  # one test module per node
    test_registration.py      # every node imports, ids unique, schema valid
```

> **Note on importing the package.** The implementation package is named
> `comfyui_yacunp`; tests import the code through the repository package
> (`yacunp.comfyui_yacunp.*`). The suite runs with either `pytest` or
> `python -m pytest` from the repository root.

## Architecture: registry + thin adapters

Two ideas keep the pack small and testable:

1. **The type registry is the single source of truth.**
   [`comfyui_yacunp/libs/type_registry.py`](comfyui_yacunp/libs/type_registry.py) maps every supported
   ComfyUI type id to a `TypeSpec` describing how it is entered (`io_factory`,
   `has_widget`), serialized (`to_jsonable` / `from_jsonable`), and stringified
   (`to_text`). Nodes, JSON encoding, and text formatting all consume it, so no
   node duplicates type logic.

2. **Nodes are thin adapters.** Each node class only wires an `io.Schema` to a
   library call and converts values via the registry / `json_codec`. All real
   logic lives in `comfyui_yacunp/libs`, so it can be exercised without a running ComfyUI.

The custom wire types (`YACUNP_KVPAIR`, `YACUNP_DICTIONARY`) and their payload
dataclasses (`YacunpKVPair`, `YacunpDictionary`) live in
[`comfyui_yacunp/libs/custom_types.py`](comfyui_yacunp/libs/custom_types.py). Runtime failures are raised
as `YacunpError` from [`comfyui_yacunp/libs/errors.py`](comfyui_yacunp/libs/errors.py).

## Dev environment setup

This repo ships with a dev container; opening it in VS Code gives you Python
3.12 with everything on `PATH`. To set up manually with a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Runtime code depends only on the Python standard library and APIs bundled with
ComfyUI, so `requirements.txt` is intentionally empty.

The `YACUNP/Local LLM` nodes optionally use `llama-cpp-python` (install the
`llama` extra: `pip install -e ".[llama]"`, ideally a vision-capable build for
multimodal models). The LM Studio nodes use only the standard library. Backends
are imported lazily, so the pack loads without these installed and raises a clear
error only when a node actually runs. Models are never downloaded — configure
local paths in `local_models.json` (copy `local_models.example.json`).

## Running the checks

```bash
ruff check .     # lint
pytest -q        # unit tests (or: python -m pytest)
```

Both must pass; CI runs exactly these two commands.

## How to add a new node

1. Create a new file in the appropriate category folder, e.g.
   `comfyui_yacunp/nodes/dictionary/my_node.py`, containing a single `io.ComfyNode`
   subclass with `define_schema()` and `execute()`. Keep it thin — delegate real
   work to a function you can unit-test, and convert values through
   `type_registry` / `json_codec`.
2. Append the class to that package's `NODES` list in the category
   `__init__.py` (e.g. `comfyui_yacunp/nodes/dictionary/__init__.py`).
3. Choose a stable, globally unique `node_id` prefixed with `YACUNP_`, a plain
   user-facing `display_name`, and a `category` of `YACUNP/<Category>`. Never
   change a released `node_id`.
4. Add a test module under the matching `tests/<category>/` folder that calls
   `MyNode.execute(...)` with plain values and asserts on outputs / errors.
5. Document the node in [NODE_LIST.md](NODE_LIST.md).

Do not create a custom node that duplicates functionality already provided by
ComfyUI core. Reuse the built-in node in examples and documentation when the
core implementation meets the need.

`registration.all_nodes()` picks up every category's `NODES` automatically, so
no central list needs editing.

## How to add a new type

Edit **only** [`comfyui_yacunp/libs/type_registry.py`](comfyui_yacunp/libs/type_registry.py): add a
`TypeSpec` (or a new entry to the opaque-types table) with the type's
`io_factory`, `has_widget` flag, and `to_jsonable` / `from_jsonable` / `to_text`
conversions. Every consumer — Make KV Pair's type dropdown, the JSON nodes, and
text formatting — updates automatically. Add coverage in
`tests/libs/test_type_registry.py`.

## Continuous integration

[`.github/workflows/test.yml`](.github/workflows/test.yml) runs on pull requests
(`opened`, `synchronize`, `reopened`, `ready_for_review`). The `test` job:

- is guarded by `if: github.event.pull_request.draft == false`, so **draft PRs
  are skipped** and only non-draft PRs are gated;
- runs a matrix of Python 3.10 / 3.11 / 3.12;
- installs `requirements-dev.txt`, then runs `ruff check .` and `pytest -q`.

## Commit and PR conventions

Commit messages and PR titles follow
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/),
e.g. `feat(dictionary): add Merge Dictionaries node` or `fix: correct JSON
escaping`.

## Enabling the required status check (merge gate)

CI only *runs* on PRs; to actually **block merges** until it passes you must
mark the check as required on `main`. This is a GitHub setting, not a repo file.
Use either a branch protection rule or a repository ruleset.

### Option A — Branch protection rule

1. Push this repository to GitHub and open at least one PR so the `test` job has
   reported at least once (this makes the check name selectable).
2. Go to **Settings → Branches → Add branch protection rule**.
3. Set **Branch name pattern** to `main`.
4. Enable **Require a pull request before merging**.
5. Enable **Require status checks to pass before merging** and, optionally,
   **Require branches to be up to date before merging**.
6. In the status-checks search box, add the check named **`test`** (the matrix
   legs appear as `test (3.10)`, `test (3.11)`, `test (3.12)` — add each one you
   want to require).
7. Save the rule.

### Option B — Repository ruleset

1. Go to **Settings → Rules → Rulesets → New ruleset → New branch ruleset**.
2. Give it a name and set **Enforcement status** to **Active**.
3. Under **Target branches**, add **Include default branch** (or a pattern
   matching `main`).
4. Enable **Require a pull request before merging**.
5. Enable **Require status checks to pass** and add the **`test`** checks
   (`test (3.10)`, `test (3.11)`, `test (3.12)`).
6. Create the ruleset.

Because the CI job is skipped for draft PRs, keep a PR in draft while iterating;
mark it **Ready for review** to trigger the required checks before merging.

## TODO: Publish to ComfyUI Registry

The pack is not yet published to the [ComfyUI Registry](https://registry.comfy.org).
Do this once the node set is stable:

1. **Set a real `PublisherId`.** In [`pyproject.toml`](pyproject.toml) under
   `[tool.comfy]`, replace the `REPLACE_WITH_PUBLISHER_ID` placeholder with your
   actual publisher id.
2. **Register a publisher + API key.** Create/register a publisher at
   [registry.comfy.org](https://registry.comfy.org) and generate an API key for it.
3. **Install the CLI.** `pip install comfy-cli`.
4. **Publish.** Run `comfy node publish` from the repo root; it prompts for the
   API key (or set it via the `COMFY_API_KEY` environment variable).
5. **Automate (optional).** Add a GitHub Actions workflow that runs
   `comfy node publish` on version tags, using a `COMFY_API_KEY` repository
   secret for authentication.

Bump the `version` field in [`pyproject.toml`](pyproject.toml) before each
publish — the registry rejects re-publishing an existing version.
