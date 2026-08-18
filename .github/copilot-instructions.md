# Copilot instructions

## Commit and pull request naming

All commit messages and pull request titles **must** follow the
[Conventional Commits 1.0.0 specification](https://www.conventionalcommits.org/en/v1.0.0/#specification).

- Structure the summary line as `<type>[optional scope][optional !]: <description>`,
  for example `feat: add URL adjustment step` or `fix(parser): handle empty input`.
- Use a `type` that communicates intent. `feat` (a new feature) and `fix` (a bug
  fix) are required to be supported; other common types include `build`, `chore`,
  `ci`, `docs`, `style`, `refactor`, `perf`, and `test`.
- An optional scope may be provided in parentheses after the type, e.g. `feat(api):`.
- Use the description to summarize the change in the imperative mood, immediately
  after the colon and a space.
- A longer body may follow the summary line after one blank line, and one or more
  footers may follow the body after another blank line.
- Indicate a breaking change either with a `!` immediately before the colon
  (e.g. `feat!:` or `feat(api)!:`) and/or a `BREAKING CHANGE:` footer describing
  the break.

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
