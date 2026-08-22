# LightGuard

LightGuard는 기존 AMI 전류 데이터를 활용해 가로등 회로의 비정상 운전 징후를
독립적으로 확인하고, 반복 유지관리 이력과 함께 원격관찰·현장점검 우선순위를
제시하는 지자체 유지관리 의사결정 지원 서비스입니다. 기존 원격제어시스템을
대체하지 않는 Second Checker입니다.

## 공모전 핵심 증거

- 부산 수영구 실제 공공자산: 분전함 204개, 자산행 약 4,076개, 실제 등 수 4,239등, 총 정격용량 약 488.44 kW
- Controlled scenario validation: 사전 정의한 46개 비정상 시나리오를 Detector 재현형 검증에서 46/46 검출
- 가명화 공모전 AMI: 자연발생 점검 후보 6건, 후보 구간 추정 초과전력량 합계 3.994 kWh
- 실제 지자체 운영근거: 대구 101,843건, 부여 3,437건, 울산 canonical 1,060건
- 외부 운영 일반화: 부여 top-10% enrichment 1.80x, 울산 TM-A
- 울산 U1-U2 결합: exact-ID/category/uniqueness gate 통과 자산 920/981
- 지역 확장: 강릉 Controller-linked Validation, 충주 Minimal Asset / Asset-only
- 실제 지자체 AMI 분전함 매핑: 세 지역 모두 0건

46/46은 controlled scenario 재현 결과이며 현장 성능지표가 아닙니다. 공모전 AMI
6건도 정비 이력 및 현장 확인이 필요한 점검 후보입니다. 대구·부여·울산 운영기록은
공모전 AMI의 직접 정답이 아닙니다.

## 실행 방법

### Flutter 기본 실행

```bash
cd lightguard_app
flutter pub get
flutter run
```

### Web 실행

```bash
cd lightguard_app
flutter run -d chrome
```

### Android 실행

```bash
cd lightguard_app
flutter build apk --debug
```

## Launch preflight(커밋 게이트)

### 1) 훅 한 번만 설치

```bash
cd /Users/bellhundred/git-repo/AMI_2026
./scripts/setup_githook.sh
```

### 2) 런칭 전 필수 검증

```bash
cd /Users/bellhundred/git-repo/AMI_2026
./scripts/launch_preflight.sh
```

실행 항목:
- flutter pub get
- flutter analyze
- flutter test
- flutter build web --release --base-href /AMI_2026/
- flutter build apk --debug

### 3) 체크 통과 후 커밋

기본 `git commit` 대신 다음 래퍼를 권장합니다.

```bash
cd /Users/bellhundred/git-repo/AMI_2026
./scripts/commit_with_checks.sh -m "..."
```

`commit_with_checks.sh`는 launch preflight를 통과해야만 커밋을 실행합니다.

#### 참고
- 훅 경로 설정이 되면 `git commit` 실행 시 자동으로 pre-commit에서 동일한 검증을 수행합니다.

## GitHub Pages

배포 주소:
https://github.com/good5229/AMI_2026/settings/pages 의 빌드 소스는 GitHub Actions입니다.
실제 배포 URL: https://good5229.github.io/AMI_2026/

## 데이터 출처

- `assets/data/suyeong_v02_seed.json`
- `assets/data/gangneung_v02_seed.json`
- `assets/data/chungju_v02_seed.json`
- `assets/data/simulation_scenarios_v02.json`
- `assets/data/simulation_validation_results_v02.csv`
- `assets/data/ami_events.csv`

## 화면/로직 정의

- **시나리오 주입(검증)**: 수영구 데이터에서만 주입 기반 이상 탐지 시나리오로 표시
- **실제 공모전 AMI**: `ami_events.csv`의 가명화 이벤트만
- **실제 지자체 AMI 직접 연계**: 현재 버전에서 지원하지 않음

## 알려진 제한사항

- 실제 원시 AMI 15분 시계열은 별도 수집이 필요합니다.
- 본 앱은 오탐지율/재현율 지표를 직접 계산하는 운영 분석 모듈이 아닙니다.
- 실제 지자체 AMI meter ID와 분전함 ID의 매핑은 아직 없습니다.
- 실제 고장 label과 정비이력이 없어 현장 정확도를 산정하지 않습니다.

## 제출 문서

- 최종 제출 패키지: `../submission/01_one_page_summary.md` ~ `08_judge_qna.md`
- Claim registry: `../lightguard_v0_1/data/submission/v21_claim_registry.json`
- Metric registry: `../lightguard_v0_1/data/submission/v21_metric_registry.json`
- 전체 제출 preflight: `../scripts/v21_preflight.sh`
