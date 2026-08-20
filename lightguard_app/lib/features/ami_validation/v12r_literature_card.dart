import 'dart:convert';

import 'package:flutter/material.dart';

class V12RLiteratureCard extends StatelessWidget {
  const V12RLiteratureCard({super.key});

  @override
  Widget build(BuildContext context) => Card(
        key: const Key('v12r-literature-card'),
        color: const Color(0xFFE8F0E8),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: FutureBuilder<String>(
            future: DefaultAssetBundle.of(context).loadString(
              'assets/data/context/v12r_literature_summary.json',
            ),
            builder: (context, snapshot) {
              if (!snapshot.hasData) return const LinearProgressIndicator();
              final data = jsonDecode(snapshot.data!) as Map<String, dynamic>;
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.menu_book_outlined,
                          color: Color(0xFFB44D2A)),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text('v0.12R 문헌 기반 이상 징후 근거',
                            style: Theme.of(context).textTheme.titleLarge),
                      ),
                      const Chip(label: Text('Level 3')),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '연구방법론 검토 완료 · 블라인드 사람 검토 대기',
                    style: TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 14),
                  Wrap(
                    spacing: 20,
                    runSpacing: 12,
                    children: [
                      _Metric('검증 출처', '${data['sources']}'),
                      _Metric('A급 출처', '${data['quality_a']}'),
                      _Metric('L2/L3 근거',
                          '${data['core_direct_or_mechanism']}'),
                      _Metric('Proxy High 매핑',
                          '${data['proxy_high_mapped']}'),
                      const _Metric('Blind packet', '62'),
                      const _Metric('Human review', 'Pending'),
                    ],
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    'A/B/C는 논문·측정·알고리즘 근거의 강도이며 고장 확률이 아닙니다. '
                    '현재 문헌은 점검할 가치가 있는 이상 징후 해석을 지지하지만 '
                    '현장 고장 여부는 분전함 매핑과 독립 점검 결과가 필요합니다.',
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
