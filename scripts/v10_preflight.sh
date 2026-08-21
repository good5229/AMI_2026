#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== v0.9 predecessor contract =="
python3 scripts/test_v09_artifacts.py

echo "== v0.10 deterministic generation pass 1 =="
python3 scripts/audit_v10_raw_ami.py
python3 scripts/build_v10_freeze.py
python3 scripts/build_v10_background_pool.py
python3 scripts/build_v10_counterfactual_pairs.py
python3 scripts/reconcile_v10_b_l_12.py
python3 scripts/run_v10_h1_transport.py
python3 scripts/run_v10_shadow_replay.py
python3 scripts/analyze_v10_meter_drift.py
python3 scripts/run_v10_cluster_bootstrap.py
python3 scripts/build_v10_final_report.py
find lightguard_v0_1/data/validation/v10 lightguard_v0_1/reports/v10 lightguard_app/assets/data/context/v10_real_background_summary.json -type f -print0 | sort -z | xargs -0 shasum -a 256 > /tmp/lightguard_v10_pass1.sha

echo "== v0.10 deterministic generation pass 2 =="
python3 scripts/audit_v10_raw_ami.py >/dev/null
python3 scripts/build_v10_freeze.py >/dev/null
python3 scripts/build_v10_background_pool.py >/dev/null
python3 scripts/build_v10_counterfactual_pairs.py >/dev/null
python3 scripts/reconcile_v10_b_l_12.py >/dev/null
python3 scripts/run_v10_h1_transport.py >/dev/null
python3 scripts/run_v10_shadow_replay.py >/dev/null
python3 scripts/analyze_v10_meter_drift.py >/dev/null
python3 scripts/run_v10_cluster_bootstrap.py >/dev/null
python3 scripts/build_v10_final_report.py >/dev/null
find lightguard_v0_1/data/validation/v10 lightguard_v0_1/reports/v10 lightguard_app/assets/data/context/v10_real_background_summary.json -type f -print0 | sort -z | xargs -0 shasum -a 256 > /tmp/lightguard_v10_pass2.sha
cmp /tmp/lightguard_v10_pass1.sha /tmp/lightguard_v10_pass2.sha
python3 scripts/test_v10_artifacts.py

echo "== Flutter quality gates =="
(cd lightguard_app && flutter pub get && flutter analyze && flutter test && flutter build web --release --base-href /AMI_2026/ && flutter build apk --release)
echo "v0.10 preflight: PASS"
