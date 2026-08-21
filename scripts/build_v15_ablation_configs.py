#!/usr/bin/env python3
"""Freeze v0.15 runtime variants before pair outcomes are accessed."""
from __future__ import annotations

from v15_common import HOLDOUT_MANIFEST, PREDECESSOR_FREEZE, DATA, VARIANT_FIELDS, canonical_json_sha, load_json, require, write_json


def main() -> None:
    freeze = load_json(PREDECESSOR_FREEZE)
    holdout = load_json(HOLDOUT_MANIFEST)
    detector = freeze["h1_registry"]["detector"]
    thresholds = detector["config"]
    variants = {
        "A0": {"label": "Full H1", "runtime": "H1", "remove": [], "threshold": thresholds, "alias_status": "PRIMARY"},
        "A1": {"label": "minus persistence", "runtime": "H1", "remove": ["persistence"], "active_only": True, "threshold": thresholds, "alias_status": "PRIMARY"},
        "A2": {"label": "minus phase, eligible pairs only", "runtime": "H1", "remove": ["phase"], "active_only": True, "requires_phase_gate": True, "threshold": thresholds, "alias_status": "PRIMARY"},
        "A3": {"label": "minus specificity/contradiction gate", "runtime": "threshold_only", "remove": ["specificity", "contradiction"], "threshold": thresholds, "alias_status": "ALIAS_OF_A4", "alias_reason": "current H1 registry has no remaining post-Stage-A action branch when specificity and contradiction are removed"},
        "A4": {"label": "Stage-A-only", "runtime": "threshold_only", "remove": ["specificity", "contradiction"], "threshold": thresholds, "alias_status": "CANONICAL_FOR_A3_ALIAS"},
        "A5": {"label": "minus baseline-relative", "runtime": "H1", "remove": ["baseline_relative"], "active_only": True, "threshold": thresholds, "alias_status": "PRIMARY"},
        "Z1": {"label": "robust meter-relative z", "runtime": "robust_meter_z", "remove": [], "threshold": thresholds, "alias_status": "COMPARATOR"},
    }
    require(tuple(variants) == VARIANT_FIELDS, "BLOCKED_VARIANT_REGISTRY_DRIFT")
    payload = {"schema_version": "lightguard.v15.ablation-config.1", "status": "PRE_OUTCOME_FROZEN", "predecessor_freeze_sha256": freeze["freeze_sha256"], "holdout_sha256": holdout["holdout_sha256"], "h1_config_sha256": freeze["h1_registry"]["config_sha256"], "active_runtime_components_only": True, "inactive_mechanism_policy": "NOT_EVALUABLE_INACTIVE_MECHANISM; never impute or ablate inactive mechanisms", "no_threshold_retune": True, "variants": variants}
    payload["config_sha256"] = canonical_json_sha(payload)
    write_json(DATA / "v15_ablation_configs.json", payload)


if __name__ == "__main__":
    main()
