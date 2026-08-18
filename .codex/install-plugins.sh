#!/usr/bin/env bash
# Ensures the Codex CLI is available, then registers and installs the plugin
# declared for this repository.
# Idempotent: safe to run when starting a ComfyUI task in a new session.
set -euo pipefail

marketplace_source="xiuuu4499/comfyui-custom-node-skills#adjusted-fork-urls"
marketplace_name="comfyui-custom-node-skills"
plugin_name="comfyui-custom-nodes@${marketplace_name}"

if ! command -v codex >/dev/null 2>&1; then
  command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 || {
    echo "curl or wget is required to install the Codex CLI." >&2
    exit 1
  }

  echo "Codex CLI is not on PATH; installing it with the official installer."
  installer_url="https://chatgpt.com/codex/install.sh"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$installer_url" | CODEX_NON_INTERACTIVE=true sh
  else
    wget -qO- "$installer_url" | CODEX_NON_INTERACTIVE=true sh
  fi

  # The installer persists PATH changes for future shells, but the current
  # shell needs the install directory added explicitly.
  codex_install_dir="${CODEX_INSTALL_DIR:-${HOME}/.local/bin}"
  export PATH="${codex_install_dir}:${PATH}"
  hash -r 2>/dev/null || true
fi

command -v codex >/dev/null 2>&1 || {
  echo "The Codex CLI installer completed, but codex is still not on PATH." >&2
  echo "Start a new shell and rerun this script." >&2
  exit 1
}

if ! codex login status >/dev/null 2>&1; then
  echo "Codex CLI is installed but not authenticated." >&2
  echo "A valid Codex client login is reused automatically (normally ~/.codex/auth.json)." >&2
  echo "Run 'codex login' once, then rerun this script." >&2
  exit 1
fi

marketplace_list="$(codex plugin marketplace list 2>/dev/null)"
if ! grep -Fq "$marketplace_name" <<<"$marketplace_list"; then
  codex plugin marketplace add "$marketplace_source"
fi

plugin_list="$(codex plugin list 2>/dev/null)"
if ! grep -Fq "comfyui-custom-nodes" <<<"$plugin_list"; then
  codex plugin add "$plugin_name"
fi

codex plugin list
