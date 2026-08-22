#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

freeze_before="$(find lightguard_v0_1/data/validation/v19 lightguard_v0_1/reports/v19 -type f -print0 | sort -z | xargs -0 shasum -a 256 | shasum -a 256)"
python3 scripts/build_v20_ulsan.py
manifest_before="$(shasum -a 256 lightguard_v0_1/data/validation/v20/v20_artifact_manifest.json)"
python3 scripts/build_v20_ulsan.py
manifest_after="$(shasum -a 256 lightguard_v0_1/data/validation/v20/v20_artifact_manifest.json)"
test "$manifest_before" = "$manifest_after"
python3 scripts/test_v20_artifacts.py
freeze_after="$(find lightguard_v0_1/data/validation/v19 lightguard_v0_1/reports/v19 -type f -print0 | sort -z | xargs -0 shasum -a 256 | shasum -a 256)"
test "$freeze_before" = "$freeze_after"

cd lightguard_app
flutter pub get
flutter analyze
flutter test
flutter build web
flutter build apk
cd ..
python3 scripts/test_v20_artifacts.py
echo "v0.20 full preflight: PASS"
