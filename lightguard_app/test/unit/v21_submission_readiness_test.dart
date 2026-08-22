import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/submission_readiness_card.dart';

void main() {
  testWidgets('submission readiness presents service flow and boundaries', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(child: SubmissionReadinessCard()),
        ),
      ),
    );

    expect(find.text('오늘의 점검 의사결정 흐름'), findsOneWidget);
    expect(find.text('전력 사용 이상 신호'), findsOneWidget);
    expect(find.text('운영 우선순위'), findsOneWidget);
    expect(find.text('현장 확인 필요'), findsOneWidget);
    expect(find.textContaining('자동 고장판정이 아닌'), findsOneWidget);
    expect(find.textContaining('검증되지 않았습니다'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
