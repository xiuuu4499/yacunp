# Copilot instructions

## Install the Copilot CLI and plugins declared for this repository

This repository declares Copilot plugins in
[`.github/copilot/settings.json`](copilot/settings.json). Those plugins are
**not installed automatically** — `enabledPlugins` only enables a plugin that is
already installed. Two hook scripts handle the setup; run them at the start of
every session, before starting any task:

1. Ensure an up-to-date Copilot CLI on `PATH`:

   ```bash
   bash .github/copilot/hooks/update-copilot-cli.sh
   ```

   In the cloud coding agent the `copilot` CLI may be missing or a stale copy
   bundled with the VS Code extension; this script installs/updates it via npm
   and puts the current version at the front of `PATH`.

2. Register the declared marketplaces and install the enabled plugins:

   ```bash
   bash .github/copilot/hooks/install-plugins.sh
   ```

   This reads `.github/copilot/settings.json`, registers every marketplace under
   `extraKnownMarketplaces` (at the declared `ref`), and installs every plugin
   whose `enabledPlugins` entry is `true`.

3. Verify the plugins installed and their skills are available:

   ```bash
   copilot plugin list
   /skills list
   ```

These scripts only affect the environment they run in and do not persist to
future sessions, so run them at the start of every session. Installing a plugin
mid-session may not retroactively load its skills into an already-running
session.

The scripts are also wired into
[`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json) as a
`postStartCommand`, so a rebuilt dev container runs them automatically. Keep the
installed plugins in sync with `.github/copilot/settings.json`: re-run
`install-plugins.sh` after changing that file, and do not rely on the settings
file alone to make a plugin's skills available.
