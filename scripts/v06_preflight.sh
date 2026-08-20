#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/lightguard_v0_1/reports/v06/reproducibility_manifest.json"
FIRST="$(mktemp)"
trap 'rm -f "$FIRST"' EXIT
cd "$ROOT"

python3 scripts/run_v05_all.py
python3 scripts/run_v06_evidence_hardening.py
cp "$MANIFEST" "$FIRST"
python3 scripts/run_v06_evidence_hardening.py
python3 - "$FIRST" "$MANIFEST" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    first = json.load(handle)
with open(sys.argv[2], encoding="utf-8") as handle:
    second = json.load(handle)
for key in ("input_hashes", "output_hashes", "frozen_config"):
    if first[key] != second[key]:
        raise SystemExit(f"v0.6 determinism failed: {key}")
print("v0.6 determinism: PASS")
PY
python3 scripts/test_v05_artifacts.py
python3 scripts/test_v06_artifacts.py

cd "$ROOT/lightguard_app"
flutter pub get
flutter analyze
flutter test
flutter build web --release --base-href /AMI_2026/
flutter build apk --release
echo "v0.6 preflight: PASS"
