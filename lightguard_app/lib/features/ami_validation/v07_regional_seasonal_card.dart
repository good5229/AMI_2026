import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final v07RegionalSeasonalSummaryProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final raw = await rootBundle.loadString(
    'assets/data/context/v07_regional_seasonal_summary.json',
  );
  return jsonDecode(raw) as Map<String, dynamic>;
});

class V07RegionalSeasonalCard extends ConsumerWidget {
  const V07RegionalSeasonalCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summary = ref.watch(v07RegionalSeasonalSummaryProvider);
    return summary.when(
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(20),
          child: LinearProgressIndicator(),
        ),
      ),
      error: (error, stackTrace) => Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Text('지역·계절 검증 요약을 불러오지 못했습니다: $error'),
        ),
      ),
      data: (data) {
        final worst = data['worst_cell'] as Map<String, dynamic>;
        final assets = data['regional_assets'] as Map<String, dynamic>;
        final chungju = assets['chungju'] as Map<String, dynamic>;
        final recall = ((data['macro_recall'] as num) * 100).toStringAsFixed(0);
        final fpr = ((data['macro_fpr'] as num) * 100).toStringAsFixed(0);
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '지역 × 계절 통제 검증',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 6),
                const Text('수영구 · 강릉 · 충주 / 겨울 · 봄 · 여름 · 가을'),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    _Metric(label: '검증 셀', value: '${data['cell_count']}'),
                    _Metric(label: '검증용 모의 사례', value: '${data['scenario_count']}'),
                    _Metric(label: '지역·계절 평균 탐지율', value: '$recall%'),
                    _Metric(label: '지역·계절 평균 정상 오분류율', value: '$fpr%'),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  '모든 셀에서 동일 판정 · 최저 셀 ${worst['cell_id']}',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                const SizedBox(height: 8),
                const Text(
                  'KMA ASOS 159·105·127과 KASI 일출·일몰을 적용했지만, '
                  '약한 이상 2종을 놓쳐 민감도 개선이 필요합니다.',
                ),
                const SizedBox(height: 12),
                _BoundaryNotice(
                  text: '충주 정격부하 가용률 '
                      '${((chungju['rated_load_coverage'] as num) * 100).toStringAsFixed(0)}% '
                      '· 임의 대체 없음',
                ),
                const SizedBox(height: 8),
                const _BoundaryNotice(
                  text: '동일 조건에서 지역·계절 영향을 비교한 결과이며, 다른 지역의 실제 전력계량 자료 검증은 아직 수행하지 못했습니다.',
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Container(
        width: 132,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: Theme.of(context).textTheme.labelMedium),
            const SizedBox(height: 4),
            Text(value, style: Theme.of(context).textTheme.titleLarge),
          ],
        ),
      );
}

class _BoundaryNotice extends StatelessWidget {
  const _BoundaryNotice({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.errorContainer,
          borderRadius: BorderRadius.circular(10),
        ),
        child: Text(text),
      );
}
