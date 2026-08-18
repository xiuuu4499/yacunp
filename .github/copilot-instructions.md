# Copilot instructions

## Install the Copilot plugins declared for this repository

This repository declares Copilot plugins in
[`.github/copilot/settings.json`](copilot/settings.json). Those plugins are
**not installed automatically** — `enabledPlugins` only enables a plugin that is
already installed. Before starting any task, install the declared plugins so
their skills are available.

Follow these steps:

1. Read `.github/copilot/settings.json`.
2. For every marketplace under `extraKnownMarketplaces`, register it using its
   `source` (GitHub `repo` and `ref`). For example, to register the
   `comfyui-custom-node-skills` marketplace:

   ```bash
   copilot plugin marketplace add xiuuu4499/comfyui-custom-node-skills#adjusted-fork-urls
   ```

3. For every entry in `enabledPlugins` that is set to `true`, install the
   plugin. The key has the form `<plugin>@<marketplace>`. For example:

   ```bash
   copilot plugin install comfyui-custom-nodes@comfyui-custom-node-skills
   ```

4. Verify the plugins installed and their skills are available:

   ```bash
   copilot plugin list
   /skills list
   ```

Keep the set of installed plugins in sync with `.github/copilot/settings.json`:
install any plugin listed there that is missing, and do not rely on the settings
file alone to make a plugin's skills available.
