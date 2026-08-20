import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('v0.10 summary preserves semi-synthetic and field-truth boundary', () {
    final data = jsonDecode(File(
      'assets/data/context/v10_real_background_summary.json',
    ).readAsStringSync()) as Map<String, dynamic>;
    expect(data['meters'], 5);
    expect(data['background_pool_units'], 200);
    expect(data['transport_gate'], 'PASS');
    expect(data['r1_triggered'], isFalse);
    expect(data['actual_ami_is_truth'], isFalse);
    expect(data['unmodified_background_is_normal_truth'], isFalse);
    expect(data['field_fault_accuracy'], isFalse);
    expect(data['context_policy'], 'no municipal/KMA/KASI/rated-load join');
  });
}

