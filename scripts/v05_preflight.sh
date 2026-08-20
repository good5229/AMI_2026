#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/lightguard_v0_1/reports/v05/reproducibility_manifest.json"
FIRST_MANIFEST="$(mktemp)"
trap 'rm -f "$FIRST_MANIFEST"' EXIT

cd "$ROOT"

echo "== v0.5 deterministic run 1 =="
python3 scripts/run_v05_all.py
cp "$MANIFEST" "$FIRST_MANIFEST"

echo "== v0.5 deterministic run 2 =="
python3 scripts/run_v05_all.py

python3 - "$FIRST_MANIFEST" "$MANIFEST" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    first = json.load(handle)
with open(sys.argv[2], encoding="utf-8") as handle:
    second = json.load(handle)

for key in ("input_hashes", "output_hashes", "frozen_config"):
    if first.get(key) != second.get(key):
        raise SystemExit(f"determinism check failed: {key} differs")
print("determinism check passed: input/output hashes and frozen configuration match")
PY

echo "== v0.5 artifact contract =="
python3 scripts/test_v05_artifacts.py

cd "$ROOT/lightguard_app"
echo "== flutter pub get =="
flutter pub get
echo "== flutter analyze =="
flutter analyze
echo "== flutter test =="
flutter test
echo "== flutter web release =="
flutter build web --release --base-href /AMI_2026/
echo "== flutter android release =="
flutter build apk --release

echo "v0.5 preflight passed"
