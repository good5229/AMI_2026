import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/data/models/context_models.dart';

void main() {
  test('v0.5 product evidence preserves honest actual AMI claim scope', () {
    final raw = File('assets/data/context/v05_validation_summary.json')
        .readAsStringSync();
    final json = jsonDecode(raw) as Map<String, dynamic>;
    final summary = V05ValidationSummary.fromJson(raw);
    expect(json['validation_scope'], contains('no confirmed fault labels'));
    expect(summary.legacyPeakConsistent, 2);
    expect(summary.adjudicatedPeakConsistent, 6);
    expect(summary.pastOnlyCoverage, 1);
    expect(
        (json['operational_evidence']
            as Map<String, dynamic>)['cost_conversion_allowed'],
        false);
    expect(
        (json['sensitivity']
            as Map<String, dynamic>)['frozen_config_changed'],
        false);
  });
}
