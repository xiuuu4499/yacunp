# Codex instructions

YACUNP is a ComfyUI custom-node pack. The implementation uses the ComfyUI V3
node API, with tests that run without a full ComfyUI installation.

## ComfyUI skills

Before changing ComfyUI node code, make the repository's Codex plugin
available:

```bash
bash .codex/install-plugins.sh
```

The script installs the official Codex CLI when it is missing, reuses the
existing Codex login when available, registers the pinned marketplace ref, and
installs `comfyui-custom-nodes`. If the plugin was installed during the
current session, start a new Codex thread before relying on its skills.

Use the relevant `comfyui-node-*` skill as the source of truth for ComfyUI
work. Prefer the V3 API for new code; use `comfyui-node-migration` for V1
migrations. The available skills cover basics, inputs, outputs, datatypes,
lifecycle, advanced features, frontend extensions, packaging, and migration.

When creating example workflows, use the regular ComfyUI canvas/LiteGraph
format by default. Use API prompt format only when it is explicitly requested.

## Codex custom agents

Project-scoped custom agents are defined in `.codex/agents/`:

- `comfyui-expert` — implements and debugs ComfyUI custom-node work using the
  plugin skills above.
- `comfyui-planner` — produces plans for large ComfyUI tasks and does not
  implement them.

When delegating specialized work, use the agent whose name matches the task.

## Development checks

Run the checks that match the change before handing it back:

```bash
ruff check .
pytest -q
```

Keep nodes thin and test reusable logic independently. Follow the repository
layout and conventions in [DEVELOPMENT.md](DEVELOPMENT.md), including stable
`YACUNP_` node IDs, plain user-facing display names, and documentation in
`NODE_LIST.md` for new nodes.

## GitHub and pull requests

Use the GitHub CLI (`gh`) for GitHub operations in this repository. It is
available for inspecting the current branch and pull request, opening pull
requests, reading checks, and investigating GitHub Actions failures.

Useful commands include:

```bash
gh auth status
gh pr view --comments
gh pr checks
gh pr create
gh run list --workflow test.yml
gh run view <run-id> --log-failed
```

For a current-branch PR, resolve the branch and repository before making
changes. Use the connected GitHub integration for structured PR or issue
metadata when it is available, and use `gh` for current-branch discovery and
Actions logs. Do not merge, close, delete, or force-push unless the user
explicitly asks.

## Commits and PR titles

Commit messages and pull request titles must follow the
[Conventional Commits 1.0.0 specification](https://www.conventionalcommits.org/en/v1.0.0/#specification):

```text
<type>[optional scope][optional !]: <imperative description>
```

Use types such as `feat`, `fix`, `build`, `chore`, `ci`, `docs`, `refactor`,
and `test`. Mark breaking changes with `!` and/or a `BREAKING CHANGE:` footer.

## Copilot CLI compatibility

Codex may call the existing Copilot CLI updater when a Copilot-compatible
workflow needs it:

```bash
bash .github/copilot/hooks/update-copilot-cli.sh
```

That script updates the GitHub Copilot CLI; it is separate from the Codex
plugin installation above. Keep both workflows intact.
