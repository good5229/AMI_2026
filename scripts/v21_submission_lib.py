#!/usr/bin/env python3
"""Deterministic LightGuard v0.21 submission evidence builder."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "lightguard_v0_1" / "data" / "submission"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v21"
SUBMISSION = ROOT / "submission"
APP_DOC = ROOT / "lightguard_app" / "docs" / "v21_submission_readiness.md"

FREEZES = {
    "v13_negative_evidence": {
        "paths": ["lightguard_v0_1/data/validation/v13", "lightguard_v0_1/reports/v13"],
        "sha256": "27cc83c9f0a4eedf4732eaccd5eae03c1ed52205b5770af9decad0e40103905b",
        "file_count": 21,
    },
    "v14_negative_evidence": {
        "paths": ["lightguard_v0_1/data/validation/v14", "lightguard_v0_1/reports/v14"],
        "sha256": "6308f7007b38289f9a87b07b6062ea01d32d127a519cd961535c5836c24671fd",
        "file_count": 20,
    },
    "v20_predecessor": {
        "paths": [
            "lightguard_v0_1/data/validation/v20", "lightguard_v0_1/reports/v20",
            "lightguard_app/docs/v20_ulsan_operational_transfer.md",
        ],
        "sha256": "872c35a65f9f229da80a288d0be9f54f80b985b21cfc233d217a31341488a460",
        "file_count": 19,
    },
}
RUBRIC_SHA = "0e4b15100f338858e6d5917ba7a86b6370ae37d936d3908c9c1c2b5f21845b50"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hash(relative_paths: list[str]) -> tuple[str, int]:
    files = []
    for relative in relative_paths:
        path = ROOT / relative
        files.extend(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else files.append(path)
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda p: str(p)):
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest(), len(files)


def verify_freezes() -> dict:
    result = {}
    for key, contract in FREEZES.items():
        actual, count = tree_hash(contract["paths"])
        if actual != contract["sha256"] or count != contract["file_count"]:
            raise RuntimeError(f"BLOCKED_PREDECESSOR_FREEZE:{key}:{actual}:{count}")
        result[key] = {"status": "PASS", "tree_sha256": actual, "file_count": count}
    rubric = next((p for p in (ROOT / "official_docs").rglob("*.pdf") if sha(p) == RUBRIC_SHA), None)
    if rubric is None:
        raise RuntimeError("BLOCKED_OFFICIAL_RUBRIC_SOURCE")
    result["official_rubric"] = {"status": "PASS", "source_file": str(rubric.relative_to(ROOT)), "sha256": RUBRIC_SHA, "pages": 2}
    return result


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def source(relative: str) -> dict:
    path = ROOT / relative
    return {"source_file": relative, "source_hash": sha(path)}


def metric_registry() -> list[dict]:
    specs = [
        ("M001", "competition_streetlight_meters", 5, "count", "lightguard_v0_1/data/data_summary.json", "json_path", ["ami", "streetlight_meter_count"], "Competition actual AMI scope"),
        ("M002", "controlled_scenarios_detected", 46, "count", "lightguard_app/assets/data/simulation_validation_results_v02.csv", "csv_rows", None, "Controlled replay only"),
        ("M003", "daegu_operational_events", 101843, "count", "lightguard_v0_1/data/validation/v17/v17_fault_events_clean.csv", "csv_rows", None, "Municipal operational records"),
        ("M004", "daegu_operational_need_grade", "ON-A", "grade", "lightguard_v0_1/data/validation/v17/v17_operational_summary.json", "json_path", ["operational_need_grade"], "Operational burden grade"),
        ("M005", "buyeo_events", 3437, "count", "lightguard_v0_1/data/validation/v19/v19_buyeo_raw_manifest.json", "json_path", ["rows"], "Independent municipal records"),
        ("M006", "buyeo_zero_shot_enrichment", 1.802120141342756, "ratio", "lightguard_v0_1/data/validation/v19/v19_zero_shot_summary.json", "json_path", ["external", "top10", "enrichment"], "Operational-priority transfer; not AMI accuracy"),
        ("M007", "ulsan_canonical_events", 1060, "count", "lightguard_v0_1/data/validation/v20/v20_ulsan_u1_manifest.json", "json_path", ["canonical_event_count"], "Municipal workflow records"),
        ("M008", "ulsan_linked_assets", 920, "count", "lightguard_v0_1/data/validation/v20/v20_u1_u2_join_summary.json", "json_path", ["safe_matched_asset_count"], "Exact-ID/category/uniqueness gated"),
        ("M009", "ulsan_total_assets", 981, "count", "lightguard_v0_1/data/validation/v20/v20_u1_u2_join_summary.json", "json_path", ["u1_unique_asset_count"], "U1 source-local assets"),
        ("M010", "ulsan_linked_events", 994, "count", "lightguard_v0_1/data/validation/v20/v20_u1_u2_join_summary.json", "json_path", ["safe_matched_event_count"], "Exact-ID/category/uniqueness gated"),
        ("M011", "ulsan_transfer_grade", "TM-A", "grade", "lightguard_v0_1/data/validation/v20/v20_zero_shot_summary.json", "json_path", ["external", "transfer_grade"], "Zero Ulsan retuning; operational transfer only"),
        ("M012", "ulsan_queue_grade", "WS-B", "grade", "lightguard_v0_1/data/validation/v20/v20_queue_replay_summary.json", "json_path", ["work_start_grade"], "Counterfactual replay; no causal delay claim"),
    ]
    rows = []
    for metric_id, name, value, unit, relative, method, path, qualification in specs:
        rows.append({"metric_id": metric_id, "metric": name, "value": value, "unit": unit, **source(relative), "extraction_method": method, "json_path": path, "qualification": qualification})
    return rows


def claim_registry() -> list[dict]:
    claims = [
        ("C001", "GREEN", "LightGuard는 기존 AMI 전류 데이터로 비정상 운전 징후를 독립 확인하고 점검 우선순위를 보조한다.", "PRODUCT", "lightguard_v0_1/data/data_summary.json", "M001", True, "현장 확인이 최종 판정 단계다.", "AMI만으로 고장을 정확히 진단"),
        ("C002", "YELLOW", "공모전 실제 가로등형 AMI 5개 계량기를 서비스 입력으로 평가했다.", "ACTUAL_AMI", "lightguard_v0_1/data/data_summary.json", "M001", True, "가명 AMI이며 지자체 분전함 직접 매핑과 현장 정답은 없다.", "5개 계량기의 현장 고장 정확도"),
        ("C003", "YELLOW", "사전 정의한 46개 controlled scenario를 재현형 detector가 검출했다.", "CONTROLLED", "lightguard_app/assets/data/simulation_validation_results_v02.csv", "M002", True, "46/46은 controlled 재현 결과이며 현장 성능지표가 아니다.", "현장 고장탐지 정확도 100%"),
        ("C004", "GREEN", "범용 전기 이상탐지기로의 외부 전이는 확인되지 않아 적용 범위를 가로등형 AMI 점검 우선순위 보조로 제한했다.", "NEGATIVE_EXTERNAL", "lightguard_v0_1/reports/v14/v14_final_summary.md", None, True, "v0.13/v0.14 negative evidence를 유지한다.", "범용 전기 고장진단 검증 완료"),
        ("C005", "GREEN", "대구 101,843건의 실제 운영기록에서 반복·처리 tail·다중 발견경로의 유지관리 부담이 관찰됐다.", "MUNICIPAL_DAEGU", "lightguard_v0_1/data/validation/v17/v17_operational_summary.json", "M003", True, "공모전 AMI 또는 현장 고장 정답과 직접 연결되지 않는다.", "AMI 고장 정확도의 대구 검증"),
        ("C006", "YELLOW", "부여 3,437건에서 고장유형과 반복이력을 독립 확인했고 고정 COMMON-OPS 점수의 top-10% enrichment는 1.80x였다.", "MUNICIPAL_BUYEO", "lightguard_v0_1/data/validation/v19/v19_zero_shot_summary.json", "M006", True, "운영 우선순위 전이이며 AMI 정확도가 아니다.", "부여 현장 고장확률 1.80배"),
        ("C007", "YELLOW", "울산 1,060건에서 무재튜닝 운영 우선순위 전이 TM-A와 접수-시작-완료 lifecycle 결합 가능성을 확인했다.", "MUNICIPAL_ULSAN", "lightguard_v0_1/data/validation/v20/v20_zero_shot_summary.json", "M011", True, "현장 지연 감소의 인과효과나 실제 staffing capacity가 아니다.", "울산 처리시간 단축 실증"),
        ("C008", "YELLOW", "울산 U1 자산 981개 중 920개가 U2와 exact-ID/category/uniqueness gate를 통과했다.", "MUNICIPAL_ULSAN_ASSET", "lightguard_v0_1/data/validation/v20/v20_u1_u2_join_summary.json", "M008", True, "13개 ambiguous와 48개 unmatched를 제외하며 historical coverage는 UNKNOWN이다.", "울산 자산 100% 연결"),
        ("C009", "GREEN", "AMI 신호 layer와 운영이력 layer를 분리해 지역별 available fields에 맞춰 단계적으로 적용할 수 있다.", "GENERALIZABILITY", "lightguard_v0_1/data/validation/v19/v19_common_feature_contract.json", None, True, "동일 모델이 모든 지자체에 그대로 적용된다는 뜻이 아니다.", "전국 동일 모델 즉시 적용"),
        ("C010", "GREEN", "기존 AMI를 활용하므로 추가 센서 하드웨어 요구를 최소화하는 구조다.", "ARCHITECTURE", "lightguard_app/README.md", None, True, "실제 장비비 절감액·ROI·payback은 산정하지 않았다.", "연간 비용 절감액"),
        ("C011", "RED", "LightGuard는 AMI만으로 가로등 고장을 정확히 진단한다.", "PROHIBITED", "lightguard_v0_1/data/validation/v20/v20_feature_availability_contract.json", None, False, "사용 금지", "항상 금지"),
        ("C012", "RED", "LightGuard 도입으로 민원·비용·인력이 감소한다.", "PROHIBITED", "lightguard_v0_1/data/validation/v20/v20_queue_replay_summary.json", None, False, "실제 dispatch, unit cost, avoidable dispatch가 없어 사용 금지", "항상 금지"),
    ]
    keys = ["claim_id", "claim_level", "claim_text", "evidence_type", "source_file", "metric", "allowed", "qualification", "prohibited_upgrade"]
    return [{**dict(zip(keys, row)), "source_hash": sha(ROOT / row[4])} for row in claims]


def rubric_registry(rubric_source: dict) -> dict:
    stage1 = [
        ("R1", "사업 적합성", "business_fit", "C005", "대구 ON-A; 부여·울산 보조", "AMI 직접 field truth 아님", 3),
        ("R2", "개발 용이성", "development_feasibility", "C001", "실제 AMI 입력 + Flutter Web/Android", "hardware 절감액 미산정", 3),
        ("R3", "Idea 창의성", "idea_creativity", "C001", "controller 독립 second-checker", "confirmed-fault system 아님", 2),
        ("R4", "Idea 구체성", "idea_specificity", "C003", "actual data + workflow + artifact trace", "field pilot 없음", 3),
    ]
    stage2 = [
        ("R5", "개발 용이성", "development_feasibility", "C001", "Flutter app + deterministic preflight", "production deployment 아님", 3),
        ("R6", "Idea 완성도", "idea_completeness", "C001", "Web/Android + tests + submission package", "production 운영 아님", 3),
        ("R7", "활용목적", "use_purpose", "C007", "점검 우선순위와 3-lane workflow", "정책효과 미실증", 3),
        ("R8", "유형효과", "expected_effectiveness", "C005", "반복·장기처리 workload와 ranking signal", "민원·비용 감소율 미산정", 2),
        ("R9", "범용성", "generalizability", "C009", "대구·부여·울산 운영 layer", "동일 schema/model 주장 아님", 2),
    ]
    def row(values, stage):
        rubric_id, official_name, normalized, claim_id, evidence, limitation, score = values
        return {"rubric_id": rubric_id, "stage": stage, "official_name": official_name, "normalized_name": normalized, "official_weight": None, "primary_claim_id": claim_id, "evidence": evidence, "limitation": limitation, "internal_readiness_score_0_to_3": score, "score_is_official": False}
    return {
        "official_source": rubric_source,
        "official_weights_published": False,
        "stage_1": [row(v, 1) for v in stage1],
        "stage_2": [row(v, 2) for v in stage2],
        "bonus": {"description": "제공 AMI 샘플을 활용한 APP 등 성과물", "required": False, "official_value": None, "proof_required_in_submission": True, "page": 1},
        "internal_scale": {"0": "evidence 없음", "1": "약함", "2": "설명 가능", "3": "강한 직접 근거", "not_official_score": True},
    }


def evidence_layers() -> list[dict]:
    return [
        {"layer": "SIGNAL", "role": "공모전 실제 AMI와 anomaly-sign 후보", "claim_ids": ["C002"], "not": "field fault truth"},
        {"layer": "PLAUSIBILITY", "role": "controlled/counterfactual validation, 문헌, negative transfer", "claim_ids": ["C003", "C004"], "not": "field accuracy"},
        {"layer": "OPERATIONS", "role": "대구·부여·울산 유지관리와 workflow evidence", "claim_ids": ["C005", "C006", "C007", "C008"], "not": "AMI-municipal direct join"},
        {"layer": "PRODUCT", "role": "3-lane triage, Flutter, explainability, claim boundary", "claim_ids": ["C001", "C009", "C010"], "not": "causal savings claim"},
    ]


def qna() -> list[tuple[str, str]]:
    return [
        ("고장 정확도가 몇 %인가?", "현장 고장 Gold/Silver label이 없어 정확도를 산정하지 않습니다. 대신 실제 AMI 신호, controlled 재현, 운영 우선순위 전이를 서로 분리해 제시합니다."),
        ("정확도를 모르는데 왜 쓸 수 있나?", "LightGuard는 자동 고장판정기가 아니라 확인 대상을 좁히는 second-checker입니다. 최종 판정은 현장 확인으로 남깁니다."),
        ("왜 AMI여야 하나?", "기존 계량 인프라의 전류·전력 시계열을 재사용해 제어명령과 실제 소비의 불일치를 독립적으로 확인할 수 있기 때문입니다."),
        ("기존 원격제어반과 무엇이 다른가?", "제어반을 대체하지 않고 명령·상태와 실제 AMI 소비를 비교하는 독립 검증 layer입니다."),
        ("고장 정답 없이 무엇을 검증했나?", "controlled scenario 재현성, 실제 AMI anomaly-sign, proxy/H1, 문헌 타당성, 세 지자체의 운영 부담과 우선순위 전이를 검증했습니다."),
        ("외부 benchmark 실패는 무엇을 의미하나?", "범용 전기 이상탐지기로의 전이가 확인되지 않았다는 뜻입니다. 그래서 범위를 가로등형 AMI 점검 우선순위 보조로 제한했습니다."),
        ("대구 데이터가 왜 유효한가?", "101,843건의 실제 접수·처리 운영기록이 반복사건과 처리 tail 등 유지관리 부담을 직접 보여주기 때문입니다."),
        ("부여 데이터가 왜 유효한가?", "독립 지자체의 고장유형·반복이력에서 고정 운영점수의 우선순위 신호를 무재튜닝으로 확인했기 때문입니다."),
        ("울산 데이터가 왜 유효한가?", "접수-작업시작-완료 lifecycle과 자산 위치정보를 제공해 실제 workflow 결합 가능성을 검증하기 때문입니다."),
        ("AMI와 지자체 기록을 직접 연결했나?", "아닙니다. 두 evidence role은 분리돼 있고 직접 truth join을 주장하지 않습니다."),
        ("경제효과는 얼마인가?", "dispatch count, unit cost, avoidable dispatch가 함께 없어 원화 절감액·ROI를 계산하지 않습니다."),
        ("민원을 얼마나 줄이나?", "현장 개입 비교자료가 없어 감소율을 주장하지 않습니다. 현재 증명한 효과는 확인 대상을 정렬하고 근거를 함께 제공하는 것입니다."),
        ("인력을 줄일 수 있나?", "그런 주장을 하지 않습니다. 울산 작업시작 건수도 staffing capacity가 아니라 관측된 replay slot입니다."),
        ("수영구에 바로 쓸 수 있나?", "자산·일출일몰·기상·scenario 구조는 준비됐지만 실제 수영구 AMI-meter와 분전함 매핑 및 현장 label 연결이 필요합니다."),
        ("범용성은 무엇으로 증명했나?", "동일 모델 보편성을 주장하지 않습니다. 신호와 운영이력을 분리해 대구·부여·울산의 서로 다른 available fields에 단계 적용할 수 있음을 보였습니다."),
        ("울산 920/981 결합은 무엇인가?", "U1-U2 관리번호가 exact match이고 시설종류가 일치하며 U2 ID가 유일한 자산만 센 결과입니다."),
        ("나머지 울산 자산은 왜 제외했나?", "13개는 U2 ID가 모호하고 48개는 미연결이라 임의 결합하지 않았습니다."),
        ("TM-A는 정확도 등급인가?", "아닙니다. 무재튜닝 운영 우선순위 전이와 불확실성 gate를 통과한 성숙도 등급입니다."),
        ("WS-B는 현장 효과인가?", "아닙니다. 관측 작업시작 slot을 이용한 반사실적 queue replay 등급이며 인과적 지연 감소를 뜻하지 않습니다."),
        ("46/46은 100% 정확도 아닌가?", "controlled scenario의 재현 성공률일 뿐 자연발생 현장 고장의 정확도·재현율이 아닙니다."),
        ("앱에서 담당자는 무엇을 하나?", "DATA_QUALITY_REVIEW를 확인하고 REMOTE_MONITOR를 재검토한 뒤 FIELD_INSPECTION_CANDIDATE 상위건의 근거를 확인합니다."),
        ("현장 확인 후에는 무엇이 달라지나?", "결과를 등록하면 향후 Gold/Silver label 구축과 우선순위 정책 검증의 기반이 됩니다. 현재 제출본은 이를 이미 확보했다고 주장하지 않습니다."),
        ("추가 센서가 필요한가?", "핵심 구조는 기존 AMI 활용을 우선해 추가 센서 요구를 최소화합니다. 실제 현장 연동비는 별도 산정이 필요합니다."),
        ("다음 실험은 무엇인가?", "새 독립 AMI, AMI-현장 Gold/Silver, controller/maintenance outcome이 확보될 때만 predictive 실험을 재개합니다."),
    ]


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    line = "| " + " | ".join(headers) + " |\n"
    line += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    return line + "".join("| " + " | ".join(str(value) for value in row) + " |\n" for row in rows)


def build_documents(metrics: list[dict], claims: list[dict], rubric: dict) -> None:
    metric = {m["metric"]: m["value"] for m in metrics}
    positioning = "LightGuard는 기존 AMI 전류 데이터를 활용해 가로등 회로의 비정상 운전 징후를 독립적으로 확인하고, 반복 유지관리 이력과 함께 원격관찰·현장점검 우선순위를 제시하는 지자체 유지관리 의사결정 지원 서비스다."
    one_page = f"""# LightGuard 제출 요약

