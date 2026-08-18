#!/usr/bin/env bash
# Ensures an up-to-date Copilot CLI on startup.
# The GitHub Copilot Chat VS Code extension ships its own `copilot` binary that
# takes precedence on PATH and cannot always self-update. When `copilot update`
# fails to reach the expected version and the active binary is that bundled copy,
# install the CLI via npm and put it at the front of PATH instead.
set -euo pipefail

version_of() { copilot --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1; }

# Latest published release is the version `copilot update` should converge on.
expected="$(npm view @github/copilot version 2>/dev/null || true)"

# Update whatever copilot is currently on PATH (best effort).
if command -v copilot >/dev/null 2>&1; then
  copilot update >/dev/null 2>&1 || true
fi

current="$(version_of || true)"

if [ -n "$expected" ] && [ "$current" = "$expected" ]; then
  echo "Copilot CLI is up to date (${current})."
  exit 0
fi

echo "Copilot CLI is ${current:-missing}; expected ${expected:-unknown}."

install_via_npm() {
  npm install -g @github/copilot
  npm_bin="$(npm prefix -g 2>/dev/null)/bin"
  export PATH="${npm_bin}:${PATH}"
  hash -r 2>/dev/null || true
  # Persist the override so interactive terminals prefer the npm copy too.
  marker="# copilot-cli-npm-path"
  if ! grep -qF "$marker" "${HOME}/.bashrc" 2>/dev/null; then
    printf '\n%s\nexport PATH="%s:$PATH"\n' "$marker" "$npm_bin" >> "${HOME}/.bashrc"
  fi
  echo "Now using $(which copilot) ($(version_of))."
}

# Fall back to npm when copilot is missing entirely or the active binary is the
# extension-bundled copy that can't self-update.
location="$(which copilot 2>/dev/null || true)"
case "$location" in
  *github.copilot-chat*)
    echo "Active copilot is bundled with the Copilot Chat extension: ${location}"
    install_via_npm
    ;;
  "")
    echo "Copilot CLI is not installed; installing via npm."
    install_via_npm
    ;;
  *)
    echo "copilot resolves to ${location}; leaving PATH unchanged." >&2
    ;;
esac
