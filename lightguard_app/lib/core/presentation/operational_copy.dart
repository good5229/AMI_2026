import '../../data/models/lightguard_models.dart';

String operationalStatusLabel(InspectionStatus status) => switch (status) {
      InspectionStatus.normal => '정상 범위',
      InspectionStatus.observe => '추적 관찰',
      InspectionStatus.inspectionRecommended => '현장 확인 권고',
      InspectionStatus.priorityInspection => '우선 확인 필요',
      InspectionStatus.dataCheckRequired => '데이터 품질 확인 필요',
    };

String operationalSignalTitle(DetectedSignal? signal) {
  return switch (signal?.eventType) {
    'daytime_partial_activation' => '소등 예상 시간대의 부분 전력 사용 신호',
    'daytime_phase_selective_activation' => '소등 예상 시간대의 상별 전력 사용 신호',
    'partial_dimming' => '예상 정격부하 대비 전력 사용 감소 신호',
    null || '' => '우선 확인이 필요한 지속 신호 없음',
    _ => '운전 기준과 다른 전력 사용 신호',
  };
}

String operationalRuleLabel(String ruleId) => switch (ruleId) {
      'daytime_partial_activation' => '소등 예상 시간대 부분 전력 사용',
      'daytime_phase_selective_activation' => '소등 예상 시간대 상별 전력 사용',
      'partial_dimming' => '예상 정격부하 대비 부하 감소',
      'post_sunrise_persistence_90m' => '일출 이후 90분 이상 전력 사용 지속',
      'scenario_injection' => '검증용 모의 신호 적용',
      _ => '등록된 전력 사용 이상 기준',
    };

String operationalCriteria(CabinetRecord cabinet) {
  if (cabinet.anomalyEvidence.ruleIds.isEmpty) return '적용 기준 없음';
  return cabinet.anomalyEvidence.ruleIds
      .map(operationalRuleLabel)
      .toSet()
      .join(' · ');
}

String operationalSignalLevel(DetectedSignal? signal) {
  if (signal == null) return '관측값 없음';
  return '탐지 기준 대비 ${(signal.maxActivation * 100).toStringAsFixed(1)}%';
}

String operationalConfidenceLabel(DetectedSignal? signal) {
  return switch (signal?.patternConfidence.toLowerCase()) {
    'high' => '높음',
    'medium' => '보통',
    'low' => '낮음',
    _ => '평가 자료 없음',
  };
}

String operationalEvidenceSourceLabel(CabinetRecord cabinet) {
  if (cabinet.evidenceSource == EvidenceSource.scenarioInjection) {
    return '검증용 모의 신호';
  }
  if (cabinet.evidenceSource == EvidenceSource.realCompetitionAmi) {
    return '공모전 제공 전력계량 자료';
  }
  if (cabinet.signalSource == SignalSource.realMunicipalAmi) {
    return '지자체 연계 전력계량 자료';
  }
  if (cabinet.evidenceSource == EvidenceSource.realMunicipalAsset) {
    return '지자체 공공자산 정보';
  }
  return '공공자산 정보 · 전력계량 자료 미연결';
}

String operationalPriorityReason(CabinetRecord cabinet) {
  final signal = cabinet.detectedSignals.firstOrNull;
  if (signal == null) {
    return cabinet.status == InspectionStatus.normal
        ? '현재 등록된 판정 기준에서 우선 확인이 필요한 지속 신호가 확인되지 않았습니다.'
        : '우선순위는 등록되어 있으나 세부 관측 신호가 없어 데이터 품질 확인이 필요합니다.';
  }
  return '${operationalSignalTitle(signal)}가 ${signal.estimatedDurationMin}분간 관측됐습니다. '
      '${operationalSignalLevel(signal)}이며 전체 대상 중 확인 순위 ${cabinet.inspectionPriority.rank}번으로 분류했습니다.';
}

String operationalRecommendedAction(InspectionStatus status) => switch (status) {
      InspectionStatus.priorityInspection =>
        '제어기 상태와 전력 신호의 지속 여부를 먼저 원격 확인하고, 신호가 계속되면 현장점검 여부를 결정합니다.',
      InspectionStatus.inspectionRecommended =>
        '최근 제어이력과 동일 시간대 전력 신호를 확인한 뒤 현장점검 필요 여부를 판단합니다.',
      InspectionStatus.observe =>
        '다음 운전 주기까지 동일 신호가 반복되는지 원격으로 관찰합니다.',
      InspectionStatus.normal =>
        '현재 운전 상태를 유지하며 정기 점검 일정에 따라 확인합니다.',
      InspectionStatus.dataCheckRequired =>
        '전력 측정값 누락 여부, 분전함 연결정보, 측정 시각을 먼저 확인합니다.',
    };

String operationalEvidenceBoundary(CabinetRecord cabinet) {
  if (cabinet.evidenceSource == EvidenceSource.scenarioInjection) {
    return '검증용 모의 신호를 적용한 탐지 결과이며 실제 고장 판정이나 현장점검 결과가 아닙니다.';
  }
  if (!cabinet.ami.hasRealAmi) {
    return '실제 지자체 전력계량 자료가 연결되지 않은 시설정보이며 현장 상태를 확정하지 않습니다.';
  }
  return '전력 사용 신호에 따른 확인 후보이며 최종 상태는 담당자의 원격확인 또는 현장점검으로 판정합니다.';
}
