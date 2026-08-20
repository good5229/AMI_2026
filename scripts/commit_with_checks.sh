#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOOKS_DIR="${PROJECT_ROOT}/.githooks"

if [[ ! -d "${HOOKS_DIR}" || ! -x "${HOOKS_DIR}/pre-commit" ]]; then
  echo "pre-commit hook is not installed."
  echo "Run: ./scripts/setup_githook.sh"
  exit 1
fi

"${SCRIPT_DIR}/launch_preflight.sh"

if [[ $# -eq 0 ]]; then
  echo "Usage: ./scripts/commit_with_checks.sh -m \"message\" [git commit args]"
  echo "Example: ./scripts/commit_with_checks.sh -m \"feat: ...\""
  exit 1
fi

echo "== lightguard preflight PASSED =="
git -C "${PROJECT_ROOT}" commit "$@"
