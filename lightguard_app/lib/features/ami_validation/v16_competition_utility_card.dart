import 'package:flutter/material.dart';

class V16CompetitionUtilityContract {
  const V16CompetitionUtilityContract._();

  static const status = 'EXPLORATORY_TARGETS_FAILED';
  static const title = 'v0.16 공모전 목적 정렬 · 3-lane 업무 정책';
  static const officialObjective =
      '사업 적합성 · 개발 용이성 · 아이디어 구체성/완성도 · 활용목적 · 유형효과 · 범용성';
  static const assetScope = '공식 129개 계기 중 가로등 5개 · 단상 2 / 삼상 3 · 모두 evaluable';
  static const recovery = 'Controlled anomaly dispatch RD: -21.95%p · 미래 목표 -10%p 이내 실패';
  static const benign = 'Controlled benign dispatch RD: -2.56%p · 미래 목표 -10%p 이하 실패';
  static const decision =
      '현재 confirmation gate는 recovery를 과도하게 줄이면서 benign dispatch 감소는 작습니다. 같은 corpus에서 추가 tuning하지 않습니다.';
  static const nextExperiment =
      '2026-06-30 이후 신규 계절 AMI와 분리된 운영자/현장 판정으로 prospective confirmatory 검증이 필요합니다.';
  static const boundary =
      'v0.15 71쌍 post-hoc replay와 B-L-12 탐색 extension입니다. 독립검증, 현장 정확도, real FPR, 고장 확률, 실제 절감액이 아닙니다.';
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
              const _ResultLine(label: 'Recovery', value: V16CompetitionUtilityContract.recovery),
              const _ResultLine(label: 'Benign', value: V16CompetitionUtilityContract.benign),
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
