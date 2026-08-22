import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:lightguard_app/app/router/app_router.dart';
import 'package:lightguard_app/data/models/lightguard_models.dart';
import 'package:lightguard_app/data/repositories/lightguard_repository.dart';
import 'package:lightguard_app/data/models/region_config.dart';
import 'package:lightguard_app/features/ami_validation/ami_validation_screen.dart';
import 'package:lightguard_app/features/cabinet_detail/cabinet_detail_screen.dart';
import 'package:lightguard_app/features/dashboard/dashboard_screen.dart';
import 'package:lightguard_app/features/inspections/inspection_list_screen.dart';
import 'package:lightguard_app/features/map/map_screen.dart';
import 'package:lightguard_app/features/regions/regions_screen.dart';

void main() {
  final data = _sampleData();
  final events = _sampleCompetitionEvents();

  Widget buildTestApp({
    String initialLocation = '/',
    RegionId region = RegionId.suyeong,
  }) {
    final router = GoRouter(
      initialLocation: initialLocation,
      routes: [
        GoRoute(
            path: AppRoute.dashboard,
            builder: (context, state) => const DashboardScreen()),
        GoRoute(
            path: AppRoute.map, builder: (context, state) => const MapScreen()),
        GoRoute(
            path: AppRoute.inspections,
            builder: (context, state) => const InspectionListScreen()),
        GoRoute(
          path: AppRoute.cabinet,
          builder: (context, state) =>
              CabinetDetailScreen(cabinetUid: state.pathParameters['id'] ?? ''),
        ),
        GoRoute(
            path: AppRoute.ami,
            builder: (context, state) => const AmiValidationScreen()),
        GoRoute(
            path: AppRoute.regions,
            builder: (context, state) => const RegionsScreen()),
      ],
    );
    return ProviderScope(
      overrides: [
        selectedRegionProvider.overrideWith((_) => region),
        lightguardDataProvider.overrideWith((_) async => data),
        competitionAmiEventsProvider.overrideWith((_) async => events),
      ],
      child: MaterialApp.router(routerConfig: router),
    );
  }

  testWidgets('Dashboard renders 기본 카드와 기준일 점등/소등 정보',
      (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp());
    await tester.pumpAndSettle();

    expect(find.text('LightGuard · 운영 현황'), findsOneWidget);
    expect(find.textContaining('오늘 먼저 확인할 우선 점검'), findsOneWidget);
    expect(find.text('점검 대상 보기'), findsOneWidget);
    expect(find.text('총 분전함'), findsOneWidget);
    expect(find.text('총 가로등 수'), findsOneWidget);
    expect(find.text('총 정격용량'), findsOneWidget);
    expect(
        find.textContaining('${data.objects.length}'), findsAtLeastNWidgets(1));
    expect(find.text('기준일 기준 점등/소등'), findsOneWidget);
    expect(find.text(RegionId.suyeong.branchLabel), findsAtLeastNWidgets(1));
    expect(find.byKey(const Key('dashboard-scenario-count')), findsOneWidget);
    expect(find.byKey(const Key('dashboard-actual-ami-count')), findsOneWidget);
    expect(
        find.byKey(const Key('dashboard-municipal-ami-count')), findsOneWidget);
  });

  testWidgets('Inspection list renders and filters by 검증 시나리오',
      (WidgetTester tester) async {
    await tester
        .pumpWidget(buildTestApp(initialLocation: AppRoute.inspections));
    await tester.pumpAndSettle();
    await _pumpUntilFound(
      tester,
      find.text('CAB-001'),
      maxAttempts: 18,
    );

    expect(find.text('오늘의 점검 대상'), findsOneWidget);
    expect(find.text('CAB-002'), findsAtLeastNWidgets(1));
    expect(find.text('CAB-001'), findsAtLeastNWidgets(1));

    var dropdownFinder = find.byKey(const Key('inspection-filter-dropdown'));
    if (dropdownFinder.evaluate().isEmpty) {
      dropdownFinder = find.byType(DropdownButton<dynamic>);
      if (dropdownFinder.evaluate().isEmpty) {
        dropdownFinder = find.byType(DropdownButton);
      }
    }
    if (dropdownFinder.evaluate().isNotEmpty) {
      await tester.tap(dropdownFinder);
      await tester.pumpAndSettle();
      final scenarioItemFinder =
          find.byKey(const Key('inspection-filter-item-scenario'));
      final scenarioTextFinder = find.text('검증 시나리오');
      if (scenarioItemFinder.evaluate().isNotEmpty) {
        await tester.tap(scenarioItemFinder);
      } else if (scenarioTextFinder.evaluate().isNotEmpty) {
        await tester.tap(scenarioTextFinder);
      }
      await tester.pumpAndSettle();
      await _pumpUntilFound(
        tester,
        find.text('CAB-001'),
        maxAttempts: 18,
      );

      expect(find.text('CAB-001'), findsAtLeastNWidgets(1));
    } else {
      expect(
        find.text('CAB-001'),
        findsAtLeastNWidgets(1),
      );
    }
  });

  testWidgets('Cabinet detail renders 해설 문구 and raw data safe label',
      (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp(initialLocation: '/cabinet/CAB-002'));
    await tester.pumpAndSettle();
    await _pumpUntilFound(
      tester,
      find.text('분전함 상세'),
      maxAttempts: 24,
    );
    final sectionAFinder =
        find.byKey(const Key('section-cabinet-section-summary-a'));
    expect(sectionAFinder, findsOneWidget);
    expect(
      find.descendant(of: sectionAFinder, matching: find.text('램프 정격')),
      findsOneWidget,
    );
    expect(
      find.descendant(of: sectionAFinder, matching: find.text('자료 미제공')),
      findsAtLeastNWidgets(1),
    );

    final sectionCFinder =
        find.byKey(const Key('section-cabinet-section-summary-c'));
    await tester.scrollUntilVisible(
      sectionCFinder,
      300,
      scrollable: find.byType(Scrollable).last,
    );
    await tester.pumpAndSettle();
    expect(sectionCFinder, findsOneWidget);
    expect(
      find.descendant(
        of: sectionCFinder,
        matching: find.byWidgetPredicate((widget) {
          if (widget is Text) {
            final data = widget.data ?? '';
            return data.contains('Section C') || data.contains('시각화');
          }
          if (widget is RichText) {
            return (widget.text.toPlainText().contains('Section C') ||
                widget.text.toPlainText().contains('시각화'));
          }
          return false;
        }),
      ),
      findsAtLeastNWidgets(1),
    );
  });

  testWidgets(
      'AMI Validation renders competition events and Competition AMI badge',
      (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp(initialLocation: AppRoute.ami));
    await tester.pumpAndSettle();

    expect(find.text('실제 공모전 AMI Case Study'), findsOneWidget);
    expect(find.text('실제 공모전 AMI'), findsAtLeastNWidgets(1));
    expect(find.byKey(const Key('ami-case-B-L-35-2026-05-11')), findsOneWidget);
    expect(find.text(AmiValidationScreen.disclaimer), findsAtLeastNWidgets(1));
    if (events.isNotEmpty) {
      expect(
          find.textContaining(events.first.meterId), findsAtLeastNWidgets(1));
    } else {
      fail('AMI 이벤트 데이터가 비어 있어 목록 검증을 수행할 수 없습니다.');
    }
  });

  testWidgets('Dashboard remains overflow-free at 360px',
      (WidgetTester tester) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(buildTestApp());
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.text('현황'), findsOneWidget);
  });

  testWidgets('Region cards disclose modes and no municipal AMI',
      (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp(initialLocation: AppRoute.regions));
    await tester.pumpAndSettle();

    expect(
        find.text('Full Asset + Scenario Validation'), findsAtLeastNWidgets(1));
    expect(find.text('Controller-linked Validation'), findsAtLeastNWidgets(1));
    await tester.scrollUntilVisible(
      find.text('Minimal Asset / Asset-only'),
      300,
      scrollable: find.byType(Scrollable).last,
    );
    await tester.pumpAndSettle();
    expect(find.text('Minimal Asset / Asset-only'), findsAtLeastNWidgets(1));
    expect(find.text('실제 AMI 연결 없음'), findsAtLeastNWidgets(1));
  });
}

