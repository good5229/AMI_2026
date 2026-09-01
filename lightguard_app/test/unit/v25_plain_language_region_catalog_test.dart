import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/generated/v24_census_summary.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('전국 지역 목록 자산은 검수된 최신 지역을 포함한다', () async {
    final text = await rootBundle.loadString(
      'assets/data/context/v24_nationwide_file_census.json',
    );
    final root = jsonDecode(text) as Map<String, dynamic>;
    final datasets = root['datasets'] as List<dynamic>;
    final regionLabels = root['analyzable_region_labels'] as List<dynamic>;
    final representedTopLevels =
        root['represented_top_level_regions'] as List<dynamic>;
    final municipal = datasets.where((raw) {
      final row = raw as Map<String, dynamic>;
      return row['municipal_scope'] == true &&
          row['acquisition_status'] == 'DOWNLOADED_ANALYZABLE';
    }).toList(growable: false);

    expect(root['analyzable_region_count'], regionLabels.length);
    expect(V24CensusSummary.analyzableRegionCount, regionLabels.length);
    expect(
      representedTopLevels.length,
      lessThanOrEqualTo(root['current_top_level_region_count'] as int),
    );
    expect(
      V24CensusSummary.representedTopLevelCount,
      representedTopLevels.length,
    );
    expect(
      V24CensusSummary.currentTopLevelCount,
      root['current_top_level_region_count'],
    );
    expect(root['municipal_analyzable_datasets'], municipal.length);
    expect(V24CensusSummary.municipalDatasetCount, municipal.length);
    expect(regionLabels, isNotEmpty);
    expect(municipal, isNotEmpty);
    expect(text, isNot(contains('content_url')));
    expect(text, isNot(contains('external_url')));
  });
}
