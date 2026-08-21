import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('v0.11 app summary preserves Route C and claim boundaries', () {
    final data = jsonDecode(
      File('assets/data/context/v11_proxy_detector_summary.json')
          .readAsStringSync(),
    ) as Map<String, dynamic>;

    expect(data['route'], 'C');
    expect(data['files_audited'], 149);
    expect(data['gold_usable'], 0);
    expect(data['silver_usable'], 0);
    expect(data['score_rows'], 29181);
    expect(data['canonical_rows_joined_after_score_seal'], 6);
    expect(data['matched_controls'], 6);
    expect(data['review_labels_collected'], isFalse);
    expect(data['claim_guard'], contains('Proxy anomaly signs only'));
  });
}
