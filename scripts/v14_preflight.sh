#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== v0.14 local raw manifest (no network) =="
python3 scripts/fetch_v14_external_sources.py
echo "== v0.14 suitability and predecessor freeze =="
python3 scripts/audit_v14_dataset_suitability.py
echo "== v0.14 physical mapping seal =="
python3 scripts/build_v14_physical_mapping.py
echo "== v0.14 London provenance gate =="
python3 scripts/run_v14_london.py
echo "== v0.14 CoDEx-VFD aggregate run evaluation =="
python3 scripts/run_v14_codex_vfd.py
echo "== v0.14 SustDataED2 UTC positive control =="
python3 scripts/run_v14_sustdata.py
echo "== v0.14 cross-dataset mechanism matrix =="
python3 scripts/build_v14_cross_dataset_matrix.py
echo "== v0.14 canonical evidence matrix =="
python3 scripts/build_v14_evidence_matrix.py
echo "== v0.14 final aggregate reports =="
python3 scripts/build_v14_final_report.py
echo "== v0.14 artifact contract =="
python3 scripts/test_v14_artifacts.py
echo "== flutter pub get =="
(cd lightguard_app && flutter pub get)
echo "== flutter analyze =="
(cd lightguard_app && flutter analyze)
echo "== flutter test =="
(cd lightguard_app && flutter test)
echo "== flutter web release =="
(cd lightguard_app && flutter build web --release --base-href /AMI_2026/)
echo "== flutter android release =="
(cd lightguard_app && flutter build apk --release)
echo "== v0.14 final artifact contract =="
python3 scripts/test_v14_artifacts.py
echo "== v0.14 preflight PASS =="
