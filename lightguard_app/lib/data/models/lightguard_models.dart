import 'dart:convert';

enum InspectionSeverity { low, medium, high, critical }

enum EvidenceSource { realMunicipalAsset, realCompetitionAmi, scenarioInjection }

enum AmiLinkMode { none, real, scenarioInjection }

enum InspectionStatus { normal, observe, inspectionRecommended, priorityInspection, dataCheckRequired }

class LightguardData {
  const LightguardData({
    required this.generatedAt,
    required this.schemaVersion,
    required this.municipality,
    required this.objects,
    required this.targetMode,
    required this.validationScenarios,
    required this.validationRows,
  });

  final DateTime generatedAt;
  final String schemaVersion;
  final String municipality;
  final List<CabinetRecord> objects;
  final Map<String, dynamic> targetMode;
  final List<ScenarioRecord> validationScenarios;
  final List<ValidationRow> validationRows;

  factory LightguardData.fromSeedJson(String seedJson, String scenariosJson, String validationCsv) {
    final seed = jsonDecode(seedJson) as Map<String, dynamic>;
    final scenarios = (jsonDecode(scenariosJson) as List<dynamic>)
        .map((e) => ScenarioRecord.fromJson(e as Map<String, dynamic>))
        .toList(growable: false);

    return LightguardData(
      generatedAt: DateTime.tryParse(seed['generated_at'] as String? ?? '') ?? DateTime.now(),
      schemaVersion: seed['schema_version']?.toString() ?? '',
      municipality: seed['municipality']?.toString() ?? 'suyeong',
      objects: (seed['objects'] as List<dynamic>? ?? const [])
          .map((e) => CabinetRecord.fromJson(e as Map<String, dynamic>))
          .toList(growable: false),
      targetMode: (seed['target_mode'] as Map<String, dynamic>? ?? const <String, dynamic>{}),
      validationScenarios: scenarios,
      validationRows: parseValidationRows(validationCsv),
    );
  }

  static List<ValidationRow> parseValidationRows(String csv) {
    final lines = LineSplitter.split(csv).toList();
    if (lines.length <= 1) return const [];
    final headers = _parseCsvLine(lines.first);
    final rows = <ValidationRow>[];
    for (var i = 1; i < lines.length; i++) {
      if (lines[i].trim().isEmpty) continue;
      final values = _parseCsvLine(lines[i]);
      final row = <String, dynamic>{};
      for (var j = 0; j < headers.length; j++) {
        row[headers[j]] = j < values.length ? values[j] : null;
      }
      rows.add(ValidationRow.fromJson(row));
    }
    return rows;
  }

  static List<String> _parseCsvLine(String line) {
    final result = <String>[];
    final buffer = StringBuffer();
    bool inQuotes = false;
    for (var i = 0; i < line.length; i++) {
      final c = line[i];
      if (c == '"') {
        inQuotes = !inQuotes;
        continue;
      }
      if (c == ',' && !inQuotes) {
        result.add(buffer.toString());
        buffer.clear();
      } else {
        buffer.write(c);
      }
    }
    result.add(buffer.toString());
    return result.map((e) => e.trim().replaceAll(RegExp(r'^"|"$'), '')).toList(growable: false);
  }

  int get totalLampCount => objects.fold(0, (acc, o) => acc + o.assetInfo.lampCount);

  int get totalFixtureCount => objects.fold(0, (acc, o) => acc + o.assetInfo.fixtureCount);

  double get totalRatedLoadKw =>
      objects.fold(0.0, (acc, o) => acc + o.expectedLoad.expectedRatedLoadKw);

  int countByStatus(InspectionStatus status) =>
      objects.where((o) => o.status == status).length;
}

class ScenarioRecord {
  const ScenarioRecord({
    required this.scenarioId,
    required this.cabinetUid,
    required this.targetDurationMin,
    required this.detectMatched,
    required this.detectedEventCount,
    required this.targetDate,
  });

  final String scenarioId;
  final String cabinetUid;
  final int targetDurationMin;
  final bool detectMatched;
  final int detectedEventCount;
  final String targetDate;

  factory ScenarioRecord.fromJson(Map<String, dynamic> json) {
    return ScenarioRecord(
      scenarioId: json['scenario_id']?.toString() ?? '',
      cabinetUid: json['cabinet_uid']?.toString() ?? '',
      targetDurationMin: int.tryParse(json['target_duration_min']?.toString() ?? '') ?? 0,
      detectMatched: (json['detect_matched']?.toString().toLowerCase() == 'true'),
      detectedEventCount: int.tryParse(json['detected_event_count']?.toString() ?? '') ?? 0,
      targetDate: json['scenario_date']?.toString() ?? '',
    );
  }
}

