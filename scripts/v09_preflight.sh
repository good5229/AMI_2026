#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== frozen predecessor contracts =="
python3 scripts/test_v07_freeze.py
python3 scripts/test_v08_artifacts.py

echo "== v0.9 deterministic generation: pass 1 =="
python3 scripts/audit_v08_false_positives.py
python3 scripts/build_v09_episode_manifest.py
python3 scripts/build_v09_scenarios.py
python3 scripts/run_v09_calibration.py
python3 scripts/run_v09_confirmatory.py
python3 scripts/run_v09_boundary_analysis.py
python3 scripts/run_v09_episode_bootstrap.py
python3 scripts/run_v09_actual_ami_regression.py
python3 scripts/build_v09_final_report.py
first="$(shasum -a 256 lightguard_v0_1/reports/v09/reproducibility_manifest.json | awk '{print $1}')"

echo "== v0.9 deterministic generation: pass 2 =="
python3 scripts/audit_v08_false_positives.py >/dev/null
python3 scripts/build_v09_episode_manifest.py >/dev/null
python3 scripts/build_v09_scenarios.py >/dev/null
python3 scripts/run_v09_calibration.py >/dev/null
python3 scripts/run_v09_confirmatory.py >/dev/null
python3 scripts/run_v09_boundary_analysis.py >/dev/null
python3 scripts/run_v09_episode_bootstrap.py >/dev/null
python3 scripts/run_v09_actual_ami_regression.py >/dev/null
python3 scripts/build_v09_final_report.py >/dev/null
second="$(shasum -a 256 lightguard_v0_1/reports/v09/reproducibility_manifest.json | awk '{print $1}')"
test "$first" = "$second"
python3 scripts/test_v09_artifacts.py

echo "== Flutter quality gates =="
(
  cd lightguard_app
  flutter pub get
  flutter analyze
  flutter test
  flutter build web --release --base-href /AMI_2026/
  flutter build apk --release
)

echo "v0.9 preflight: PASS"
