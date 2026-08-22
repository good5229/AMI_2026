import 'package:flutter/material.dart';

class V19BuyeoEvidenceCard extends StatelessWidget {
  const V19BuyeoEvidenceCard({super.key});
  @override Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Text('독립 지자체 유지관리 유형 - 부여군 공개데이터', style: Theme.of(context).textTheme.titleMedium),
    const SizedBox(height: 8), const Text('주간점등 · 불점등 · 점멸 · 시간조정'),
    const SizedBox(height: 6), const Text('원본 3,437건 중 낮 시간 점등 관련 운영기록 25건을 확인했습니다.'),
    const SizedBox(height: 6), const Text('부여군 유지관리 기록은 분석용 전력계량 자료와 직접 연결된 고장 정답이 아닙니다.'),
    const SizedBox(height: 6), const Text('대구 자료로 정한 공통 판정 기준을 다시 조정하지 않고 부여 자료에 적용했습니다. 이는 고장 정확도나 수리시간 단축 효과가 아닙니다.'),
  ])));
}
