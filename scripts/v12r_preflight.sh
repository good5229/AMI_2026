#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== v0.12R freeze =="
python3 scripts/build_v12r_freeze.py
echo "== literature registry and evidence joins =="
python3 scripts/build_v12r_evidence_artifacts.py
echo "== blinded review packet freeze =="
python3 scripts/build_v12r_review_manifest.py
echo "== human import gate =="
python3 scripts/import_v12r_human_review.py
echo "== human analysis gate =="
python3 scripts/analyze_v12r_human_review.py
echo "== release report =="
python3 scripts/build_v12r_final_report.py
echo "== v0.12R artifact contract =="
python3 scripts/test_v12r_artifacts.py

cd lightguard_app
echo "== Flutter dependencies =="
flutter pub get
echo "== Flutter analyze =="
flutter analyze
echo "== Flutter test =="
flutter test
echo "== Flutter web release =="
flutter build web
echo "== Flutter Android release =="
flutter build apk
cd "$ROOT"

echo "== final release seal =="
V12R_PREFLIGHT_PASS=1 python3 scripts/build_v12r_final_report.py
python3 scripts/test_v12r_artifacts.py
echo "== v0.12R preflight PASS =="
