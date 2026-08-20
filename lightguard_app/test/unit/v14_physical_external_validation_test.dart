import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/v14_physical_external_card.dart';

void main() {
  test('v0.14 physical external contract preserves scope boundaries', () {
    expect(V14PhysicalExternalContract.status, 'SUITABILITY_GATED');
    expect(V14PhysicalExternalContract.v13Freeze,
        contains('NOT_EVALUABLE_INCOMPLETE_COVERAGE'));

    final claims = {
      for (final dataset in V14PhysicalExternalContract.datasets)
        dataset.name: dataset,
    };
    expect(claims, hasLength(4));
    expect(claims['London Met']?.status, 'PRIMARY_BLOCKED_PROVENANCE');
    expect(claims['CoDEx-VFD']?.scope, contains('VFD/EMI 전류 메커니즘'));
    expect(claims['SustDataED2']?.status,
        'TRANSITION_POSITIVE_CONTROL_ONLY');
    expect(claims['3PhaseInsight']?.status, 'REFERENCE_ONLY');
    expect(V14PhysicalExternalContract.pmc3, contains('PMC-3 unavailable'));
    expect(V14PhysicalExternalContract.claimBoundary, contains('가로등 현장 정확도'));
    expect(V14PhysicalExternalContract.claimBoundary, contains('실제 고장 확률'));
  });
}
