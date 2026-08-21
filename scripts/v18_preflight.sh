#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
python3 scripts/build_v18_triage.py
python3 scripts/test_v18_artifacts.py
(cd lightguard_app && flutter pub get && flutter analyze && flutter test && flutter build web --release --base-href /AMI_2026/ && flutter build apk --release)
python3 scripts/test_v18_artifacts.py
echo "v0.18 retrospective operational triage preflight PASS"