## 한 문장

{positioning}

## 문제와 해결

지자체 가로등 유지관리에는 반복 접수와 긴 처리 tail이 존재하지만, AMI 신호와 운영이력은 분리돼 있다. LightGuard는 기존 제어시스템을 대체하지 않고 AMI 이상징후를 second-check한 뒤 `DATA_QUALITY_REVIEW → REMOTE_MONITOR → FIELD_INSPECTION_CANDIDATE`로 확인 대상을 좁힌다.

## 핵심 증거

- 공모전 가로등형 AMI: **{metric['competition_streetlight_meters']}개 계량기**
- 대구 운영기록: **{metric['daegu_operational_events']:,}건**, 운영 필요성 **{metric['daegu_operational_need_grade']}**
- 부여 독립기록: **{metric['buyeo_events']:,}건**, top-10% enrichment **{metric['buyeo_zero_shot_enrichment']:.2f}x**
- 울산 lifecycle: **{metric['ulsan_canonical_events']:,}건**, exact-linked asset **{metric['ulsan_linked_assets']}/{metric['ulsan_total_assets']}**, transfer **{metric['ulsan_transfer_grade']}**

## 증거 경계

현장 고장 정확도·확률, 확정 고장, 민원·비용·인력 감소, 실제 처리시간 단축을 주장하지 않는다. 지자체 운영기록은 공모전 AMI의 직접 정답이 아니며 현장 확인이 최종 단계다.
"""
    write(SUBMISSION / "01_one_page_summary.md", one_page)
    write(SUBMISSION / "02_problem_evidence.md", f"""# 문제 근거

