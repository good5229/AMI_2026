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
      error: (error, _) => Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text('v0.9 specificity evidence load failed: $error'),
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
                  '${data['confirmatory_cases']} scenarios · ${data['confirmatory_episodes']} untouched episodes · date/KMA overlap 0',
                  style: const TextStyle(fontSize: 12),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 16,
                  runSpacing: 10,
                  children: [
                    _Metric(label: 'Recall', value: _rate(metrics['recall']), detail: 'Wilson ${_interval(metrics['recall_wilson_95'])}'),
                    _Metric(label: 'Normal FPR', value: _rate(metrics['fpr']), detail: 'Wilson ${_interval(metrics['fpr_wilson_95'])}'),
                    _Metric(label: 'Hard-negative FPR', value: _rate(metrics['hard_negative_fpr']), detail: 'Wilson ${_interval(metrics['hard_negative_fpr_wilson_95'])}'),
                    _Metric(label: 'Worst cell recall', value: _rate(metrics['worst_cell_recall']), detail: '3 regions × 4 seasons'),
                  ],
                ),
                const SizedBox(height: 12),
                const Text(
                  'Controlled generated holdout only. 실제 지역 AMI 정확도·현장 고장 recall·운영 배포 승격을 의미하지 않습니다. Weather weight 0, load imputation 없음.',
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
