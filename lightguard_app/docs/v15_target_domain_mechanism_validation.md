# v0.15 대상 도메인 메커니즘 기여 검증 표시 계약

## 목적

v0.15 화면은 아직 결과가 생성되기 전의 정적 protocol/status disclosure다.
화면은 어떤 비교와 ablation이 예정되어 있는지, 무엇을 보존하는지, 어떤
주장을 금지하는지만 표시한다. 결과 summary가 나중에 수치를 제공하더라도
이 claim boundary를 넘어 해석하지 않는다.

## 고정 상태

| 항목 | 상태 | 표시 범위 |
|---|---|---|
| v0.10–v0.14 freeze | `FROZEN` | 선행 결과·H1 runtime·threshold 보존 |
| New disjoint holdout | `FROZEN_BEFORE_RESULTS` | v0.10 pool 및 canonical-six buffer와 분리 |
| Same-threshold ablation | `PRE_REGISTERED` | 활성 runtime component만 제거, threshold 동일 |
| Anomaly / controlled-benign pair | `PAIRED_DESIGN` | 같은 meter-day에서 anomaly와 benign escalation을 함께 기록 |
| Robust-z | `COMPARATOR_ONLY` | 단순 비교군, H1 retuning/대체 금지 |
| Natural shadow | `NO_TRUTH` | truth 없는 diagnostic/candidate trace |
| Canonical six | `DIAGNOSTIC_ONLY` | coverage/trace 확인만, truth·recall 판정 금지 |
| v0.13 / v0.14 | `FAILURE_PRESERVED` | 기존 negative/non-evaluable 및 외부 제한 결과 보존 |

## 해석 경계

v0.15의 대상은 frozen target-domain runtime mechanism의 기여와 controlled
benign escalation 동작이다. 이는 다음을 의미하지 않는다.

- field accuracy
- real-background FPR 또는 specificity
- fault probability
- general electrical anomaly performance
- 실제 현장 고장 원인 또는 정비 결과

Natural shadow의 출력은 현장 truth가 없는 점검 후보/진단 trace다. canonical
six은 diagnostic coverage만 제공하며, 정답 label이나 recall의 분모로 쓰지
않는다. v0.13 MAD의 `negative / NOT_EVALUABLE` 결과와 v0.14 외부 데이터의
제한·실패 판정은 후속 수치가 생겨도 변경하지 않는다.

## 구현 계약

Flutter 카드는 `V15TargetMechanismContract`의 정적 `const` 데이터를 사용한다.
현재 상태는 `PRE_REGISTERED_NO_RESULTS`이며, 이 단계에서는 데이터 파일,
실험 결과, threshold, comparator output을 로드하지 않는다. 상태 또는 claim
boundary를 바꾸려면 protocol 및 독립 검수 근거를 함께 갱신해야 한다.
