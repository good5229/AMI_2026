import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../core/presentation/operational_copy.dart';
import '../../core/storage/inspection_outcome_storage.dart';
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
  late Map<String, Map<String, String>> _outcomes;

  @override
  void initState() {
    super.initState();
    _outcomes = loadInspectionOutcomes();
  }

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
          title: '점검 대상 분전함과 선정 사유',
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
                    trailing: Text('등록 분전함 ${data.objects.length}개'),
                  ),
                );
              }

              final c = rows[index - 1];
              final status = statusToLabel(c.status);
              final signal =
                  c.detectedSignals.isNotEmpty ? c.detectedSignals.first : null;
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
                                  Text('관리번호: ${c.cabinetUid}',
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
                          if (signal != null &&
                              c.status != InspectionStatus.normal) ...[
                            const SizedBox(height: 12),
                            Container(
                            width: double.infinity,
                            padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
                            decoration: const BoxDecoration(
                              color: Color(0xFFFFFAF1),
                              border: Border(
                                left: BorderSide(
                                  color: Color(0xFFD97706),
                                  width: 3,
                                ),
                              ),
                            ),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Icon(
                                  Icons.priority_high_rounded,
                                  size: 20,
                                  color: Color(0xFF8A5200),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        '우선 확인 사유',
                                        style: Theme.of(context)
                                            .textTheme
                                            .labelLarge
                                            ?.copyWith(
                                              color: const Color(0xFF6E4600),
                                              fontWeight: FontWeight.w700,
                                            ),
                                      ),
                                      const SizedBox(height: 3),
                                      Text(
                                        operationalSignalTitle(signal),
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                        style: Theme.of(context)
                                            .textTheme
                                            .bodyMedium
                                            ?.copyWith(
                                              fontWeight: FontWeight.w600,
                                              height: 1.35,
                                            ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            ),
                          ],
                          if (_outcomes[c.cabinetUid] case final outcome?) ...[
                            const SizedBox(height: 8),
                            Semantics(
                            liveRegion: true,
                            label: '저장된 확인 결과 ${outcome['status']}',
                              child: Row(
                                children: [
                                  const Icon(Icons.check_circle_outline,
                                      size: 18, color: Color(0xFF347149)),
                                  const SizedBox(width: 6),
                                  Text(
                                    '확인 결과 · ${outcome['status']}',
                                    style: const TextStyle(
                                      color: Color(0xFF28583A),
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  '상세 근거 보기',
                                  style: Theme.of(context)
                                      .textTheme
                                      .labelLarge
                                      ?.copyWith(fontWeight: FontWeight.w700),
                                ),
                              ),
                              const Icon(Icons.chevron_right_rounded),
                              const SizedBox(width: 8),
                              OutlinedButton.icon(
                                onPressed: () => _recordOutcome(context, c),
                                icon: const Icon(Icons.edit_note_outlined),
                                label: Text(
                                  _outcomes.containsKey(c.cabinetUid)
                                      ? '확인 결과 수정'
                                      : '확인 결과 기록',
                                ),
                              ),
                            ],
                          ),
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
      _InspectionFilter.all => '전체 분전함',
      _InspectionFilter.targeted => '추가 연계자료가 있는 분전함',
      _InspectionFilter.priority => '우선 확인 대상',
      _InspectionFilter.recommended => '현장점검 검토 대상',
      _InspectionFilter.observe => '추적 관찰 대상',
      _InspectionFilter.normal => '특이 신호 없음',
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

  Future<void> _recordOutcome(
      BuildContext context, CabinetRecord cabinet) async {
    final existing = _outcomes[cabinet.cabinetUid];
    var status = existing?['status'] ?? '원격 확인 예정';
    final noteController = TextEditingController(text: existing?['note'] ?? '');
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Text('${cabinet.assetInfo.cabinetName} 확인 결과'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('담당자가 확인한 결과를 이 브라우저에 저장합니다.'),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: status,
                  decoration: const InputDecoration(
                    labelText: '확인 상태',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: '원격 확인 예정', child: Text('원격 확인 예정')),
                    DropdownMenuItem(value: '추적 관찰', child: Text('추적 관찰')),
                    DropdownMenuItem(value: '현장점검 필요', child: Text('현장점검 필요')),
                    DropdownMenuItem(value: '정상 확인', child: Text('정상 확인')),
                    DropdownMenuItem(value: '고장 확인', child: Text('고장 확인')),
                    DropdownMenuItem(value: '조치 완료', child: Text('조치 완료')),
                  ],
                  onChanged: (value) =>
                      setDialogState(() => status = value ?? status),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: noteController,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: '확인 메모',
                    hintText: '예: 제어기 상태 정상, 다음 운전 주기까지 관찰',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  '브라우저에만 저장되며 서버나 공공데이터 원본에는 반영되지 않습니다.',
                  style: TextStyle(fontSize: 12),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('취소'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, {
                'status': status,
                'note': noteController.text.trim(),
              }),
              child: const Text('저장'),
            ),
          ],
        ),
      ),
    );
    noteController.dispose();
    if (result == null || !mounted) return;
    setState(() => _outcomes[cabinet.cabinetUid] = result);
    saveInspectionOutcomes(_outcomes);
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