대구의 {metric['daegu_operational_events']:,}건 운영기록은 다중 발견경로, 반복 접수, 처리 tail을 보여주며 운영 필요성은 {metric['daegu_operational_need_grade']}다. 부여 {metric['buyeo_events']:,}건과 울산 {metric['ulsan_canonical_events']:,}건은 다른 지역에서도 반복 이력과 workflow가 존재함을 보여준다.

이 자료는 유지관리 burden의 직접 운영근거지만 AMI fault truth는 아니다. LightGuard의 유형효과는 담당자가 확인할 대상을 한 화면에서 정렬하고 AMI 근거와 반복이력을 함께 보는 것으로 제한한다.
""")
    write(SUBMISSION / "03_solution_architecture.md", """# 해결 구조

```text
기존 제어시스템 ─┐
                  ├─ LightGuard second-checker ─ 신호 설명 ─ 운영 우선순위 ─ 현장 확인
기존 AMI 전류 ───┘                         └─ 반복 유지관리 이력
```

## 네 개 Evidence Layer

1. `SIGNAL`: 공모전 실제 AMI와 anomaly-sign 후보
2. `PLAUSIBILITY`: 문헌, controlled/counterfactual validation, negative transfer
3. `OPERATIONS`: 대구·부여·울산 운영기록
4. `PRODUCT`: 3-lane triage, Flutter, 설명가능성, claim boundary

