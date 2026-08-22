#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/build_v21_submission_package.py
before="$(find lightguard_v0_1/data/submission lightguard_v0_1/reports/v21 submission lightguard_app/docs/v21_submission_readiness.md -type f -print0 | sort -z | xargs -0 shasum -a 256 | shasum -a 256)"
python3 scripts/build_v21_submission_package.py
after="$(find lightguard_v0_1/data/submission lightguard_v0_1/reports/v21 submission lightguard_app/docs/v21_submission_readiness.md -type f -print0 | sort -z | xargs -0 shasum -a 256 | shasum -a 256)"
test "$before" = "$after"
python3 scripts/audit_v21_metrics.py
python3 scripts/audit_v21_forbidden_claims.py
python3 scripts/test_v21_submission.py

cd lightguard_app
flutter pub get
flutter analyze
flutter test
flutter build web
flutter build apk
cd ..
python3 scripts/audit_v21_metrics.py
python3 scripts/audit_v21_forbidden_claims.py
python3 scripts/test_v21_submission.py
python3 - <<'PY'
import json
from pathlib import Path

path = Path("lightguard_v0_1/reports/v21/v21_preflight_report.json")
report = {
    "version": "0.21",
    "status": "PASS",
    "deterministic_submission_rebuild": "PASS",
    "predecessor_integrity": "PASS",
    "metric_consistency": "PASS",
    "forbidden_claim_scan": "PASS",
    "submission_contract": "PASS",
    "flutter_pub_get": "PASS",
    "flutter_analyze": "PASS_NO_ISSUES",
    "flutter_test": "PASS",
    "flutter_web_release_build": "PASS",
    "flutter_android_release_build": "PASS",
    "web_artifact": "lightguard_app/build/web",
    "android_artifact": "lightguard_app/build/app/outputs/flutter-apk/app-release.apk",
    "predictive_retuning_count": 0,
}
path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
python3 scripts/build_v21_evidence_manifest.py
python3 scripts/audit_v21_metrics.py
python3 scripts/audit_v21_forbidden_claims.py
python3 scripts/test_v21_submission.py
echo "v0.21 full preflight: PASS"
