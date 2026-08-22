import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/v18_operational_triage_card.dart';

void main() {
  test('v0.18 preserves retrospective operational triage boundary', () {
    expect(V18OperationalTriageContract.primary, contains('30일 반복 기록'));
    expect(V18OperationalTriageContract.queue, contains('하위 기준 0건'));
    expect(V18OperationalTriageContract.workflow,
        contains('원격 확인 후보'));
    expect(V18OperationalTriageContract.workflow,
        contains('현장점검 후보'));
    expect(V18OperationalTriageContract.boundary, contains('사후 모의분석'));
    expect(V18OperationalTriageContract.boundary, contains('고장 확률'));
    expect(V18OperationalTriageContract.boundary, contains('전력자료 정확도'));
    expect(V18OperationalTriageContract.boundary, contains('실제 수리시간 단축'));
    expect(V18OperationalTriageContract.boundary, contains('민원 감소'));
    expect(V18OperationalTriageContract.boundary, contains('비용절감'));
    expect(V18OperationalTriageContract.boundary, contains('대구 결과의 수영구 직접 적용'));
  });
}
