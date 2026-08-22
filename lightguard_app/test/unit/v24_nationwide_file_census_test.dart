import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/nationwide_file_census_card.dart';

void main() {
  testWidgets('전국 파일데이터 조사 범위와 해석 경계를 표시한다', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(child: NationwideFileCensusCard()),
        ),
      ),
    );

    expect(find.text('전국 공개파일 구조 조사'), findsOneWidget);
    expect(find.text('16 / 16'), findsOneWidget);
    expect(find.text('83개'), findsOneWidget);
    expect(find.text('125개'), findsOneWidget);
    expect(find.text('전력·상태 신호'), findsOneWidget);
    expect(find.textContaining('동일한 탐지 성능이나 운영 효과'), findsOneWidget);
  });
}
