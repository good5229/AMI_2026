import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/lightguard_models.dart';
import '../sources/local_asset_source.dart';
import '../models/region_config.dart';
import '../models/context_models.dart';

class ValidationEvent {
  const ValidationEvent({
    required this.eventId,
    required this.meterId,
    required this.eventType,
    required this.firstSample,
    required this.lastSample,
    required this.durationMin,
    required this.maxActivation,
    required this.activePhases,
    required this.peakCurrentA,
    required this.offBaselineA,
    required this.onBaselineA,
    required this.patternConfidence,
    required this.estimatedExcessKwh,
    required this.energyMethod,
    required this.faultStatus,
    required this.sourceMode,
    required this.payloadRaw,
  });

  final String eventId;
  final String meterId;
  final String eventType;
  final String firstSample;
  final String lastSample;
  final int durationMin;
  final double maxActivation;
  final String activePhases;
  final double peakCurrentA;
  final double offBaselineA;
  final double onBaselineA;
  final String patternConfidence;
  final double estimatedExcessKwh;
  final String energyMethod;
  final String faultStatus;
  final String sourceMode;
  final String payloadRaw;

  static ValidationEvent fromCsv(Map<String, String> row) {
    return ValidationEvent(
      eventId: row['event_id'] ?? '',
      meterId: row['meter_id'] ?? '',
      eventType: row['event_type'] ?? '',
      firstSample: row['first_sample'] ?? '',
      lastSample: row['last_sample'] ?? '',
      durationMin: int.tryParse(row['estimated_duration_min'] ?? '') ?? 0,
      maxActivation: double.tryParse(row['max_activation'] ?? '') ?? 0.0,
      activePhases: row['active_phases'] ?? '',
      peakCurrentA: double.tryParse(row['peak_current_a'] ?? '') ?? 0.0,
      offBaselineA: double.tryParse(row['off_baseline_a'] ?? '') ?? 0.0,
      onBaselineA: double.tryParse(row['on_baseline_a'] ?? '') ?? 0.0,
      patternConfidence: row['pattern_confidence'] ?? '',
      estimatedExcessKwh:
          double.tryParse(row['estimated_excess_kwh'] ?? '') ?? 0.0,
      energyMethod: row['energy_method'] ?? '',
      faultStatus: row['fault_status'] ?? '',
      sourceMode: row['source_mode'] ?? '',
      payloadRaw: row.toString(),
    );
  }

  String get badge => '실제 공모전 AMI';
}

class LightguardRepository {
  LightguardRepository(this._assetSource);

  final LocalAssetSource _assetSource;

  Future<LightguardData> loadData(RegionId region) async {
    final seed = await _assetSource.readSeedByRegion(region);
    final scenarios = await _assetSource.readScenarios();
    final validation = await _assetSource.readValidationRows();
    return LightguardData.fromSeedJson(
      seed,
      scenarios,
      validation,
      allowRealMunicipalAmi: region.supportsRealMunicipalAmi,
    );
  }

  Future<List<ValidationEvent>> loadCompetitionAmiEvents() async {
    final csv = await _assetSource.readAmiEvents();
    final rows = const LineSplitter().convert(csv);
    if (rows.isEmpty) return const <ValidationEvent>[];
    final headers = _splitCsv(rows.first, isHeader: true);
    final events = <ValidationEvent>[];
    for (var i = 1; i < rows.length; i++) {
      if (rows[i].trim().isEmpty) continue;
      final values = _splitCsv(rows[i]);
      final m = <String, String>{};
      for (var h = 0; h < headers.length; h++) {
        if (h < values.length) m[headers[h]] = values[h];
      }
      events.add(ValidationEvent.fromCsv(m));
    }
    return events;
  }

  Future<OfficialContextBundle> loadOfficialContext() async {
    final values = await Future.wait<String>([
      _assetSource.readKasiContext(),
      _assetSource.readKmaContext(),
    ]);
    return OfficialContextBundle.fromJson(values[0], values[1]);
  }

