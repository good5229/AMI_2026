#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 scripts/normalize_source_semantics.py
python3 scripts/fetch_kasi_context.py
python3 scripts/fetch_kma_context.py
python3 scripts/run_context_ablation.py
python3 scripts/extract_ami_event_windows.py

cd lightguard_app
flutter analyze
flutter test
flutter build web --release --base-href /AMI_2026/
flutter build apk --debug