AMI와 지자체 운영기록은 직접 truth join하지 않는다. 지역 확장은 동일 모델 강제가 아니라 available fields에 따른 단계 적용이다.
""")
    write(SUBMISSION / "04_validation_evidence.md", f"""# 검증 근거

| 층 | 확인한 것 | 확인하지 않은 것 |
| --- | --- | --- |
| 실제 AMI | {metric['competition_streetlight_meters']}개 가로등형 계량기의 anomaly-sign | 현장 고장 정답 |
| Controlled | {metric['controlled_scenarios_detected']}/46 사전정의 scenario 재현 | 자연발생 정확도 |
| Negative external | 범용 전기 이상탐지 전이 미확인 | 범용 고장진단 |
| 부여 zero-shot | top-10% enrichment {metric['buyeo_zero_shot_enrichment']:.2f}x | AMI 정확도 |
| 울산 zero-shot | {metric['ulsan_transfer_grade']}, 무재튜닝 0회 | 현장 인과효과 |

“범용 전기 이상탐지기로의 외부 전이는 확인되지 않아, 범용 고장진단이 아닌 가로등형 AMI의 점검 우선순위 보조로 범위를 제한했습니다.”
""")
    write(SUBMISSION / "05_municipal_operations_evidence.md", f"""# 지자체 운영근거

