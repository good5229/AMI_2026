import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:lightguard_app/app/theme/app_theme.dart';
import 'package:lightguard_app/core/storage/inspection_outcome_storage.dart';
import 'package:lightguard_app/data/models/context_models.dart';
import 'package:lightguard_app/data/repositories/lightguard_repository.dart';
import 'package:lightguard_app/features/ami_validation/ami_replay_screen.dart';

Future<void> reveal(WidgetTester tester, Finder target) async {
  for (var i = 0; i < 40 && target.hitTestable().evaluate().isEmpty; i++) {
    await tester.drag(find.byType(ListView).first, const Offset(0, -220));
    await tester.pump();
  }
  expect(target.hitTestable(), findsOneWidget);
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late List<ValidationEvent> events;
  late Map<String, List<AmiReplaySample>> windows;
  setUpAll(() async {
    final container = ProviderContainer();
    try {
      events = await container.read(competitionAmiEventsProvider.future);
      windows = await container.read(amiReplayWindowsProvider.future);
    } finally {
      container.dispose();
    }
    expect(events, hasLength(6));
    expect(windows.values.fold<int>(0, (sum, rows) => sum + rows.length), 110);
  });

  for (final width in [360.0, 412.0, 1024.0]) {
    testWidgets('actual AMI replay at ${width.toInt()}px preserves field records',
        (tester) async {
      tester.view.physicalSize = Size(width, 1000);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await saveInspectionOutcomes({
        'regional-existing': {'outcomeCode': 'normal', 'assignee': 'Existing'},
      });
      final router = GoRouter(
        initialLocation: '/ami-events',
        routes: [
          GoRoute(path: '/ami-events', builder: (_, __) => const AmiReplayScreen()),
        ],
      );
      addTearDown(router.dispose);
      await tester.pumpWidget(ProviderScope(
        overrides: [
          competitionAmiEventsProvider.overrideWith((ref) async => events),
          amiReplayWindowsProvider.overrideWith((ref) async => windows),
        ],
        child: MaterialApp.router(
          theme: AppTheme.light(),
          routerConfig: router,
          builder: (context, child) => MediaQuery(
            data: MediaQuery.of(context).copyWith(
              textScaler: const TextScaler.linear(1.3),
            ),
            child: child!,
          ),
        ),
      ));
      await tester.pumpAndSettle();
      expect(find.textContaining('B-L-35'), findsWidgets);
      expect(tester.takeException(), isNull);
      final play = find.byKey(const Key('ami-play'));
      await reveal(tester, play);
      await tester.tap(play);
      await tester.pump();
      expect(find.text('일시 정지'), findsOneWidget);
      await tester.pump(const Duration(milliseconds: 900));
      expect(find.text('2 / 18 관측점'), findsOneWidget);
      expect(tester.widget<Text>(find.byKey(const Key('ami-current-sample'))).data,
          contains('미수집'));
      await tester.tap(play);
      await tester.pump();
      expect(find.text('기록 재생'), findsOneWidget);
      expect(tester.takeException(), isNull);
      await reveal(tester, find.widgetWithText(TextField, '검토 메모'));
      await tester.enterText(find.widgetWithText(TextField, '검토 메모'),
          'Test: source observations reviewed');
      await reveal(tester, find.text('검토 기록 저장'));
      await tester.tap(find.text('검토 기록 저장'));
      await tester.pumpAndSettle();
      final saved = await loadInspectionOutcomes();
      expect(saved['regional-existing']?['assignee'], 'Existing');
      expect(saved['regional-existing']?['outcomeCode'], 'normal');
      final review = saved.entries.singleWhere((e) => e.key.startsWith('ami-review:'));
      expect(review.value['recordType'], 'ami_analysis_review');
      expect(review.value.containsKey('outcomeCode'), isFalse);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox.shrink());
      await saveInspectionOutcomes({});
    });
  }
}
