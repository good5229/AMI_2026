#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_v23_regional_file_expansion.py
python3 scripts/test_v23_artifacts.py
echo "v23 regional file-data preflight: PASS"
