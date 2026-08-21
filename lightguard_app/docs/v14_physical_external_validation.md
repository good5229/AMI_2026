# v0.14 물리 출처 외부 재현 검증 표시 계약

## 목적

AMI 검증 화면은 외부 데이터셋의 적합성 판정과 허용된 물리 메커니즘 범위를 성능 수치보다 먼저 표시한다. 이 표시는 외부 실험 결과를 수영구 가로등 현장 성능으로 확대 해석하지 않도록 하는 claim boundary다.

## 고정 표시

| 항목 | 상태 | 허용 범위 |
|---|---|---|
| v0.13 MAD | `NOT_EVALUABLE_INCOMPLETE_COVERAGE` | 기존 negative/non-evaluable 결과를 변경 없이 보존 |
| London Met | `PRIMARY_BLOCKED_PROVENANCE` | 라이선스·라벨·측정 출처 확인 전 성능 평가 보류 |
| CoDEx-VFD | `CONTROLLED_MECHANISM_ONLY` | 통제된 VFD/EMI 전류 메커니즘 검증만 허용 |
| SustDataED2 | `TRANSITION_POSITIVE_CONTROL_ONLY` | 기기 전환 persistence/change positive control만 허용 |
| 3PhaseInsight | `REFERENCE_ONLY` | 물리 데이터 모델 참고용이며 성능 benchmark에서 제외 |
| PMC-3 | `UNAVAILABLE` | 검증 가능한 3상 동기 채널과 위상 정보가 없어 계산·주장하지 않음 |

## Claim boundary

외부 결과는 물리 신호 메커니즘의 제한적 재현만 설명한다. 가로등 현장 정확도, 수영구 운영 성능, 실제 고장 확률을 의미하지 않으며 이를 추정하는 값으로 사용하지 않는다.

## 구현 계약

화면 문구와 단위 테스트는 `V14PhysicalExternalContract`의 정적 `const` 데이터를 함께 사용한다. 데이터셋 상태 또는 claim boundary를 변경하려면 계약과 검증 근거를 동시에 갱신해야 한다.
