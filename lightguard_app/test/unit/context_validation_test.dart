import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/data/models/lightguard_models.dart';

void main() {
  test('source semantics are fixed at 204 municipal / 46 scenario / 158 none', () {
    final seed = File('assets/data/suyeong_v02_seed.json').readAsStringSync();
    final scenarios =
        File('assets/data/simulation_scenarios_v02.json').readAsStringSync();
    final validation =
        File('assets/data/simulation_validation_results_v02.csv').readAsStringSync();
    final data = LightguardData.fromSeedJson(seed, scenarios, validation);
    expect(data.objects.length, 204);
    expect(data.objects.every((row) => row.assetSource == AssetSource.municipalPublicData), true);
    expect(data.objects.where((row) => row.signalSource == SignalSource.scenarioInjection).length, 46);
    expect(data.objects.where((row) => row.signalSource == SignalSource.none).length, 158);
    expect(data.objects.where((row) => row.signalSource == SignalSource.realMunicipalAmi), isEmpty);
  });

  test('KASI snapshot has four requested dates or explicit unavailable errors', () {
    final payload = jsonDecode(File('assets/data/context/kasi_solar_context_2026.json').readAsStringSync()) as Map<String, dynamic>;
    final dates = payload['dates'] as List<dynamic>;
    expect(dates.map((row) => row['date']).toSet(), {
      '2026-01-14', '2026-04-15', '2026-07-15', '2026-10-15'
    });
    if (payload['context_source'] == 'official') {
      expect(dates.every((row) => row['sunrise'] != null && row['sunset'] != null && row['civil_twilight_start'] != null && row['civil_twilight_end'] != null), true);
    } else {
      expect(payload['errors'], isNotEmpty);
      expect(dates.every((row) => row['source'] == 'unavailable'), true);
    }
  });

  test('KMA station 159 preserves observations or explicit missing state', () {
    final payload = jsonDecode(File('assets/data/context/kma_asos_busan_2026.json').readAsStringSync()) as Map<String, dynamic>;
    expect(payload['station_id'], '159');
    expect((payload['requested_dates'] as List<dynamic>).length, 4);
    final observations = (payload['observations'] as List<dynamic>)
        .whereType<Map<String, dynamic>>()
        .toList(growable: false);
    if (observations.isNotEmpty) {
      expect(
          observations.every((row) =>
              DateTime.tryParse(row['timestamp']?.toString() ?? '') != null),
          true);
      expect(observations.every((row) => row.containsKey('cloud_amount')), true);
    } else {
      expect(payload['context_source'], 'unavailable');
      expect(payload['errors'], isNotEmpty);
    }
  });

  test('ablation uses one frozen set and never invents unavailable metrics', () {
    final rows = File('assets/data/context/context_ablation_results.csv')
        .readAsLinesSync()
        .where((line) => line.trim().isNotEmpty)
        .toList();
    expect(rows.length, 5);
    final values = rows.skip(1).map((line) => line.split(',')).toList();
    expect(values.map((row) => row[0]).toList(), ['M0', 'M1', 'M2', 'M3']);
    expect(values.map((row) => row.last).toSet().length, 1);
    expect(values.first[1], 'available');
    for (final row in values.skip(1).where((row) => row[1] != 'available')) {
      expect(row[2], isEmpty);
      expect(row[3], isEmpty);
    }
  });

  test('six replay windows contain only traceable meter/date source rows', () {
    const expected = <String, String>{
      'B-L-35_2026-05-11.csv': 'B-L-35',
      'B-L-14_2026-05-19.csv': 'B-L-14',
      'B-L-9_2026-05-20.csv': 'B-L-9',
      'B-L-9_2026-05-21.csv': 'B-L-9',
      'B-L-14_2026-05-29.csv': 'B-L-14',
      'B-L-13_2026-06-23.csv': 'B-L-13',
    };
    for (final entry in expected.entries) {
      final lines = File('assets/data/ami_event_windows/${entry.key}').readAsLinesSync();
      expect(lines.first, contains('source_row'));
      expect(lines.length, greaterThan(1));
      final date = entry.key.substring(entry.key.length - 14, entry.key.length - 4);
      for (final line in lines.skip(1)) {
        final cells = line.split(',');
        expect(cells[0].startsWith(date), true);
        expect(cells[1], entry.value);
        expect(int.tryParse(cells.last), greaterThan(2));
      }
    }
  });
}
