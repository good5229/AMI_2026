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

  static const title = '다른 조건에서 판정 요소의 영향 비교';
  static const status = '일부 조건에서만 효과 확인';
  static const freeze =
      '이전 검증 단계의 판정 기준을 유지했으며 실행 경로와 판정 한계값을 바꾸지 않았습니다.';
  static const claimBoundary =
      '71개 대상 조건 조합을 비교한 결과이며 가로등 현장 정확도, 실제 정상 오분류율, 고장 확률 또는 모든 이상 유형의 성능을 의미하지 않습니다.';
  static const naturalShadow =
      '실제 자료 관찰 구간에는 현장 정답이 없으므로 진단 기록으로만 사용하며 성능 평가에는 사용하지 않습니다.';
  static const canonicalSix =
      '대표 6개 구간은 판정 동작 확인에만 사용하며 현장 정답이나 탐지율 계산에는 사용하지 않습니다.';

  static const disclosures = <V15MechanismDisclosure>[
    V15MechanismDisclosure(
      name: '새로 분리한 검증자료',
      status: '71개 조건 조합 확인 완료',
      scope: '이전 기준 설정 자료 및 대표 6개 구간과 중복 없음',
    ),
    V15MechanismDisclosure(
      name: '동일 판정 기준에서 구성요소별 영향 비교',
      status: '비교 완료',
      scope: '비교할 구성요소만 제거하고 판정 한계값은 동일하게 유지',
    ),
    V15MechanismDisclosure(
      name: '이상 사례와 정상 사례 비교',
      status: '조건에 따라 결과가 다름',
      scope: '한 구성요소가 이상 사례 탐지에는 도움이 됐지만 일부 정상 사례의 우선순위도 높였습니다.',
    ),
    V15MechanismDisclosure(
      name: '보조 통계 기준과 비교',
      status: '참고용 결과',
      scope: '기본 판정 기준을 대체하지 않는 비교이며 운영상 우월성을 입증하지 않습니다.',
    ),
    V15MechanismDisclosure(
      name: '실제 자료 관찰 구간',
      status: '현장 정답 없이 확인 완료',
      scope: '현장 정답이 없어 확인 후보와 판정 과정만 표시합니다.',
    ),
    V15MechanismDisclosure(
      name: '외부자료 검증 근거',
      status: '개선 효과 확인 안 됨',
      scope: '분석 불가 또는 개선 효과가 없었던 외부자료 결과도 그대로 공개합니다.',
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
