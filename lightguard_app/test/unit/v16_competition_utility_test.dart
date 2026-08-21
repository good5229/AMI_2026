import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/v16_competition_utility_card.dart';

void main() {
  test('v0.16 exposes failed exploratory targets and claim boundary', () {
    expect(V16CompetitionUtilityContract.status, 'EXPLORATORY_TARGETS_FAILED');
    expect(V16CompetitionUtilityContract.officialObjective, contains('사업 적합성'));
    expect(V16CompetitionUtilityContract.officialObjective, contains('범용성'));
    expect(V16CompetitionUtilityContract.assetScope, contains('가로등 5개'));
    expect(V16CompetitionUtilityContract.assetScope, contains('모두 evaluable'));
    expect(V16CompetitionUtilityContract.recovery, contains('-21.95%p'));
    expect(V16CompetitionUtilityContract.recovery, contains('실패'));
    expect(V16CompetitionUtilityContract.benign, contains('-2.56%p'));
    expect(V16CompetitionUtilityContract.benign, contains('실패'));
    expect(V16CompetitionUtilityContract.decision, contains('추가 tuning하지 않습니다'));
    expect(V16CompetitionUtilityContract.nextExperiment, contains('신규 계절 AMI'));
    expect(V16CompetitionUtilityContract.boundary, contains('독립검증'));
    expect(V16CompetitionUtilityContract.boundary, contains('현장 정확도'));
    expect(V16CompetitionUtilityContract.boundary, contains('real FPR'));
    expect(V16CompetitionUtilityContract.boundary, contains('고장 확률'));
  });
}
