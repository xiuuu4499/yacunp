#!/usr/bin/env bash
# Installs the Copilot CLI and the plugins declared in .github/copilot/settings.json.
# Idempotent: safe to run on every session start; it re-syncs marketplaces and plugins.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
settings="$repo_root/.github/copilot/settings.json"
cache_dir="${HOME}/.copilot/repo-marketplace-cache"

# Ensure the Copilot CLI is available (not on PATH by default in the cloud agent).
if ! command -v copilot >/dev/null 2>&1; then
  npm install -g @github/copilot
fi

[ -f "$settings" ] || { echo "No settings.json at $settings; nothing to install."; exit 0; }

# Register every marketplace under extraKnownMarketplaces.
# The CLI cannot add a GitHub marketplace at a specific ref, so when a ref is
# declared we clone that ref locally and register the checkout by path.
while IFS=$'\t' read -r key repo ref; do
  [ -n "$repo" ] || continue
  if [ -n "$ref" ] && [ "$ref" != "null" ]; then
    dest="$cache_dir/$key"
    rm -rf "$dest"
    mkdir -p "$cache_dir"
    git clone --quiet --depth 1 --branch "$ref" "https://github.com/${repo}.git" "$dest"
    source="$dest"
  else
    source="$repo"
  fi
marketplace_output="$(copilot plugin marketplace add "$source" 2>&1)" || {
  if [[ "$marketplace_output" != *"already registered"* ]]; then
    printf '%s\n' "$marketplace_output" >&2
    exit 1
  fi
}
printf '%s\n' "$marketplace_output" | grep -v 'already registered' || true
done < <(jq -r '
  .extraKnownMarketplaces // {}
  | to_entries[]
  | [.key, .value.source.repo, (.value.source.ref // "")]
  | @tsv' "$settings")

# Install every plugin whose enabledPlugins entry is true.
while IFS= read -r plugin; do
  [ -n "$plugin" ] || continue
  # `plugin install` is a no-op ("already installed") for an existing plugin, so it
  # never picks up a new marketplace revision. Uninstall first to force a reinstall
  # from the freshly refreshed marketplace checkout.
  copilot plugin uninstall "$plugin" >/dev/null 2>&1 || true
  copilot plugin install "$plugin"
done < <(jq -r '
  .enabledPlugins // {}
  | to_entries[]
  | select(.value == true)
  | .key' "$settings")

copilot plugin list || true
