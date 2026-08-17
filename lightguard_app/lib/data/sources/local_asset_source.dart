import 'package:flutter/services.dart' show rootBundle;

class LocalAssetSource {
  Future<String> readSeed() {
    return rootBundle.loadString('assets/data/suyeong_v02_seed.json');
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
