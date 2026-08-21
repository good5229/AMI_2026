#!/usr/bin/env python3
"""Freeze v0.10 current-only injection provenance without detector outcomes."""

import json

from v10_ami import ROOT
from v10_counterfactual import construct_pairs

OUTPUT = ROOT / "lightguard_v0_1/data/validation/v10/v10_injection_manifest.json"

if __name__ == "__main__":
    pairs, manifest = construct_pairs()
    OUTPUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {status: sum(row["status"] == status for row in manifest["rows"]) for status in {row["status"] for row in manifest["rows"]}}
    print(json.dumps({"pool_units": len(manifest["rows"]), "constructable_pairs": len(pairs), "status_counts": counts, "manifest_sha256": manifest["injection_manifest_sha256"]}))

