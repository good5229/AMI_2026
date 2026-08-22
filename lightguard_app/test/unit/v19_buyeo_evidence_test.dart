import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/v19_buyeo_evidence_card.dart';

void main() {
  testWidgets('v0.19 Buyeo evidence preserves independent operational boundary', (tester) async {
    await tester.pumpWidget(const TestApp());
    expect(find.textContaining('부여군 공개데이터'), findsOneWidget);
    expect(find.textContaining('낮 시간 점등'), findsWidgets);
    expect(find.textContaining('직접 연결된 고장 정답이 아닙니다'), findsOneWidget);
    expect(find.textContaining('판정 기준을 다시 조정하지 않고'), findsOneWidget);
  });
}

class TestApp extends StatelessWidget {
  const TestApp({super.key});
  @override
  Widget build(BuildContext context) => const MaterialApp(home: Scaffold(body: V19BuyeoEvidenceCard()));
}
