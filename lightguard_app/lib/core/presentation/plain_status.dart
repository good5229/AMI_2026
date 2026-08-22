String plainStatusLabel(Object? value) {
  final normalized = value?.toString().trim().toUpperCase() ?? '';
  return switch (normalized) {
    '' || 'NULL' || 'NONE' => '확인 자료 없음',
    'AVAILABLE' || 'COMPLETED' || 'PASS' || 'PASSED' => '확인 완료',
    'PARTIAL' || 'PARTIAL_JOIN' => '일부 자료만 연결됨',
    'NO_SPATIAL_JOIN' || 'NO_JOIN' => '자료 간 연결번호 없음',
    'NON_EVALUABLE' || 'NOT_EVALUABLE' => '현재 자료로 평가할 수 없음',
    'NEGATIVE' || 'FAILED' || 'FAILURE_PRESERVED' => '개선 효과 확인 안 됨',
    'POSITIVE' => '개선 효과 확인됨',
    'MIXED' || 'MIXED_RESULT' => '조건에 따라 결과가 다름',
    'SECONDARY_ONLY' => '참고자료로만 사용',
    'TRUTH_FREE_COMPLETED' => '현장 정답 없이 확인 완료',
    'DATA_INSUFFICIENT' => '자료 부족으로 판정 보류',
    _ => _sentenceCase(value?.toString() ?? '확인 자료 없음'),
  };
}

String plainSensitivityLabel(Object? value) {
  final normalized = value?.toString().trim().toLowerCase() ?? '';
  return switch (normalized) {
    'stable' || 'robust' => '조건 변화에도 결과가 안정적',
    'sensitive' => '조건 변화에 따라 결과가 달라짐',
    'mixed' => '일부 조건에서 결과가 달라짐',
    'insufficient' || 'data_insufficient' => '자료 부족으로 평가할 수 없음',
    _ => plainStatusLabel(value),
  };
}

String _sentenceCase(String value) {
  if (!RegExp(r'^[A-Z0-9_\- ]+$').hasMatch(value)) return value;
  return value
      .toLowerCase()
      .replaceAll('_', ' ')
      .replaceAll('-', ' ')
      .trim();
}
