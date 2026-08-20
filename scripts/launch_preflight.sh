#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
APP_DIR="${PROJECT_ROOT}/lightguard_app"

cd "${APP_DIR}"

echo "== lightguard preflight: flutter pub get =="
flutter pub get

echo "== lightguard preflight: flutter analyze =="
flutter analyze

echo "== lightguard preflight: flutter test =="
flutter test --reporter expanded --no-dds

echo "== lightguard preflight: flutter build web --release --base-href /AMI_2026/ =="
flutter build web --release --base-href /AMI_2026/

echo "== lightguard preflight: flutter build apk --debug =="
flutter build apk --debug

echo "== lightguard preflight: PASS =="
