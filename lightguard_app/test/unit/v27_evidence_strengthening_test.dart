import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/evidence_strengthening_panel.dart';

const _assetPath = 'assets/data/evidence/v27_evidence_strengthening.json';

void main() {
  testWidgets(
    'v0.27 실제 번들 근거를 순서대로 표시하고 모바일에서 안전하게 펼친다',
    (tester) async {
      tester.view.physicalSize = const Size(360, 800);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      final decoded = jsonDecode(await rootBundle.loadString(_assetPath))
          as Map<String, dynamic>;
      final stages = (decoded['ordered_stages'] as List)
          .cast<Map<String, dynamic>>()
        ..sort((a, b) =>
            (a['order'] as num).toInt().compareTo((b['order'] as num).toInt()));

      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              padding: EdgeInsets.all(12),
              child: EvidenceStrengtheningPanel(),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(stages, hasLength(5));
      expect(find.text(decoded['title'] as String), findsOneWidget);
      expect(
        find.text(
          '현장 고장 정확도와 실현 절감 효과는 현장 연결 전까지 입증 범위가 아닙니다.',
        ),
        findsOneWidget,
      );

      var previousY = double.negativeInfinity;
      for (final stage in stages) {
        final title = '${stage['order']}. ${stage['title']}';
        final titleFinder = find.text(title);
        expect(titleFinder, findsOneWidget);
        expect(find.text(stage['status_label'] as String), findsWidgets);
        final y = tester.getTopLeft(titleFinder).dy;
        expect(y, greaterThan(previousY));
        previousY = y;
      }

      final technical = stages.firstWhere(
        (stage) => (stage['id'] as String).contains('technical'),
      );
      expect(
        find.byKey(Key('v27-stage-body-${technical['id']}')),
        findsOneWidget,
      );

      await _expandStage(tester, 'external_context');
      expect(find.text('실제 AMI 미연결 · 기상자료는 참고용'), findsOneWidget);
      expect(
        find.textContaining('보정 효과나 오탐 감소를 입증한 결과가 아닙니다'),
        findsOneWidget,
      );

      await _expandStage(tester, 'field_linkage');
      final linkage = stages.firstWhere(
        (stage) => stage['id'] == 'field_linkage',
      );
      final expectedChain = _joinChain(linkage['join_chain']);
      expect(find.text('현장 데이터 연결 순서'), findsOneWidget);
      expect(find.text(expectedChain), findsOneWidget);
      expect(find.text('현장 검증에 필요한 자료'), findsOneWidget);
      expect(find.byKey(const Key('v27-field-join-chain')), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}

Future<void> _expandStage(WidgetTester tester, String id) async {
  final finder = find.byKey(Key('v27-stage-$id'));
  await tester.scrollUntilVisible(
    finder,
    260,
    scrollable: find.byType(Scrollable).first,
  );
  await tester.tap(finder);
  await tester.pumpAndSettle();
}

String _joinChain(Object? value) {
  if (value is List) {
    return value.map(_plainText).where((item) => item.isNotEmpty).join(' → ');
  }
  return _plainText(value);
}

String _plainText(Object? value) {
  if (value == null) return '';
  if (value is Map) {
    return value.values
        .map(_plainText)
        .where((item) => item.isNotEmpty)
        .join(' → ');
  }
  return value.toString().trim();
}
