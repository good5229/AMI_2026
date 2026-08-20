# LightGuard App MVP v0.2 제출형 고도화

## 구현 범위
- Flutter 단일 코드베이스(Web + Android 중심)
- 수영구 204개 분전함 시연 중심 MVP
- 실제 자산/실제 AMI/검증 시나리오를 명시적으로 분리
- 실제 공모전 AMI 6건 및 대표 Case Study 3건
- 지역별 capability와 실제 지자체 AMI 0건 불변식

## 구조
- 앱 진입: `main.dart`
- 라우팅: `lib/app/router/app_router.dart`
- Shell 레이아웃: `lib/core/widgets/app_scaffold.dart`
- 데이터 소스: `assets/data/suyeong_v02_seed.json`, `assets/data/simulation_*`, `assets/data/ami_events.csv`
- Repository: `lib/data/repositories/lightguard_repository.dart`
- 모델: `lib/data/models/lightguard_models.dart`

## 주요 화면
- Dashboard: `lib/features/dashboard/dashboard_screen.dart`
- Map: `lib/features/map/map_screen.dart`
- Inspection Priority: `lib/features/inspections/inspection_list_screen.dart`
- Cabinet Detail: `lib/features/cabinet_detail/cabinet_detail_screen.dart`
- AMI Validation: `lib/features/ami_validation/ami_validation_screen.dart`
- Region: `lib/features/regions/regions_screen.dart`

## 데이터 분리
- 실제 공공자산: 자산 계층(asset_info, expected_load, expected_schedule)
- 실제 공모전 AMI: `ami_events.csv`에서 이벤트를 읽고 "실제 공모전 AMI" badge 적용
- Scenario Injection: `suyeong_v02_seed`의 `ami.virtual_link_mode == scenario_injection` 조건

## 실행법
- Web: 현재 Flutter 실행 환경에서 `flutter run -d chrome` (권장)
- Android: `flutter run -d <android-device>`

## Web 빌드
- `flutter build web`

## Android 빌드
- `flutter build apk --debug` 또는 `flutter build appbundle`

## 알려진 제한
- Flutter 실행 바이너리가 실행 환경에 따라 제약 가능성 있음
- 지도 타일이 실패 시 기본 목록/상세/대시보드는 별도 동작

## 현재 검증 기준

- 수영구 분전함 204개와 지도 좌표 204개
- Controlled scenario 46개 중 재현 검출 46개
- 실제 공모전 AMI 점검 후보 6건
- 실제 지자체 AMI 매핑 0건
- 강릉 Controller-linked / 충주 Asset-only 분기

## 다음 단계

- 실제 AMI meter ID와 지자체 분전함 ID 매핑
- 정비이력 및 현장 고장 label 연계
- 원본 event 전후 시계열을 확보한 경우에만 실제 시계열 시각화
