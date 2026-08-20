import 'package:flutter/services.dart' show rootBundle;
import '../models/region_config.dart';

class LocalAssetSource {
  Future<String> readSeedByRegion(RegionId region) {
    return rootBundle.loadString(region.seedAsset);
  }

  Future<String> readScenarios() {
    return rootBundle.loadString('assets/data/simulation_scenarios_v02.json');
  }

  Future<String> readValidationRows() {
    return rootBundle.loadString('assets/data/simulation_validation_results_v02.csv');
  }

  Future<String> readAmiEvents() {
    return rootBundle.loadString('assets/data/ami_events.csv');
  }

  Future<String> readKasiContext() {
    return rootBundle.loadString('assets/data/context/kasi_solar_context_2026.json');
  }

  Future<String> readKmaContext() {
    return rootBundle.loadString('assets/data/context/kma_asos_busan_2026.json');
  }

  Future<String> readAblationResults() {
    return rootBundle.loadString('assets/data/context/context_ablation_results.csv');
  }

  Future<String> readV04ValidationSummary() {
    return rootBundle.loadString('assets/data/context/v04_validation_summary.json');
  }

  Future<String> readReplayWindow(String filename) {
    return rootBundle.loadString('assets/data/ami_event_windows/$filename');
  }
}
