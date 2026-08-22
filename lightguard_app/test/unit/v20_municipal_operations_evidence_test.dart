import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/municipal_operations_evidence_card.dart';

void main() {
  testWidgets('municipal evidence presents seven-region roles and boundaries', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(body: MunicipalOperationsEvidenceCard()),
      ),
    );

    expect(find.text('Municipal Operations Evidence'), findsOneWidget);
    expect(find.text('7개 지역'), findsOneWidget);
    expect(find.text('101,843건'), findsOneWidget);
    expect(find.text('11,892건'), findsOneWidget);
    expect(find.text('43,082자산'), findsOneWidget);
    expect(find.text('339분전함'), findsOneWidget);
    expect(find.textContaining('920/981'), findsOneWidget);
    expect(find.textContaining('SIGNAL과 OPERATIONS'), findsOneWidget);
    expect(find.textContaining('AMI 현장 고장 정답'), findsOneWidget);
    expect(find.textContaining('실제 처리시간 단축'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
