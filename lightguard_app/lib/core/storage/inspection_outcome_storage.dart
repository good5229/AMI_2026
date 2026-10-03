import 'inspection_outcome_storage_stub.dart'
    if (dart.library.html) 'inspection_outcome_storage_web.dart'
    as implementation;

Future<Map<String, Map<String, String>>> loadInspectionOutcomes() =>
    implementation.loadInspectionOutcomes().then(normalizeInspectionOutcomes);

Future<void> saveInspectionOutcomes(
        Map<String, Map<String, String>> outcomes) =>
    implementation.saveInspectionOutcomes(outcomes);

Map<String, Map<String, String>> inspectionOutcomesForCases(
  Map<String, Map<String, String>> outcomes,
  Iterable<String> caseIds,
) {
  final includedIds = caseIds.toSet();
  return Map.fromEntries(outcomes.entries.where(
    (entry) => includedIds.contains(entry.key),
  ));
}

Map<String, Map<String, String>> normalizeInspectionOutcomes(
        Map<String, Map<String, String>> outcomes) =>
    outcomes.map((uid, raw) {
      final record = Map<String, String>.from(raw);
      final legacy = record['status'];
      if (record['outcomeCode'] == null && legacy != null) {
        final mapped = switch (legacy) {
          '정상 확인' => 'normal',
          '고장 확인' => 'fault_observed',
          '조치 완료' => 'action_completed',
          '운영상 예외' => 'operational_exception',
          '자료 문제' => 'data_issue',
          _ => '',
        };
        if (mapped.isNotEmpty) record['outcomeCode'] = mapped;
        record['stage'] = switch (legacy) {
          '현장점검 필요' => 'field_review',
          '추적 관찰' => 'observation',
          '정상 확인' || '고장 확인' || '조치 완료' => 'field_review',
          _ => 'remote_review',
        };
      }
      return MapEntry(uid, record);
    });
