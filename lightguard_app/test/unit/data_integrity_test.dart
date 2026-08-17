import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/data/models/lightguard_models.dart';

void main() {
  test('model parser should preserve required chain fields', () {
    final Map<String, dynamic> data = {
      'cabinet_uid': 'X-1',
      'asset_info': <String, dynamic>{
        'cabinet_uid': 'X-1',
        'cabinet_name': 't',
        'latitude': 35.1,
        'longitude': 129.1,
        'fixture_count': 1,
        'lamp_count': 1,
        'fixtures': <Map<String, dynamic>>[],
      },
      'expected_schedule': <String, dynamic>{
        'date': '2026-01-01',
        'sunrise': '07:00',
        'sunset': '17:00',
        'civil_twilight_start': '06:30',
        'civil_twilight_end': '18:30',
        'expected_on_window': <String, dynamic>{},
      },
      'expected_load': <String, dynamic>{'rated_power_w': 3000, 'expected_rated_load_kW': 3.0, 'lamp_count': 1, 'fixture_rows': 1},
      'weather_context': <String, dynamic>{
        'station_name':'s',
        'station_type':'t',
        'forecast_hourly': <Map<String, dynamic>>[],
        'observation_at':'2026-01-01T00:00:00Z',
      },
      'ami': <String, dynamic>{'has_real_ami': false, 'ami_state':'unlinked', 'virtual_link_mode':'scenario_injection', 'ami_meter_id': null},
      'detected_signals': <Map<String, dynamic>>[],
      'anomaly_evidence': <String, dynamic>{
        'rule_ids': <String>[],
        'payload': <String, dynamic>{},
      },
      'inspection_priority': <String, dynamic>{'score': 0, 'severity':'low', 'rank':1, 'reason':'test'},
    };

    final record = CabinetRecord.fromJson(data);
    expect(record.evidenceSource, EvidenceSource.scenarioInjection);
    expect(record.status, InspectionStatus.normal);
    expect(record.modeLabel, '검증 시나리오');
  });
}
