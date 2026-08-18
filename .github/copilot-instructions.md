# Copilot instructions

## Install the Copilot plugins declared for this repository

This repository declares Copilot plugins in
[`.github/copilot/settings.json`](copilot/settings.json). Those plugins are
**not installed automatically** — `enabledPlugins` only enables a plugin that is
already installed. Before starting any task, install the declared plugins so
their skills are available.

Follow these steps:

1. Make sure the `copilot` CLI is available. In the cloud coding agent it is
   **not on `PATH` by default**, so the commands below would otherwise fail with
   `copilot: command not found`. If `command -v copilot` prints nothing, install
   it (the npm registry is reachable from the agent):

   ```bash
   command -v copilot || npm install -g @github/copilot
   ```

   After this, `copilot --version` should work.

2. Read `.github/copilot/settings.json`.
3. For every marketplace under `extraKnownMarketplaces`, register it using its
   `source` (GitHub `repo` and `ref`). For example, to register the
   `comfyui-custom-node-skills` marketplace:

   ```bash
   copilot plugin marketplace add xiuuu4499/comfyui-custom-node-skills#adjusted-fork-urls
   ```

4. For every entry in `enabledPlugins` that is set to `true`, install the
   plugin. The key has the form `<plugin>@<marketplace>`. For example:

   ```bash
   copilot plugin install comfyui-custom-nodes@comfyui-custom-node-skills
   ```

5. Verify the plugins installed and their skills are available:

   ```bash
   copilot plugin list
   /skills list
   ```

These steps only affect the environment they run in and do not persist to future
sessions, so run them at the start of every session. Installing a plugin
mid-session may not retroactively load its skills into an already-running
session.

Keep the set of installed plugins in sync with `.github/copilot/settings.json`:
install any plugin listed there that is missing, and do not rely on the settings
file alone to make a plugin's skills available.
