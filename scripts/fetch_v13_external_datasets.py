#!/usr/bin/env python3
"""Offline v0.13 source locator.

The frozen protocol prohibits automatic downloading.  This script records only
what an operator has already placed in ignored official_docs/external_benchmarks.
"""
from __future__ import annotations

import argparse
import json

from v13_common import RAW_ROOT, V13_DATA, V13ContractError, atomic_write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Report offline v0.13 source availability; never download.")
    parser.add_argument("--acknowledge-no-download", action="store_true", help="Required explicit acknowledgement.")
    args = parser.parse_args()
    if not args.acknowledge_no_download:
        raise V13ContractError("Automatic download is prohibited; rerun with --acknowledge-no-download")
    inventory = {
        "schema_version": "v13-offline-source-locator-1",
        "network_access": "DISABLED_BY_PROTOCOL",
        "raw_root": str(RAW_ROOT),
        "availability": {
            "MAD": (RAW_ROOT / "MAD" / "MAD.npz").is_file(),
            "REFIT_ANNOTATED_LOAD": (RAW_ROOT / "REFIT").exists(),
            "UCR_ITALIANPOWERDEMAND": (RAW_ROOT / "UCR_Italianpowerdemand").is_dir(),
        },
    }
    atomic_write_json(V13_DATA / "v13_offline_source_locator.json", inventory)
    print(json.dumps(inventory, sort_keys=True))


if __name__ == "__main__":
    main()
