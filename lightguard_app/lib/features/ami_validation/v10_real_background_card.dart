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
                  Text('Real-Background Validation',
                      style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 6),
                  const Text(
                    'Real AMI Background + Controlled Current Injection',
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
                      _Metric('Benign escalation', '$benign%'),
                      _Metric('Gate', '${data['transport_gate']}'),
                    ],
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    'Not field fault accuracy. 익명 AMI에는 고장·정비 정답이 없으며 '
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
