import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/data/models/lightguard_models.dart';

void main() {
  test('priority severity maps to inspection status', () {
    final record = CabinetRecord(
      cabinetUid: 'x',
      assetInfo: AssetInfo(
        cabinetUid: 'x', cabinetName: 'x', latitude: 0, longitude: 0,
        fixtureCount: 1, lampCount: 1, controllerType: '', linkStatus: '', address: '', fixtures: <FixtureInfo>[],
      ),
      expectedSchedule: ExpectedSchedule(
        date: '2026-01-01',
        sunrise: '07:00',
        sunset: '18:00',
        civilTwilightStart: '06:30',
        civilTwilightEnd: '18:30',
        expectedOnWindow: {},
      ),
      expectedLoad: ExpectedLoad(ratedPowerW: 100, expectedRatedLoadKw: 0.1, lampCount: 1, fixtureRows: 1),
      weatherContext: WeatherContext(
        stationName: 's',
        stationType: 't',
        distanceKmToStation: 1,
        forecastHourly: <Map<String, dynamic>>[],
        observationAt: '',
      ),
      ami: AmiPayload(hasRealAmi: false, amiState: 'unlinked', virtualLinkMode: 'none', amiMeterId: null),
      detectedSignals: <DetectedSignal>[],
      anomalyEvidence: AnomalyEvidence(ruleIds: <String>[], payload: {}),
      inspectionPriority: InspectionPriority(score: 2, severity: 'critical', rank: 1, reason: 'x'),
    );

    expect(record.status, InspectionStatus.priorityInspection);
  });
}
