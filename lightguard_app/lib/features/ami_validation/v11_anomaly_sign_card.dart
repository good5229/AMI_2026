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
                      const Chip(label: Text('Route C')),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '전체 원본 감사 결과 현장확인 Gold 0건 · 운영상태 Silver 0건',
                    style: TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 14),
                  Wrap(
                    spacing: 20,
                    runSpacing: 12,
                    children: [
                      _Metric('감사 파일', '${data['files_audited']}'),
                      _Metric('May-Jun origins', '${data['score_rows']}'),
                      _Metric('Proxy High',
                          '${data['high_confidence_proxy_candidates']}'),
                      _Metric('후보 밀도', '$density%'),
                      _Metric('H1 + Proxy High',
                          '${data['h1_proxy_high_agreement']}'),
                      _Metric('Matched uplift',
                          '+${(data['paired_proxy_family_uplift'] as num).toStringAsFixed(2)}'),
                    ],
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    'April-only 기준을 고정한 뒤 May-Jun을 평가했습니다. '
                    '동일 AMI에서 만든 세 proxy family의 합의이며 실제 고장 정확도나 고장률이 아닙니다. '
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
