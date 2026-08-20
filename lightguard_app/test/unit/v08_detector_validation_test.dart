import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('v0.8 failed candidate gate and claim boundary remain visible', () {
    final data = jsonDecode(
      File('assets/data/context/v08_detector_summary.json').readAsStringSync(),
    ) as Map<String, dynamic>;
    expect(data['confirmatory_cases'], 432);
    expect(data['selected_candidate'], isNull);
    expect(data['candidate_gate'], 'failed_fpr_limit');
    expect(data['weather_policy'], 'context_only');
    expect(data['actual_external_regional_ami'], 'unavailable');
    final c1 = data['experimental_c1'] as Map<String, dynamic>;
    expect(c1['recall'], greaterThan((data['baseline'] as Map<String, dynamic>)['recall'] as num));
    expect(c1['fpr'], greaterThan(0.05));
    final chungju = data['chungju'] as Map<String, dynamic>;
    expect(chungju['rated_load'], 'unavailable');
    expect(chungju['imputation'], 'none');
  });
}
