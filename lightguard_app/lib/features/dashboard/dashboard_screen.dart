import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../app/theme/app_theme.dart';
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
              '우선 확인 필요',
              '${data.countByStatus(InspectionStatus.priorityInspection)}',
              Icons.error_outline),
          _MetricCard(
              '현장 확인 권고',
              '${data.countByStatus(InspectionStatus.inspectionRecommended)}',
              Icons.warning_amber_rounded),
          _MetricCard('추적 관찰', '${data.countByStatus(InspectionStatus.observe)}',
              Icons.remove_red_eye_outlined),
          _MetricCard('정상 범위', '${data.countByStatus(InspectionStatus.normal)}',
              Icons.check_circle_outline),
          _MetricCard(
              '총 분전함', '${data.objects.length}개', Icons.electrical_services),
          _MetricCard(
              '총 가로등 수', '${data.totalLampCount}개', Icons.lightbulb_outline),
          _MetricCard('총 정격용량',
              '${data.totalRatedLoadKw.toStringAsFixed(1)} kW', Icons.bolt),
        ];

        final today = data.objects.isNotEmpty ? data.objects.first : null;

        return LightguardShell(
          title: 'LightGuard · 운영 현황',
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
                _DashboardHero(
                  region: region,
                  priorityCount: data
                      .countByStatus(InspectionStatus.priorityInspection),
                  recommendedCount: data
                      .countByStatus(InspectionStatus.inspectionRecommended),
                  onInspect: () => context.go('/inspections'),
                  onMap: () => context.go('/map'),
                ),
                const SizedBox(height: 18),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: Text('자산 및 점검 현황',
                      style: Theme.of(context).textTheme.titleLarge),
                ),
                const SizedBox(height: 8),
                Wrap(spacing: 12, runSpacing: 12, children: cards),
                const SizedBox(height: 22),
                Text('자료 구분 및 활용 범위',
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    _EvidenceMetricCard(
                      label: '지자체 공공자산 정보',
                      value: '${data.objects.length}개 분전함',
                      detail: '${region.label} 자산 데이터',
                      icon: Icons.location_city_outlined,
                    ),
                    _EvidenceMetricCard(
                      key: const Key('dashboard-scenario-count'),
                      label: '검증용 모의 신호',
                      value: '$scenarioDetections건',
                      detail: region.supportsScenarioInjection
                          ? '사전 정의 시나리오 탐지 결과'
                          : '해당 지역은 모의 신호 검증 미적용',
                      icon: Icons.science_outlined,
                    ),
                    _EvidenceMetricCard(
                      key: const Key('dashboard-actual-ami-count'),
                      label: '가명 처리 전력계량 자료 분석',
                      value: '${events.length}건',
                      detail:
                          '현장 확인 전 분석 후보 · 추정 초과사용량 ${excessKwh.toStringAsFixed(3)} kWh',
                      icon: Icons.bolt_outlined,
                    ),
                    _EvidenceMetricCard(
                      key: const Key('dashboard-municipal-ami-count'),
                      label: '지자체 전력계량 자료 연결 상태',
                      value: '$realMunicipalAmiMappings개',
                      detail: '분전함 식별자 연계 정보 없음',
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
                  color: const Color(0xFFE8F3EE),
                  child: ListTile(
                    leading: const Icon(Icons.public_outlined,
                        color: Color(0xFF176B4D)),
                    title: const Text('7개 지역 운영·확장 근거'),
                    subtitle: const Text(
                      '대구·부여·울산 남구·양주·미추홀·대전·강릉의 공개데이터로 운영 필요성과 지역별 적용 경로를 확인했습니다.',
                    ),
                    onTap: () => context.go('/ami-events'),
                    trailing: const Icon(Icons.chevron_right),
                  ),
                ),
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
                    title: const Text('전력계량 자료 분석 사례 보기'),
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
      appBar: AppBar(title: const Text('LightGuard 운영 현황')),
      body: Center(
        child: Text(msg),
      ),
    );
  }
}

class _DashboardHero extends StatelessWidget {
  const _DashboardHero({
    required this.region,
    required this.priorityCount,
    required this.recommendedCount,
    required this.onInspect,
    required this.onMap,
  });

  final RegionId region;
  final int priorityCount;
  final int recommendedCount;
  final VoidCallback onInspect;
  final VoidCallback onMap;

