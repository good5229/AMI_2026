# LightGuard Competition Story

## 1. Problem

가로등 제어 명령이 시스템상 성공해도 실제 회로의 소비전력이 기대 상태와 일치하는지는
별도 검증이 필요합니다. LightGuard는 현장 운영을 과장해 단정하지 않고, 실제 전력과
자산 기대값의 불일치를 점검 후보로 좁히는 문제에 집중합니다.

## 2. Idea

기존 원격제어시스템을 교체하지 않습니다. 이미 설치된 AMI를 추가 센서 없이 활용해
제어상태 + AMI 실제 전력 + 자산 기대부하 + 운전시간 context를 비교하는 Second
Checker를 추가합니다.

## 3. Evidence

- 가명화 공모전 AMI에서 현장 미확인 점검 후보 6건
- 부산 수영구 실제 공공자산 분전함 204개, 실제 등 수 4,239등
- 사전 정의한 controlled abnormal scenario 46개를 재현형 검증에서 46/46 검출
- 강릉 Controller-linked Validation과 충주 Minimal Asset / Asset-only schema 확장

46/46은 실제 고장탐지 정확도 100%가 아닙니다. 공모전 AMI 후보 6건도 실제 고장으로
확정하지 않습니다.

## 4. Benefit

- 기존 AMI 및 관제 인프라 재활용
- 추가 현장 센서 설치 최소화 가능성
- 현장 출동 전 점검 대상 우선순위화
- 자산·운전시간·관측신호를 함께 제시하는 설명 가능한 판단

금액 절감은 실증 단가가 없어 주장하지 않습니다. 현재 근거로 계산 가능한 수치는 후보
구간 추정 초과전력량 합계 3.994 kWh입니다.

## 5. Limitation

- 실제 지자체 AMI meter와 분전함 ID 매핑 없음
- 실제 고장 label 및 정비이력 없음
- 현장 accuracy 미산정
- 실제 원본 15분 시계열은 앱 seed에 포함하지 않음

## 6. Next commercialization step

1. AMI meter ID와 municipal cabinet ID 매핑
2. 정비이력과 점검 결과 연계
3. 실제 pilot에서 오탐·미탐 및 출동 감소 효과 측정
4. 검증된 요금 단가와 운영비 기준으로 경제성 산정
