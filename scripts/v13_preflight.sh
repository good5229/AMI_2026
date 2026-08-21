#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== v0.13 offline locator =="
python3 scripts/fetch_v13_external_datasets.py --acknowledge-no-download
echo "== v0.13 preconfirmatory audit =="
python3 scripts/audit_v13_external_datasets.py
echo "== v0.13 feature/config seal =="
python3 scripts/build_v13_feature_mapping.py
echo "== v0.13 MAD train/calibration =="
python3 scripts/run_v13_mad_train.py
echo "== v0.13 MAD confirmatory =="
python3 scripts/run_v13_mad_confirmatory.py
echo "== v0.13 REFIT gate =="
python3 scripts/run_v13_refit.py
echo "== v0.13 UCR gate =="
python3 scripts/run_v13_ucr.py
echo "== v0.13 canonical evidence =="
python3 scripts/build_v13_evidence_matrix.py
echo "== v0.13 final reports =="
python3 scripts/build_v13_final_report.py
echo "== v0.13 artifact contract =="
python3 scripts/test_v13_artifacts.py
echo "== flutter pub get =="
(cd lightguard_app && flutter pub get)
echo "== flutter analyze =="
(cd lightguard_app && flutter analyze)
echo "== flutter test =="
(cd lightguard_app && flutter test)
echo "== flutter web release =="
(cd lightguard_app && flutter build web --release --base-href /AMI_2026/)
echo "== flutter android release =="
(cd lightguard_app && flutter build apk --release)
echo "== v0.13 final artifact contract =="
python3 scripts/test_v13_artifacts.py
echo "== v0.13 preflight PASS =="
