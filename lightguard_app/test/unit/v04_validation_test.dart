import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/data/models/context_models.dart';

void main() {
  test('v0.4 summary preserves frozen baseline and controlled labels', () {
    final raw = File('assets/data/context/v04_validation_summary.json')
        .readAsStringSync();
    final json = jsonDecode(raw) as Map<String, dynamic>;
    final summary = V04ValidationSummary.fromJson(raw);
    expect(json['v03_frozen_set_sha256'],
        '935bc5ea7d70e878f15113dc08d11dfee7ebcbb350d90d421f46a7704cf27368');
    expect(json['controlled_validation'], true);
    expect(json['cost_conversion'], 'prohibited');
    expect(summary.baselineCandidateCount,
        greaterThan(summary.bestCandidateCount));
    expect(summary.bestCandidateCount, greaterThan(0));
    expect(summary.weatherLabel,
        anyOf('기상 Context 반영', '기상 Context 참고정보'));
  });

  test('calibration and confirmatory holdout metadata are separated', () {
    final calibration = jsonDecode(File(
            '../lightguard_v0_1/data/validation/v04_calibration_set.json')
        .readAsStringSync()) as Map<String, dynamic>;
    final holdout = jsonDecode(File(
            '../lightguard_v0_1/data/validation/v04_confirmatory_holdout.json')
        .readAsStringSync()) as Map<String, dynamic>;
    expect(calibration['deterministic_seed'], isNot(holdout['deterministic_seed']));
    expect(calibration['set_sha256'], isNot(holdout['set_sha256']));
    expect(calibration['case_count'], inInclusiveRange(120, 240));
    expect(holdout['case_count'], 204);
  });
}
