# LightGuard Data Provenance

## 화면별 데이터 출처

### 수영구 지도
- `suyeong_v02_seed.json`의 `objects` 안 `asset_info`(위치/분전함/가로등 수/정격 관련)

### 점검 후보 목록/우선순위
- `suyeong_v02_objects.json`의 `objects`에서 `detected_signals`, `inspection_priority`, `anomaly_evidence`

### 분전함 상세
- `asset_info`, `expected_schedule`, `expected_load`, `weather_context`, `ami`, `anomaly_evidence`를 `suyeong_v02_seed.json`에서 그대로 사용

### 실제 AMI 사례
- `ami_events.csv` 원본을 파싱하여 표시

### 시나리오 주입
- `simulation_scenarios_v02.json`, `simulation_validation_results_v02.csv`
- seed 내 `target_mode` 및 각 객체 `ami.virtual_link_mode`로 식별

## 분리 원칙
- 금지: 수영구 자산을 실제 AMI 데이터와 임의 매핑
- 금지: Scenario 결과를 실제 AMI로 라벨링
- 금지: 46/46을 고장탐지 정확도라고 표현
