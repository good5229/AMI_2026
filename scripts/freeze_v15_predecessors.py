#!/usr/bin/env python3
"""Freeze v0.10-v0.14 reproducibility/final claims and the H1 runtime config."""
from __future__ import annotations

from v15_common import DATA, LEGACY_PREDECESSOR_FREEZE, PREDECESSOR_FREEZE, RAW_SHA256, ROOT, V10, canonical_json_sha, file_hashes, load_json, require, sha256_file, write_json


def main() -> None:
    predecessor_paths = []
    for version in ("v10", "v11", "v13", "v14"):
        predecessor_paths.extend((ROOT / f"lightguard_v0_1/reports/{version}/reproducibility_manifest.json", ROOT / f"lightguard_v0_1/reports/{version}/{version}_final_summary.md"))
    predecessor_paths.extend((ROOT / "lightguard_v0_1/reports/v12r/reproducibility_manifest.json", ROOT / "lightguard_v0_1/reports/v12r/v12r_final_summary.md"))
    v09 = V10 / "v09_freeze_manifest.json"
    raw_manifest = V10 / "v10_raw_ami_manifest.json"
    raw = load_json(raw_manifest)
    require(raw.get("source", {}).get("sha256") == RAW_SHA256, "BLOCKED_RAW_AMI_HASH_MISMATCH")
    h1 = load_json(v09).get("candidate", {})
    require(h1.get("name") == "H1", "BLOCKED_H1_REGISTRY_MISSING")
    payload = {
        "schema_version": "lightguard.v15.predecessor-freeze.1",
        "status": "PRE_OUTCOME_FROZEN",
        "predecessor_artifacts": file_hashes(predecessor_paths),
        "raw_ami": {"manifest": str(raw_manifest.relative_to(ROOT)), "manifest_sha256": sha256_file(raw_manifest), "source_sha256": RAW_SHA256, "raw_values_written": False},
        "h1_registry": {"path": str(v09.relative_to(ROOT)), "file_sha256": sha256_file(v09), "detector": h1, "config_sha256": canonical_json_sha(h1)},
        "prohibitions": ["no predecessor modification", "no raw AMI write", "no Office write", "no outcome-dependent selection", "no threshold retune"],
    }
    payload["freeze_sha256"] = canonical_json_sha(payload)
    # The v0.15 contract requires the v14-named predecessor freeze.  Keep the
    # initial Wave-2 name as a byte-equivalent compatibility alias.
    write_json(PREDECESSOR_FREEZE, payload)
    write_json(LEGACY_PREDECESSOR_FREEZE, payload)


if __name__ == "__main__":
    main()
