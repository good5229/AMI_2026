Map<String, Map<String, String>> _memory = {};

Map<String, Map<String, String>> loadInspectionOutcomes() =>
    _memory.map((key, value) => MapEntry(key, Map<String, String>.from(value)));

void saveInspectionOutcomes(Map<String, Map<String, String>> outcomes) {
  _memory = outcomes.map(
    (key, value) => MapEntry(key, Map<String, String>.from(value)),
  );
}