class ValidationRow {
  const ValidationRow({
    required this.scenarioId,
    required this.cabinetUid,
    required this.detectMatched,
    required this.detectedEventCount,
  });

  final String scenarioId;
  final String cabinetUid;
  final bool detectMatched;
  final int detectedEventCount;

  factory ValidationRow.fromJson(Map<String, dynamic> json) {
    return ValidationRow(
      scenarioId: json['scenario_id']?.toString() ?? '',
      cabinetUid: json['cabinet_uid']?.toString() ?? '',
      detectMatched: (json['detect_matched']?.toString().toLowerCase() == 'true'),
      detectedEventCount: int.tryParse(json['detected_event_count']?.toString() ?? '') ?? 0,
    );
  }
}

class CabinetRecord {
  const CabinetRecord({
    required this.cabinetUid,
    required this.assetInfo,
    required this.expectedSchedule,
    required this.expectedLoad,
    required this.weatherContext,
    required this.ami,
    required this.detectedSignals,
    required this.anomalyEvidence,
    required this.inspectionPriority,
  });

  final String cabinetUid;
  final AssetInfo assetInfo;
  final ExpectedSchedule expectedSchedule;
  final ExpectedLoad expectedLoad;
  final WeatherContext weatherContext;
  final AmiPayload ami;
  final List<DetectedSignal> detectedSignals;
  final AnomalyEvidence anomalyEvidence;
  final InspectionPriority inspectionPriority;

  factory CabinetRecord.fromJson(Map<String, dynamic> json) {
    return CabinetRecord(
      cabinetUid: json['cabinet_uid']?.toString() ?? '',
      assetInfo: AssetInfo.fromJson(json['asset_info'] as Map<String, dynamic>? ?? const {}),
      expectedSchedule: ExpectedSchedule.fromJson(json['expected_schedule'] as Map<String, dynamic>? ?? const {}),
      expectedLoad: ExpectedLoad.fromJson(json['expected_load'] as Map<String, dynamic>? ?? const {}),
      weatherContext: WeatherContext.fromJson(json['weather_context'] as Map<String, dynamic>? ?? const {}),
      ami: AmiPayload.fromJson(json['ami'] as Map<String, dynamic>? ?? const {}),
      detectedSignals: (json['detected_signals'] as List<dynamic>? ?? const [])
          .map((e) => DetectedSignal.fromJson(e as Map<String, dynamic>))
          .toList(growable: false),
      anomalyEvidence: AnomalyEvidence.fromJson(json['anomaly_evidence'] as Map<String, dynamic>? ?? const {}),
      inspectionPriority: InspectionPriority.fromJson(
        json['inspection_priority'] as Map<String, dynamic>? ?? const {},
      ),
    );
  }

  InspectionStatus get status {
    if (inspectionPriority.severity == 'critical') return InspectionStatus.priorityInspection;
    if (inspectionPriority.severity == 'high') return InspectionStatus.inspectionRecommended;
    if (inspectionPriority.severity == 'medium' && detectedSignals.isNotEmpty) {
      return InspectionStatus.inspectionRecommended;
    }
    if (detectedSignals.isNotEmpty) return InspectionStatus.observe;
    return InspectionStatus.normal;
  }

  EvidenceSource get evidenceSource {
    if (ami.virtualLinkMode == 'scenario_injection') return EvidenceSource.scenarioInjection;
    return EvidenceSource.realCompetitionAmi;
  }

  String get modeLabel {
    if (ami.hasRealAmi) return '실제 AMI';
    if (ami.virtualLinkMode == 'scenario_injection') return '검증 시나리오';
    return '실측 없음';
  }
}

class AssetInfo {
  const AssetInfo({
    required this.cabinetUid,
    required this.cabinetName,
    required this.latitude,
    required this.longitude,
    required this.fixtureCount,
    required this.lampCount,
    required this.controllerType,
    required this.linkStatus,
    required this.address,
    required this.fixtures,
  });

  final String cabinetUid;
  final String cabinetName;
  final double? latitude;
  final double? longitude;
  final int fixtureCount;
  final int lampCount;
  final String controllerType;
  final String linkStatus;
  final String address;
  final List<FixtureInfo> fixtures;

