#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT"
echo "== v0.4: official KMA weather regimes =="
python3 scripts/fetch_kma_weather_regimes.py
echo "== v0.4: ranking and holdout validation =="
python3 scripts/run_v04_validation.py
echo "== v0.4: artifact integrity =="
python3 scripts/test_v04_artifacts.py
cd "$ROOT/lightguard_app"
echo "== v0.4: flutter analyze =="
flutter analyze
echo "== v0.4: flutter test =="
flutter test
echo "== v0.4: flutter web release =="
flutter build web --release --base-href /AMI_2026/
echo "== v0.4: android debug =="
flutter build apk --debug
echo "== v0.4 preflight: PASS =="
