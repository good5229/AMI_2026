import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/regions/region_onboarding_card.dart';

void main() {
  testWidgets('새 지역 CSV 열 이름에서 연결 가능한 항목을 설명한다', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(child: RegionOnboardingCard()),
        ),
      ),
    );
    await tester.tap(find.text('새 지역 자료 연결 준비'));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byType(TextField),
      '관리번호,위도,경도,정격용량,접수일,처리일',
    );
    await tester.tap(find.text('연결 가능 항목 확인'));
    await tester.pump();

    expect(find.text('가로등 시설정보'), findsOneWidget);
    expect(find.text('설치 위치'), findsOneWidget);
    expect(find.text('설비용량 정보'), findsOneWidget);
    expect(find.text('고장 접수·처리 이력'), findsOneWidget);
    expect(find.textContaining('추가로 필요한 항목'), findsOneWidget);
  });
}