  factory AssetInfo.fromJson(Map<String, dynamic> json) {
    return AssetInfo(
      cabinetUid: json['cabinet_uid']?.toString() ?? '',
      cabinetName: json['cabinet_name']?.toString() ?? 'Unknown Cabinet',
      latitude: double.tryParse(json['latitude']?.toString() ?? ''),
      longitude: double.tryParse(json['longitude']?.toString() ?? ''),
      fixtureCount: int.tryParse(json['fixture_count']?.toString() ?? '') ?? 0,
      lampCount: int.tryParse(json['lamp_count']?.toString() ?? '') ?? 0,
      controllerType: json['metadata'] is Map<String, dynamic>
          ? json['metadata']['controller_type']?.toString() ?? ''
          : json['controller_type']?.toString() ?? '',
      linkStatus: json['metadata'] is Map<String, dynamic>
          ? json['metadata']['controller_link_status']?.toString() ?? ''
          : json['controller_link_status']?.toString() ?? '',
      address: json['metadata'] is Map<String, dynamic>
          ? json['metadata']['address']?.toString() ?? ''
          : json['address']?.toString() ?? '',
      fixtures: (json['fixtures'] as List<dynamic>? ?? const [])
          .map((e) => FixtureInfo.fromJson(e as Map<String, dynamic>))
          .toList(growable: false),
    );
  }

  String get location => address.isNotEmpty ? address : '$latitude, $longitude';
}

class FixtureInfo {
  const FixtureInfo({
    required this.fixtureUid,
    required this.sourceFixtureId,
    required this.roadName,
    required this.lampCount,
    required this.lampWatt,
    required this.ratedPowerW,
    required this.latitude,
    required this.longitude,
  });

  final String fixtureUid;
  final String sourceFixtureId;
  final String roadName;
  final int lampCount;
  final double? lampWatt;
  final double? ratedPowerW;
  final double? latitude;
  final double? longitude;

  factory FixtureInfo.fromJson(Map<String, dynamic> json) {
    return FixtureInfo(
      fixtureUid: json['fixture_uid']?.toString() ?? '',
      sourceFixtureId: json['source_fixture_id']?.toString() ?? '',
      roadName: json['road_name']?.toString() ?? '',
      lampCount: int.tryParse(json['lamp_count']?.toString() ?? '') ?? 0,
      lampWatt: double.tryParse(json['lamp_watt']?.toString() ?? ''),
      ratedPowerW: double.tryParse(json['rated_power_w']?.toString() ?? ''),
      latitude: double.tryParse(json['latitude']?.toString() ?? ''),
      longitude: double.tryParse(json['longitude']?.toString() ?? ''),
    );
  }
}

class ExpectedSchedule {
  const ExpectedSchedule({
    required this.date,
    required this.sunrise,
    required this.sunset,
    required this.civilTwilightStart,
    required this.civilTwilightEnd,
    required this.expectedOnWindow,
  });

  final String date;
  final String sunrise;
  final String sunset;
  final String civilTwilightStart;
  final String civilTwilightEnd;
  final Map<String, dynamic> expectedOnWindow;

  factory ExpectedSchedule.fromJson(Map<String, dynamic> json) {
    return ExpectedSchedule(
      date: json['date']?.toString() ?? '',
      sunrise: json['sunrise']?.toString() ?? '',
      sunset: json['sunset']?.toString() ?? '',
      civilTwilightStart: json['civil_twilight_start']?.toString() ?? '',
      civilTwilightEnd: json['civil_twilight_end']?.toString() ?? '',
      expectedOnWindow: json['expected_on_window'] as Map<String, dynamic>? ?? const {},
    );
  }
}

class ExpectedLoad {
  const ExpectedLoad({
    required this.ratedPowerW,
    required this.expectedRatedLoadKw,
    required this.lampCount,
    required this.fixtureRows,
  });

  final double ratedPowerW;
  final double expectedRatedLoadKw;
  final int lampCount;
  final int fixtureRows;

  factory ExpectedLoad.fromJson(Map<String, dynamic> json) {
    return ExpectedLoad(
      ratedPowerW: double.tryParse(json['rated_power_w']?.toString() ?? '') ?? 0.0,
      expectedRatedLoadKw: double.tryParse(json['expected_rated_load_kW']?.toString() ?? '') ?? 0.0,
      lampCount: int.tryParse(json['lamp_count']?.toString() ?? '') ?? 0,
      fixtureRows: int.tryParse(json['fixture_rows']?.toString() ?? '') ?? 0,
    );
  }
}

class WeatherContext {
  const WeatherContext({
    required this.stationName,
    required this.stationType,
    required this.distanceKmToStation,
    required this.forecastHourly,
    required this.observationAt,
  });

