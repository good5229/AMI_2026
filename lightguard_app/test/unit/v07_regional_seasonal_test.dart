import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('v0.7 summary preserves regional-seasonal claim boundaries', () {
    final payload = jsonDecode(
      File('assets/data/context/v07_regional_seasonal_summary.json')
          .readAsStringSync(),
    ) as Map<String, dynamic>;

    expect(payload['region_count'], 3);
    expect(payload['season_count'], 4);
    expect(payload['cell_count'], 12);
    expect(payload['scenario_count'], 96);
    expect(payload['validation_kind'], 'controlled_cross_context_invariance');
    expect(
      (payload['external_ami_validation'] as Map<String, dynamic>)['status'],
      'unavailable',
    );

    final config = payload['frozen_detector_config'] as Map<String, dynamic>;
    expect(config['threshold'], 0.55);
    expect(config['weather_weight'], 0.0);

    final assets = payload['regional_assets'] as Map<String, dynamic>;
    final chungju = assets['chungju'] as Map<String, dynamic>;
    expect(chungju['asset_count'], 871);
    expect(chungju['rated_load_coverage'], 0.0);
    expect(chungju['rated_load_status'], 'unavailable_no_imputation');
  });
}
