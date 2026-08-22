import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final v09SpecificitySummaryProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final raw = await rootBundle.loadString(
    'assets/data/context/v09_specificity_summary.json',
  );
  return jsonDecode(raw) as Map<String, dynamic>;
});

class V09SpecificityCard extends ConsumerWidget {
  const V09SpecificityCard({super.key});

  String _rate(Object? value) =>
      value is num ? '${(value.toDouble() * 100).toStringAsFixed(1)}%' : 'unavailable';

  String _interval(Object? value) {
    final interval = value is List ? value : const <dynamic>[];
    if (interval.length != 2) return 'unavailable';
    return '${_rate(interval[0])}–${_rate(interval[1])}';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summary = ref.watch(v09SpecificitySummaryProvider);
    return summary.when(
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: LinearProgressIndicator(),
        ),
      ),
      error: (error, _) => const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('정상 상태 구분 검증 결과를 불러오지 못했습니다.'),
        ),
      ),
      data: (data) {
        final metrics = data['metrics'] as Map<String, dynamic>;
        final promoted = data['promotion_passed'] == true;
        return Card(
          key: const Key('v09-specificity-validation'),
          color: promoted ? const Color(0xFFE9F4ED) : const Color(0xFFFFF2E5),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'v0.9 · Episode-Separated Specificity',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 6),
                Text(
                  promoted
                      ? '${data['selected_candidate']} passed controlled promotion gates'
                      : 'Candidate not promoted',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    color: promoted ? const Color(0xFF175C37) : const Color(0xFF8A3C08),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '별도 검증 사례 ${data['confirmatory_cases']}개 · 판정 기준 조정에 사용하지 않은 구간 ${data['confirmatory_episodes']}개 · 날짜와 기상자료 중복 0건',
                  style: const TextStyle(fontSize: 12),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 16,
                  runSpacing: 10,
                  children: [
                    _Metric(label: '이상 사례 탐지율', value: _rate(metrics['recall']), detail: '95% 예상 범위 ${_interval(metrics['recall_wilson_95'])}'),
                    _Metric(label: '정상 오분류율', value: _rate(metrics['fpr']), detail: '95% 예상 범위 ${_interval(metrics['fpr_wilson_95'])}'),
                    _Metric(label: '구분하기 어려운 정상 사례 오분류율', value: _rate(metrics['hard_negative_fpr']), detail: '95% 예상 범위 ${_interval(metrics['hard_negative_fpr_wilson_95'])}'),
                    _Metric(label: '지역·계절별 최저 탐지율', value: _rate(metrics['worst_cell_recall']), detail: '3개 지역 × 4개 계절'),
                  ],
                ),
                const SizedBox(height: 12),
                const Text(
                  '조건을 정해 만든 별도 검증자료의 결과입니다. 실제 지역 전력자료 정확도, 현장 고장 탐지율 또는 즉시 운영 가능함을 의미하지 않습니다. 기상 가중치는 사용하지 않았고 누락된 부하값도 임의로 채우지 않았습니다.',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
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
  const _Metric({required this.label, required this.value, required this.detail});

  final String label;
  final String value;
  final String detail;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 180,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 12)),
          Text(value, style: Theme.of(context).textTheme.titleLarge),
          Text(detail, style: const TextStyle(fontSize: 11)),
        ],
      ),
    );
  }
}
