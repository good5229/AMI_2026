#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/test_v24_artifacts.py
echo "v24 nationwide census preflight: PASS"
