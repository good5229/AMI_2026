#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== v0.7 deterministic artifact generation =="
python3 scripts/run_v07_regional_seasonal_validation.py
first="$(shasum -a 256 lightguard_v0_1/reports/v07/reproducibility_manifest.json | awk '{print $1}')"
python3 scripts/run_v07_regional_seasonal_validation.py
second="$(shasum -a 256 lightguard_v0_1/reports/v07/reproducibility_manifest.json | awk '{print $1}')"
test "$first" = "$second"

echo "== artifact contracts =="
python3 scripts/test_v05_artifacts.py
python3 scripts/test_v06_artifacts.py
python3 scripts/test_v07_artifacts.py

echo "== Flutter quality gates =="
(
  cd lightguard_app
  flutter pub get
  flutter analyze
  flutter test
  flutter build web --release
  flutter build apk --release
)

echo "v0.7 preflight: PASS"
