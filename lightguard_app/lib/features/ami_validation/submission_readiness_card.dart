import 'package:flutter/material.dart';

class SubmissionReadinessCard extends StatelessWidget {
  const SubmissionReadinessCard({super.key});

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Card(
      color: colors.surfaceContainerHigh,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.route_outlined, color: colors.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '오늘의 점검 의사결정 흐름',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
                const Chip(label: Text('제출 검수 완료')),
              ],
            ),
            const SizedBox(height: 12),
            const Wrap(
              spacing: 6,
              runSpacing: 6,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                _FlowStep(label: '문제'),
                Icon(Icons.arrow_forward, size: 18),
                _FlowStep(label: '전력 사용 이상 신호'),
                Icon(Icons.arrow_forward, size: 18),
                _FlowStep(label: '운영 우선순위'),
                Icon(Icons.arrow_forward, size: 18),
                _FlowStep(label: '현장 확인 필요'),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'SIGNAL · PLAUSIBILITY · OPERATIONS · PRODUCT 근거를 분리해 자동 고장판정이 아닌 점검 우선순위를 제시합니다.',
            ),
            const SizedBox(height: 8),
            const Text(
              '현장 고장 정확도·확률, 민원·비용·인력 감소, 실제 처리시간 단축은 검증되지 않았습니다.',
            ),
          ],
        ),
      ),
    );
  }
}

class _FlowStep extends StatelessWidget {
  const _FlowStep({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(label),
    );
  }
}
