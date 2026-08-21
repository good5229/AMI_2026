#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
find lightguard_v0_1/data/validation/v18 lightguard_v0_1/reports/v18 -type f -exec shasum -a 256 {} + | LC_ALL=C sort > /tmp/lightguard_v18_before.sha
python3 scripts/build_v19_buyeo.py
shasum -a 256 lightguard_v0_1/data/validation/v19/v19_artifact_manifest.json > /tmp/lightguard_v19_first.sha
python3 scripts/build_v19_buyeo.py
shasum -a 256 lightguard_v0_1/data/validation/v19/v19_artifact_manifest.json > /tmp/lightguard_v19_second.sha
cmp /tmp/lightguard_v19_first.sha /tmp/lightguard_v19_second.sha
find lightguard_v0_1/data/validation/v18 lightguard_v0_1/reports/v18 -type f -exec shasum -a 256 {} + | LC_ALL=C sort > /tmp/lightguard_v18_after.sha
cmp /tmp/lightguard_v18_before.sha /tmp/lightguard_v18_after.sha
python3 scripts/test_v19_artifacts.py
cd lightguard_app
flutter pub get
flutter analyze
flutter test
flutter build web
flutter build apk
cd ..
python3 scripts/test_v19_artifacts.py
echo "v0.19 Buyeo independent municipal validation preflight PASS"
