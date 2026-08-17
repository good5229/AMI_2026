import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/repositories/lightguard_repository.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/models/region_config.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dataAsync = ref.watch(lightguardDataProvider);

    return dataAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (err, stack) => _error(context, '데이터 로드 실패: $err'),
      data: (data) {
        final region = ref.watch(selectedRegionProvider);

        final cards = [
          _MetricCard('총 분전함', '${data.objects.length}개', Icons.electrical_services),
          _MetricCard('총 가로등 수', '${data.totalLampCount}개', Icons.lightbulb_outline),
          _MetricCard('총 정격용량', '${data.totalRatedLoadKw.toStringAsFixed(1)} kW', Icons.bolt),
          _MetricCard('정상', '${data.countByStatus(InspectionStatus.normal)}', Icons.check_circle_outline),
          _MetricCard('관찰', '${data.countByStatus(InspectionStatus.observe)}', Icons.remove_red_eye_outlined),
          _MetricCard('점검 권고', '${data.countByStatus(InspectionStatus.inspectionRecommended)}', Icons.warning_amber_rounded),
          _MetricCard('우선 점검', '${data.countByStatus(InspectionStatus.priorityInspection)}', Icons.error_outline),
        ];

        final today = data.objects.isNotEmpty ? data.objects.first : null;

        return LightguardShell(
          title: 'LightGuard Dashboard · ${region.label}',
          actions: [
            if (today != null)
              const Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: const StatusBadge(type: BadgeType.validation, label: '검증 모드'),
              ),
            ],
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(spacing: 12, runSpacing: 12, children: cards),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _MiniPill(label: '우선점검 ${data.countByStatus(InspectionStatus.priorityInspection)}개'),
                    _MiniPill(label: '점검권고 ${data.countByStatus(InspectionStatus.inspectionRecommended)}개'),
                    _MiniPill(label: '관찰 ${data.countByStatus(InspectionStatus.observe)}개'),
                    _MiniPill(label: '정상 ${data.countByStatus(InspectionStatus.normal)}개'),
                  ],
                ),
                  const SizedBox(height: 12),
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.schedule),
                    title: const Text('오늘 예측 점등/소등'),
                    subtitle: Text(
                      today == null
                          ? '데이터 없음'
                          : '점등: ${today.expectedSchedule.sunset} / 소등: ${today.expectedSchedule.sunrise}',
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
