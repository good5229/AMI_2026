import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/v15_target_mechanism_card.dart';

void main() {
  test('v0.15 target mechanism result is mixed and claim-safe', () {
    expect(V15TargetMechanismContract.status, '일부 조건에서만 효과 확인');
    expect(V15TargetMechanismContract.freeze, contains('판정 기준을 유지'));
    expect(V15TargetMechanismContract.disclosures, hasLength(6));

    final statuses = {
      for (final disclosure in V15TargetMechanismContract.disclosures)
        disclosure.name: disclosure.status,
    };
    expect(statuses['새로 분리한 검증자료'], '71개 조건 조합 확인 완료');
    expect(statuses['동일 판정 기준에서 구성요소별 영향 비교'], '비교 완료');
    expect(statuses['이상 사례와 정상 사례 비교'], '조건에 따라 결과가 다름');
    expect(statuses['보조 통계 기준과 비교'], '참고용 결과');
    expect(statuses['실제 자료 관찰 구간'], '현장 정답 없이 확인 완료');
    expect(statuses['외부자료 검증 근거'], '개선 효과 확인 안 됨');
    expect(V15TargetMechanismContract.naturalShadow, contains('현장 정답이 없으므로'));
    expect(V15TargetMechanismContract.canonicalSix, contains('판정 동작 확인'));
    expect(V15TargetMechanismContract.claimBoundary, contains('현장 정확도'));
    expect(V15TargetMechanismContract.claimBoundary, contains('실제 정상 오분류율'));
    expect(V15TargetMechanismContract.claimBoundary, contains('고장 확률'));
    expect(V15TargetMechanismContract.claimBoundary,
        contains('모든 이상 유형의 성능'));
  });
}
