#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

git config core.hooksPath .githooks
chmod +x .githooks/pre-push

printf 'Configured Git hooks for %s\n' "$repo_root"
printf 'Active hooks path: %s\n' "$(git config --get core.hooksPath)"
