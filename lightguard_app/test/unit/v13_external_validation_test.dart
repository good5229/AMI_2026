import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('v0.13 external validation asset preserves claim boundaries', () {
    final data = jsonDecode(
      File('assets/data/context/v13_external_validation_summary.json')
          .readAsStringSync(),
    ) as Map<String, dynamic>;
    final primary = data['primary_dataset'] as Map<String, dynamic>;
    final secondary = (data['secondary_datasets'] as List<dynamic>)
        .cast<Map<String, dynamic>>();

    expect(data['status'], 'CONFIRMATORY_RESULT_AVAILABLE');
    expect(data['external_validity_scope'],
        'signal-mechanism external validity');
    expect(data['streetlight_field_accuracy_available'], isFalse);
    expect(data['actual_fault_probability_available'], isFalse);
    expect(data['human_review_status'], 'PENDING');
    expect(data['field_confirmation'], 'NOT_AVAILABLE');
    expect(primary['dataset_id'], 'MAD');
    expect(primary['status'], 'NOT_EVALUABLE_INCOMPLETE_COVERAGE');
    expect(primary['track_b'], 'NOT_ASSESSABLE');
    expect(primary['lg_s3'], 'UNAVAILABLE_NORMALIZATION_PROVENANCE');
    expect(secondary, hasLength(2));
    expect(secondary[0]['status'], 'BLOCKED_EXTERNAL_DATA');
    expect(secondary[1]['status'], 'WITHHELD_LICENSE_UNKNOWN');
    expect(data['pseudo_label_policy']['external_gold_allowed'], isFalse);
    expect(data['external_ev_grade'], 'NO_EV_GRADE_NOT_EVALUABLE');
    expect(data['metrics']['config_frozen_before_labels'], isTrue);
    expect(data['metrics']['primary_gate'],
        'NOT_EVALUABLE_INCOMPLETE_COVERAGE');
  });
}
