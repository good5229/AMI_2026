import 'package:flutter/material.dart';

class V16CompetitionUtilityContract {
  const V16CompetitionUtilityContract._();

  static const status = '탐색 목표를 충족하지 못함';
  static const title = '공모전 목적과 3단계 업무 분류 기준 비교';
  static const officialObjective =
      '사업 적합성 · 개발 용이성 · 아이디어 구체성/완성도 · 활용목적 · 유형효과 · 범용성';
  static const assetScope = '공식 계량기 129개 중 가로등 계량기 5개 · 단상 2개 / 삼상 3개 · 모두 분석 가능';
  static const recovery = '검증용 이상 사례 전달 차이 -21.95%p · 목표 범위인 -10%p 이내를 충족하지 못함';
  static const benign = '검증용 정상 사례 전달 차이 -2.56%p · 목표 범위인 -10%p 이하를 충족하지 못함';
  static const decision =
      '현재 추가 확인 기준은 이상 사례 탐지를 지나치게 줄이는 반면 정상 사례의 불필요한 전달 감소는 작습니다. 같은 자료로 판정 기준을 추가 조정하지 않습니다.';
  static const nextExperiment =
      '2026-06-30 이후의 새로운 계절 전력자료와 별도로 수집한 담당자·현장 판정으로 향후 재검증이 필요합니다.';
  static const boundary =
      '이전 단계의 71개 조건 조합을 사후 재분석하고 일부 구간을 추가 탐색한 결과입니다. 독립적으로 수집한 자료의 검증, 현장 정확도, 실제 정상 오분류율, 고장 확률 또는 실제 절감액을 뜻하지 않습니다.';
}

class V16CompetitionUtilityCard extends StatelessWidget {
  const V16CompetitionUtilityCard({super.key});

  @override
  Widget build(BuildContext context) => Card(
        key: const Key('v16-competition-utility-card'),
        color: const Color(0xFFFFF1E8),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.alt_route, color: Color(0xFF9A3412)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(V16CompetitionUtilityContract.title,
                        style: Theme.of(context).textTheme.titleLarge),
                  ),
                  const Chip(label: Text(V16CompetitionUtilityContract.status)),
                ],
              ),
              const SizedBox(height: 10),
              const Text(V16CompetitionUtilityContract.officialObjective,
                  style: TextStyle(fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              const Text(V16CompetitionUtilityContract.assetScope),
              const SizedBox(height: 12),
              const _ResultLine(label: '이상 사례 탐지 결과', value: V16CompetitionUtilityContract.recovery),
              const _ResultLine(label: '정상 사례 구분 결과', value: V16CompetitionUtilityContract.benign),
              const Divider(height: 24),
              const Text(V16CompetitionUtilityContract.decision,
                  style: TextStyle(fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              const Text(V16CompetitionUtilityContract.nextExperiment),
              const SizedBox(height: 8),
              const Text(V16CompetitionUtilityContract.boundary,
                  style: TextStyle(fontSize: 12, color: Color(0xFF7C2D12))),
            ],
          ),
        ),
      );
}

class _ResultLine extends StatelessWidget {
  const _ResultLine({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 3),
        child: Text('$label · $value'),
      );
}