## 대구

- 운영 사건 {metric['daegu_operational_events']:,}건
- 운영 필요성 {metric['daegu_operational_need_grade']}

## 부여

- 독립 사건 {metric['buyeo_events']:,}건
- 고정 COMMON-OPS top-10% enrichment {metric['buyeo_zero_shot_enrichment']:.2f}x

## 울산

- canonical event {metric['ulsan_canonical_events']:,}건
- U1-U2 safe link {metric['ulsan_linked_assets']}/{metric['ulsan_total_assets']} assets, {metric['ulsan_linked_events']}/{metric['ulsan_canonical_events']} events
- transfer {metric['ulsan_transfer_grade']}, queue replay {metric['ulsan_queue_grade']}

세 지역 기록은 운영 burden·반복·workflow의 근거다. 공모전 AMI와 직접 ID 결합하거나 물리 고장 정답으로 사용하지 않는다.
""")
    write(SUBMISSION / "06_claim_boundaries.md", """# Claim Boundaries

## 허용

- 기존 AMI를 활용한 독립 second-check와 점검 우선순위 보조
- 실제 운영기록에서 관찰된 반복·처리 tail·workflow
- 무재튜닝 operational-priority transfer
- 추가 센서 하드웨어 요구를 최소화하는 구조

## qualification 필수

