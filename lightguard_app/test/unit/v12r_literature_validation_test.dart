import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('v0.12R literature summary preserves evidence and review boundaries', () {
    final data = jsonDecode(
      File('assets/data/context/v12r_literature_summary.json')
          .readAsStringSync(),
    ) as Map<String, dynamic>;

    expect(data['status'], 'PHASE_A_LITERATURE_COMPLETE');
    expect(data['review_status'], 'HUMAN_REVIEW_PENDING');
    expect(data['sources'], 21);
    expect(data['quality_a'], 19);
    expect(data['proxy_high_mapped'], 765);
    expect(data['gold_usable'], 0);
    expect(data['silver_usable'], 0);
    expect(data['maximum_current_claim_level'], 3);
    expect(data['fault_probability_available'], isFalse);
  });
}
