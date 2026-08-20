import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('v0.9 app evidence preserves controlled promotion boundary', () {
    final data = jsonDecode(
      File('assets/data/context/v09_specificity_summary.json').readAsStringSync(),
    ) as Map<String, dynamic>;
    final metrics = data['metrics'] as Map<String, dynamic>;

    expect(data['validation_kind'], 'episode_separated_controlled_confirmatory_holdout');
    expect(data['confirmatory_episodes'], 24);
    expect(data['confirmatory_cases'], 576);
    expect(data['episode_overlap'], 0);
    expect(data['date_overlap'], 0);
    expect(data['kma_observation_overlap'], 0);
    expect(data['weather_weight'], 0.0);
    expect(data['load_imputation'], 'none');
    expect(data['actual_ami_is_truth'], isFalse);
    expect(metrics['recall'], greaterThanOrEqualTo(0.70));
    expect(metrics['fpr'], lessThanOrEqualTo(0.05));
    expect(metrics['hard_negative_fpr'], lessThanOrEqualTo(0.05));
    expect(metrics['worst_cell_recall'], greaterThanOrEqualTo(0.55));
    expect(metrics['recall_wilson_95'], hasLength(2));
    expect(metrics['fpr_wilson_95'], hasLength(2));
    expect(metrics['hard_negative_fpr_wilson_95'], hasLength(2));
  });
}