- controlled 46/46은 현장 성능지표가 아님
- 부여·울산 전이는 AMI 정확도가 아님
- 울산 queue는 staffing capacity나 인과효과가 아님
- 920/981은 exact-ID/category/uniqueness gate 통과 수치

## 금지

- AMI만으로 정확한 고장진단
- 현장 고장 확률 또는 확정 고장
- 민원 감소율, 비용 절감액, 인력 절감
- 실제 처리시간 단축 실증
- AMI와 지자체 운영기록의 직접 truth join
""")
    write(SUBMISSION / "07_demo_script.md", """# 5분 Demo Script

1. 홈에서 오늘의 점검 우선순위 화면으로 이동한다.
2. `DATA_QUALITY_REVIEW`를 열어 결측·품질 검토 대상을 먼저 확인한다.
3. `REMOTE_MONITOR`에서 지속성 또는 context 변화가 필요한 대상을 재검토한다.
4. `FIELD_INSPECTION_CANDIDATE` 상위건을 선택한다.
5. 상세 화면에서 AMI 이상패턴, 지속성, 예상 운전시간·부하, 반복관리 이력을 확인한다.
6. “현장 확인 필요” 경계를 보여주고 자동 고장판정이 아님을 설명한다.
7. 현장 결과 등록이 향후 Gold/Silver label 구축의 다음 단계임을 제시한다.

