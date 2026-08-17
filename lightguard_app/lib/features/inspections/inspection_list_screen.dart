import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/repositories/lightguard_repository.dart';

class InspectionListScreen extends ConsumerStatefulWidget {
  const InspectionListScreen({super.key});

  @override
  ConsumerState<InspectionListScreen> createState() => _InspectionListScreenState();
}

class _InspectionListScreenState extends ConsumerState<InspectionListScreen> {
  String _filter = 'all';

  @override
  Widget build(BuildContext context) {
    final dataAsync = ref.watch(lightguardDataProvider);

    return dataAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, s) => Scaffold(body: Center(child: Text('점검 데이터 로드 실패: $e'))),
      data: (data) {
        final rows = _filterRows(data.objects);
        return LightguardShell(
          title: '점검 우선순위',
          actions: [
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: DropdownButton<String>(
                value: _filter,
                underline: const SizedBox.shrink(),
                items: const [
                  DropdownMenuItem(value: 'all', child: Text('전체')),
                  DropdownMenuItem(value: 'priority', child: Text('우선 점검')),
                  DropdownMenuItem(value: 'recommended', child: Text('점검 권고')),
                  DropdownMenuItem(value: 'observe', child: Text('관찰')),
                  DropdownMenuItem(value: 'normal', child: Text('정상')),
                  DropdownMenuItem(value: 'scenario', child: Text('검증 시나리오만')),
                  DropdownMenuItem(value: 'real_ami', child: Text('실제 AMI만')),
                ],
                onChanged: (v) => setState(() => _filter = v ?? 'all'),
              ),
            ),
          ],
          child: ListView.separated(
            itemCount: rows.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final c = rows[index];
              final status = statusToLabel(c.status);
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                child: ListTile(
                  title: Text(c.assetInfo.cabinetName),
                  subtitle: Text('UID: ${c.cabinetUid}\n이상 유형: ${c.anomalyEvidence.ruleIds.join(', ')}'),
                  trailing: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      StatusBadge(type: statusToBadge(c.status), label: status),
                      const SizedBox(height: 6),
                      Text(c.inspectionPriority.reason, maxLines: 2),
                    ],
                  ),
                  onTap: () => context.go('/cabinet/${c.cabinetUid}'),
                ),
              );
            },
          ),
        );
      },
    );
  }

  List<CabinetRecord> _filterRows(List<CabinetRecord> rows) {
    final copy = [...rows]..sort((a, b) => a.inspectionPriority.rank.compareTo(b.inspectionPriority.rank));
    if (_filter == 'all') return copy;
    if (_filter == 'priority') return copy.where((r) => r.status == InspectionStatus.priorityInspection).toList();
    if (_filter == 'recommended') return copy.where((r) => r.status == InspectionStatus.inspectionRecommended).toList();
    if (_filter == 'observe') return copy.where((r) => r.status == InspectionStatus.observe).toList();
    if (_filter == 'normal') return copy.where((r) => r.status == InspectionStatus.normal).toList();
    if (_filter == 'scenario') return copy.where((r) => r.evidenceSource == EvidenceSource.scenarioInjection).toList();
    if (_filter == 'real_ami') return copy.where((r) => r.evidenceSource == EvidenceSource.realCompetitionAmi).toList();
    return copy;
  }
}
