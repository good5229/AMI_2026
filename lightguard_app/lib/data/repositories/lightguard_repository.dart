import "dart:convert";
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/lightguard_models.dart';
import '../sources/local_asset_source.dart';

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
      sourceMode: row['source_mode'] ?? '',
      payloadRaw: row.toString(),
    );
  }

  String get badge => '실제 AMI';
}

class LightguardRepository {
  LightguardRepository(this._assetSource);

  final LocalAssetSource _assetSource;

  Future<LightguardData> loadData() async {
    final seed = await _assetSource.readSeed();
    final scenarios = await _assetSource.readScenarios();
    final validation = await _assetSource.readValidationRows();
    return LightguardData.fromSeedJson(seed, scenarios, validation);
  }

  Future<List<ValidationEvent>> loadCompetitionAmiEvents() async {
    final csv = await _assetSource.readAmiEvents();
    final rows = const LineSplitter().convert(csv);
    if (rows.isEmpty) return const <ValidationEvent>[];
    final headers = _splitCsv(rows.first);
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

  static List<String> _splitCsv(String line) {
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
    return result;
  }
}

final lightguardSourceProvider = Provider<LocalAssetSource>((_) => LocalAssetSource());
final lightguardRepositoryProvider = Provider<LightguardRepository>(
  (ref) => LightguardRepository(ref.watch(lightguardSourceProvider)),
);

final lightguardDataProvider = FutureProvider.autoDispose<LightguardData>((ref) async {
  final repo = ref.watch(lightguardRepositoryProvider);
  return repo.loadData();
});

final competitionAmiEventsProvider = FutureProvider.autoDispose<List<ValidationEvent>>((ref) async {
  final repo = ref.watch(lightguardRepositoryProvider);
  return repo.loadCompetitionAmiEvents();
});
