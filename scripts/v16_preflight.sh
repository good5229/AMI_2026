#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
python3 scripts/build_v16_asset_scope.py
python3 scripts/freeze_v16_protocol.py
python3 scripts/build_v16_holdout.py
python3 scripts/run_v16_service_policy.py
python3 scripts/run_v16_service_statistics.py
python3 scripts/build_v16_report.py
python3 scripts/test_v16_artifacts.py
(cd lightguard_app && flutter pub get && flutter analyze && flutter test && flutter build web --release --base-href /AMI_2026/ && flutter build apk --release)
python3 scripts/test_v16_artifacts.py
echo "v0.16 experiment preflight PASS"
