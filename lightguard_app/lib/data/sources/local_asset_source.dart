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
}
