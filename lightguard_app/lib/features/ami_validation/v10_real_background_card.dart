import 'dart:convert';

import 'package:flutter/material.dart';

class V10RealBackgroundCard extends StatelessWidget {
  const V10RealBackgroundCard({super.key});

  @override
  Widget build(BuildContext context) => Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: FutureBuilder<String>(
            future: DefaultAssetBundle.of(context).loadString(
              'assets/data/context/v10_real_background_summary.json',
            ),
            builder: (context, snapshot) {
              if (!snapshot.hasData) {
                return const LinearProgressIndicator();
              }
              final data = jsonDecode(snapshot.data!) as Map<String, dynamic>;
              final irr = ((data['injection_recovery_rate'] as num) * 100)
                  .toStringAsFixed(1);
              final benign = ((data['benign_escalation_rate'] as num) * 100)
                  .toStringAsFixed(1);
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('실제 정상 사용자료 기반 검증',
                      style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 6),
                  const Text(
                    '실제 정상 전력자료에 검증용 전류 변화를 추가한 시험',
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 14),
                  Wrap(
                    spacing: 20,
                    runSpacing: 12,
                    children: [
                      _Metric('Meters', '${data['meters']}'),
                      const _Metric('Period', '3 months'),
                      _Metric('Paired recovery', '$irr%'),
                      _Metric('정상 사례의 불필요한 우선순위 상승', '$benign%'),
                      _Metric('Gate', '${data['transport_gate']}'),
                    ],
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    '현장 고장 정확도가 아닙니다. 가명 처리된 전력계량 자료에는 고장·정비 정답이 없으며 '
                    '지자체 자산, KMA/KASI, 정격부하를 결합하지 않았습니다.',
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
                    ?.copyWith(fontWeight: FontWeight.w700)),
          ],
        ),
      );
}
