#!/usr/bin/env python3
"""Freeze predecessor hashes and the three-lane policy before outcomes."""
from v16_common import DATA, REPORT, V10, V15, canonical_sha, load_json, require, sha256_file, write_json


def main() -> None:
    asset = load_json(DATA / "v16_asset_scope_registry.json")
    v09 = load_json(V10 / "v09_freeze_manifest.json")
    h1 = v09["candidate"]
    require(h1["name"] == "H1", "BLOCKED_H1_FREEZE_MISSING")
    predecessors = [
        V15 / "v14_freeze_manifest.json",
        V15 / "v15_background_holdout_manifest.json",
        V15 / "v15_pair_results_manifest.json",
        REPORT.parent / "v15/v15_final_summary.md",
        REPORT.parent / "v15/v15_independent_audit.md",
    ]
    payload = {
        "schema_version": "lightguard.v16.protocol-freeze.1",
        "status": "POST_HOC_EXPLORATORY_POLICY_REVISION_2",
        "predecessor_sha256": {str(path.relative_to(DATA.parents[3])): sha256_file(path) for path in predecessors},
        "asset_registry_sha256": asset["registry_sha256"],
        "h1_candidate": h1,
        "h1_threshold_retuned": False,
        "confirmation_boundary": 0.5,
        "policies": {
            "P0_COLLAPSED_NON_NORMAL": "normal=no_action; every non-normal action=field_inspection_candidate, reproducing the v0.15 collapsed endpoint semantics",
            "P1_GUARDED_LANES": "same H1 threshold; data_check_required=data_quality_review; observe/inspect requires activation+persistence >=0.5 and phase>=0.5 only when expected_phase_count=3",
        },
        "descriptive_endpoints": ["controlled_anomaly_field_dispatch_capture", "controlled_benign_field_dispatch_escalation"],
        "prospective_noninferiority_margin": -0.10,
        "inferential_statistics_permitted": False,
        "selection_uses_outcome": False,
        "claim_boundary": "post-hoc controlled service-routing replay only",
    }
    payload["freeze_sha256"] = canonical_sha(payload)
    write_json(DATA / "v16_protocol_freeze.json", payload)


if __name__ == "__main__":
    main()
