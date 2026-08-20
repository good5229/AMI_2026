#!/usr/bin/env bash

set -euo pipefail

git config core.hooksPath .githooks
git config --get core.hooksPath

if [[ ! -x ".githooks/pre-commit" ]]; then
  echo "⚠️  pre-commit hook is missing or not executable at .githooks/pre-commit"
  exit 1
fi

echo "✅ Git hook path configured to .githooks"
