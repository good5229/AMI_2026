import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/data/models/context_models.dart';

void main() {
  test('v0.6 evidence exposes uncertainty abstention and no field truth', () {
    final raw = File('assets/data/context/v06_evidence_summary.json')
        .readAsStringSync();
    final json = jsonDecode(raw) as Map<String, dynamic>;
    final summary = V06EvidenceSummary.fromJson(raw);

    expect(json['claim_scope'], contains('actual AMI remains unlabeled'));
    expect(summary.coveragePoint, 1.0);
    expect(summary.coverageLower, lessThan(0.62));
    expect(summary.coverageLower, greaterThan(0.60));
    expect(summary.gap120Upper, greaterThan(0.38));
    expect(summary.abstentionRuleCount, 5);
    expect(summary.fieldTruthAvailable, isFalse);
    expect(
        (json['interaction_diagnostic']
            as Map<String, dynamic>)['frozen_configuration_changed'],
        isFalse);
  });
}
