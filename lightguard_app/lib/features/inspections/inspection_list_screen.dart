import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../core/presentation/operational_copy.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/models/region_config.dart';
import '../../data/repositories/lightguard_repository.dart';

class InspectionListScreen extends ConsumerStatefulWidget {
  const InspectionListScreen({super.key});

  @override
  ConsumerState<InspectionListScreen> createState() =>
      _InspectionListScreenState();
}

class _InspectionListScreenState extends ConsumerState<InspectionListScreen> {
  _InspectionFilter _filter = _InspectionFilter.all;

  @override
  Widget build(BuildContext context) {
    final dataAsync = ref.watch(lightguardDataProvider);

    return dataAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, s) => Scaffold(body: Center(child: Text('점검 데이터 로드 실패: $e'))),
      data: (data) {
        final region = ref.watch(selectedRegionProvider);
        final targetCabinetIds =
            _extractTargetCabinets(data.targetMode, region.targetModeField);
        final targetCount = data.objects
            .where((c) => targetCabinetIds.contains(c.cabinetUid))
            .length;
        final scenarioCount = data.objects
            .where((c) =>
                targetCabinetIds.contains(c.cabinetUid) &&
                c.evidenceSource == EvidenceSource.scenarioInjection)
            .length;
        final municipalCount = data.objects
            .where((c) => c.evidenceSource == EvidenceSource.realMunicipalAsset)
            .length;

        final supportedFilters = _supportedFilters(
          region: region,
          targetCount: targetCount,
          scenarioCount: scenarioCount,
          municipalCount: municipalCount,
        );
        final activeFilter = supportedFilters.contains(_filter)
            ? _filter
            : supportedFilters.first;
        final rows = _filterRows(data.objects, activeFilter, targetCabinetIds);

        return LightguardShell(
          title: '확인 대상 및 판정 사유',
          actions: [
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: DropdownButton<dynamic>(
                key: const Key('inspection-filter-dropdown'),
                value: activeFilter,
                underline: const SizedBox.shrink(),
                items: [
                  for (final filter in supportedFilters)
                    DropdownMenuItem<dynamic>(
                      value: filter,
                      key: Key('inspection-filter-item-${filter.name}'),
                      child: Text(_filterLabel(filter)),
                    ),
                ],
                onChanged: (value) => setState(() => _filter =
                    value is _InspectionFilter ? value : _InspectionFilter.all),
              ),
            ),
          ],
          child: ListView.separated(
            itemCount: rows.length + 1,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              if (index == 0) {
                return Card(
                  margin: const EdgeInsets.fromLTRB(12, 12, 12, 0),
                  child: ListTile(
                    leading: const Icon(Icons.location_city_outlined),
                    key: const Key('inspection-region-summary'),
                    title: Text(region.label),
                    subtitle: Text(region.regionalFilterHint),
                    trailing: Text('총 ${data.objects.length}개'),
                  ),
                );
              }

              final c = rows[index - 1];
              final status = statusToLabel(c.status);
              final signal =
                  c.detectedSignals.isNotEmpty ? c.detectedSignals.first : null;
              final source = operationalEvidenceSourceLabel(c);
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 12),
                clipBehavior: Clip.antiAlias,
                child: InkWell(
                  onTap: () => context.go('/cabinet/${c.cabinetUid}'),
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(c.assetInfo.cabinetName,
                                      style: Theme.of(context)
                                          .textTheme
                                          .titleMedium),
                                  Text('UID: ${c.cabinetUid}',
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodySmall),
                                ],
                              ),
                            ),
                            StatusBadge(
                                type: statusToBadge(c.status), label: status),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            StatusBadge(
                              type: c.evidenceSource ==
                                      EvidenceSource.scenarioInjection
                                  ? BadgeType.scenario
                                  : BadgeType.validation,
                              label: '자료 구분: $source',
                            ),
                            _EvidenceChip(
                                label: '확인 순위',
                                value: '#${c.inspectionPriority.rank}'),
                            _EvidenceChip(
                              label: '관측 항목',
                              value: operationalSignalTitle(signal),
                            ),
                            _EvidenceChip(
                              label: '신호 수준',
                              value: operationalSignalLevel(signal),
                            ),
                            _EvidenceChip(
                              label: '관측 지속시간',
                              value: signal == null
                                  ? '측정값 없음'
                                  : '${signal.estimatedDurationMin}분',
                            ),
                            _EvidenceChip(
                              label: '예상 부하',
                              value: c.expectedLoad.expectedRatedLoadKw > 0
                                  ? '${c.expectedLoad.expectedRatedLoadKw.toStringAsFixed(2)} kW'
                                  : '정격정보 제한',
                            ),
                            _EvidenceChip(
                              label: '판정 신뢰도',
                              value: operationalConfidenceLabel(signal),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text('분류 사유: ${operationalPriorityReason(c)}',
                            maxLines: 3),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }

  List<_InspectionFilter> _supportedFilters({
    required RegionId region,
    required int targetCount,
    required int scenarioCount,
    required int municipalCount,
  }) {
    final filters = <_InspectionFilter>[_InspectionFilter.all];
    if (targetCount > 0) {
      filters.add(_InspectionFilter.targeted);
    }
    if (region.supportsScenarioInjection && scenarioCount > 0) {
      filters.add(_InspectionFilter.scenario);
    }
    if (!region.supportsScenarioInjection && municipalCount > 0) {
      filters.add(_InspectionFilter.municipalAsset);
    }
    filters.addAll(const [
      _InspectionFilter.priority,
      _InspectionFilter.recommended,
      _InspectionFilter.observe,
      _InspectionFilter.normal,
    ]);
    return filters;
  }

  List<CabinetRecord> _filterRows(List<CabinetRecord> rows,
      _InspectionFilter filter, Set<String> targetCabinetIds) {
    final copy = [...rows]..sort((a, b) =>
        a.inspectionPriority.rank.compareTo(b.inspectionPriority.rank));
    return switch (filter) {
      _InspectionFilter.all => copy,
      _InspectionFilter.targeted => copy
          .where((r) => targetCabinetIds.contains(r.cabinetUid))
          .toList(growable: false),
      _InspectionFilter.priority => copy
          .where((r) => r.status == InspectionStatus.priorityInspection)
          .toList(),
      _InspectionFilter.recommended => copy
          .where((r) => r.status == InspectionStatus.inspectionRecommended)
          .toList(),
      _InspectionFilter.observe =>
        copy.where((r) => r.status == InspectionStatus.observe).toList(),
      _InspectionFilter.normal =>
        copy.where((r) => r.status == InspectionStatus.normal).toList(),
      _InspectionFilter.scenario => copy
          .where((r) =>
              targetCabinetIds.contains(r.cabinetUid) &&
              r.evidenceSource == EvidenceSource.scenarioInjection)
          .toList(),
      _InspectionFilter.municipalAsset => copy
          .where((r) => r.evidenceSource == EvidenceSource.realMunicipalAsset)
          .toList(),
    };
  }

  String _filterLabel(_InspectionFilter filter) {
    return switch (filter) {
      _InspectionFilter.all => '전체',
      _InspectionFilter.targeted => '연계 자료 있음',
      _InspectionFilter.priority => '우선 확인 필요',
      _InspectionFilter.recommended => '현장 확인 권고',
      _InspectionFilter.observe => '추적 관찰',
      _InspectionFilter.normal => '정상 범위',
      _InspectionFilter.scenario => '검증용 모의 신호',
      _InspectionFilter.municipalAsset => '지자체 공공자산 정보',
    };
  }

  Set<String> _extractTargetCabinets(
      Map<String, dynamic> targetMode, String key) {
    final raw = targetMode[key];
    if (raw is List) return raw.map((value) => value.toString()).toSet();
    if (raw is String) return <String>{raw};
    return const <String>{};
  }

}

class _EvidenceChip extends StatelessWidget {
  const _EvidenceChip({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(maxWidth: 260),
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFFF2F5F7),
        borderRadius: BorderRadius.circular(8),
      ),
      child:
          Text('$label: $value', maxLines: 2, overflow: TextOverflow.ellipsis),
    );
  }
}

enum _InspectionFilter {
  all,
  targeted,
  priority,
  recommended,
  observe,
  normal,
  scenario,
  municipalAsset,
}
