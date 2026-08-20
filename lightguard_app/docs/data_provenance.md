# LightGuard Data Provenance

## 런타임 데이터 흐름

- 지역 선택/전환: `selectedRegionProvider` (`RegionId`)
- 데이터 로드: `lightguardDataProvider` → `LightguardRepository.loadData(region)`
- 입력 파일:
  - `suyeong_v02_seed.json`
  - `gangneung_v02_seed.json`
  - `chungju_v02_seed.json`
- 파서: `LightguardRepository` → `LocalAssetSource.readSeedByRegion()` → `LightguardData.fromSeedJson()`

## 시나리오/검증 데이터

- `simulation_scenarios_v02.json` + `simulation_validation_results_v02.csv`
- 검증 시나리오 대상은 `target_mode` 및 `validation_rows`로 판정합니다.

## 실제 AMI 데이터 분리

- `assets/data/ami_events.csv`는 **실제 공모전 AMI 검증 사례** 전용입니다.
- 지자체 실데이터의 AMI와 같은 의미로 표시하지 않습니다.
- `ValidationEvent`는 가명화 공모전 AMI의 점검 후보 6건을 화면에 제공합니다.
- 이벤트의 `off_baseline_a`, `peak_current_a`, `on_baseline_a`만 비교 시각화하며 원시 시계열을 재구성하지 않습니다.
- `estimated_excess_kwh` 합계는 3.994 kWh이며, 근거 단가가 없어 비용으로 환산하지 않습니다.

## 지역별 AMI capability

- 부산 수영구: Full Asset + Scenario Validation, 실제 지자체 AMI 매핑 0건
- 강릉시: Controller-linked Validation, 실제 지자체 AMI 매핑 0건
- 충주시: Minimal Asset / Asset-only, 실제 지자체 AMI 매핑 0건
- 강릉 seed의 legacy AMI 연결 필드는 제어기 연계 구조를 표현한 이전 산출물이며 런타임에서 실제 AMI로 승인하지 않습니다.

## 유의해야 할 표현 규칙

- 허용: 검증 시나리오, 실제 공공자산, 실제 공모전 AMI, 점검 후보, 제어기 연계 검증, Asset-only
- 비허용: 실제 지자체 AMI 연동, 실제 고장 확정, 46/46를 현장 정확도로 해석

## 부가 노트

- `suyeong_v02_objects.json`은 현재 Flutter 런타임 입력이 아닌 분석용 산출물입니다.
