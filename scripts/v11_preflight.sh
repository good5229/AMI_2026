#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== v0.11 full raw label audit =="
python3 scripts/audit_all_label_sources.py
echo "== v0.11 independent proxy scoring =="
python3 scripts/run_v11_independent_detectors.py
echo "== v0.11 release assembly =="
python3 scripts/build_v11_release.py
echo "== v0.11 artifact contract =="
python3 scripts/test_v11_artifacts.py
echo "== Flutter dependencies =="
cd lightguard_app
flutter pub get
echo "== Flutter analyze =="
flutter analyze
echo "== Flutter test =="
flutter test
echo "== Flutter web release =="
flutter build web
echo "== Flutter Android release =="
flutter build apk
echo "== v0.11 preflight PASS =="
