import 'inspection_outcome_storage_stub.dart'
    if (dart.library.html) 'inspection_outcome_storage_web.dart' as implementation;

Map<String, Map<String, String>> loadInspectionOutcomes() =>
    implementation.loadInspectionOutcomes();

void saveInspectionOutcomes(Map<String, Map<String, String>> outcomes) =>
    implementation.saveInspectionOutcomes(outcomes);
