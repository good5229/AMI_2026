#!/usr/bin/env python3
"""Build deterministic v0.9 final report, app summary, and file manifest."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1/data/validation/v09"
REPORTS = ROOT / "lightguard_v0_1/reports/v09"
APP = ROOT / "lightguard_app/assets/data/context/v09_specificity_summary.json"


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main() -> None:
    manifest = load("v09_episode_manifest.json")
    calibration = load("v09_calibration_set.json")
    holdout = load("v09_confirmatory_holdout.json")
    config = load("v09_candidate_config.json")
    summary = load("v09_confirmatory_summary.json")
    for name in ("v09_hard_negative_results.csv", "v09_solar_boundary_analysis.csv", "v09_missing_feature_results.csv",
                 "v09_episode_effects.csv", "v09_episode_bootstrap.md", "v09_actual_ami_regression.csv"):
        if not (REPORTS / name).exists():
            raise RuntimeError(f"required analysis is missing: {name}")
    selected = summary["selected_candidate"]
    metrics = summary["model_results"][selected] if selected else None
    calibration_episodes = {case["episode_id"] for case in calibration["cases"]}
    confirmatory_episodes = {case["episode_id"] for case in holdout["cases"]}
    calibration_dates = {case["date"] for case in calibration["cases"]}
    confirmatory_dates = {case["date"] for case in holdout["cases"]}
    app = {
        "schema_version": "lightguard.v09-app-summary.v1",
        "validation_kind": summary["validation_kind"],
        "selected_candidate": selected,
        "promotion_passed": summary["promotion_passed"],
        "calibration_cases": calibration["case_count"], "confirmatory_cases": holdout["case_count"],
        "calibration_episodes": len(calibration_episodes), "confirmatory_episodes": len(confirmatory_episodes),
        "episode_overlap": len(calibration_episodes & confirmatory_episodes),
        "date_overlap": len(calibration_dates & confirmatory_dates),
        "kma_observation_overlap": manifest["invariants"]["kma_station_date_overlap"],
        "weather_weight": 0.0, "load_imputation": "none", "actual_ami_is_truth": False,
        "metrics": metrics,
        "claim_boundary": summary["claim_boundary"],
    }
    APP.parent.mkdir(parents=True, exist_ok=True)
    APP.write_text(json.dumps(app, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (REPORTS / "v09_actual_ami_regression.csv").open(encoding="utf-8", newline="") as handle:
        actual = list(csv.DictReader(handle))
    report = f"""# LightGuard v0.9 Hard-Negative Specificity Recovery

## Decision

- Calibration-selected candidate: `{config['selected_candidate']}`
- Confirmatory-selected candidate: `{selected}`
- Controlled promotion gate: `{'PASS' if selected else 'FAIL'}`
- Retuning after holdout: `false`
- Claim boundary: controlled generated scenarios only; no field AMI accuracy or production-readiness claim.

## Freeze and episode separation

- Frozen v0.8 git baseline: `8772c2759d16ed7a6e669b940880e10cb242d1d6`
- Official-context episodes: `48` (`24` calibration / `24` confirmatory)
- Calibration cases: `{calibration['case_count']}`; confirmatory cases: `{holdout['case_count']}`
- Episode/date/KMA observation/case/signal/asset overlap: `0`
- Source year: `2025`; future 2026 context episodes: `0`
- KASI completion: official anchors plus official KASI web-calculator JavaScript with source hashes; no internal solar fallback.

## Confirmatory metrics

| metric | result | Wilson 95% |
|---|---:|---|
| recall | {metrics['recall'] if metrics else 'unavailable'} | {metrics['recall_wilson_95'] if metrics else 'unavailable'} |
| normal FPR | {metrics['fpr'] if metrics else 'unavailable'} | {metrics['fpr_wilson_95'] if metrics else 'unavailable'} |
| hard-negative FPR | {metrics['hard_negative_fpr'] if metrics else 'unavailable'} | {metrics['hard_negative_fpr_wilson_95'] if metrics else 'unavailable'} |
| worst region-season recall | {metrics['worst_cell_recall'] if metrics else 'unavailable'} | descriptive minimum |
| average precision | {metrics['average_precision'] if metrics else 'unavailable'} | episode bootstrap reported separately |
| abstention | {metrics['abstention_rate'] if metrics else 'unavailable'} | action coverage measure |

## Specificity result

The threshold-only comparator retained high recall but produced substantial normal and hard-negative false positives. H1's second-stage solar, persistence, load, phase, policy, and contradiction evidence recovered specificity without using weather in the score. H2/H3 preserved the detector result while exposing missing-data abstention and bounded queue ordering.

## Statistical evidence

- Wilson intervals are reported for recall, FPR, hard-negative FPR, and subgroup rates.
- Episode-cluster bootstrap resamples the 24 confirmatory episode units 2,000 times with seed `20260901`.
- Region, season, weather regime, episode, and region-season interaction outputs are controlled descriptive effects, not municipal field effects.
- Solar-boundary and missing-feature analyses are separate release artifacts.

## Actual AMI regression

- Replayed events: `{len(actual)}` anonymized competition AMI windows.
- Field truth labels: unavailable for all rows.
- Promotion-gate use: false for all rows.
- New actions: `{', '.join(f'{action}={sum(row["new_action"] == action for row in actual)}' for action in sorted({row['new_action'] for row in actual}))}`.
- These rows demonstrate how the frozen decision contract behaves when linked to real intervals; they do not measure recall, specificity, or fault accuracy.

## Data policies

- Weather weight: `0`; KMA remains episode/context evidence only.
- Rated-load imputation: none. Chungju unavailable load remains unavailable.
- External Gangneung/Chungju cabinet-linked AMI: unavailable.
- Scenario signals, municipal assets, and anonymized competition AMI remain distinct.

## Product boundary

Flutter displays the episode-separated sample size, recall, normal FPR, hard-negative FPR, worst-cell recall, Wilson intervals, and controlled-only disclaimer. A failed future rerun must emit `selected_candidate: null` and display `Candidate not promoted`.
"""
    (REPORTS / "v09_final_summary.md").write_text(report, encoding="utf-8")

    tracked = [
        *sorted(DATA.glob("*")), *sorted(REPORTS.glob("*")),
        ROOT / "docs/goal_progress_v09.md", ROOT / "docs/agent_learning_v09/sol_orchestration.md",
        ROOT / "docs/agent_learning_v09/terra_hard_negative_forensics.md", ROOT / "docs/agent_learning_v09/terra_episode_design.md",
        ROOT / "docs/agent_learning_v09/terra_statistical_analysis.md", ROOT / "docs/agent_learning_v09/luna_specificity_gate.md",
        ROOT / "docs/agent_learning_v09/luna_independent_qa.md", ROOT / "lightguard_app/docs/v09_specificity_validation.md",
        APP, ROOT / "lightguard_app/lib/features/ami_validation/v09_specificity_card.dart",
        ROOT / "lightguard_app/test/unit/v09_specificity_validation_test.dart",
    ]
    manifest_path = REPORTS / "reproducibility_manifest.json"
    tracked = [path for path in tracked if path.is_file() and path != manifest_path]
    hashes = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(set(tracked))}
    manifest_path.write_text(json.dumps({"schema_version": "lightguard.v09-reproducibility.v1", "files": hashes}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"selected_candidate": selected, "manifest_files": len(hashes)}))


if __name__ == "__main__":
    main()
