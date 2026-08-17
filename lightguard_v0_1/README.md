# AMI LightGuard v0.1

공모전 제공 AMI와 지자체 공개 가로등 데이터를 이용한 **독립 검증·점검 후보 생성**용 데이터 레이어입니다.

## 핵심 원칙
- 실제 AMI↔지자체 분전함 매핑은 제공되지 않았습니다. `ami_cabinet_mappings`는 비어 있으며 임의 매핑을 만들지 않습니다.
- AMI 이벤트는 고장 확정이 아니라 점검 후보입니다.
- 수영구는 Full Asset, 강릉은 Controller-linked, 충주는 Minimal Asset mode로 정규화합니다.

## 주요 파일
- `lightguard_v0_1.sqlite`: 앱/백엔드가 바로 읽을 수 있는 DB
- `app_seed/*.json`: Flutter/Web 데모용 seed
- `data/ami_events.csv`: Detector v0.1 실제 탐지 이벤트
- `data/ami_meter_profiles.csv`: 5개 가로등 AMI baseline/profile
- `data/cabinets.csv`, `data/fixtures.csv`, `data/controllers.csv`: 공통 자산 모델
- `reports/validation_report.md`: 분석 결과와 구현 원칙

## 현재 범위
- 수영구: 4,076 fixture rows / 204 cabinets
- 강릉: 5,667 fixture rows / 339 referenced cabinets
- 충주: 871 cabinet rows
- AMI: 5 streetlight meters / 6 daytime inspection candidates

## v0.2 실행 가이드 (수영구 검증 강화)
- 목적: 실제 AMI 미연결 상태를 노출하고, 수영구 204개 분전함(정격 3.4kW ±600W 근사 대상)에 대해 시나리오 주입으로 Detector 동작을 재현/검증
- 실행 스크립트: `lightguard_v0_1/src/build_lightguard_v02.py`
- 실행 커맨드:
  - `python3 lightguard_v0_1/src/build_lightguard_v02.py`
- 생성 산출물:
  - `lightguard_v0_1/data/suyeong_v02_objects.json`
  - `lightguard_v0_1/data/simulation_scenarios_v02.json`
  - `lightguard_v0_1/data/simulation_validation_results_v02.csv`
  - `lightguard_v0_1/app_seed/suyeong_v02_seed.json`
  - `lightguard_v0_1/data/suyeong_weather_stations_v02.csv`
  - `lightguard_v0_1/reports/validation_report_v02.md`
  - `lightguard_v0_1/source_manifest.json`
- 객체 스키마 핵심 형태(요청 스펙):
  - `cabinet_uid -> asset_info -> expected_schedule -> expected_load -> ami -> anomaly_evidence -> inspection_priority`
