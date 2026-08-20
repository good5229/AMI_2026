#!/usr/bin/env python3
"""Seal the already reviewed v0.13 feature mapping/config before test access."""
from __future__ import annotations

from v13_common import (
    RAW_ROOT, V13ContractError, atomic_write_json, load_json, protocol_paths, sha256_file,
)


def main() -> None:
    paths = protocol_paths()
    raw_manifest = load_json(paths["raw_manifest"])
    if raw_manifest.get("phase") != "PRE_CONFIRMATORY":
        raise V13ContractError("Raw manifest must be created before any confirmatory test-label access")
    mapping = load_json(paths["mapping"])
    config = load_json(paths["config"])
    if mapping.get("status") != "PRE_OUTCOME_FROZEN" or config.get("status") != "PRE_OUTCOME_FROZEN":
        raise V13ContractError("Feature mapping/config are not frozen")
    mad_hash = sha256_file(RAW_ROOT / "MAD" / "MAD.npz")
    if raw_manifest.get("datasets", {}).get("MAD", {}).get("mad_npz_sha256") != mad_hash:
        raise V13ContractError("Raw MAD hash differs from pre-confirmatory audit")
    seal = {
        "schema_version": "v13-preconfirmatory-config-seal-1",
        "phase": "PRE_CONFIRMATORY",
        "claim_boundary": config["primary_metric"]["claim_boundary"],
        "threshold_grid": config["split_and_calibration"]["threshold_grid"],
        "lg_s3_status": "UNAVAILABLE_NORMALIZATION_PROVENANCE",
        "track_b_status": "NOT_ASSESSABLE_NO_METER_IDS_OR_TIMESTAMPS",
        "input_sha256": {
            "mapping": sha256_file(paths["mapping"]),
            "config": sha256_file(paths["config"]),
            "protocol": sha256_file(paths["protocol"]),
            "raw_mad_npz": mad_hash,
        },
    }
    atomic_write_json(paths["feature_seal"], seal, immutable=True)
    print(f"Pre-confirmatory seal verified: {paths['feature_seal']}")


if __name__ == "__main__":
    main()
