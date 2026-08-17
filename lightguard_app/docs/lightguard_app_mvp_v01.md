# LightGuard App MVP v0.1

## 구현 범위
- Flutter 단일 코드베이스(Web + Android 중심)
- 수영구 204개 분전함 시연 중심 MVP
- 실제 자산/실제 AMI/검증 시나리오를 명시적으로 분리

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
- 실제 AMI: `ami_events.csv`에서 이벤트를 읽고 "실제 AMI" badge 적용
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

## 다음 단계
- 강릉/충주 데이터 실제 적용 스위치
- 상세 필터링(날짜, 상태, 이상 유형) 강화
- 탐지 이벤트의 시계열 원본 데이터 시각화를 위한 실제 시그널 적재
