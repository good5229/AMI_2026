import 'package:flutter/material.dart';

class MunicipalOperationsEvidenceCard extends StatelessWidget {
  const MunicipalOperationsEvidenceCard({super.key});

  static const _regions = <_RegionEvidence>[
    _RegionEvidence(
      region: '대구',
      metric: '101,843건',
      role: '운영부담',
      detail: '고장 접수·처리, 반복 기록, 발견경로와 처리 tail',
      group: _EvidenceGroup.operations,
    ),
    _RegionEvidence(
      region: '부여',
      metric: '3,437건',
      role: '유형·반복',
      detail: '고장유형과 반복이력, 고정 운영점수 무재튜닝 평가',
      group: _EvidenceGroup.operations,
    ),
    _RegionEvidence(
      region: '울산 남구',
      metric: '1,060건',
      role: '업무 생애주기',
      detail: '접수→작업시작→완료와 위치자산 920/981 안전 연결',
      group: _EvidenceGroup.operations,
    ),
    _RegionEvidence(
      region: '양주',
      metric: '11,892건',
      role: '민원·재접수',
      detail: '운영 민원 규모와 90일 재접수 7.46%',
      group: _EvidenceGroup.discovery,
    ),
    _RegionEvidence(
      region: '인천 미추홀',
      metric: '34개월',
      role: '발견경로',
      detail: '월별 민원처리와 IoT 자체보수 업무 비중 28.06%',
      group: _EvidenceGroup.discovery,
    ),
    _RegionEvidence(
      region: '대전',
      metric: '43,082자산',
      role: '공간 배치',
      detail: '도시 규모 가로등 자산과 좌표 완전성 100%',
      group: _EvidenceGroup.asset,
    ),
    _RegionEvidence(
      region: '강릉',
      metric: '339분전함',
      role: '자산 계약',
      detail: '분전함·가로등·등용량 구조와 용량 완전성 99.63%',
      group: _EvidenceGroup.asset,
    ),
    _RegionEvidence(
      region: '성남',
      metric: '826분전함',
      role: '연결 규모',
      detail: '분전함별 등주·등 수를 통한 유지관리 대상 규모 확인',
      group: _EvidenceGroup.asset,
    ),
    _RegionEvidence(
      region: '충주',
      metric: '871분전함',
      role: '분전함 공간계약',
      detail: '분전함 식별자·연결 등주 수·좌표를 통한 적용 구조 확인',
      group: _EvidenceGroup.asset,
    ),
    _RegionEvidence(
      region: '군포',
      metric: '250분전함',
      role: '설치연도·공간계약',
      detail: '설치일·등주/등 수·좌표를 통한 자산 구성 확인',
      group: _EvidenceGroup.asset,
    ),
    _RegionEvidence(
      region: '통영',
      metric: '4,025자산',
      role: '기술 자산계약',
      detail: '개별 가로등·분전함 연결·기술 속성·좌표 구조 확인',
      group: _EvidenceGroup.asset,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Card(
      key: const Key('municipal-operations-evidence-card'),
      color: const Color(0xFFF2F5EF),
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
            Wrap(
              spacing: 8,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                const Icon(Icons.hub_outlined, color: Color(0xFF176B4D)),
                Text('지자체 적용 근거',
                    style: Theme.of(context).textTheme.titleLarge),
                const Chip(label: Text('11개 지역')),
              ],
            ),
            const SizedBox(height: 8),
            const Text(
              '전국에 동일한 모델 성능을 가정하지 않고, 지역별 가용 데이터에 맞춰 신호·운영·자산 계층을 분리 적용할 수 있는지 확인했습니다.',
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 16),
            LayoutBuilder(
              builder: (context, constraints) {
                final columns = constraints.maxWidth >= 720
                    ? 3
                    : constraints.maxWidth >= 480
                        ? 2
                        : 1;
                final width =
                    (constraints.maxWidth - (columns - 1) * 10) / columns;
                return Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    for (final region in _regions)
                      SizedBox(
                        width: width,
                        child: _RegionEvidenceTile(evidence: region),
                      ),
                  ],
                );
              },
            ),
            const SizedBox(height: 14),
            const Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _LayerChip(
                    label: '운영 이력', color: Color(0xFF176B4D)),
                _LayerChip(
                    label: '발견·민원', color: Color(0xFFB65D2E)),
                _LayerChip(
                    label: '공간·자산', color: Color(0xFF2A6F97)),
              ],
            ),
            const Divider(height: 26),
            const Text(
              '해석 한계 · 외부 지자체 기록은 운영 필요성과 적용 구조의 근거입니다. AMI 현장 고장 정답, 민원·비용·인력 감소, 실제 처리시간 단축을 입증하지 않습니다.',
              style: TextStyle(fontSize: 12, color: Color(0xFF14513B)),
            ),
            ],
          ),
        ),
      ),
    );
  }
}

enum _EvidenceGroup { operations, discovery, asset }

class _RegionEvidence {
  const _RegionEvidence({
    required this.region,
    required this.metric,
    required this.role,
    required this.detail,
    required this.group,
  });

  final String region;
  final String metric;
  final String role;
  final String detail;
  final _EvidenceGroup group;
}

class _RegionEvidenceTile extends StatelessWidget {
  const _RegionEvidenceTile({required this.evidence});

  final _RegionEvidence evidence;

  Color get _accent => switch (evidence.group) {
        _EvidenceGroup.operations => const Color(0xFF176B4D),
        _EvidenceGroup.discovery => const Color(0xFFB65D2E),
        _EvidenceGroup.asset => const Color(0xFF2A6F97),
      };

  @override
  Widget build(BuildContext context) => DecoratedBox(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border(left: BorderSide(color: _accent, width: 4)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(evidence.region,
                  style: const TextStyle(fontWeight: FontWeight.w700)),
              const SizedBox(height: 4),
              Text(evidence.metric,
                  style: Theme.of(context)
                      .textTheme
                      .headlineSmall
                      ?.copyWith(color: _accent, fontWeight: FontWeight.w800)),
              const SizedBox(height: 6),
              Text(evidence.role,
                  style: TextStyle(color: _accent, fontWeight: FontWeight.w700)),
              const SizedBox(height: 3),
              Text(evidence.detail, style: const TextStyle(fontSize: 12)),
            ],
          ),
        ),
      );
}

class _LayerChip extends StatelessWidget {
  const _LayerChip({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(999),
        ),
        child: Text(label,
            style: TextStyle(
                color: color, fontSize: 12, fontWeight: FontWeight.w700)),
      );
}
