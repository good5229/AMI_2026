import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/v16_competition_utility_card.dart';

void main() {
  test('v0.16 exposes failed exploratory targets and claim boundary', () {
    expect(V16CompetitionUtilityContract.status, '탐색 목표를 충족하지 못함');
    expect(V16CompetitionUtilityContract.officialObjective, contains('사업 적합성'));
    expect(V16CompetitionUtilityContract.officialObjective, contains('범용성'));
    expect(V16CompetitionUtilityContract.assetScope, contains('가로등 계량기 5개'));
    expect(V16CompetitionUtilityContract.assetScope, contains('모두 분석 가능'));
    expect(V16CompetitionUtilityContract.recovery, contains('-21.95%p'));
    expect(V16CompetitionUtilityContract.recovery, contains('충족하지 못함'));
    expect(V16CompetitionUtilityContract.benign, contains('-2.56%p'));
    expect(V16CompetitionUtilityContract.benign, contains('충족하지 못함'));
    expect(V16CompetitionUtilityContract.decision, contains('판정 기준을 추가 조정하지 않습니다'));
    expect(V16CompetitionUtilityContract.nextExperiment, contains('새로운 계절 전력자료'));
    expect(V16CompetitionUtilityContract.boundary, contains('독립적으로 수집한 자료의 검증'));
    expect(V16CompetitionUtilityContract.boundary, contains('현장 정확도'));
    expect(V16CompetitionUtilityContract.boundary, contains('실제 정상 오분류율'));
    expect(V16CompetitionUtilityContract.boundary, contains('고장 확률'));
  });
}