  Future<List<ControlledMetric>> loadControlledMetrics() async {
    final csv = await _assetSource.readAblationResults();
    final rows = const LineSplitter().convert(csv);
    if (rows.length <= 1) return const <ControlledMetric>[];
    final headers = _splitCsv(rows.first, isHeader: true);
    return [
      for (var i = 1; i < rows.length; i++)
        if (rows[i].trim().isNotEmpty)
          ControlledMetric.fromCsv(_csvMap(headers, _splitCsv(rows[i]))),
    ];
  }

  Future<V04ValidationSummary> loadV04ValidationSummary() async {
    return V04ValidationSummary.fromJson(
        await _assetSource.readV04ValidationSummary());
  }

  Future<Map<String, List<AmiReplaySample>>> loadAmiReplayWindows() async {
    const files = <String>[
      'B-L-35_2026-05-11.csv',
      'B-L-14_2026-05-19.csv',
      'B-L-9_2026-05-20.csv',
      'B-L-9_2026-05-21.csv',
      'B-L-14_2026-05-29.csv',
      'B-L-13_2026-06-23.csv',
    ];
    final result = <String, List<AmiReplaySample>>{};
    for (final file in files) {
      final csv = await _assetSource.readReplayWindow(file);
      final rows = const LineSplitter().convert(csv);
      if (rows.length <= 1) continue;
      final headers = _splitCsv(rows.first, isHeader: true);
      result[file] = [
        for (var i = 1; i < rows.length; i++)
          if (rows[i].trim().isNotEmpty)
            AmiReplaySample.fromCsv(_csvMap(headers, _splitCsv(rows[i]))),
      ];
    }
    return result;
  }

  static Map<String, String> _csvMap(
      List<String> headers, List<String> values) {
    return <String, String>{
      for (var i = 0; i < headers.length; i++)
        headers[i]: i < values.length ? values[i] : '',
    };
  }

  static List<String> _splitCsv(String line, {bool isHeader = false}) {
    final result = <String>[];
    final b = StringBuffer();
    var inQuote = false;
    for (var i = 0; i < line.length; i++) {
      final c = line[i];
      if (c == '"') {
        inQuote = !inQuote;
        continue;
      }
      if (c == ',' && !inQuote) {
        result.add(b.toString());
        b.clear();
      } else {
        b.write(c);
      }
    }
    result.add(b.toString());
    if (isHeader && result.isNotEmpty && result.first.startsWith('\uFEFF')) {
      result[0] = result.first.replaceAll('\uFEFF', '');
    }
    return result;
  }
}

final lightguardSourceProvider =
    Provider<LocalAssetSource>((_) => LocalAssetSource());
final selectedRegionProvider = StateProvider<RegionId>((_) => RegionId.suyeong);
final lightguardRepositoryProvider = Provider<LightguardRepository>(
  (ref) => LightguardRepository(ref.watch(lightguardSourceProvider)),
);

final lightguardDataProvider =
    FutureProvider.autoDispose<LightguardData>((ref) async {
  final repo = ref.watch(lightguardRepositoryProvider);
  final region = ref.watch(selectedRegionProvider);
  return repo.loadData(region);
});

final competitionAmiEventsProvider =
    FutureProvider.autoDispose<List<ValidationEvent>>((ref) async {
  final repo = ref.watch(lightguardRepositoryProvider);
  return repo.loadCompetitionAmiEvents();
});

final officialContextProvider =
    FutureProvider.autoDispose<OfficialContextBundle>((ref) async {
  return ref.watch(lightguardRepositoryProvider).loadOfficialContext();
});

final controlledMetricsProvider =
    FutureProvider.autoDispose<List<ControlledMetric>>((ref) async {
  return ref.watch(lightguardRepositoryProvider).loadControlledMetrics();
});

final v04ValidationSummaryProvider =
    FutureProvider.autoDispose<V04ValidationSummary>((ref) async {
  return ref.watch(lightguardRepositoryProvider).loadV04ValidationSummary();
});

final amiReplayWindowsProvider =
    FutureProvider.autoDispose<Map<String, List<AmiReplaySample>>>((ref) async {
  return ref.watch(lightguardRepositoryProvider).loadAmiReplayWindows();
});