  final String stationName;
  final String stationType;
  final double? distanceKmToStation;
  final List<Map<String, dynamic>> forecastHourly;
  final String observationAt;

  factory WeatherContext.fromJson(Map<String, dynamic> json) {
    final hourly = <Map<String, dynamic>>[];
    final f = json['forecast_hourly'] as List<dynamic>? ?? const [];
    for (final e in f) {
      if (e is Map) {
        hourly.add(Map<String, dynamic>.from(e));
      }
    }
    return WeatherContext(
      stationName: json['station_name']?.toString() ?? '',
      stationType: json['station_type']?.toString() ?? '',
      distanceKmToStation: double.tryParse(json['distance_km_to_station']?.toString() ?? ''),
      forecastHourly: hourly,
      observationAt: json['observation_at']?.toString() ?? '',
    );
  }
}

class AmiPayload {
  const AmiPayload({
    required this.hasRealAmi,
    required this.amiState,
    required this.virtualLinkMode,
    required this.amiMeterId,
  });

  final bool hasRealAmi;
  final String amiState;
  final String virtualLinkMode;
  final String? amiMeterId;

  factory AmiPayload.fromJson(Map<String, dynamic> json) {
    return AmiPayload(
      hasRealAmi: (json['has_real_ami']?.toString() == 'true'),
      amiState: json['ami_state']?.toString() ?? 'unlinked',
      virtualLinkMode: json['virtual_link_mode']?.toString() ?? 'none',
      amiMeterId: json['ami_meter_id']?.toString(),
    );
  }

  EvidenceSource get source {
    if (virtualLinkMode == 'scenario_injection') return EvidenceSource.scenarioInjection;
    if (hasRealAmi) return EvidenceSource.realCompetitionAmi;
    return EvidenceSource.realMunicipalAsset;
  }

  AmiLinkMode get linkMode {
    if (virtualLinkMode == 'scenario_injection') return AmiLinkMode.scenarioInjection;
    if (hasRealAmi) return AmiLinkMode.real;
    return AmiLinkMode.none;
  }
}

class DetectedSignal {
  const DetectedSignal({
    required this.eventType,
    required this.firstSample,
    required this.lastSample,
    required this.estimatedDurationMin,
    required this.maxActivation,
    required this.patternConfidence,
  });

  final String eventType;
  final String firstSample;
  final String lastSample;
  final int estimatedDurationMin;
  final double maxActivation;
  final String patternConfidence;

  factory DetectedSignal.fromJson(Map<String, dynamic> json) {
    return DetectedSignal(
      eventType: json['event_type']?.toString() ?? '',
      firstSample: json['first_sample']?.toString() ?? '',
      lastSample: json['last_sample']?.toString() ?? '',
      estimatedDurationMin: int.tryParse(json['estimated_duration_min']?.toString() ?? '') ?? 0,
      maxActivation: double.tryParse(json['max_activation']?.toString() ?? '') ?? 0.0,
      patternConfidence: json['pattern_confidence']?.toString() ?? '',
    );
  }
}

class AnomalyEvidence {
  const AnomalyEvidence({
    required this.ruleIds,
    required this.payload,
  });

  final List<String> ruleIds;
  final Map<String, dynamic> payload;

  factory AnomalyEvidence.fromJson(Map<String, dynamic> json) {
    return AnomalyEvidence(
      ruleIds: List<String>.from(json['rule_ids'] as List<dynamic>? ?? const []),
      payload: Map<String, dynamic>.from(json['payload'] as Map<String, dynamic>? ?? const {}),
    );
  }

  String get summary {
    final expected = payload['expected'];
    final observed = payload['observed'];
    if (expected is Map && observed is Map) {
      return '예상 ${expected['expected_duration_min']}분 / 관측 ${observed['duration_min']}분';
    }
    return '검증 근거 미등록';
  }
}

class InspectionPriority {
  const InspectionPriority({
    required this.score,
    required this.severity,
    required this.rank,
    required this.reason,
  });

  final double score;
  final String severity;
  final int rank;
  final String reason;

  factory InspectionPriority.fromJson(Map<String, dynamic> json) {
    return InspectionPriority(
      score: double.tryParse(json['score']?.toString() ?? '') ?? 0.0,
      severity: json['severity']?.toString() ?? 'low',
      rank: int.tryParse(json['rank']?.toString() ?? '') ?? 0,
      reason: json['reason']?.toString() ?? '',
    );
  }
}
