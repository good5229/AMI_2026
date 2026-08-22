import 'dart:convert';

import 'package:flutter/material.dart';

class V11AnomalySignCard extends StatelessWidget {
  const V11AnomalySignCard({super.key});

  @override
  Widget build(BuildContext context) => Card(
        key: const Key('v11-anomaly-sign-card'),
        color: const Color(0xFFF3EFE2),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: FutureBuilder<String>(
            future: DefaultAssetBundle.of(context).loadString(
              'assets/data/context/v11_proxy_detector_summary.json',
            ),
            builder: (context, snapshot) {
              if (!snapshot.hasData) return const LinearProgressIndicator();
              final data = jsonDecode(snapshot.data!) as Map<String, dynamic>;
              final density =
                  ((data['high_confidence_proxy_density'] as num) * 100)
                      .toStringAsFixed(2);
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.manage_search, color: Color(0xFFB34F2A)),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text('v0.11 이상 징후 근거 감사',
                            style: Theme.of(context).textTheme.titleLarge),
                      ),
                      const Chip(label: Text('직접 비교 방식')),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '전체 원본 확인 결과 현장 고장 확정자료 0건 · 운영상태 확인자료 0건',
                    style: TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 14),
                  Wrap(
                    spacing: 20,
                    runSpacing: 12,
                    children: [
                      _Metric('감사 파일', '${data['files_audited']}'),
                      _Metric('May-Jun origins', '${data['score_rows']}'),
                      _Metric('간접 기준 높은 일치',
                          '${data['high_confidence_proxy_candidates']}'),
                      _Metric('후보 밀도', '$density%'),
                      _Metric('기본 판정과 간접 기준 동시 일치',
                          '${data['h1_proxy_high_agreement']}'),
                      _Metric('Matched uplift',
                          '+${(data['paired_proxy_family_uplift'] as num).toStringAsFixed(2)}'),
                    ],
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    'April-only 기준을 고정한 뒤 May-Jun을 평가했습니다. '
                    '동일한 전력계량 자료에서 서로 다른 세 가지 간접 기준이 일치한 결과이며 실제 고장 정확도나 고장률이 아닙니다. '
                    '점검 판단에는 분전함 매핑과 현장 확인이 필요합니다.',
                    style: TextStyle(fontSize: 12),
                  ),
                ],
              );
            },
          ),
        ),
      );
}

class _Metric extends StatelessWidget {
  const _Metric(this.label, this.value);
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 132,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: Theme.of(context).textTheme.bodySmall),
            Text(value,
                style: Theme.of(context)
                    .textTheme
                    .titleMedium
                    ?.copyWith(fontWeight: FontWeight.w800)),
          ],
        ),
      );
}
