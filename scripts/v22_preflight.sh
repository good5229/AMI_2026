#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_v22_regional_expansion.py
python3 scripts/test_v22_artifacts.py
echo "v22 regional expansion preflight: PASS"
