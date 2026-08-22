import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('전국 지역 목록 자산은 검수된 83개 지역을 포함한다', () async {
    final text = await rootBundle.loadString(
      'assets/data/context/v24_nationwide_file_census.json',
    );
    final root = jsonDecode(text) as Map<String, dynamic>;
    final datasets = root['datasets'] as List<dynamic>;
    final municipal = datasets.where((raw) {
      final row = raw as Map<String, dynamic>;
      return row['municipal_scope'] == true &&
          row['acquisition_status'] == 'DOWNLOADED_ANALYZABLE';
    }).toList(growable: false);

    expect(root['analyzable_region_count'], 83);
    expect(root['current_top_level_region_count'], 16);
    expect(root['municipal_analyzable_datasets'], 125);
    expect(municipal, hasLength(125));
    expect(text, isNot(contains('content_url')));
    expect(text, isNot(contains('external_url')));
  });
}
