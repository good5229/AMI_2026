import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/v15_target_mechanism_card.dart';

void main() {
  test('v0.15 target mechanism contract is pre-result and claim-safe', () {
    expect(V15TargetMechanismContract.status, 'PRE_REGISTERED_NO_RESULTS');
    expect(V15TargetMechanismContract.freeze, contains('v0.10–v0.14 freeze'));
    expect(V15TargetMechanismContract.disclosures, hasLength(6));

    final statuses = {
      for (final disclosure in V15TargetMechanismContract.disclosures)
        disclosure.name: disclosure.status,
    };
    expect(statuses['New disjoint holdout'], 'FROZEN_BEFORE_RESULTS');
    expect(statuses['Same-threshold runtime ablation'], 'PRE_REGISTERED');
    expect(statuses['Anomaly / controlled-benign pair'], 'PAIRED_DESIGN');
    expect(statuses['Robust-z comparator'], 'COMPARATOR_ONLY');
    expect(statuses['Natural shadow'], 'NO_TRUTH');
    expect(statuses['External v0.13 / v0.14 evidence'], 'FAILURE_PRESERVED');
    expect(V15TargetMechanismContract.naturalShadow, contains('truth 미확보'));
    expect(V15TargetMechanismContract.canonicalSix, contains('diagnostic'));
    expect(V15TargetMechanismContract.claimBoundary, contains('현장 정확도'));
    expect(V15TargetMechanismContract.claimBoundary, contains('real FPR'));
    expect(V15TargetMechanismContract.claimBoundary, contains('고장 확률'));
    expect(V15TargetMechanismContract.claimBoundary,
        contains('일반 anomaly 성능'));
  });
}
