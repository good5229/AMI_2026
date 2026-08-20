#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== v0.7 freeze integrity =="
python3 scripts/test_v07_freeze.py

echo "== v0.8 deterministic generation: pass 1 =="
python3 scripts/run_v08_failure_audit.py
python3 scripts/build_v08_design.py --check
python3 scripts/run_v08_calibration.py
python3 scripts/test_v08_calibration.py
python3 scripts/run_v08_confirmatory.py
python3 scripts/run_v08_factor_analysis.py
python3 scripts/run_v08_feature_availability.py
python3 scripts/build_v08_final_report.py
first="$(shasum -a 256 lightguard_v0_1/reports/v08/reproducibility_manifest.json | awk '{print $1}')"

echo "== v0.8 deterministic generation: pass 2 =="
python3 scripts/run_v08_calibration.py >/dev/null
python3 scripts/run_v08_confirmatory.py >/dev/null
python3 scripts/run_v08_factor_analysis.py >/dev/null
python3 scripts/run_v08_feature_availability.py >/dev/null
python3 scripts/build_v08_final_report.py >/dev/null
second="$(shasum -a 256 lightguard_v0_1/reports/v08/reproducibility_manifest.json | awk '{print $1}')"
test "$first" = "$second"
python3 scripts/test_v08_artifacts.py

echo "== Flutter quality gates =="
(
  cd lightguard_app
  flutter pub get
  flutter analyze
  flutter test
  flutter build web --release --base-href /AMI_2026/
  flutter build apk --release
)

echo "v0.8 preflight: PASS"
