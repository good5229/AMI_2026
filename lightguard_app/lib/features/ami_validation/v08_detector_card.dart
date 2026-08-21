import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final v08DetectorSummaryProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final raw = await rootBundle.loadString(
    'assets/data/context/v08_detector_summary.json',
  );
  return jsonDecode(raw) as Map<String, dynamic>;
});

class V08DetectorCard extends ConsumerWidget {
  const V08DetectorCard({super.key});

  String _pct(dynamic value) => '${((value as num) * 100).toStringAsFixed(1)}%';

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summary = ref.watch(v08DetectorSummaryProvider);
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
          child: Text('v0.8 검증 결과를 불러오지 못했습니다: $error'),
        ),
      ),
      data: (data) {
        final baseline = data['baseline'] as Map<String, dynamic>;
        final candidate = data['experimental_c1'] as Map<String, dynamic>;
        final c2 = data['experimental_c2'] as Map<String, dynamic>;
        final chungju = data['chungju'] as Map<String, dynamic>;
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('v0.8 독립 통제 Holdout', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 6),
                Text('${data['confirmatory_cases']}개 시나리오 · baseline과 experimental candidate 분리'),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    _Metric(label: 'Frozen v0.4 Recall', value: _pct(baseline['recall'])),
                    _Metric(label: 'C1 Recall', value: _pct(candidate['recall'])),
                    _Metric(label: 'C1 FPR', value: _pct(candidate['fpr'])),
                    _Metric(label: 'C2 보류', value: _pct(c2['abstention_rate'])),
                  ],
                ),
                const SizedBox(height: 16),
                _Notice(
                  color: Theme.of(context).colorScheme.errorContainer,
                  text: '후보 채택 안 함 · C1/C2 FPR ${_pct(candidate['fpr'])}가 사전 한도 5.0%를 초과했습니다.',
                ),
                const SizedBox(height: 8),
                _Notice(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  text: '전체표본 기준 Wilson 95% CI · C1 Recall ${candidate['recall_wilson_95']} · FPR ${candidate['fpr_wilson_95']}',
                ),
                const SizedBox(height: 8),
                _Notice(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  text: '보류 제외 C2 평가 · Recall ${_pct(c2['recall_evaluable'])} · FPR ${_pct(c2['fpr_evaluable'])}',
                ),
                const SizedBox(height: 8),
                _Notice(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  text: '충주 정격부하 ${chungju['rated_load']} · No imputation · weather는 context_only',
                ),
                const SizedBox(height: 8),
                const Text('실제 강릉·충주 AMI 성능이 아닌 통제 시나리오 검증입니다.'),
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
        width: 150,
        padding: const EdgeInsets.all(12),
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

class _Notice extends StatelessWidget {
  const _Notice({required this.color, required this.text});

  final Color color;
  final String text;

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(10)),
        child: Text(text),
      );
}