금지 데모 문구: “고장입니다”, “정확도 95%”, “민원 30% 감소”, “연간 X억원 절감”.
""")
    qna_text = "# Judge Q&A\n\n" + "\n\n".join(f"## Q{i}. {q}\n\n{a}" for i, (q, a) in enumerate(qna(), 1))
    write(SUBMISSION / "08_judge_qna.md", qna_text)

    rubric_rows = rubric["stage_1"] + rubric["stage_2"]
    mapping = "# v0.21 Rubric Mapping\n\n공식 PDF는 평가항목만 제시하며 배점은 공개하지 않았다. 아래 0~3은 공식 점수가 아닌 내부 readiness stress test다.\n\n"
    mapping += markdown_table(["단계", "공식 평가항목", "직접/qualified evidence", "제한", "내부 readiness"], [[r["stage"], r["official_name"], r["evidence"], r["limitation"], r["internal_readiness_score_0_to_3"]] for r in rubric_rows])
    mapping += "\nAMI 샘플 기반 APP 성과물은 공식 문서상 가점 요소지만 필수 제출물은 아니며 가점 수치는 공개되지 않았다.\n"
    write(REPORT / "v21_rubric_mapping.md", mapping)

    trace = "# v0.21 Evidence Traceability\n\n" + markdown_table(["Claim", "Level", "Evidence type", "Source", "Metric", "Qualification"], [[c["claim_id"], c["claim_level"], c["evidence_type"], c["source_file"], c["metric"] or "-", c["qualification"]] for c in claims])
    write(REPORT / "v21_evidence_traceability.md", trace)
    red = "# v0.21 Judge Red Team\n\n" + "\n\n".join(f"## {q}\n\n{a}" for q, a in qna()[:16])
    write(REPORT / "v21_judge_red_team.md", red)
    write(REPORT / "v21_claim_audit.md", "# v0.21 Claim Audit\n\n- GREEN/YELLOW/RED registry generated.\n- Accuracy, probability, confirmed-fault, complaint, cost, staffing and causal upgrades are blocked.\n- AMI, controlled, literature, and municipal evidence roles remain separated.\n- v0.13/v0.14 negative evidence is retained.\n- Automated forbidden-claim and metric audits are required by preflight.\n")
    stress = "# v0.21 Internal Rubric Stress Test\n\n" + markdown_table(["항목", "내부 점수", "판정"], [[r["official_name"], r["internal_readiness_score_0_to_3"], "강한 직접 근거" if r["internal_readiness_score_0_to_3"] == 3 else "qualified evidence"] for r in rubric_rows])
    stress += "\n## 가장 약한 두 항목\n\n1. 유형효과: 인과적 절감률 대신 실제 운영 burden과 담당자 확인대상 축소 UX를 전면화한다.\n2. 범용성: 동일 모델 주장을 버리고 SIGNAL/OPERATIONS layer 분리와 지역별 field contract를 도식화한다.\n\n새 predictive tuning은 수행하지 않는다.\n"
    write(REPORT / "v21_internal_rubric_stress_test.md", stress)
    readiness = f"# v0.21 Final Readiness\n\n- Grade: **SR-A**\n- Positioning: {positioning}\n- Official rubric: 9 criteria mapped; official weights unavailable.\n- Submission package: 8 documents and {len(qna())} judge Q&A.\n- Predictive retuning: 0.\n- Stop rule: new independent AMI, field Gold/Silver, controller/maintenance outcome, or materially new evidence is required before another predictive version.\n"
    write(REPORT / "v21_final_readiness.md", readiness)
    write(APP_DOC, readiness)


def build_manifests(freeze: dict) -> None:
    submission_files = sorted(p for p in SUBMISSION.glob("*.md") if p.is_file())
    submission_manifest = {"version": "0.21", "status": "FROZEN", "files": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in submission_files], "raw_data_included": False}
    dump(SUBMISSION / "evidence_manifest.json", submission_manifest)
    evidence_files = []
    for base in (DATA, REPORT, SUBMISSION):
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.name not in {"v21_evidence_manifest.json", "evidence_manifest.json"}:
                evidence_files.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
    release_surfaces = [
        APP_DOC,
        ROOT / "lightguard_app" / "README.md",
        ROOT / "lightguard_app" / "lib" / "features" / "ami_validation" / "ami_validation_screen.dart",
        ROOT / "lightguard_app" / "lib" / "features" / "ami_validation" / "submission_readiness_card.dart",
        ROOT / "lightguard_app" / "test" / "unit" / "v21_submission_readiness_test.dart",
        ROOT / "scripts" / "v21_submission_lib.py",
        ROOT / "scripts" / "build_v21_claim_registry.py",
        ROOT / "scripts" / "build_v21_evidence_manifest.py",
        ROOT / "scripts" / "build_v21_submission_package.py",
        ROOT / "scripts" / "audit_v21_metrics.py",
        ROOT / "scripts" / "audit_v21_forbidden_claims.py",
        ROOT / "scripts" / "test_v21_submission.py",
        ROOT / "scripts" / "v21_preflight.sh",
    ]
    evidence_files.extend({"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in release_surfaces)
    evidence_files = sorted({item["path"]: item for item in evidence_files}.values(), key=lambda item: item["path"])
    dump(DATA / "v21_evidence_manifest.json", {"version": "0.21", "status": "SR-A", "release_snapshot": "ARTIFACT_HASH_FREEZE", "git_commit_required_by_contract": False, "predecessor_freeze": freeze, "artifacts": evidence_files, "privacy": "NO_RAW_DATA", "predictive_retuning_count": 0})


def build_all() -> None:
    freeze = verify_freezes()
    rubric_source = freeze["official_rubric"]
    metrics = metric_registry()
    claims = claim_registry()
    rubric = rubric_registry(rubric_source)
    dump(DATA / "v21_metric_registry.json", metrics)
    dump(DATA / "v21_claim_registry.json", claims)
    dump(DATA / "v21_rubric.json", rubric)
    dump(DATA / "v21_evidence_layers.json", evidence_layers())
    build_documents(metrics, claims, rubric)
    build_manifests(freeze)
    print(json.dumps({"status": "BUILT", "claims": len(claims), "metrics": len(metrics), "rubric_items": 9, "judge_qna": len(qna()), "readiness": "SR-A"}, ensure_ascii=False))


if __name__ == "__main__":
    build_all()
