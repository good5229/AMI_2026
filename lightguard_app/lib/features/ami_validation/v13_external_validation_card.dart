import 'dart:convert';

import 'package:flutter/material.dart';
import '../../core/presentation/plain_status.dart';

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
                        child: Text('외부 정답 포함 전력자료로 판정 방식 검증',
                            style: Theme.of(context).textTheme.titleLarge),
                      ),
                      const Chip(label: Text('외부자료 검증 결과')),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '고장 정답이 포함된 외부 전력자료는 전력 신호 판정 방식이 다른 자료에서도 작동하는지만 확인합니다.',
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
                      _Metric('내부 전력계량 자료', plainStatusLabel(data['internal_ami_observation'])),
                      _Metric('간접 기준 일치 여부', plainStatusLabel(data['h1_proxy_status'])),
                      _Metric('Human review', '${data['human_review_status']}'),
                      _Metric('Field confirmation', '${data['field_confirmation']}'),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Text('변경하지 않은 LightGuard 전력 신호 판정 기준',
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
                    '현재 값은 검증 전 임시 표시값이며, 간접적으로 만든 분류값을 외부 고장 확정자료로 사용하지 않습니다.',
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