  @override
  Widget build(BuildContext context) => Card(
        clipBehavior: Clip.antiAlias,
        margin: const EdgeInsets.fromLTRB(0, 4, 0, 8),
        child: DecoratedBox(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF102A43), Color(0xFF0F5D59)],
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.all(22),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    const Icon(Icons.bolt_rounded,
                        color: Color(0xFFF7C948), size: 20),
                    Text(region.label,
                        style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w800)),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 9, vertical: 5),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(999),
                      ),
                      child: Text(region.branchLabel,
                          style: const TextStyle(
                              color: Color(0xFFD9F4EE), fontSize: 11)),
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                Text('오늘 우선 확인이 필요한 분전함 $priorityCount건',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w900,
                        height: 1.18)),
                const SizedBox(height: 8),
                Text(
                  '현장 확인 권고 $recommendedCount건의 관측 사유와 전력 신호를 확인하고, 현장 출동 전에 원격 확인 대상을 선별합니다.',
                  style: const TextStyle(
                      color: Color(0xFFD8E7E5), height: 1.5),
                ),
                const SizedBox(height: 18),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    FilledButton.icon(
                      onPressed: onInspect,
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFFF7C948),
                        foregroundColor: AppTheme.ink,
                      ),
                      icon: const Icon(Icons.fact_check_outlined, size: 19),
                      label: const Text('확인 대상 및 사유 보기'),
                    ),
                    OutlinedButton.icon(
                      onPressed: onMap,
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.white,
                        side: const BorderSide(color: Color(0xFF8EC5BB)),
                      ),
                      icon: const Icon(Icons.map_outlined, size: 19),
                      label: const Text('현장 지도'),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                const Text(
                  '전력 사용 분석은 고장을 확정하지 않으며 담당자의 원격확인 또는 현장점검이 최종 판단 단계입니다.',
                  style: TextStyle(color: Color(0xFFAED4CD), fontSize: 12),
                ),
              ],
            ),
          ),
        ),
      );
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
            Text('공식 자료 기반 통제 검증',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 10),
            Wrap(spacing: 18, runSpacing: 8, children: [
              Text(solar == null
                  ? '천문자료: 한국천문연구원 자료 미수집'
                  : '천문자료: 한국천문연구원 ${solar['date']} · ${solar['sunrise']} / ${solar['sunset']}'),
              Text(weather == null
                  ? '기상자료: 기상청 ASOS 부산관측소(159) 자료 미수집'
                  : '기상자료: 기상청 부산 종관기상관측소(지점 159) · ${weather['timestamp']}'),
            ]),
            const SizedBox(height: 8),
            Text(
              '전력자료만 사용했을 때 정상 오분류율 ${_percent(m0?.normalFpr)} · 운영정보를 함께 사용했을 때 정상 오분류율 ${_percent(m3?.normalFpr)} · 우선 확인 20건의 일치율 ${_percent(m3?.precisionAt20)}',
            ),
            if (m3?.status != 'available')
              const Padding(
                padding: EdgeInsets.only(top: 6),
                child: Text('공식 운전자료가 수집되지 않은 평가항목은 산출하지 않으며 내부 추정값이나 합성값으로 대체하지 않습니다.',
                    style: TextStyle(fontSize: 12, color: Color(0xFF795548))),
              ),
          ],
        ),
      ),
    );
  }

  String _percent(double? value) =>
      value == null ? '자료 없음' : '${(value * 100).toStringAsFixed(1)}%';
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
    final viewportWidth = MediaQuery.sizeOf(context).width;
    final cardWidth = viewportWidth < 600 ? viewportWidth - 24 : 250.0;
    return SizedBox(
      width: cardWidth,
      child: Card(
        margin: EdgeInsets.zero,
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
            Text('기존 관제를 보완하는 독립 전력 확인 체계',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 10),
            const Wrap(
              spacing: 8,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                _FlowPill('제어상태'),
                Text('+'),
                _FlowPill('시간대별 실제 전력 사용량'),
                Text('+'),
                _FlowPill('자산 기대부하'),
                Text('+'),
                _FlowPill('운전시간 기준'),
                Icon(Icons.arrow_forward),
                _FlowPill('상태 불일치 · 점검 우선순위'),
              ],
            ),
            const SizedBox(height: 10),
            const Text(
                '기존 원격제어시스템을 교체하지 않고, 이미 설치된 전력계량 장치를 실제 전력 상태를 확인하는 별도 확인 수단으로 활용합니다.'),
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
    final viewportWidth = MediaQuery.sizeOf(context).width;
    final cardWidth = viewportWidth < 600
        ? (viewportWidth - 36) / 2
        : 210.0;
    final isPriority = title == '우선 점검';
    final isRecommended = title == '점검 권고';
    final accent = isPriority
        ? const Color(0xFFB42318)
        : isRecommended
            ? const Color(0xFFD97706)
            : AppTheme.ink;
    return SizedBox(
      width: cardWidth,
      height: 94,
      child: Card(
        margin: EdgeInsets.zero,
        color: isPriority
            ? const Color(0xFFFFF1F0)
            : isRecommended
                ? const Color(0xFFFFF7E6)
                : null,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Icon(icon, color: accent),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: Theme.of(context).textTheme.labelMedium),
                    const SizedBox(height: 6),
                    Text(value,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(color: accent)),
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
