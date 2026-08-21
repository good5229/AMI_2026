import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/repositories/lightguard_repository.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/models/region_config.dart';
import '../../data/models/context_models.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dataAsync = ref.watch(lightguardDataProvider);
    final events = ref.watch(competitionAmiEventsProvider).asData?.value ??
        const <ValidationEvent>[];
    final officialContext = ref.watch(officialContextProvider).asData?.value;
    final controlledMetrics =
        ref.watch(controlledMetricsProvider).asData?.value ??
            const <ControlledMetric>[];

    return dataAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (err, stack) => _error(context, '데이터 로드 실패: $err'),
      data: (data) {
        final region = ref.watch(selectedRegionProvider);
        final isCompact = MediaQuery.sizeOf(context).width < 600;
        final scenarioDetections = region.supportsScenarioInjection
            ? data.validationRows.where((row) => row.detectMatched).length
            : 0;
        final realMunicipalAmiMappings =
            data.objects.where((cabinet) => cabinet.ami.hasRealAmi).length;
        final excessKwh = events.fold<double>(
            0, (sum, event) => sum + event.estimatedExcessKwh);

        final cards = [
          _MetricCard(
              '총 분전함', '${data.objects.length}개', Icons.electrical_services),
          _MetricCard(
              '총 가로등 수', '${data.totalLampCount}개', Icons.lightbulb_outline),
          _MetricCard('총 정격용량',
              '${data.totalRatedLoadKw.toStringAsFixed(1)} kW', Icons.bolt),
          _MetricCard('정상', '${data.countByStatus(InspectionStatus.normal)}',
              Icons.check_circle_outline),
          _MetricCard('관찰', '${data.countByStatus(InspectionStatus.observe)}',
              Icons.remove_red_eye_outlined),
          _MetricCard(
              '점검 권고',
              '${data.countByStatus(InspectionStatus.inspectionRecommended)}',
              Icons.warning_amber_rounded),
          _MetricCard(
              '우선 점검',
              '${data.countByStatus(InspectionStatus.priorityInspection)}',
              Icons.error_outline),
        ];

        final today = data.objects.isNotEmpty ? data.objects.first : null;

        return LightguardShell(
          title: 'LightGuard Dashboard · ${region.label}',
          actions: [
            if (today != null && !isCompact)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: StatusBadge(
                    type: BadgeType.validation, label: region.branchLabel),
              ),
          ],
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                StatusBadge(
                    type: BadgeType.validation, label: region.branchLabel),
                const SizedBox(height: 10),
                Wrap(spacing: 12, runSpacing: 12, children: cards),
                Padding(
                  padding: const EdgeInsets.fromLTRB(4, 4, 4, 12),
                  child: Text(region.modeDescription),
                ),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _MiniPill(
                        label:
                            '우선점검 ${data.countByStatus(InspectionStatus.priorityInspection)}개'),
                    _MiniPill(
                        label:
                            '점검권고 ${data.countByStatus(InspectionStatus.inspectionRecommended)}개'),
                    _MiniPill(
                        label:
                            '관찰 ${data.countByStatus(InspectionStatus.observe)}개'),
                    _MiniPill(
                        label:
                            '정상 ${data.countByStatus(InspectionStatus.normal)}개'),
                  ],
                ),
                const SizedBox(height: 12),
                Text('검증 자산을 섞지 않고 표시합니다',
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    _EvidenceMetricCard(
                      label: '실제 공공자산',
                      value: '${data.objects.length}개 분전함',
                      detail: '${region.label} 자산 데이터',
                      icon: Icons.location_city_outlined,
                    ),
                    _EvidenceMetricCard(
                      key: const Key('dashboard-scenario-count'),
                      label: 'Scenario validation',
                      value: '$scenarioDetections건',
                      detail: region.supportsScenarioInjection
                          ? 'controlled scenario 재현 검출'
                          : '지원하지 않는 모드',
                      icon: Icons.science_outlined,
                    ),
                    _EvidenceMetricCard(
                      key: const Key('dashboard-actual-ami-count'),
                      label: '실제 공모전 AMI',
                      value: '${events.length}건',
                      detail:
                          '현장 미확인 점검 후보 · ${excessKwh.toStringAsFixed(3)} kWh',
                      icon: Icons.bolt_outlined,
                    ),
                    _EvidenceMetricCard(
                      key: const Key('dashboard-municipal-ami-count'),
                      label: '실제 지자체 AMI 연결',
                      value: '$realMunicipalAmiMappings개',
                      detail: '분전함 ID 매핑 미구축',
                      icon: Icons.link_off_outlined,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _OfficialContextCard(
                  contextBundle: officialContext,
                  metrics: controlledMetrics,
                ),
                const SizedBox(height: 12),
                const _SecondCheckerCard(),
                const SizedBox(height: 12),
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.schedule),
                    title: const Text('기준일 기준 점등/소등'),
                    subtitle: Text(
                      today == null
                          ? '데이터 없음'
                          : '${today.expectedSchedule.date.isNotEmpty ? today.expectedSchedule.date : '일자 미제공'} 기준 · 점등 ${today.expectedSchedule.sunset} / 소등 ${today.expectedSchedule.sunrise}',
                    ),
                    trailing: ElevatedButton(
                      onPressed: () => context.go('/map'),
                      child: const Text('지도에서 보기'),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.list),
                    title: const Text('점검 우선순위 보기'),
                    onTap: () => context.go('/inspections'),
                    trailing: const Icon(Icons.chevron_right),
                  ),
                ),
                const SizedBox(height: 8),
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.bug_report_outlined),
                    title: const Text('실제 AMI 검증 사례 보기'),
                    onTap: () => context.go('/ami-events'),
                    trailing: const Icon(Icons.chevron_right),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _error(BuildContext context, String msg) {
    return Scaffold(
      appBar: AppBar(title: const Text('LightGuard Dashboard')),
      body: Center(
        child: Text(msg),
      ),
    );
  }
}