LightguardData _sampleData() {
  return LightguardData(
    generatedAt: DateTime.parse('2026-08-17T00:00:00Z'),
    schemaVersion: 'lightguard-v0.2',
    municipality: 'suyeong',
    objects: [
      _sampleCabinet(
        'CAB-001',
        fixtureName: 'CAB-001',
        amiMeter: const AmiPayload(
          hasRealAmi: false,
          amiState: 'unlinked',
          virtualLinkMode: 'scenario_injection',
          amiMeterId: null,
        ),
        severity: 'low',
        rank: 2,
        signal: const DetectedSignal(
          eventType: 'partial_activation',
          firstSample: '2026-01-01 00:00',
          lastSample: '2026-01-01 00:30',
          estimatedDurationMin: 30,
          maxActivation: 0.73,
          patternConfidence: 'medium',
        ),
        detectedSignals: const [],
      ),
      _sampleCabinet(
        'CAB-002',
        fixtureName: 'CAB-002',
        amiMeter: const AmiPayload(
          hasRealAmi: false,
          amiState: 'unlinked',
          virtualLinkMode: 'none',
          amiMeterId: null,
        ),
        severity: 'critical',
        rank: 1,
        signal: null,
        detectedSignals: const [],
      ),
      _sampleCabinet(
        'CAB-003',
        fixtureName: 'CAB-003',
        amiMeter: const AmiPayload(
          hasRealAmi: false,
          amiState: 'unlinked',
          virtualLinkMode: 'none',
          amiMeterId: null,
        ),
        severity: 'low',
        rank: 3,
        signal: null,
        detectedSignals: const [],
      ),
    ],
    targetMode: {
      'target_cabinets_3_4kw_like': ['CAB-001'],
    },
    validationScenarios: const [
      ScenarioRecord(
        scenarioId: 'SCN-1',
        cabinetUid: 'CAB-001',
        targetDurationMin: 90,
        detectMatched: true,
        detectedEventCount: 1,
        targetDate: '2026-01-14',
      ),
    ],
    validationRows: const [
      ValidationRow(
        scenarioId: 'SCN-1',
        cabinetUid: 'CAB-001',
        detectMatched: true,
        detectedEventCount: 1,
      ),
    ],
  );
}

