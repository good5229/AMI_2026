#!/usr/bin/env python3
"""Fail-closed v0.14 aggregate artifact contract."""
from __future__ import annotations

import subprocess

from v14_common import CLAIM, DATA, REPORTS, ROOT, load_json, read_csv, require, sha256


def main() -> None:
    freeze = load_json(DATA / "v13_freeze_manifest.json")
    require(freeze["primary_gate"] == "NOT_EVALUABLE_INCOMPLETE_COVERAGE", "v0.13 status changed")
    require(freeze["mad_sc3_balanced_accuracy"] == 0.52004485, "v0.13 MAD value changed")
    require(freeze["z_score_balanced_accuracy"] == 0.66598258, "v0.13 comparator value changed")
    raw = load_json(DATA / "v14_raw_external_manifest.json")
    require(all(not x.get("partial_run") or x["bytes"] <= 16 * 1024 * 1024 for x in raw["files"]), "CoDEx byte cap violated")
    require(len(raw["files"]) == 59 and all(str(x.get("source", "")).startswith("https://") for x in raw["files"]), "raw source provenance is incomplete")
    london = read_csv(REPORTS / "v14_london_results.csv")
    require(london[0]["status"] == "PRIMARY_BLOCKED_PROVENANCE", "London provenance block weakened")
    codex = read_csv(REPORTS / "v14_codex_vfd_results.csv")
    sust = read_csv(REPORTS / "v14_sustdata_results.csv")
    require(all(x["independent_unit"] == "measurement_run" for x in codex), "CoDEx inference unit is not run")
    require(all(x["role"] == "TRANSITION_POSITIVE_CONTROL_ONLY" for x in sust), "SustData fault overclaim")
    evaluated = sum(any(x["status"].startswith("EVALUATED") for x in rows) for rows in (codex, sust))
    require(evaluated >= 2, "v0.14 requires two actually evaluated eligible physical-provenance tracks")
    cross = read_csv(REPORTS / "v14_cross_dataset_mechanism_matrix.csv")
    require(not any("LIMITED_MECHANISM_SIGN" in x["transfer_conclusion"] for x in cross), "execution was overclaimed as a mechanism sign")
    pmc3 = {x["dataset"]: x["status"] for x in cross if x["mechanism"] == "PMC-3"}
    require(pmc3.get("CoDEx-VFD") == "NOT_AVAILABLE", "CoDEx PMC-3 must be unavailable")
    require(pmc3.get("SustDataED2") == "N/A", "SustData PMC-3 must be N/A")
    case = read_csv(DATA / "v14_case_evidence_matrix.csv")
    require(len(case) == 6, "canonical-six count changed")
    forbidden = {"probability", "accuracy", "recall", "precision", "fpr", "specificity"}
    require(not forbidden.intersection(x.lower() for x in case[0]), "case matrix contains prohibited metric column")
    manifest = load_json(REPORTS / "reproducibility_manifest.json")
    for item in manifest["files"]:
        path = ROOT / item["path"]
        require(path.is_file() and sha256(path) == item["sha256"], f"hash mismatch: {item['path']}")
    tracked = subprocess.run(["git", "ls-files", "official_docs/external_benchmarks_v14"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    require(not tracked, "raw v0.14 data is tracked")
    texts = "\n".join((REPORTS / name).read_text(encoding="utf-8") for name in ("v14_final_summary.md", "v14_mad_predecessor_context.md"))
    require(CLAIM in texts, "claim boundary missing")
    require("0 of 30 injection-positive" in texts and "not replicated" in texts, "CoDEx negative outcome is missing")
    require("2 of 18 appliance clusters" in texts and "inconclusive" in texts, "SustData inconclusive outcome is missing")
    print("v0.14 artifact contract PASS")


if __name__ == "__main__":
    main()
