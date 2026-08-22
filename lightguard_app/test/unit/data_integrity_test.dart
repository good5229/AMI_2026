import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/data/models/lightguard_models.dart';
import 'package:lightguard_app/data/models/region_config.dart';

void main() {
  final sample = _lightguardData();

  test('data integrity for bundled suyeong sample', () {
    expect(sample.municipality, 'suyeong');
    expect(sample.objects.length, 204);
    expect(
        sample.objects
            .where((cabinet) => cabinet.assetInfo.latitude != null)
            .length,
        204);
    expect(sample.validationScenarios.length, 46);
    expect(sample.validationRows.where((row) => row.detectMatched).length, 46);

    expect(sample.objects.every((cabinet) => !cabinet.ami.hasRealAmi), true);
    expect(
      sample.objects.any((cabinet) =>
          cabinet.evidenceSource == EvidenceSource.scenarioInjection),
      true,
    );
    expect(
      sample.objects.every((cabinet) =>
          cabinet.evidenceSource != EvidenceSource.realMunicipalAsset),
      true,
    );
    expect(
      sample.validationRows.every((row) => row.detectedEventCount >= 0),
      true,
    );

    final targets = sample.targetMode['target_cabinet_ids'];
    final targetList = targets is List
        ? targets
        : sample.targetMode['target_cabinets_3_4kw_like'];
    expect(targetList is List, true);
    expect((targetList! as List).length, 46);
  });

  test('all region capabilities preserve zero real municipal AMI mappings', () {
    final gangneung = _lightguardDataFrom('gangneung_v02_seed.json');
    final chungju = _lightguardDataFrom('chungju_v02_seed.json');

    expect(gangneung.objects.length, 339);
    expect(chungju.objects.length, 871);
    expect(
      <LightguardData>[sample, gangneung, chungju].every((regionData) =>
          regionData.objects.every((cabinet) => !cabinet.ami.hasRealAmi)),
      true,
    );
    expect(RegionId.suyeong.supportsRealMunicipalAmi, false);
    expect(RegionId.gangneung.supportsRealMunicipalAmi, false);
    expect(RegionId.chungju.supportsRealMunicipalAmi, false);
    expect(RegionId.gangneung.supportsControllerData, true);
    expect(RegionId.gangneung.modeDescription, '시설정보와 제어기 연결정보 제공');
    expect(RegionId.chungju.modeDescription, '기본 시설정보 제공');
  });

  test('competition AMI event count and source', () {
    final raw = File('assets/data/ami_events.csv').readAsStringSync();
    final rows = raw.split('\n');
    final header = _splitCsvLine(rows.first, isHeader: true);
    expect(header.contains('source_mode'), true);

    final events = <Map<String, String>>[];
    for (var i = 1; i < rows.length; i++) {
      final line = rows[i].trim();
      if (line.isEmpty) continue;
      final values = _splitCsvLine(line);
      final row = <String, String>{};
      for (var j = 0; j < header.length && j < values.length; j++) {
        row[header[j]] = values[j];
      }
      events.add(row);
    }

    expect(events.length, 6);
    expect(
        events.every((row) => row['source_mode']?.isNotEmpty ?? false), true);
    expect(events.first['event_id'], isNotEmpty);
    expect(
        events.every(
            (row) => row['fault_status'] == 'unverified inspection candidate'),
        true);
    final totalExcess = events.fold<double>(
      0,
      (sum, row) =>
          sum + (double.tryParse(row['estimated_excess_kwh'] ?? '') ?? 0),
    );
    expect(totalExcess, closeTo(3.994, 0.0001));
    expect(
      events.any((row) =>
          row['meter_id'] == 'B-L-35' &&
          row['first_sample']?.startsWith('2026-05-11') == true),
      true,
    );
    expect(
      events.any((row) =>
          row['meter_id'] == 'B-L-9' &&
          row['first_sample']?.startsWith('2026-05-20') == true),
      true,
    );
    expect(
      events.any((row) =>
          row['meter_id'] == 'B-L-14' &&
          row['first_sample']?.startsWith('2026-05-29') == true),
      true,
    );
  });
}

LightguardData _lightguardData() {
  return _lightguardDataFrom('suyeong_v02_seed.json');
}

LightguardData _lightguardDataFrom(String seedName) {
  final seed = File('assets/data/$seedName').readAsStringSync();
  final scenarios =
      File('assets/data/simulation_scenarios_v02.json').readAsStringSync();
  final validation = File('assets/data/simulation_validation_results_v02.csv')
      .readAsStringSync();
  return LightguardData.fromSeedJson(seed, scenarios, validation);
}

List<String> _splitCsvLine(String line, {bool isHeader = false}) {
  final values = <String>[];
  final buffer = StringBuffer();
  var inQuotes = false;
  for (var i = 0; i < line.length; i++) {
    final c = line[i];
    if (c == '"') {
      inQuotes = !inQuotes;
      continue;
    }
    if (c == ',' && !inQuotes) {
      values.add(buffer.toString().trim());
      buffer.clear();
      continue;
    }
    buffer.write(c);
  }
  values.add(buffer.toString().trim());

  if (isHeader && values.isNotEmpty && values[0].startsWith('\uFEFF')) {
    values[0] = values[0].replaceAll('\uFEFF', '');
  }
  return values;
}
