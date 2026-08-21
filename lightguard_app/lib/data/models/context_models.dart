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

class V05ValidationSummary {
  const V05ValidationSummary({
    required this.legacyPeakConsistent,
    required this.adjudicatedPeakConsistent,
    required this.pastOnlyCoverage,
    required this.missing20Coverage,
    required this.downsample60Coverage,
    required this.gap120Coverage,
    required this.sensitivityClassification,
    required this.frozenBaselineFpr,
    required this.activationPlus20Fpr,
  });

  final int legacyPeakConsistent;
  final int adjudicatedPeakConsistent;
  final double pastOnlyCoverage;
  final double missing20Coverage;
  final double downsample60Coverage;
  final double gap120Coverage;
  final String sensitivityClassification;
  final double frozenBaselineFpr;
  final double activationPlus20Fpr;

  factory V05ValidationSummary.fromJson(String source) {
    final value = jsonDecode(source) as Map<String, dynamic>;
    final peak = value['actual_ami_peak'] as Map<String, dynamic>;
    final causal = value['causal_replay'] as Map<String, dynamic>;
    final coverage = causal['canonical_candidate_coverage'] as Map<String, dynamic>;
    final robustness = value['robustness'] as Map<String, dynamic>;
    final sensitivity = value['sensitivity'] as Map<String, dynamic>;
    return V05ValidationSummary(
      legacyPeakConsistent:
          (peak['legacy_metric_consistent'] as num).toInt(),
      adjudicatedPeakConsistent:
          (peak['adjudicated_metric_consistent'] as num).toInt(),
      pastOnlyCoverage: (coverage['30d'] as num).toDouble(),
      missing20Coverage:
          (robustness['random_missing_20pct_coverage'] as num).toDouble(),
      downsample60Coverage:
          (robustness['downsample_60m_coverage'] as num).toDouble(),
      gap120Coverage:
          (robustness['gap_120m_coverage'] as num).toDouble(),
      sensitivityClassification:
          sensitivity['classification']?.toString() ?? 'unavailable',
      frozenBaselineFpr:
          (sensitivity['frozen_baseline_normal_fpr'] as num).toDouble(),
      activationPlus20Fpr:
          (sensitivity['activation_plus_20_normal_fpr'] as num).toDouble(),
    );
  }
}

class V06EvidenceSummary {
  const V06EvidenceSummary({
    required this.coveragePoint,
    required this.coverageLower,
    required this.coverageUpper,
    required this.gap120Upper,
    required this.candidateDensityPoint,
    required this.candidateDensityLower,
    required this.candidateDensityUpper,
    required this.largestInteractionTerm,
    required this.largestInteractionEffect,
    required this.abstentionRuleCount,
    required this.fieldTruthAvailable,
  });

  final double coveragePoint;
  final double coverageLower;
  final double coverageUpper;
  final double gap120Upper;
  final double candidateDensityPoint;
  final double candidateDensityLower;
  final double candidateDensityUpper;
  final String largestInteractionTerm;
  final double largestInteractionEffect;
  final int abstentionRuleCount;
  final bool fieldTruthAvailable;

  factory V06EvidenceSummary.fromJson(String source) {
    final value = jsonDecode(source) as Map<String, dynamic>;
    final coverage = value['known_candidate_coverage'] as Map<String, dynamic>;
    final gap = value['gap_120m_coverage'] as Map<String, dynamic>;
    final density = value['candidate_density'] as Map<String, dynamic>;
    final interaction = value['interaction_diagnostic'] as Map<String, dynamic>;
    final abstention = value['abstention'] as Map<String, dynamic>;
    final truth = value['field_truth'] as Map<String, dynamic>;
    return V06EvidenceSummary(
      coveragePoint: (coverage['coverage_point'] as num).toDouble(),
      coverageLower: (coverage['wilson_95_lower'] as num).toDouble(),
      coverageUpper: (coverage['wilson_95_upper'] as num).toDouble(),
      gap120Upper: (gap['wilson_95_upper'] as num).toDouble(),
      candidateDensityPoint:
          (density['candidate_density_point'] as num).toDouble(),
      candidateDensityLower:
          (density['candidate_density_95_lower'] as num).toDouble(),
      candidateDensityUpper:
          (density['candidate_density_95_upper'] as num).toDouble(),
      largestInteractionTerm:
          interaction['largest_two_factor_fpr_term']?.toString() ?? '',
      largestInteractionEffect:
          (interaction['largest_two_factor_fpr_effect'] as num).toDouble(),
      abstentionRuleCount: (abstention['rule_count'] as num).toInt(),
      fieldTruthAvailable: truth['available'] == true,
    );
  }
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
