# Copilot instructions

## Install the Copilot CLI and plugins declared for this repository

This repository declares Copilot plugins in
[`.github/copilot/settings.json`](copilot/settings.json). Supported Copilot
clients — both the Copilot CLI and the cloud coding agent — read this file and
auto-install every plugin whose `enabledPlugins` entry is `true`, so no manual
setup is normally required. The two hook scripts below are a compatibility
fallback for older, unsupported clients that do not honor `enabledPlugins`; run
them only if the declared plugins are missing:

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
future sessions, so run them only as a fallback when a client has not
auto-installed the declared plugins. Installing a plugin mid-session may not
retroactively load its skills into an already-running session.

The scripts are also wired into
[`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json) as a
`postStartCommand`, so a rebuilt dev container runs them as a fallback. Keep the
`enabledPlugins` entries in `.github/copilot/settings.json` up to date so
supported clients auto-install the intended plugins.
