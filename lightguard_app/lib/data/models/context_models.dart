import 'dart:convert';

class OfficialContextBundle {
  const OfficialContextBundle({
    required this.solarStatus,
    required this.weatherStatus,
    required this.solarDays,
    required this.weatherObservations,
  });

  final String solarStatus;
  final String weatherStatus;
  final List<Map<String, dynamic>> solarDays;
  final List<Map<String, dynamic>> weatherObservations;

  factory OfficialContextBundle.fromJson(String solarJson, String weatherJson) {
    final solar = jsonDecode(solarJson) as Map<String, dynamic>;
    final weather = jsonDecode(weatherJson) as Map<String, dynamic>;
    return OfficialContextBundle(
      solarStatus: solar['context_source']?.toString() ?? 'unavailable',
      weatherStatus: weather['context_source']?.toString() ?? 'unavailable',
      solarDays: (solar['dates'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .toList(growable: false),
      weatherObservations:
          (weather['observations'] as List<dynamic>? ?? const [])
              .whereType<Map<String, dynamic>>()
              .toList(growable: false),
    );
  }

  Map<String, dynamic>? get firstOfficialSolar {
    for (final row in solarDays) {
      if (row['source'] == 'KASI_RISE_SET_OFFICIAL') return row;
    }
    return null;
  }

  Map<String, dynamic>? get firstOfficialWeather =>
      weatherObservations.isEmpty ? null : weatherObservations.first;

  bool get hasOfficialSolar => firstOfficialSolar != null;
  bool get hasOfficialWeather => firstOfficialWeather != null;
}

class ControlledMetric {
  const ControlledMetric({
    required this.model,
    required this.status,
    required this.anomalyRecall,
    required this.normalFpr,
    required this.precisionAt20,
    required this.candidateCount,
  });

  final String model;
  final String status;
  final double? anomalyRecall;
  final double? normalFpr;
  final double? precisionAt20;
  final int? candidateCount;

  factory ControlledMetric.fromCsv(Map<String, String> row) {
    return ControlledMetric(
      model: row['model'] ?? '',
      status: row['status'] ?? 'unavailable',
      anomalyRecall: double.tryParse(row['anomaly_recall'] ?? ''),
      normalFpr: double.tryParse(row['normal_fpr'] ?? ''),
      precisionAt20: double.tryParse(row['precision_at_20'] ?? ''),
      candidateCount: int.tryParse(row['inspection_candidate_count'] ?? ''),
    );
  }
}

class V04ValidationSummary {
  const V04ValidationSummary({
    required this.baselineCandidateCount,
    required this.bestCandidateCount,
    required this.normalFpr,
    required this.precisionAt10,
    required this.precisionAt20,
    required this.weatherDecision,
  });

  final int baselineCandidateCount;
  final int bestCandidateCount;
  final double normalFpr;
  final double precisionAt10;
  final double precisionAt20;
  final String weatherDecision;

  factory V04ValidationSummary.fromJson(String source) {
    final value = jsonDecode(source) as Map<String, dynamic>;
    final best = value['best_v04'] as Map<String, dynamic>? ?? const {};
    return V04ValidationSummary(
      baselineCandidateCount:
          (value['baseline_m0_candidate_count'] as num?)?.toInt() ?? 0,
      bestCandidateCount:
          (best['inspection_candidate_count'] as num?)?.toInt() ?? 0,
      normalFpr: (best['normal_fpr'] as num?)?.toDouble() ?? 0,
      precisionAt10: (best['precision_at_10'] as num?)?.toDouble() ?? 0,
      precisionAt20: (best['precision_at_20'] as num?)?.toDouble() ?? 0,
      weatherDecision: value['weather_decision']?.toString() ?? 'context_only',
    );
  }

  String get weatherLabel => weatherDecision == 'scoring_keep'
      ? '기상 Context 반영'
      : '기상 Context 참고정보';
}

class AmiReplaySample {
  const AmiReplaySample({
    required this.timestamp,
    required this.meterId,
    required this.i1,
    required this.i2,
    required this.i3,
    required this.activeEnergyKwh,
    required this.sourceRow,
  });

  final DateTime timestamp;
  final String meterId;
  final double? i1;
  final double? i2;
  final double? i3;
  final double? activeEnergyKwh;
  final int sourceRow;

  factory AmiReplaySample.fromCsv(Map<String, String> row) {
    return AmiReplaySample(
      timestamp: DateTime.parse(row['timestamp'] ?? ''),
      meterId: row['meter_id'] ?? '',
      i1: double.tryParse(row['i1'] ?? ''),
      i2: double.tryParse(row['i2'] ?? ''),
      i3: double.tryParse(row['i3'] ?? ''),
      activeEnergyKwh: double.tryParse(row['active_energy_kwh'] ?? ''),
      sourceRow: int.tryParse(row['source_row'] ?? '') ?? 0,
    );
  }
}