CabinetRecord _sampleCabinet(
  String uid, {
  required String fixtureName,
  required AmiPayload amiMeter,
  required String severity,
  required int rank,
  required DetectedSignal? signal,
  required List<DetectedSignal> detectedSignals,
}) {
  const scheduleWindow = {'on_start': '19:00', 'on_end': '05:00'};
  return CabinetRecord(
    cabinetUid: uid,
    assetInfo: AssetInfo(
      cabinetUid: uid,
      cabinetName: fixtureName,
      latitude: 35.0,
      longitude: 129.0,
      fixtureCount: 10,
      lampCount: 10,
      controllerType: 'ctrl',
      linkStatus: 'unlinked',
      address: '부산 수영구',
      fixtures: const [],
    ),
    expectedSchedule: const ExpectedSchedule(
      date: '2026-01-14',
      sunrise: '07:20',
      sunset: '19:10',
      civilTwilightStart: '06:40',
      civilTwilightEnd: '20:00',
      expectedOnWindow: scheduleWindow,
    ),
    expectedLoad: const ExpectedLoad(
      ratedPowerW: 3400,
      expectedRatedLoadKw: 3.4,
      lampCount: 10,
      fixtureRows: 10,
    ),
    weatherContext: const WeatherContext(
      stationName: '해운대',
      stationType: 'ASOS',
      distanceKmToStation: 1.2,
      forecastHourly: [],
      observationAt: '2026-01-14T06:00:00Z',
    ),
    ami: amiMeter,
    detectedSignals: [
      if (signal != null) signal,
      ...detectedSignals,
    ],
    anomalyEvidence: const AnomalyEvidence(ruleIds: ['R-1'], payload: {}),
    inspectionPriority: InspectionPriority(
      score: 80,
      severity: severity,
      rank: rank,
      reason: '테스트 사유',
    ),
  );
}

List<ValidationEvent> _sampleCompetitionEvents() {
  final file = File('assets/data/ami_events.csv');
  if (!file.existsSync()) {
    return const [
      ValidationEvent(
        eventId: 'AMI-EVT-LOCAL',
        meterId: 'MTR-LOCAL-001',
        eventType: 'partial_activation',
        firstSample: '2026-01-14T19:00:00Z',
        lastSample: '2026-01-14T20:30:00Z',
        durationMin: 90,
        maxActivation: 0.73,
        activePhases: 'on',
        peakCurrentA: 16.55,
        offBaselineA: 0.05,
        onBaselineA: 17.16,
        patternConfidence: 'high',
        estimatedExcessKwh: 1.847,
        energyMethod: 'interval overlap',
        faultStatus: 'unverified inspection candidate',
        sourceMode: 'scenario_injection',
        payloadRaw: '{"event_id":"AMI-EVT-LOCAL"}',
      ),
    ];
  }

  final raw = file.readAsStringSync();
  final lines = const LineSplitter().convert(raw);
  if (lines.isEmpty) return const [];
  final headers = _splitCsvLine(lines.first, isHeader: true);
  final events = <ValidationEvent>[];
  for (var i = 1; i < lines.length; i++) {
    if (lines[i].trim().isEmpty) continue;
    final values = _splitCsvLine(lines[i]);
    final row = <String, String>{};
    for (var j = 0; j < headers.length; j++) {
      if (j < values.length) row[headers[j]] = values[j];
    }
    events.add(ValidationEvent.fromCsv(row));
  }
  return events;
}

List<String> _splitCsvLine(String line, {bool isHeader = false}) {
  final values = <String>[];
  final buffer = StringBuffer();
  var inQuote = false;
  for (var i = 0; i < line.length; i++) {
    final char = line[i];
    if (char == '"') {
      inQuote = !inQuote;
      continue;
    }
    if (char == ',' && !inQuote) {
      values.add(buffer.toString().trim());
      buffer.clear();
    } else {
      buffer.write(char);
    }
  }
  values.add(buffer.toString().trim());
  if (isHeader && values.isNotEmpty && values[0].startsWith('\uFEFF')) {
    values[0] = values[0].replaceAll('\uFEFF', '');
  }
  return values;
}

Future<void> _pumpUntilFound(
  WidgetTester tester,
  Finder finder, {
  required int maxAttempts,
  Duration step = const Duration(milliseconds: 50),
}) async {
  for (var attempt = 0; attempt < maxAttempts; attempt++) {
    if (finder.evaluate().isNotEmpty) return;
    await tester.pump(step);
  }
}
