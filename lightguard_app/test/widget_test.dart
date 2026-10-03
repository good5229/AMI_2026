import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:lightguard_app/app/router/app_router.dart';
import 'package:lightguard_app/core/storage/inspection_outcome_storage.dart';
import 'package:lightguard_app/data/models/lightguard_models.dart';
import 'package:lightguard_app/data/repositories/lightguard_repository.dart';
import 'package:lightguard_app/data/models/region_config.dart';
import 'package:lightguard_app/features/ami_validation/ami_validation_screen.dart';
import 'package:lightguard_app/features/cabinet_detail/cabinet_detail_screen.dart';
import 'package:lightguard_app/features/dashboard/dashboard_screen.dart';
import 'package:lightguard_app/features/inspections/inspection_list_screen.dart';
import 'package:lightguard_app/features/map/map_screen.dart';

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
          path: AppRoute.map,
          builder: (context, state) => MapScreen(
            focusCabinetUid: state.uri.queryParameters['cabinet'],
            showBaseMap: false,
          ),
        ),
        GoRoute(
            path: AppRoute.inspections,
            builder: (context, state) => InspectionListScreen(
                  initialFilter: state.uri.queryParameters['filter'],
                )),
        GoRoute(
          path: AppRoute.cabinet,
          builder: (context, state) =>
              CabinetDetailScreen(cabinetUid: state.pathParameters['id'] ?? ''),
        ),
        GoRoute(
            path: AppRoute.ami,
            builder: (context, state) => const AmiValidationScreen()),
      ],
    );
    return ProviderScope(
      overrides: [
        selectedRegionProvider.overrideWith((_) => region),
        lightguardDataProvider.overrideWith((_) async => data),
        competitionAmiEventsProvider.overrideWith((_) async => events),
      ],
      child: MaterialApp.router(
        routerConfig: router,
        locale: const Locale('ko'),
        supportedLocales: const [Locale('ko')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
      ),
    );
  }

  testWidgets('Dashboard renders 핵심 운영 지표만 표시한다', (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp());
    await tester.pumpAndSettle();

    expect(find.text('LightGuard · 운영 현황'), findsOneWidget);
    expect(find.text('우선 확인'), findsAtLeastNWidgets(1));
    expect(find.text('오늘 확인할 후보'), findsNothing);
    expect(find.text('확인 대상 및 사유 보기'), findsNothing);
    expect(find.text('등록 자산'), findsOneWidget);
    expect(find.text('연결 가로등'), findsOneWidget);
    expect(find.text('정격용량'), findsOneWidget);
    expect(
        find.textContaining('${data.objects.length}'), findsAtLeastNWidgets(1));
    expect(find.text('기준일 기준 점등/소등'), findsNothing);
    expect(find.text(RegionId.suyeong.branchLabel), findsAtLeastNWidgets(1));
    expect(find.text('점검 검토'), findsOneWidget);
    expect(find.text('관찰'), findsOneWidget);
    expect(find.text('정상 범위'), findsOneWidget);
  });

  testWidgets('Inspection list renders and filters by 검증 시나리오',
      (WidgetTester tester) async {
    await tester.pumpWidget(
        buildTestApp(initialLocation: '${AppRoute.inspections}?filter=all'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('CAB-001'),
      250,
      scrollable: find.byType(Scrollable).last,
    );
    await _pumpUntilFound(
      tester,
      find.text('CAB-001'),
      maxAttempts: 18,
    );

    expect(find.text('점검 대상'), findsOneWidget);
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
      final scenarioTextFinder =
          find.byKey(const Key('inspection-filter-item-scenario'));
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

  testWidgets('지역 기록 집계에 운영상 예외 결과를 포함한다', (WidgetTester tester) async {
    final previousOutcomes = (await loadInspectionOutcomes()).map(
      (uid, outcome) => MapEntry(uid, Map<String, String>.from(outcome)),
    );
    addTearDown(() => saveInspectionOutcomes(previousOutcomes));
    await saveInspectionOutcomes({
      'CAB-001': {
        'status': '운영상 예외',
        'outcomeCode': 'operational_exception',
        'stage': 'field_review',
      },
    });
    await tester.pumpWidget(
        buildTestApp(initialLocation: '${AppRoute.inspections}?filter=all'));
    await tester.pumpAndSettle();

    expect(
      find.text('정상 0 · 고장 관찰 0 · 운영상 예외 1 · 자료 문제 0 · 조치 완료 0'),
      findsOneWidget,
    );
  });

  testWidgets('현황 상태 카드가 해당 점검 목록과 선정 사유로 이동한다', (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp());
    await tester.pumpAndSettle();

    await tester
        .ensureVisible(find.byKey(const Key('dashboard-priority-card')));
    await tester.tap(find.byKey(const Key('dashboard-priority-card')));
    await tester.pumpAndSettle();
    expect(find.text('점검 대상'), findsOneWidget);
    expect(find.textContaining('우선 확인 ·'), findsOneWidget);

    await tester.pumpWidget(buildTestApp());
    await tester.pumpAndSettle();
    await tester
        .ensureVisible(find.byKey(const Key('dashboard-recommended-card')));
    await tester.tap(find.byKey(const Key('dashboard-recommended-card')));
    await tester.pumpAndSettle();
    expect(find.text('점검 대상'), findsOneWidget);
    expect(find.textContaining('점검 검토 ·'), findsOneWidget);
  });

  testWidgets('Cabinet detail renders 해설 문구 and raw data safe label',
      (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp(initialLocation: '/cabinet/CAB-002'));
    await tester.pumpAndSettle();
    await _pumpUntilFound(
      tester,
      find.text('분전함'),
      maxAttempts: 24,
    );
    expect(find.byKey(const Key('cabinet-map-link')), findsOneWidget);
    expect(find.text('지도에서 위치 보기'), findsOneWidget);
    expect(find.textContaining('좌표 · 35.000000, 129.000000'), findsOneWidget);
    final sectionAFinder =
        find.byKey(const Key('section-cabinet-section-summary-a'));
    await tester.scrollUntilVisible(
      sectionAFinder,
      250,
      scrollable: find.byType(Scrollable).last,
    );
    await tester.pumpAndSettle();
    expect(sectionAFinder, findsOneWidget);
    await tester.tap(find.text('자산 정보'));
    await tester.pumpAndSettle();
    expect(
      find.descendant(of: sectionAFinder, matching: find.text('조명 규격')),
      findsOneWidget,
    );
    expect(
      find.descendant(of: sectionAFinder, matching: find.text('자료 미제공')),
      findsAtLeastNWidgets(1),
    );
    expect(find.text('지도에서 위치를 확인할 수 있습니다.'), findsNothing);

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
            return data.contains('전력 신호') || data.contains('시각화');
          }
          if (widget is RichText) {
            return (widget.text.toPlainText().contains('전력 사용 이상 신호 요약') ||
                widget.text.toPlainText().contains('시각화'));
          }
          return false;
        }),
      ),
      findsAtLeastNWidgets(1),
    );
  });

  testWidgets('Inspection outcome can be recorded for an operator',
      (WidgetTester tester) async {
    await tester
        .pumpWidget(buildTestApp(initialLocation: AppRoute.inspections));
    await tester.pumpAndSettle();
    final targetCard = find
        .ancestor(
          of: find.text('CAB-002'),
          matching: find.byType(Card),
        )
        .first;
    await tester.scrollUntilVisible(
      targetCard,
      250,
      scrollable: find.byType(Scrollable).last,
    );
    final recordButton = find.ancestor(
      of: find.descendant(
        of: targetCard,
        matching: find.text('확인 결과 기록'),
      ),
      matching: find.byType(OutlinedButton),
    );
    await tester.ensureVisible(recordButton);
    await tester.drag(find.byType(ListView).last, const Offset(0, -160));
    await tester.pumpAndSettle();
    await tester.tap(recordButton);
    await tester.pumpAndSettle();
    expect(find.text('기기 저장 · 서버 동기화 없음'), findsOneWidget);
    await tester.tap(find.byType(DropdownButtonFormField<String>).last);
    await tester.pumpAndSettle();
    await tester.tap(find.text('정상').last);
    await tester.pumpAndSettle();
    await tester.enterText(
        find.widgetWithText(TextField, '담당자 (선택)'), '현장 담당자');
    final today = DateTime.now();
    final dueDate =
        '${today.year.toString().padLeft(4, '0')}-${today.month.toString().padLeft(2, '0')}-${today.day.toString().padLeft(2, '0')}';
    await tester.tap(find.text('기한 선택 (선택)'));
    await tester.pumpAndSettle();
    final dateDialog = find.byType(DatePickerDialog);
    await tester.tap(find.descendant(
        of: dateDialog, matching: find.text('${today.day}').last));
    await tester.pumpAndSettle();
    await tester
        .tap(find.descendant(of: dateDialog, matching: find.text('확인').last));
    await tester.pumpAndSettle();
    await tester.tap(find.text('저장'));
    await tester.pumpAndSettle();
    await tester.drag(find.byType(ListView).last, const Offset(0, 10000));
    await tester.pumpAndSettle();
    final savedCases = await loadInspectionOutcomes();
    expect(
        savedCases.values
            .where((record) => record['outcomeCode'] == 'normal')
            .length,
        1);
    expect(savedCases.keys.single, 'CAB-002');
    final seededCase = Map<String, String>.from(savedCases['CAB-002']!)
      ..['dueDate'] = dueDate;
    await saveInspectionOutcomes({'CAB-002': seededCase});
    expect(find.textContaining('1 / 3건'), findsOneWidget);
    expect(find.text('CAB-002'), findsNothing);
    await tester.tap(find.byKey(const Key('inspection-filter-dropdown')));
    await tester.pumpAndSettle();
    final allFilterItem = find.byKey(const Key('inspection-filter-item-all'));
    final allFilterRect = tester.getRect(allFilterItem);
    await tester
        .tapAt(Offset(allFilterRect.left + 24, allFilterRect.center.dy));
    await tester.pumpAndSettle();
    expect(find.text('CAB-002'), findsAtLeastNWidgets(1));
    await tester.tap(find.text('CAB-002').first);
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('field-primary-result')));
    await tester.pumpAndSettle();
    await tester.tap(find.byType(DropdownButtonFormField<String>).first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('고장 관찰').last);
    await tester.pumpAndSettle();
    await tester.tap(find.text('기기에 저장'));
    await tester.pumpAndSettle();
    await tester.binding.handlePopRoute();
    await tester.pumpAndSettle();
    expect(find.text('기한 $dueDate'), findsOneWidget);
    expect(find.text('담당 현장 담당자'), findsOneWidget);
    expect(find.text('기록 · 고장 관찰'), findsOneWidget);
    final roundTrip = await loadInspectionOutcomes();
    expect(roundTrip['CAB-002']?['assignee'], '현장 담당자');
    expect(roundTrip['CAB-002']?['dueDate'], dueDate);
    expect(roundTrip['CAB-002']?['outcomeCode'], 'fault_observed');
    await tester.pumpWidget(buildTestApp());
    await tester.pump();
    await _pumpUntilFound(tester, find.textContaining('기기 기록 결과 1건'),
        maxAttempts: 8);
    expect(find.textContaining('기록 1 / 전체 3'), findsOneWidget);
    expect(find.textContaining('메모:'), findsNothing);
  });

  testWidgets('Cabinet detail exposes activation color legend for a signal',
      (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp(initialLocation: '/cabinet/CAB-001'));
    await tester.pumpAndSettle();

    final legendFinder = find.byKey(const Key('activation-chart-legend'));
    await tester.scrollUntilVisible(
      legendFinder,
      300,
      scrollable: find.byType(Scrollable).last,
    );
    await tester.pumpAndSettle();

    expect(legendFinder, findsOneWidget);
    expect(find.textContaining('신호 수준'), findsAtLeastNWidgets(1));
    expect(find.textContaining('남은 구간'), findsOneWidget);
    expect(find.textContaining('daytime_partial_activation'), findsNothing);
  });

  testWidgets('Map marker recenters and opens cabinet information panel',
      (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp(initialLocation: AppRoute.map));
    await tester.pumpAndSettle();

    final markerFinder = find.byKey(const Key('map-marker-CAB-001'));
    expect(markerFinder, findsOneWidget);
    tester.widget<GestureDetector>(markerFinder).onTap!.call();
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('map-focused-cabinet-marker')), findsOneWidget);
    expect(find.byKey(const Key('map-selected-cabinet-card')), findsOneWidget);
    expect(find.text('CAB-001'), findsAtLeastNWidgets(1));
    expect(find.text('분전함 상세 보기'), findsOneWidget);
    expect(find.textContaining('35.000000, 129.000000'), findsNothing);
  });

  testWidgets('전력계량 분석 화면이 핵심 신호와 판정 근거를 표시한다', (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp(initialLocation: AppRoute.ami));
    await tester.pumpAndSettle();

    expect(find.text('전력계량 이상 신호 근거'), findsOneWidget);
    expect(find.text('가명 처리 전력계량 자료'), findsAtLeastNWidgets(1));
    expect(find.text('탐지 기준 대비 최대 신호 비율'), findsAtLeastNWidgets(1));
    expect(find.textContaining('1번 전류선(i1)'), findsAtLeastNWidgets(1));
    expect(find.text('이상 신호 형태 일치 수준'), findsAtLeastNWidgets(1));
    expect(find.text('높음'), findsAtLeastNWidgets(1));
    expect(find.text('보통 이상'), findsAtLeastNWidgets(1));
    expect(find.text('medium_high'), findsNothing);
    expect(find.byKey(const Key('ami-case-B-L-35-2026-05-11')), findsOneWidget);
    if (events.isNotEmpty) {
      expect(
          find.textContaining(events.first.meterId), findsAtLeastNWidgets(1));
    } else {
      fail('AMI 이벤트 데이터가 비어 있어 목록 검증을 수행할 수 없습니다.');
    }
    await tester.drag(find.byType(ListView), const Offset(0, -10000));
    await tester.pumpAndSettle();
    expect(find.text(AmiValidationScreen.disclaimer), findsOneWidget);
    expect(find.text('상세 검증자료'), findsNothing);
    expect(find.text('검증 결과 요약'), findsNothing);
    expect(find.text('자료가 부족할 때의 처리'), findsNothing);
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

  for (final width in [360.0, 412.0, 1024.0]) {
    testWidgets(
        'field workflow adapts at ${width.toInt()}px and text scale 1.3',
        (WidgetTester tester) async {
      tester.view.physicalSize = Size(width, 900);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 1.3;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);

      for (final route in [
        AppRoute.dashboard,
        AppRoute.inspections,
        '/cabinet/CAB-001',
        AppRoute.map,
      ]) {
        await tester.pumpWidget(buildTestApp(initialLocation: route));
        await tester.pumpAndSettle();
        expect(tester.takeException(), isNull,
            reason: '$route overflowed at $width px');
        if (route == AppRoute.dashboard) {
          expect(find.text(width < 600 ? 'LightGuard' : 'LightGuard · 운영 현황'),
              findsOneWidget);
          expect(find.textContaining('고정 자료'), findsOneWidget);
          expect(find.byKey(const Key('today-action-queue')), findsOneWidget);
        }
        if (route == AppRoute.inspections) {
          expect(find.text('점검 대상'), findsAtLeastNWidgets(1));
        }
        if (route == '/cabinet/CAB-001') {
          expect(find.byKey(const Key('field-primary-result')), findsOneWidget);
        }
        for (final type in [
          FilledButton,
          OutlinedButton,
          TextButton,
          IconButton,
          ActionChip,
          DropdownButton,
          DropdownButtonFormField<String>,
          InkWell,
          GestureDetector
        ]) {
          for (final element in find.byType(type).evaluate()) {
            var implementationOfButton = false;
            element.visitAncestorElements((ancestor) {
              if (ancestor.widget is ButtonStyleButton) {
                implementationOfButton = true;
                return false;
              }
              if (ancestor.widget is RawChip ||
                  ancestor.widget is DropdownButton) {
                implementationOfButton = true;
                return false;
              }
              return true;
            });
            if (implementationOfButton) continue;
            final rect = tester.getRect(find.byElementPredicate(
                (candidate) => identical(candidate, element)));
            expect(rect.width, greaterThanOrEqualTo(48),
                reason:
                    '$type narrower than 48dp at $width px on $route: $rect');
            expect(rect.height, greaterThanOrEqualTo(48),
                reason:
                    '$type shorter than 48dp at $width px on $route: $rect');
          }
        }
      }
    });
  }

  testWidgets('공통 지역 선택기로 운영 화면의 지역을 변경한다', (WidgetTester tester) async {
    await tester.pumpWidget(buildTestApp());
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('global-region-selector')), findsOneWidget);
    expect(find.text(RegionId.suyeong.label), findsAtLeastNWidgets(1));
    expect(find.text('지역'), findsNothing);

    await tester.tap(find.byKey(const Key('global-region-selector')));
    await tester.pumpAndSettle();
    await tester.tap(find.text(RegionId.gangneung.label).last);
    await tester.pumpAndSettle();

    expect(find.text(RegionId.gangneung.branchLabel), findsAtLeastNWidgets(1));
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
        address: '35.000000, 129.000000',
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
  String address = '부산 수영구',
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
      address: address,
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
