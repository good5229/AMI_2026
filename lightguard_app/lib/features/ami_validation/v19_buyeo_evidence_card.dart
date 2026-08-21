import 'package:flutter/material.dart';

class V19BuyeoEvidenceCard extends StatelessWidget {
  const V19BuyeoEvidenceCard({super.key});
  @override Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Text('독립 지자체 유지관리 유형 - 부여군 공개데이터', style: Theme.of(context).textTheme.titleMedium),
    const SizedBox(height: 8), const Text('주간점등 · 불점등 · 점멸 · 시간조정'),
    const SizedBox(height: 6), const Text('원본 3,437건 중 주간점등 운영기록 25건 · 운영 일반화 OG-B'),
    const SizedBox(height: 6), const Text('부여군 유지관리 기록은 공모전 AMI와 직접 연결된 정답 데이터가 아닙니다.'),
    const SizedBox(height: 6), const Text('대구에서 동결한 공통 운영이력 모델을 부여에서 재튜닝 없이 외부 평가했습니다. 이는 고장 정확도나 수리시간 단축 효과가 아닙니다.'),
  ])));
}
