import 'package:flutter/material.dart';

class NationwideFileCensusCard extends StatelessWidget {
  const NationwideFileCensusCard({super.key});

  static const topLevelCoverage = 16;
  static const analyzableRegionCount = 83;
  static const municipalDatasetCount = 125;

  @override
  Widget build(BuildContext context) {
    return Card(
      key: const Key('nationwide-file-census-card'),
      color: const Color(0xFFF3F7F2),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '전국 공개파일 구조 조사',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        '공공데이터포털의 가로등·보안등 관련 파일을 수집해 지역별 활용 가능 필드를 확인했습니다.',
                        style: TextStyle(fontSize: 12, height: 1.45),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0xFFDCEBDD),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: const Text(
                    'v0.24 검수 통과',
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            const Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                _CensusMetric(
                  value: '16 / 16',
                  label: '현재 광역단위 포함',
                ),
                _CensusMetric(
                  value: '83개',
                  label: '분석 가능 지역 라벨',
                ),
                _CensusMetric(
                  value: '125개',
                  label: '지자체 범위 데이터셋',
                ),
              ],
            ),
            const SizedBox(height: 14),
            const Text(
              '확인 가능한 데이터 범위',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            const Wrap(
              spacing: 6,
              runSpacing: 6,
              children: [
                _RoleChip(label: '전력·상태 신호'),
                _RoleChip(label: '고장·정비 이력'),
                _RoleChip(label: '분전함 정보'),
                _RoleChip(label: '정격·부하 정보'),
                _RoleChip(label: '위치 정보'),
                _RoleChip(label: '시설물 정보'),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              '해석 기준: 전국 적용에 필요한 데이터 구조의 존재를 확인한 결과입니다. '
              '모든 지역에서 동일한 탐지 성능이나 운영 효과가 입증됐다는 의미는 아닙니다. '
              '실제 적용 시에는 지역별 데이터 품질과 연결키를 별도로 검증합니다.',
              style: TextStyle(fontSize: 12, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}

class _CensusMetric extends StatelessWidget {
  const _CensusMetric({required this.value, required this.label});

  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 180,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFC8D8C8)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            value,
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 2),
          Text(label, style: const TextStyle(fontSize: 12)),
        ],
      ),
    );
  }
}

class _RoleChip extends StatelessWidget {
  const _RoleChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
      decoration: BoxDecoration(
        color: const Color(0xFFE7EFE6),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(label, style: const TextStyle(fontSize: 11)),
    );
  }
}
