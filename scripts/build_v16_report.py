#!/usr/bin/env python3
import csv

from v16_common import DATA, REPORT, load_json


def read(path):
    with path.open(newline="", encoding="utf-8") as stream: return list(csv.DictReader(stream))


def main() -> None:
    assets = load_json(DATA / "v16_asset_scope_registry.json")
    holdout = load_json(DATA / "v16_service_holdout_manifest.json")
    utility = read(REPORT / "v16_paired_service_utility.csv")
    results = read(DATA / "v16_service_policy_results.csv")
    single = {row["meter_id"] for row in results if row["policy"] == "P1_GUARDED_LANES" and row["expected_phase_count"] == "1" and row["status"] == "OK"}
    triple = {row["meter_id"] for row in results if row["policy"] == "P1_GUARDED_LANES" and row["expected_phase_count"] == "3" and row["status"] == "OK"}
    lines = [
        "# LightGuard v0.16 competition-aligned action utility", "",
        "## Official competition alignment", "",
        "- Business fit: converts AMI evidence into explicit operator work lanes.",
        "- Development feasibility: reuses frozen H1 and adds a deterministic action policy.",
        "- Idea specificity and completeness: fixes asset eligibility, evidence, lane, and next action contracts.",
        "- Use purpose and tangible effect: reports controlled field-dispatch candidates avoided, never actual savings.",
        "- Generality: covers all official streetlight assets and both official supply-phase classes.", "",
        "## Frozen v0.15 failure diagnosis", "",
        "- Data-quality review and field dispatch were conflated in the benign endpoint.",
        "- Frozen H1 emitted normal, observe, and data_check_required but no inspect action on the replay corpus.",
        "- A5 removed the general action-generating evidence rather than a targeted benign guardrail.",
        "- A2 was structurally unavailable on the two official single-phase meters.", "",
        "## Official asset scope", "",
        f"- Official meters: {assets['official_asset_count']}",
        f"- Streetlight eligible: {assets['streetlight_eligible_count']}",
        f"- Out of LightGuard scope: {assets['out_of_scope_count']}",
        "- The 124 out-of-scope meters are eligibility controls, not normal labels or FPR evidence.", "",
        "## Frozen disjoint holdout", "",
        f"- Pairs: {holdout['selected_count']}", f"- Meters: {holdout['meter_count']}",
        f"- v0.10 overlap: {holdout['v10_overlap_count']}", f"- v0.15 replayed pairs: {holdout['v15_reused_pair_count']}", f"- Pre-outcome B-L-12 extension pairs: {holdout['b_l_12_extension_count']}", f"- canonical overlap: {holdout['canonical_overlap_count']}",
        "- Independent validation: false; all runtime-eligible meter-days were already consumed by v0.15.",
        f"- Holdout SHA-256: `{holdout['holdout_sha256']}`", "",
        "## Exploratory paired service routing", "",
        "| Endpoint | P1 rate | P0 rate | RD | Status | Prospective target |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in utility: lines.append(f"| {row['endpoint']} | {row['p1_rate']} | {row['p0_rate']} | {row['paired_rd']} | {row['analysis_status']} | {row['prospective_target']} |")
    lines += ["", "## Service coverage", "", f"- Evaluable official single-phase meters: {len(single)}/2", f"- Evaluable official three-phase meters: {len(triple)}/3", "- Single-phase absence of Ib/Ic is treated as asset topology, not telemetry failure.", "", "## Required prospective confirmatory experiment", "", "- Collect at least one new season of AMI after 2026-06-30 for all five streetlight meters.", "- Freeze at least 30 history days, then reserve later meter-days before inspecting outcomes.", "- Record operator disposition for data-quality review, remote monitor, and field inspection separately.", "- Link field inspection results only after the queue and decision have been frozen.", "- Test the prospective targets R RD >= -0.10 and B RD <= -0.10 with meter-day clustered inference.", "", "## Interpretation", "", "The output is a post-hoc work-routing replay: data-quality review, remote monitor, or field-inspection candidate. Human review remains mandatory before maintenance.", "", "## Claim boundary", "", "No independent validation, field-fault accuracy, real-background FPR or specificity, fault probability, confirmed maintenance truth, or actual cost-saving claim is permitted."]
    REPORT.mkdir(parents=True, exist_ok=True)
    (REPORT / "v16_final_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
