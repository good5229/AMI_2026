import 'package:flutter/material.dart';

class V15MechanismDisclosure {
  const V15MechanismDisclosure({
    required this.name,
    required this.status,
    required this.scope,
  });

  final String name;
  final String status;
  final String scope;
}

class V15TargetMechanismContract {
  const V15TargetMechanismContract._();

  static const title = 'v0.15 대상 도메인 메커니즘 기여 검증';
  static const status = 'COMPLETED_MIXED_RESULT';
  static const freeze =
      'v0.10–v0.14 freeze 보존 · H1 runtime 경로와 threshold 변경 없음';
  static const claimBoundary =
      '71개 target-domain pair의 통제 결과이며 가로등 현장 정확도, real FPR/specificity, 고장 확률, 일반 anomaly 성능을 의미하지 않습니다.';
  static const naturalShadow =
      'Natural shadow는 truth 미확보 상태의 진단 기록이며 성능 평가가 아닙니다.';
  static const canonicalSix =
      'Canonical six는 diagnostic coverage만 허용하며 truth/recall 판정에 사용하지 않습니다.';

  static const disclosures = <V15MechanismDisclosure>[
    V15MechanismDisclosure(
      name: 'New disjoint holdout',
      status: '71_PAIRS_COMPLETED',
      scope: 'v0.10 pool 및 canonical-six buffer overlap 0',
    ),
    V15MechanismDisclosure(
      name: 'Same-threshold runtime ablation',
      status: 'COMPLETED',
      scope: '활성 runtime mechanism만 제거했고 H1 threshold는 동일하게 유지',
    ),
    V15MechanismDisclosure(
      name: 'Anomaly / controlled-benign pair',
      status: 'MIXED_A5_RESULT',
      scope: 'A5는 recovery 기여 신호와 controlled-benign adverse escalation을 동시에 보임',
    ),
    V15MechanismDisclosure(
      name: 'Robust-z comparator',
      status: 'SECONDARY_ONLY',
      scope: 'H1을 대체하지 않는 비교군이며 운영 우월성을 입증하지 않음',
    ),
    V15MechanismDisclosure(
      name: 'Natural shadow',
      status: 'TRUTH_FREE_COMPLETED',
      scope: '현장 truth 없는 candidate/diagnostic trace만 표시',
    ),
    V15MechanismDisclosure(
      name: 'External v0.13 / v0.14 evidence',
      status: 'FAILURE_PRESERVED',
      scope: 'v0.13 negative/non-evaluable 및 v0.14 외부 제한 결과를 보존',
    ),
  ];
}

class V15TargetMechanismCard extends StatelessWidget {
  const V15TargetMechanismCard({super.key});

  @override
  Widget build(BuildContext context) => Card(
        key: const Key('v15-target-mechanism-card'),
        color: const Color(0xFFF1EEE5),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.rule_folder_outlined,
                      color: Color(0xFF7A5325)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      V15TargetMechanismContract.title,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ),
                  const Chip(
                    label: Text(V15TargetMechanismContract.status),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                V15TargetMechanismContract.freeze,
                style: TextStyle(fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 14),
              for (final disclosure in V15TargetMechanismContract.disclosures)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${disclosure.name} · ${disclosure.status}',
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                      Text(disclosure.scope,
                          style: const TextStyle(fontSize: 12)),
                    ],
                  ),
                ),
              const Divider(height: 20),
              const Text(
                V15TargetMechanismContract.naturalShadow,
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 6),
              const Text(
                V15TargetMechanismContract.canonicalSix,
                style: TextStyle(fontSize: 12),
              ),
              const SizedBox(height: 6),
              const Text(
                V15TargetMechanismContract.claimBoundary,
                style: TextStyle(fontSize: 12, color: Color(0xFF6B4D00)),
              ),
            ],
          ),
        ),
      );
}
