import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/core/storage/inspection_outcome_storage.dart';

void main() {
  test('v1 local case records remain readable and normalize saved outcomes',
      () {
    final migrated = normalizeInspectionOutcomes({
      'CAB-1': {'status': '조치 완료', 'note': '등기구 교체'},
      'CAB-2': {'status': '원격 확인 예정'},
    });
    expect(migrated['CAB-1']?['status'], '조치 완료');
    expect(migrated['CAB-1']?['outcomeCode'], 'action_completed');
    expect(migrated['CAB-1']?['stage'], 'field_review');
    expect(migrated['CAB-2']?['outcomeCode'], isNull);
    expect(migrated['CAB-2']?['stage'], 'remote_review');
  });

  test('case saves round-trip through the platform storage adapter', () async {
    TestWidgetsFlutterBinding.ensureInitialized();
    final expected = {
      'CAB-LOCAL': {
        'status': '정상',
        'outcomeCode': 'normal',
        'note': '현장 확인',
      },
    };
    await saveInspectionOutcomes(expected);
    expect(await loadInspectionOutcomes(), expected);
  });

  test('case summaries can be limited to the selected region dataset', () {
    final outcomes = {
      'CAB-IN-REGION': {'outcomeCode': 'normal'},
      'CAB-OTHER-REGION': {'outcomeCode': 'fault_observed'},
    };
    expect(
      inspectionOutcomesForCases(outcomes, ['CAB-IN-REGION']),
      {
        'CAB-IN-REGION': {'outcomeCode': 'normal'}
      },
    );
  });
}
