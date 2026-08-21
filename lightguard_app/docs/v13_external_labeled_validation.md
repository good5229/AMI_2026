# v0.13 외부 라벨 AMI 메커니즘 검증

v0.13은 실제 라벨이 있는 외부 전기·AMI 데이터셋에서 LightGuard Signal Core(LG-SC)의 신호 메커니즘이 다른 도메인에서도 관찰되는지를 확인하기 위한 준비 단계다.

외부 라벨 전기/AMI benchmark는 **signal-mechanism external validity만** 지지한다. 이는 streetlight field accuracy나 actual fault probability를 의미하지 않는다. 외부 데이터의 성능 수치는 스마트그리드 계량 이상 또는 일반 전기 부하 이상에 대한 결과이며, 수영구·강릉·충주 가로등의 실제 고장 성능으로 전이할 수 없다.

## 증거 층위

| 층위 | 의미 | 현재 상태 |
| --- | --- | --- |
| Literature grade | 문헌이 지지하는 메커니즘의 설명 근거 | `EVIDENCE_A_TO_C_SEPARATE` |
| External empirical EV grade | 외부 라벨 데이터에서 LG-SC가 라벨과 연결되는 정도 | `PENDING_METRICS` |
| Internal AMI observation | LightGuard 내부 AMI에서 관찰된 이상징후 | `OBSERVATIONAL_ONLY` |
| H1/Proxy | 내부 점등 기대상태와 Proxy anomaly sign | `INTERNAL_REFERENCE_ONLY` |
| Human review | 블라인드 사람 검토 결과 | `PENDING` |
| Field confirmation | 실제 분전함·정비·현장 outcome 확인 | `NOT_AVAILABLE` |

## 데이터셋 처리 원칙

MAD는 실제 AMI와 전문 또는 현장 라벨 여부를 원문 확인한 뒤 주 검증 후보로 편입한다. 편입 전에는 `DG-A_CANDIDATE` 및 `PENDING_SOURCE_CONFIRMATION`으로 표시한다.

REFIT와 UCR Power Demand는 보조 후보로 기록하되, 논문·라벨 규칙·라이선스·누수 없는 train/test 분할·전기적 메커니즘 유사성을 확인하기 전에는 `SECONDARY_BLOCKED`로 유지한다. 차단 상태를 데이터가 없는 상태에서 임의로 정상 또는 실패로 해석하지 않는다.

pseudo-labeled 데이터는 외부 Gold로 사용할 수 없다. 필요하면 별도의 weak-label stress test에만 사용한다.

## LG-SC feature freeze

외부 데이터의 라벨을 보기 전에 다음 신호 메커니즘과 원천 feature 매핑을 고정해야 한다.

- `LG-S1`: meter-relative baseline deviation
- `LG-S2`: persistence / temporal accumulation
- `LG-S3`: phase asymmetry / phase-selective behavior
- `LG-S4`: abrupt or structural change
- `LG-S5`: multivariate evidence combination

가로등 전용 KASI 일출·일몰, 지자체 정격부하, 분전함 매핑, 점등 정책은 외부 데이터에 존재하지 않으면 생성하거나 대체하지 않는다.

현재 자산은 `PRE_CONFIRMATORY` placeholder다. `n_test`, AUROC, average precision, balanced accuracy, confidence interval은 원자료 fingerprint, 라벨 provenance, split, feature mapping, 사전 동결이 완료된 뒤에만 교체한다. 인간 검토와 현장 확인은 외부 benchmark 결과로 대체하지 않는다.
