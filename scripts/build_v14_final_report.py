#!/usr/bin/env python3
"""Create aggregate v0.14 reports and a hash-bound reproducibility manifest."""
from __future__ import annotations

from v14_common import CLAIM, DATA, REPORTS, ROOT, read_csv, sha256, write_json


def main() -> None:
    london = read_csv(REPORTS / "v14_london_results.csv")
    codex = read_csv(REPORTS / "v14_codex_vfd_results.csv")
    sust = read_csv(REPORTS / "v14_sustdata_results.csv")
    evaluated = sum(any(x["status"].startswith("EVALUATED") for x in rows) for rows in (london, codex, sust))
    codex_positive = sum(x.get("actual_label") == "1" for x in codex)
    codex_escalated = sum(x.get("pmc_prediction") == "1" for x in codex)
    sust_escalated = sum(x.get("pmc_prediction") == "1" for x in sust)
    predecessor = DATA / "v13_freeze_manifest.json"
    mad = f"""# v0.13 predecessor context\n\n- Status: FROZEN_NEGATIVE_NON_EVALUABLE\n- MAD SC3 balanced accuracy: 0.52004485\n- z-score comparator balanced accuracy: 0.66598258\n- Primary gate: NOT_EVALUABLE_INCOMPLETE_COVERAGE\n- The v0.14 study does not revise, replace, or rehabilitate this result.\n\n{CLAIM}\n"""
    summary = f"""# LightGuard v0.14 Physical-Provenance External Replication\n\n## Release state\n- v0.13 predecessor: FROZEN_NEGATIVE_NON_EVALUABLE\n- London Met: {london[0]['status']}\n- CoDEx-VFD: {codex[0]['status']}\n- SustDataED2: {sust[0]['status']}\n- 3PhaseInsight: REFERENCE_ONLY_NO_PUBLIC_LABELLED_RAW_DATA\n- Evaluated physical-provenance tracks: {evaluated}\n\n## Interpretation\nCoDEx-VFD is a controlled injected-disturbance mechanism test and every downloaded run is a 16 MiB partial prefix. SustDataED2 transitions are positive controls only, not faults. Independent units are runs or day/appliance clusters; individual rows are never inference units.\n\n## Claim boundary\n{CLAIM}\n"""
    outcome_text = (
        "\n## Frozen outcome interpretation\n"
        f"- CoDEx-VFD: {codex_escalated} of {codex_positive} injection-positive partial-run prefixes escalated; "
        "the controlled disturbance mechanism was not replicated under the frozen composite threshold.\n"
        f"- SustDataED2: {sust_escalated} of {len(sust)} appliance clusters escalated; this is inconsistent and "
        "inconclusive positive-control evidence, not fault evidence.\n"
        "- PMC-2, PMC-4, and PMC-5 were not separately scored, so no component-specific transfer claim is permitted. "
        "PMC-3 remained unavailable.\n"
    )
    summary = summary.replace("\n## Claim boundary", outcome_text + "\n## Claim boundary")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "v14_mad_predecessor_context.md").write_text(mad, encoding="utf-8")
    (REPORTS / "v14_final_summary.md").write_text(summary, encoding="utf-8")
    files = [predecessor, DATA / "v14_dataset_registry.json", DATA / "v14_raw_external_manifest.json",
             DATA / "v14_physical_feature_mapping.json", DATA / "v14_case_evidence_matrix.csv",
             REPORTS / "v14_london_results.csv", REPORTS / "v14_codex_vfd_results.csv",
             REPORTS / "v14_sustdata_results.csv", REPORTS / "v14_cross_dataset_mechanism_matrix.csv",
             REPORTS / "v14_mad_predecessor_context.md", REPORTS / "v14_final_summary.md"]
    write_json(REPORTS / "reproducibility_manifest.json", {
        "schema_version": "lightguard.v14.reproducibility.1", "claim_boundary": CLAIM,
        "evaluated_track_count": evaluated,
        "files": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in files],
    })
    print(f"v0.14 final report: {evaluated} evaluated tracks")


if __name__ == "__main__":
    main()
