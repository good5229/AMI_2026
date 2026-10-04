import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../app/theme/app_theme.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../core/storage/inspection_outcome_storage.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/repositories/lightguard_repository.dart';
import '../../data/models/region_config.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final region = ref.watch(selectedRegionProvider);
    return ref.watch(lightguardDataProvider).when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (_, __) => const Scaffold(body: Center(child: Text('자산자료를 불러오지 못했습니다.'))),
      data: (data) => LightguardShell(
        title: '지역 자산',
        child: ListView(padding: const EdgeInsets.all(16), children: [
          Card(color: AppTheme.ink, child: Padding(
            padding: const EdgeInsets.all(22),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(region.label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
              const SizedBox(height: 12),
              Text('전력 상태 미관측', style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: Colors.white)),
              const SizedBox(height: 8),
              const Text('AMI 미연결 · 현재 정상/이상 여부를 판단할 수 없습니다.', style: TextStyle(color: Color(0xFFD5DFDF))),
              const SizedBox(height: 18),
              Wrap(spacing: 12, runSpacing: 10, children: [
                FilledButton.icon(onPressed: () => context.go('/ami-events'), icon: const Icon(Icons.insights_outlined), label: const Text('실제 AMI 기록 분석')),
                OutlinedButton.icon(style: OutlinedButton.styleFrom(foregroundColor: Colors.white), onPressed: () => context.go('/map'), icon: const Icon(Icons.map_outlined), label: const Text('자산 지도')),
              ]),
            ]),
          )),
          const SizedBox(height: 14),
          Text('공개 자산자료', style: Theme.of(context).textTheme.titleLarge),
          Text('자료 묶음 생성 ${data.generatedAt.toIso8601String().split('T').first} · 실시간 자료 아님'),
          const SizedBox(height: 10),
          LayoutBuilder(builder: (context, constraints) {
            final columns = constraints.maxWidth >= 900 ? 4 : constraints.maxWidth >= 600 ? 2 : 1;
            final width = (constraints.maxWidth - (columns - 1) * 12) / columns;
            final metrics = <(String, String)>[
              ('등록 분전함', '${data.objects.length}개'),
              ('연결 가로등', '${data.totalLampCount}등'),
              ('조명 합산 정격용량', data.totalRatedLoadKw > 0 ? '${data.totalRatedLoadKw.toStringAsFixed(1)} kW' : '자료 미제공'),
              ('미관측', '${data.countByStatus(InspectionStatus.dataCheckRequired)}개'),
            ];
            return Wrap(spacing: 12, runSpacing: 12, children: [for (final metric in metrics)
              SizedBox(width: width, child: Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(metric.$1), const SizedBox(height: 8), Text(metric.$2, style: Theme.of(context).textTheme.titleLarge)])))),
            ]);
          }),
          const SizedBox(height: 14),
          _FieldRecords(data: data),
          const SizedBox(height: 14),
          const _PublicAssetCoverageCard(),
        ]),
      ),
    );
  }
}

class _FieldRecords extends StatefulWidget {
  const _FieldRecords({required this.data});
  final LightguardData data;
  @override
  State<_FieldRecords> createState() => _FieldRecordsState();
}
class _FieldRecordsState extends State<_FieldRecords> {
  late final Future<Map<String, Map<String, String>>> records = loadInspectionOutcomes();
  @override
  Widget build(BuildContext context) => Card(child: Padding(
    padding: const EdgeInsets.all(18),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text('직접 점검과 기록', style: Theme.of(context).textTheme.titleLarge),
      const SizedBox(height: 8),
      const Text('담당자 배정과 현장 확인 결과를 기록할 수 있습니다. 자동 탐지 순위는 제공하지 않습니다.'),
      FutureBuilder<Map<String, Map<String, String>>>(future: records, builder: (context, snapshot) {
        if (snapshot.hasError) return const Text('기기 기록을 불러오지 못했습니다.');
        if (!snapshot.hasData) return const Text('기기 기록을 불러오는 중');
        final own = inspectionOutcomesForCases(snapshot.data!, widget.data.objects.map((c) => c.cabinetUid));
        final count = own.values.where((r) => (r['outcomeCode'] ?? '').isNotEmpty).length;
        return Text('결과 입력 $count건 · 이 기기에 저장된 기록');
      }),
      const SizedBox(height: 10),
      FilledButton(onPressed: () => context.go('/inspections?filter=all'), child: const Text('자산·점검 기록 열기')),
    ]),
  ));
}

class _PublicAssetCoverageCard extends StatelessWidget {
  const _PublicAssetCoverageCard();

  static const _regions = <(String, String, String)>[
    ('진주', '자산 12,107 · 분전함 키 807', '분전함 키 일치 100%'),
    ('구미', '분전함 1,046 · 계기번호 94.9%', '계기번호 기재율'),
    ('아산', '자산 17,755 · 분전함 1,136', '분전함 ID 일치 0건'),
    ('충주', '자산 18,897 · 분전함 871', '공개 연결키 없음'),
  ];

  @override
  Widget build(BuildContext context) {
    return Card(
      key: const Key('public-asset-coverage-card'),
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text('공개 자산자료 적용 현황',
                      style: Theme.of(context).textTheme.titleLarge),
                ),
                const StatusBadge(
                    type: BadgeType.validation, label: '4개 지역 자산 변환'),
              ],
            ),
            const SizedBox(height: 4),
            Text('2026-10-03 공개파일 기준 · 기관 협조 없이 변환·연결 검토 완료',
                style: Theme.of(context).textTheme.bodySmall),
            const Divider(height: 20),
            for (var index = 0; index < _regions.length; index++) ...[
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 42,
                      child: Text(_regions[index].$1,
                          style: const TextStyle(fontWeight: FontWeight.w800)),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(_regions[index].$2,
                              style:
                                  const TextStyle(fontWeight: FontWeight.w700)),
                          const SizedBox(height: 2),
                          Text('${_regions[index].$3} · 시간대별 AMI 미공개',
                              style: Theme.of(context).textTheme.bodySmall),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              if (index < _regions.length - 1) const Divider(height: 1),
            ],
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.surfaceMuted,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Text(
                '적용 완료는 공개 자산자료를 공통 구조로 변환했다는 뜻입니다. 실제 AMI 고장 탐지 정확도 검증은 아닙니다.',
                style: TextStyle(fontWeight: FontWeight.w700),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

