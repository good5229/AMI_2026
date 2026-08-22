// ignore_for_file: avoid_web_libraries_in_flutter, deprecated_member_use

import 'dart:convert';
import 'dart:html';

const _storageKey = 'lightguard.inspection_outcomes.v1';

Map<String, Map<String, String>> loadInspectionOutcomes() {
  final raw = window.localStorage[_storageKey];
  if (raw == null || raw.isEmpty) return {};
  try {
    final decoded = jsonDecode(raw) as Map<String, dynamic>;
    return decoded.map(
      (key, value) => MapEntry(
        key,
        Map<String, String>.from(value as Map<String, dynamic>),
      ),
    );
  } catch (_) {
    return {};
  }
}

void saveInspectionOutcomes(Map<String, Map<String, String>> outcomes) {
  window.localStorage[_storageKey] = jsonEncode(outcomes);
}
