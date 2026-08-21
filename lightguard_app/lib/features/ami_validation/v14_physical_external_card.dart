import 'package:flutter/material.dart';

class V14DatasetClaim {
  const V14DatasetClaim({
    required this.name,
    required this.status,
    required this.scope,
  });

  final String name;
  final String status;
  final String scope;
}

class V14PhysicalExternalContract {
  const V14PhysicalExternalContract._();

  static const title = 'v0.14 물리 출처 외부 재현 검증';
  static const status = 'SUITABILITY_GATED';
  static const v13Freeze =
      'v0.13 MAD 결과 보존: negative / NOT_EVALUABLE_INCOMPLETE_COVERAGE';
  static const pmc3 =
      'PMC-3 unavailable: 검증 가능한 3상 동기 채널과 위상 정보가 없습니다.';
  static const claimBoundary =
      '외부 결과는 물리 신호 메커니즘의 제한적 재현만 설명하며, 가로등 현장 정확도 또는 실제 고장 확률을 의미하지 않습니다.';

  static const datasets = <V14DatasetClaim>[
    V14DatasetClaim(
      name: 'London Met',
      status: 'PRIMARY_BLOCKED_PROVENANCE',
      scope: '라이선스·라벨·측정 출처 확인 전 성능 평가 보류',
    ),
    V14DatasetClaim(
      name: 'CoDEx-VFD',
      status: 'CONTROLLED_MECHANISM_ONLY',
      scope: '통제된 VFD/EMI 전류 메커니즘 검증만 허용',
    ),
    V14DatasetClaim(
      name: 'SustDataED2',
      status: 'TRANSITION_POSITIVE_CONTROL_ONLY',
      scope: '기기 전환 persistence/change positive control만 허용',
    ),
    V14DatasetClaim(
      name: '3PhaseInsight',
      status: 'REFERENCE_ONLY',
      scope: '물리 데이터 모델 참고용이며 성능 benchmark에서 제외',
    ),
  ];
}

class V14PhysicalExternalCard extends StatelessWidget {
  const V14PhysicalExternalCard({super.key});

  @override
  Widget build(BuildContext context) => Card(
        key: const Key('v14-physical-external-card'),
        color: const Color(0xFFF1EEE5),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.science_outlined,
                      color: Color(0xFF7A5325)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      V14PhysicalExternalContract.title,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ),
                  const Chip(
                    label: Text(V14PhysicalExternalContract.status),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                V14PhysicalExternalContract.v13Freeze,
                style: TextStyle(fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 14),
              for (final dataset in V14PhysicalExternalContract.datasets)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${dataset.name} · ${dataset.status}',
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                      Text(dataset.scope,
                          style: const TextStyle(fontSize: 12)),
                    ],
                  ),
                ),
              const Divider(height: 20),
              const Text(
                V14PhysicalExternalContract.pmc3,
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 6),
              const Text(
                V14PhysicalExternalContract.claimBoundary,
                style: TextStyle(fontSize: 12, color: Color(0xFF6B4D00)),
              ),
            ],
          ),
        ),
      );
}