class _OfficialContextCard extends StatelessWidget {
  const _OfficialContextCard({
    required this.contextBundle,
    required this.metrics,
  });

  final OfficialContextBundle? contextBundle;
  final List<ControlledMetric> metrics;

  @override
  Widget build(BuildContext context) {
    final solar = contextBundle?.firstOfficialSolar;
    final weather = contextBundle?.firstOfficialWeather;
    final m0 = metrics.where((row) => row.model == 'M0').firstOrNull;
    final m3 = metrics.where((row) => row.model == 'M3').firstOrNull;
    return Card(
      key: const Key('dashboard-official-context'),
      color: const Color(0xFFF0F6F1),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('공식 Context · Controlled Validation',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 10),
            Wrap(spacing: 18, runSpacing: 8, children: [
              Text(solar == null
                  ? '천문 Context: KASI 미수집'
                  : '천문 Context: KASI ${solar['date']} · ${solar['sunrise']} / ${solar['sunset']}'),
              Text(weather == null
                  ? '기상 Context: KMA ASOS 159 미수집'
                  : '기상 Context: KMA ASOS 159 · ${weather['timestamp']}'),
            ]),
            const SizedBox(height: 8),
            Text(
              'AMI-only FPR ${_percent(m0?.normalFpr)} · Context-aware FPR ${_percent(m3?.normalFpr)} · Top-20 precision ${_percent(m3?.precisionAt20)}',
            ),
            if (m3?.status != 'available')
              const Padding(
                padding: EdgeInsets.only(top: 6),
                child: Text('공식 Context 미수집으로 M1-M3는 unavailable이며 내부/합성값으로 대체하지 않습니다.',
                    style: TextStyle(fontSize: 12, color: Color(0xFF795548))),
              ),
          ],
        ),
      ),
    );
  }

  String _percent(double? value) =>
      value == null ? 'unavailable' : '${(value * 100).toStringAsFixed(1)}%';
}

class _EvidenceMetricCard extends StatelessWidget {
  const _EvidenceMetricCard({
    super.key,
    required this.label,
    required this.value,
    required this.detail,
    required this.icon,
  });

  final String label;
  final String value;
  final String detail;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 250,
      child: Card(
        color: const Color(0xFFF7FAFC),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Icon(icon, size: 18),
                const SizedBox(width: 7),
                Expanded(child: Text(label))
              ]),
              const SizedBox(height: 8),
              Text(value, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 4),
              Text(detail, style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        ),
      ),
    );
  }
}

class _SecondCheckerCard extends StatelessWidget {
  const _SecondCheckerCard();

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFFEAF3F8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('기존 관제를 교체하지 않는 Second Checker',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 10),
            const Wrap(
              spacing: 8,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                _FlowPill('제어상태'),
                Text('+'),
                _FlowPill('AMI 실제 전력'),
                Text('+'),
                _FlowPill('자산 기대부하'),
                Text('+'),
                _FlowPill('운전시간 context'),
                Icon(Icons.arrow_forward),
                _FlowPill('상태 불일치 · 점검 우선순위'),
              ],
            ),
            const SizedBox(height: 10),
            const Text(
                '기존 원격제어시스템을 교체하지 않고, 이미 설치된 AMI를 실제 전력 상태를 확인하는 독립 검증 수단으로 추가합니다.'),
          ],
        ),
      ),
    );
  }
}

class _FlowPill extends StatelessWidget {
  const _FlowPill(this.label);

  final String label;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFF9CB7C9)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
        child: Text(label,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard(this.title, this.value, this.icon);

  final String title;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 210,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Icon(icon),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: Theme.of(context).textTheme.labelMedium),
                    const SizedBox(height: 6),
                    Text(value, style: Theme.of(context).textTheme.titleLarge),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MiniPill extends StatelessWidget {
  const _MiniPill({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: Colors.black12),
        borderRadius: BorderRadius.circular(999),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      child: Text(label, style: const TextStyle(fontSize: 12)),
    );
  }
}
