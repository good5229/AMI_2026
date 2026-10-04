import '../../data/models/lightguard_models.dart';

String operationalStatusLabel(InspectionStatus status) => switch (status) {
      InspectionStatus.normal => '정상 범위',
      InspectionStatus.observe => '관찰',
      InspectionStatus.inspectionRecommended => '점검 검토',
      InspectionStatus.priorityInspection => '우선 확인',
      InspectionStatus.dataCheckRequired => '미관측',
    };

String operationalSignalTitle(DetectedSignal? signal) {
  return switch (signal?.eventType) {
    'daytime_partial_activation' => '주간 부분 점등',
    'daytime_phase_selective_activation' => '주간 상별 점등',
    'partial_dimming' => '정격 대비 부하 감소',
    null || '' => '관측 자료 없음',
    _ => '운전 기준 이탈',
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
  return '${(signal.maxActivation * 100).toStringAsFixed(1)}%';
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
    return '가명 처리 전력계량 자료';
  }
  if (cabinet.signalSource == SignalSource.realMunicipalAmi) {
    return '지자체 연계 전력계량 자료';
  }
  if (cabinet.evidenceSource == EvidenceSource.realMunicipalAsset) {
    return '지자체 공공자산 정보';
  }
  return '공공자산 정보 · 전력계량 자료 미연결';
}

String operationalAssetSourceLabel(CabinetRecord cabinet) =>
    switch (cabinet.assetSource) {
      AssetSource.municipalPublicData => '지자체 공공자산 자료',
    };

String operationalSignalSourceLabel(CabinetRecord cabinet) =>
    switch (cabinet.signalSource) {
      SignalSource.scenarioInjection => '검증용 모의 전력 신호',
      SignalSource.realCompetitionAmi => '가명 처리 AMI 전력 신호',
      SignalSource.realMunicipalAmi => '지자체 연계 AMI 전력 신호',
      SignalSource.none => '전력 신호 미연결',
    };

String operationalPriorityReason(CabinetRecord cabinet) {
  final signal = cabinet.detectedSignals.firstOrNull;
  if (cabinet.signalSource == SignalSource.none) {
    return 'AMI 미연결 · 현재 상태 판단 불가';
  }
  if (signal == null) {
    return cabinet.status == InspectionStatus.normal
        ? '지속 신호 없음'
        : '신호 자료 없음 · 자료 확인 필요';
  }
  return '${operationalSignalTitle(signal)} · ${signal.estimatedDurationMin}분 · '
      '${operationalSignalLevel(signal)} · 순위 ${cabinet.inspectionPriority.rank}';
}

String operationalRecommendedAction(InspectionStatus status) =>
    switch (status) {
      InspectionStatus.priorityInspection =>
        '원격 확인 → 지속 시 현장점검',
      InspectionStatus.inspectionRecommended =>
        '이력·동시간대 비교 → 점검 판단',
      InspectionStatus.observe => '다음 주기 재확인',
      InspectionStatus.normal => '정기 점검 유지',
      InspectionStatus.dataCheckRequired =>
        '계량기 연결자료 확보 또는 직접 점검',
    };

String operationalEvidenceBoundary(CabinetRecord cabinet) {
  if (cabinet.evidenceSource == EvidenceSource.scenarioInjection) {
    return '모의 신호 · 고장/점검 결과 아님';
  }
  if (!cabinet.ami.hasRealAmi) {
    return 'AMI 미연결 · 현장 상태 미확정';
  }
  return '확인 후보 · 담당자 판단 필요';
}
