import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../app/theme/app_theme.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/models/region_config.dart';
import '../../data/repositories/lightguard_repository.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dataAsync = ref.watch(lightguardDataProvider);
    return dataAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (error, _) => Scaffold(body: Center(child: Text('운영 자료를 불러오지 못했습니다: $error'))),
      data: (data) {
        final region = ref.watch(selectedRegionProvider);
        final isCompact = MediaQuery.sizeOf(context).width < 600;
        final cards = <Widget>[
          _MetricCard('${region.label} 우선 확인 분전함', '${data.countByStatus(InspectionStatus.priorityInspection)}개', Icons.error_outline, key: const Key('dashboard-priority-card'), onTap: () => context.go('/inspections?filter=priority')),
          _MetricCard('${region.label} 현장점검 검토 분전함', '${data.countByStatus(InspectionStatus.inspectionRecommended)}개', Icons.warning_amber_rounded, key: const Key('dashboard-recommended-card'), onTap: () => context.go('/inspections?filter=recommended')),
          _MetricCard('${region.label} 추적 관찰 분전함', '${data.countByStatus(InspectionStatus.observe)}개', Icons.remove_red_eye_outlined),
          _MetricCard('${region.label} 특이 신호 없는 분전함', '${data.countByStatus(InspectionStatus.normal)}개', Icons.check_circle_outline),
          _MetricCard('${region.label} 등록 분전함 수', '${data.objects.length}개', Icons.electrical_services),
          _MetricCard('${region.label} 연결 가로등 수', '${data.totalLampCount}개', Icons.lightbulb_outline),
          _MetricCard('${region.label} 조명 합산 정격용량', '${data.totalRatedLoadKw.toStringAsFixed(1)} kW', Icons.bolt),
        ];
        return LightguardShell(
          title: 'LightGuard · 운영 현황',
          actions: [
            if (!isCompact)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: StatusBadge(type: BadgeType.validation, label: region.branchLabel),
              ),
          ],
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _DashboardHero(
                  region: region,
                  priorityCount: data.countByStatus(InspectionStatus.priorityInspection),
                  onInspect: () => context.go('/inspections'),
                  onMap: () => context.go('/map'),
                ),
                const SizedBox(height: 18),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: Text('${region.label} 자산 및 점검 현황', style: Theme.of(context).textTheme.titleLarge),
                ),
                const SizedBox(height: 8),
                Wrap(spacing: 12, runSpacing: 12, children: cards),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _DashboardHero extends StatelessWidget {
  const _DashboardHero({required this.region, required this.priorityCount, required this.onInspect, required this.onMap});
  final RegionId region;
  final int priorityCount;
  final VoidCallback onInspect;
  final VoidCallback onMap;

  @override
  Widget build(BuildContext context) => Card(
    clipBehavior: Clip.antiAlias,
    margin: const EdgeInsets.fromLTRB(0, 4, 0, 8),
    child: DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [Color(0xFF102A43), Color(0xFF0F5D59)]),
      ),
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              const Icon(Icons.bolt_rounded, color: Color(0xFFF7C948), size: 20),
              const SizedBox(width: 8),
              Text(region.label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
            ]),
            const SizedBox(height: 18),
            Text('오늘 ${region.label} 우선 확인 분전함 $priorityCount개', style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: Colors.white, fontWeight: FontWeight.w900, height: 1.18)),
            const SizedBox(height: 18),
            Wrap(spacing: 10, runSpacing: 10, children: [
              FilledButton.icon(onPressed: onInspect, style: FilledButton.styleFrom(backgroundColor: const Color(0xFFF7C948), foregroundColor: AppTheme.ink), icon: const Icon(Icons.fact_check_outlined, size: 19), label: const Text('확인 대상 보기')),
              OutlinedButton.icon(onPressed: onMap, style: OutlinedButton.styleFrom(foregroundColor: Colors.white, side: const BorderSide(color: Color(0xFF8EC5BB))), icon: const Icon(Icons.map_outlined, size: 19), label: const Text('현장 지도')),
            ]),
            const SizedBox(height: 14),
            const Text('이상 신호는 고장 확정이 아니며 원격 확인 또는 현장점검이 필요합니다.', style: TextStyle(color: Color(0xFFAED4CD), fontSize: 12)),
          ],
        ),
      ),
    ),
  );
}

class _MetricCard extends StatelessWidget {
  const _MetricCard(this.title, this.value, this.icon, {this.onTap, super.key});
  final String title;
  final String value;
  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final viewportWidth = MediaQuery.sizeOf(context).width;
    final width = viewportWidth < 600 ? (viewportWidth - 36) / 2 : 210.0;
    final critical = title.contains('우선 확인');
    final caution = title.contains('현장점검 검토');
    final accent = critical ? const Color(0xFFB42318) : caution ? const Color(0xFFD97706) : AppTheme.ink;
    final background = critical ? const Color(0xFFFFF1F0) : caution ? const Color(0xFFFFF7E6) : AppTheme.paper;
    return SizedBox(
      width: width,
      height: 98,
      child: Card(
        margin: EdgeInsets.zero,
        color: background,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(children: [
              Container(width: 34, height: 34, decoration: BoxDecoration(color: accent.withValues(alpha: 0.09), borderRadius: BorderRadius.circular(9)), child: Icon(icon, color: accent, size: 20)),
              const SizedBox(width: 12),
              Expanded(child: Column(mainAxisAlignment: MainAxisAlignment.center, crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(title, maxLines: 2, overflow: TextOverflow.ellipsis, style: Theme.of(context).textTheme.labelMedium),
                const SizedBox(height: 4),
                Row(children: [
                  Expanded(child: Text(value, maxLines: 1, overflow: TextOverflow.ellipsis, style: Theme.of(context).textTheme.titleLarge?.copyWith(color: accent))),
                  if (onTap != null) Icon(Icons.arrow_forward_rounded, size: 18, color: accent),
                ]),
              ])),
            ]),
          ),
        ),
      ),
    );
  }
}
