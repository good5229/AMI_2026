#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"

python3 scripts/freeze_v15_predecessors.py
python3 scripts/audit_v15_active_mechanisms.py
python3 scripts/build_v15_remaining_pool.py
python3 scripts/build_v15_counterfactual_holdout.py
python3 scripts/build_v15_ablation_configs.py
python3 scripts/run_v15_ablation.py

# Fail closed before statistics if any generator contract is incomplete.
for expected in lightguard_v0_1/data/validation/v15/v15_pair_results.csv lightguard_v0_1/data/validation/v15/v15_background_holdout_manifest.json lightguard_v0_1/data/validation/v15/v15_active_mechanism_registry.json; do
  [[ -f "$expected" ]] || { echo "missing required TERRA A artifact: $expected" >&2; exit 1; }
done
python3 scripts/run_v15_paired_statistics.py
python3 scripts/run_v15_natural_shadow.py
python3 scripts/build_v15_mechanism_grade.py
python3 scripts/build_v15_evidence_matrix.py
python3 scripts/build_v15_final_report.py
python3 scripts/test_v15_artifacts.py
(cd lightguard_app && flutter pub get && flutter analyze && flutter test && flutter build web --release --base-href /AMI_2026/ && flutter build apk --release)
python3 scripts/test_v15_artifacts.py
echo "v0.15 preflight PASS"
