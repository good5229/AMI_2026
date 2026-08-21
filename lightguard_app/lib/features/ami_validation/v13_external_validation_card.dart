import 'dart:convert';

import 'package:flutter/material.dart';

class V13ExternalValidationCard extends StatelessWidget {
  const V13ExternalValidationCard({super.key});

  @override
  Widget build(BuildContext context) => Card(
        key: const Key('v13-external-validation-card'),
        color: const Color(0xFFE8F0F4),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: FutureBuilder<String>(
            future: DefaultAssetBundle.of(context).loadString(
              'assets/data/context/v13_external_validation_summary.json',
            ),
            builder: (context, snapshot) {
              if (!snapshot.hasData) return const LinearProgressIndicator();
              final data = jsonDecode(snapshot.data!) as Map<String, dynamic>;
              final primary = data['primary_dataset'] as Map<String, dynamic>;
              final secondary = (data['secondary_datasets'] as List<dynamic>)
                  .cast<Map<String, dynamic>>();
              final mechanisms = (data['signal_mechanisms'] as List<dynamic>)
                  .cast<Map<String, dynamic>>();

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.compare_arrows_outlined,
                          color: Color(0xFF1B647A)),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text('v0.13 외부 라벨 AMI 메커니즘 검증',
                            style: Theme.of(context).textTheme.titleLarge),
                      ),
                      Chip(label: Text('${data['status']}')),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '외부 라벨 전기/AMI benchmark는 signal-mechanism external validity만 지지합니다.',
                    style: TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    '이는 streetlight field accuracy 또는 actual fault probability를 의미하지 않습니다.',
                    style: TextStyle(fontSize: 12),
                  ),
                  const SizedBox(height: 14),
                  Wrap(
                    spacing: 20,
                    runSpacing: 12,
                    children: [
                      _Metric('Primary benchmark', '${primary['dataset_id']}'),
                      _Metric('External EV grade', '${data['external_ev_grade']}'),
                      _Metric('Literature grade', '${data['literature_grade']}'),
                      _Metric('Internal AMI', '${data['internal_ami_observation']}'),
                      _Metric('H1 / Proxy', '${data['h1_proxy_status']}'),
                      _Metric('Human review', '${data['human_review_status']}'),
                      _Metric('Field confirmation', '${data['field_confirmation']}'),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Text('고정된 LightGuard Signal Core',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 6),
                  for (final mechanism in mechanisms)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Text(
                        '${mechanism['id']} · ${mechanism['label']} · ${mechanism['external_ev_grade']}',
                        style: const TextStyle(fontSize: 12),
                      ),
                    ),
                  const SizedBox(height: 10),
                  Text('보조 데이터셋 상태',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 6),
                  for (final dataset in secondary)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Text(
                        '${dataset['dataset_id']} · ${dataset['status']} · ${dataset['reason']}',
                        style: const TextStyle(fontSize: 12),
                      ),
                    ),
                  const SizedBox(height: 10),
                  const Text(
                    '외부 데이터의 라벨·라이선스·분할 조건이 확인되기 전에는 성능 수치를 생성하지 않습니다. '
                    '현재 값은 검증 전 placeholder이며, pseudo-label은 외부 Gold로 사용하지 않습니다.',
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
        width: 156,
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
