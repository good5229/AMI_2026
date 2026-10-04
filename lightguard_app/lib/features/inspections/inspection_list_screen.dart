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
  const InspectionListScreen({super.key, this.initialFilter});

  final String? initialFilter;

  @override
  ConsumerState<InspectionListScreen> createState() =>
      _InspectionListScreenState();
}

class _InspectionListScreenState extends ConsumerState<InspectionListScreen> {
  late _InspectionFilter _filter;
  late Map<String, Map<String, String>> _outcomes;

  @override
  void initState() {
    super.initState();
    _filter = switch (widget.initialFilter) {
      'priority' => _InspectionFilter.priority,
      'recommended' => _InspectionFilter.recommended,
      'all' => _InspectionFilter.all,
      _ => _InspectionFilter.all,
    };
    _outcomes = {};
    loadInspectionOutcomes().then((saved) {
      if (context.mounted) {
        setState(() => _outcomes = {...saved, ..._outcomes});
      }
    });
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
        final regionOutcomes = inspectionOutcomesForCases(
          _outcomes,
          data.objects.map((cabinet) => cabinet.cabinetUid),
        );
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
        final now = DateTime.now();
        final overdueCount = regionOutcomes.values
            .where((o) =>
                o['dueDate'] != null &&
                DateTime.tryParse(o['dueDate']!)
                        ?.isBefore(DateTime(now.year, now.month, now.day)) ==
                    true &&
                (o['outcomeCode'] == null || o['outcomeCode']!.isEmpty))
            .length;
        final completedCount = regionOutcomes.values
            .where(
                (o) => o['outcomeCode'] != null && o['outcomeCode']!.isNotEmpty)
            .length;
        final isDesktop = MediaQuery.sizeOf(context).width >= 1024;
        final impact = regionOutcomes.values
            .where((o) => (o['outcomeCode'] ?? '').isNotEmpty)
            .toList();
        final desktopSummaryPane = SizedBox(
          width: 286,
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(16, 16, 0, 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Card(
                  key: const Key('inspection-region-summary'),
                  margin: EdgeInsets.zero,
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(region.label,
                            style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 4),
                        Text('기준 ${_datasetDate(data.generatedAt)}'),
                        Text('${rows.length} / ${data.objects.length}개'),
                        const SizedBox(height: 10),
                        DropdownButton<_InspectionFilter>(
                          key: const Key('inspection-filter-dropdown'),
                          isExpanded: true,
                          value: activeFilter,
                          underline: const SizedBox.shrink(),
                          items: [
                            for (final filter in supportedFilters)
                              DropdownMenuItem<_InspectionFilter>(
                                value: filter,
                                key: Key(
                                    'inspection-filter-item-${filter.name}'),
                                child: Text(
                                  '${_filterLabel(filter)} · ${_filterRows(data.objects, filter, targetCabinetIds).length}',
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                          ],
                          onChanged: (value) => setState(() =>
                              _filter = value ?? _InspectionFilter.active),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                Card(
                  key: const Key('local-observed-impact'),
                  margin: EdgeInsets.zero,
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('기기 기록',
                            style: Theme.of(context).textTheme.titleSmall),
                        const SizedBox(height: 4),
                        Text(
                            '${impact.length} / ${data.objects.length}건'),
                        if (impact.isNotEmpty) ...[
                          const SizedBox(height: 4),
                          Text(
                            '정상 ${impact.where((o) => o['outcomeCode'] == 'normal').length} · 고장 ${impact.where((o) => o['outcomeCode'] == 'fault_observed').length} · 예외 ${impact.where((o) => o['outcomeCode'] == 'operational_exception').length} · 자료 문제 ${impact.where((o) => o['outcomeCode'] == 'data_issue').length} · 조치 ${impact.where((o) => o['outcomeCode'] == 'action_completed').length}',
                          ),
                        ],
                        const SizedBox(height: 10),
                        Wrap(spacing: 6, runSpacing: 6, children: [
                          _queueCount('기한 초과', overdueCount,
                              _InspectionFilter.overdue),
                          _queueCount(
                              '원격 확인',
                              regionOutcomes.values
                                  .where((o) =>
                                      o['stage'] == 'remote_review' &&
                                      (o['outcomeCode'] ?? '').isEmpty)
                                  .length,
                              _InspectionFilter.remoteReview),
                          _queueCount(
                              '현장 확인',
                              regionOutcomes.values
                                  .where((o) =>
                                      o['stage'] == 'field_review' &&
                                      (o['outcomeCode'] ?? '').isEmpty)
                                  .length,
                              _InspectionFilter.fieldReview),
                          _queueCount(
                              '자료 확인',
                              regionOutcomes.values
                                  .where((o) =>
                                      o['stage'] == 'data_review' &&
                                      (o['outcomeCode'] ?? '').isEmpty)
                                  .length,
                              _InspectionFilter.dataReview),
                          _queueCount('완료', completedCount,
                              _InspectionFilter.completed),
                        ]),
                        const SizedBox(height: 4),
                        const Text('기기 저장 · 동기화 없음',
                            style: TextStyle(fontSize: 12)),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        );

        Widget workCard(CabinetRecord c) {
          final status = statusToLabel(c.status);
          final signal =
              c.detectedSignals.isNotEmpty ? c.detectedSignals.first : null;
          return Card(
            margin: EdgeInsets.zero,
            clipBehavior: Clip.antiAlias,
            child: InkWell(
              onTap: () => _openCabinet(c.cabinetUid),
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
                                  style: Theme.of(context).textTheme.titleMedium),
                              Text('ID · ${c.cabinetUid}',
                                  style: Theme.of(context).textTheme.bodySmall),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        StatusBadge(
                            type: statusToBadge(c.status), label: status),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Wrap(spacing: 6, runSpacing: 4, children: [
                      _smallTag('자료 · ${operationalEvidenceSourceLabel(c)}'),
                      if (_outcomes[c.cabinetUid]?['stage'] case final stage?)
                        _smallTag(_stageLabel(stage)),
                      if (_outcomes[c.cabinetUid]?['dueDate'] case final due?)
                        _smallTag('기한 $due'),
                      if ((_outcomes[c.cabinetUid]?['assignee'] ?? '').isNotEmpty)
                        _smallTag('담당 ${_outcomes[c.cabinetUid]!['assignee']}'),
                    ]),
                    const SizedBox(height: 8),
                    Text(_nextAction(c, _outcomes[c.cabinetUid]),
                        style: Theme.of(context).textTheme.bodyMedium),
                    if (signal != null && c.status != InspectionStatus.normal) ...[
                      const SizedBox(height: 10),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
                        decoration: const BoxDecoration(
                          color: Color(0xFFFFFAF1),
                          border: Border(
                            left: BorderSide(
                                color: Color(0xFFD97706), width: 3),
                          ),
                        ),
                        child: Text(
                          '신호 · ${operationalSignalTitle(signal)}',
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.w600,
                                height: 1.35,
                              ),
                        ),
                      ),
                    ],
                    if (_outcomes[c.cabinetUid] case final outcome?) ...[
                      const SizedBox(height: 8),
                      Semantics(
                        liveRegion: true,
                        label: '저장된 확인 결과 ${outcome['status']}',
                        child: Text(
                          '기록 · ${outcome['status']} · ${outcome['updatedAt'] ?? ''}',
                          softWrap: true,
                          style: const TextStyle(
                              color: Color(0xFF28583A),
                              fontWeight: FontWeight.w600),
                        ),
                      ),
                    ],
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: Text('상세 근거 보기',
                              style: Theme.of(context)
                                  .textTheme
                                  .labelLarge
                                  ?.copyWith(fontWeight: FontWeight.w700)),
                        ),
                        OutlinedButton.icon(
                          onPressed: () => _recordOutcome(context, c),
                          icon: const Icon(Icons.edit_note_outlined),
                          label: Text(_outcomes.containsKey(c.cabinetUid)
                              ? '결과 수정'
                              : '결과 기록'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          );
        }

        return LightguardShell(
          title: '자산·점검 기록',
          compactTitle: '자산·점검 기록',
          child: isDesktop
              ? Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    desktopSummaryPane,
                    const VerticalDivider(width: 1),
                    Expanded(
                      child: Center(
                        child: ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 860),
                          child: ListView.separated(
                            padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
                            itemCount: rows.length,
                            separatorBuilder: (_, __) =>
                                const SizedBox(height: 10),
                            itemBuilder: (context, index) =>
                                workCard(rows[index]),
                          ),
                        ),
                      ),
                    ),
                  ],
                )
              : ListView.separated(
            padding: EdgeInsets.only(
                bottom: MediaQuery.paddingOf(context).bottom + 96),
            itemCount: rows.length + 2,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              if (index == 0) {
                return Card(
                  margin: const EdgeInsets.fromLTRB(12, 12, 12, 0),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    child: Column(children: [
                      ListTile(
                        leading: const Icon(Icons.location_city_outlined),
                        key: const Key('inspection-region-summary'),
                        contentPadding: EdgeInsets.zero,
                        title: Text(region.label),
                        subtitle: Text(
                            '기준 ${_datasetDate(data.generatedAt)} · ${rows.length}개'),
                        trailing: Text('전체 ${data.objects.length}개'),
                      ),
                      SizedBox(
                          width: double.infinity,
                          child: DropdownButton<_InspectionFilter>(
                            key: const Key('inspection-filter-dropdown'),
                            isExpanded: true,
                            value: activeFilter,
                            underline: const SizedBox.shrink(),
                            items: [
                              for (final filter in supportedFilters)
                                DropdownMenuItem<_InspectionFilter>(
                                  value: filter,
                                  key: Key(
                                      'inspection-filter-item-${filter.name}'),
                                  child: Text(
                                      '${_filterLabel(filter)} · ${_filterRows(data.objects, filter, targetCabinetIds).length}'),
                                ),
                            ],
                            onChanged: (value) => setState(() =>
                                _filter = value ?? _InspectionFilter.active),
                          )),
                    ]),
                  ),
                );
              }

              if (index == 1) {
                final impact = regionOutcomes.values
                    .where((o) =>
                        o['outcomeCode'] != null &&
                        o['outcomeCode']!.isNotEmpty)
                    .toList();
                return Card(
                  key: const Key('local-observed-impact'),
                  margin: const EdgeInsets.fromLTRB(12, 0, 12, 0),
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('기기 기록',
                              style: Theme.of(context).textTheme.titleSmall),
                          const SizedBox(height: 4),
                          Text(
                              '${impact.length} / ${data.objects.length}건 · 기기 저장'),
                          if (impact.isNotEmpty)
                            Text(
                                '정상 ${impact.where((o) => o['outcomeCode'] == 'normal').length} · 고장 관찰 ${impact.where((o) => o['outcomeCode'] == 'fault_observed').length} · 운영상 예외 ${impact.where((o) => o['outcomeCode'] == 'operational_exception').length} · 자료 문제 ${impact.where((o) => o['outcomeCode'] == 'data_issue').length} · 조치 완료 ${impact.where((o) => o['outcomeCode'] == 'action_completed').length}'),
                          const SizedBox(height: 8),
                          Wrap(spacing: 8, runSpacing: 8, children: [
                            _queueCount('기한 초과', overdueCount,
                                _InspectionFilter.overdue),
                            _queueCount(
                                '원격 확인',
                                regionOutcomes.values
                                    .where((o) =>
                                        o['stage'] == 'remote_review' &&
                                        (o['outcomeCode'] ?? '').isEmpty)
                                    .length,
                                _InspectionFilter.remoteReview),
                            _queueCount(
                                '현장 확인',
                                regionOutcomes.values
                                    .where((o) =>
                                        o['stage'] == 'field_review' &&
                                        (o['outcomeCode'] ?? '').isEmpty)
                                    .length,
                                _InspectionFilter.fieldReview),
                            _queueCount(
                                '자료 확인',
                                regionOutcomes.values
                                    .where((o) =>
                                        o['stage'] == 'data_review' &&
                                        (o['outcomeCode'] ?? '').isEmpty)
                                    .length,
                                _InspectionFilter.dataReview),
                            _queueCount('완료', completedCount,
                                _InspectionFilter.completed),
                          ]),
                          const SizedBox(height: 4),
                          const Text('기기 저장 · 동기화 없음',
                              style: TextStyle(fontSize: 12)),
                        ]),
                  ),
                );
              }

              final c = rows[index - 2];
              final status = statusToLabel(c.status);
              final signal =
                  c.detectedSignals.isNotEmpty ? c.detectedSignals.first : null;
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 12),
                clipBehavior: Clip.antiAlias,
                child: InkWell(
                  onTap: () => _openCabinet(c.cabinetUid),
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
                                  Text('ID · ${c.cabinetUid}',
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
                        const SizedBox(height: 6),
                        Wrap(spacing: 6, runSpacing: 4, children: [
                          _smallTag('자료 · ${operationalEvidenceSourceLabel(c)}'),
                          if (_outcomes[c.cabinetUid]?['stage']
                              case final stage?)
                            _smallTag(_stageLabel(stage)),
                          if (_outcomes[c.cabinetUid]?['dueDate']
                              case final due?)
                            _smallTag('기한 $due'),
                          if ((_outcomes[c.cabinetUid]?['assignee'] ?? '')
                              .isNotEmpty)
                            _smallTag(
                                '담당 ${_outcomes[c.cabinetUid]!['assignee']}'),
                        ]),
                        const SizedBox(height: 8),
                        Text(_nextAction(c, _outcomes[c.cabinetUid]),
                            style: Theme.of(context).textTheme.bodyMedium),
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
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Icon(Icons.check_circle_outline,
                                    size: 18, color: Color(0xFF347149)),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    '기록 · ${outcome['status']} · ${outcome['updatedAt'] ?? ''}',
                                    softWrap: true,
                                    style: const TextStyle(
                                      color: Color(0xFF28583A),
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                        const SizedBox(height: 8),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text(
                              '상세 근거 보기',
                              style: Theme.of(context)
                                  .textTheme
                                  .labelLarge
                                  ?.copyWith(fontWeight: FontWeight.w700),
                            ),
                            const SizedBox(height: 4),
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
    final filters = <_InspectionFilter>[
      _InspectionFilter.active,
      _InspectionFilter.all,
    ];
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
      _InspectionFilter.overdue,
      _InspectionFilter.remoteReview,
      _InspectionFilter.fieldReview,
      _InspectionFilter.dataReview,
      _InspectionFilter.completed,
    ]);
    return filters;
  }

  List<CabinetRecord> _filterRows(List<CabinetRecord> rows,
      _InspectionFilter filter, Set<String> targetCabinetIds) {
    final copy = [...rows]..sort((a, b) {
      if (!a.ami.hasRealAmi || !b.ami.hasRealAmi) {
        return a.cabinetUid.compareTo(b.cabinetUid);
      }
      return a.inspectionPriority.rank.compareTo(b.inspectionPriority.rank);
    });
    final current = DateTime.now();
    final today = DateTime(current.year, current.month, current.day);
    return switch (filter) {
      _InspectionFilter.all => copy,
      _InspectionFilter.active => copy.where((r) {
          final code = _outcomes[r.cabinetUid]?['outcomeCode'];
          return (r.ami.hasRealAmi && r.status != InspectionStatus.normal ||
                  (_outcomes[r.cabinetUid]?['stage'] ?? '').isNotEmpty) &&
              (code == null || code.isEmpty);
        }).toList(),
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
      _InspectionFilter.overdue => copy.where((r) {
          final outcome = _outcomes[r.cabinetUid];
          final code = outcome?['outcomeCode'];
          return outcome?['dueDate'] != null &&
              DateTime.tryParse(outcome!['dueDate']!)?.isBefore(today) ==
                  true &&
              (code == null || code.isEmpty);
        }).toList(),
      _InspectionFilter.remoteReview => copy
          .where((r) =>
              _outcomes[r.cabinetUid]?['stage'] == 'remote_review' &&
              (_outcomes[r.cabinetUid]?['outcomeCode'] ?? '').isEmpty)
          .toList(),
      _InspectionFilter.fieldReview => copy
          .where((r) =>
              _outcomes[r.cabinetUid]?['stage'] == 'field_review' &&
              (_outcomes[r.cabinetUid]?['outcomeCode'] ?? '').isEmpty)
          .toList(),
      _InspectionFilter.dataReview => copy
          .where((r) =>
              _outcomes[r.cabinetUid]?['stage'] == 'data_review' &&
              (_outcomes[r.cabinetUid]?['outcomeCode'] ?? '').isEmpty)
          .toList(),
      _InspectionFilter.completed => copy.where((r) {
          final code = _outcomes[r.cabinetUid]?['outcomeCode'];
          return code != null && code.isNotEmpty;
        }).toList(),
    };
  }

  String _filterLabel(_InspectionFilter filter) {
    return switch (filter) {
      _InspectionFilter.all => '전체',
      _InspectionFilter.active => '진행 중',
      _InspectionFilter.targeted => '연계자료 있음',
      _InspectionFilter.priority => '우선 확인',
      _InspectionFilter.recommended => '점검 검토',
      _InspectionFilter.observe => '관찰',
      _InspectionFilter.normal => '정상 범위',
      _InspectionFilter.scenario => '모의 신호',
      _InspectionFilter.municipalAsset => '공공자산',
      _InspectionFilter.overdue => '기한 초과',
      _InspectionFilter.remoteReview => '원격 확인',
      _InspectionFilter.fieldReview => '현장 확인',
      _InspectionFilter.dataReview => '자료 확인',
      _InspectionFilter.completed => '기록 완료',
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
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => _InspectionOutcomeDialog(
        cabinet: cabinet,
        existing: existing,
      ),
    );
    if (result == null || !mounted) return;
    final updated = {..._outcomes, cabinet.cabinetUid: result};
    try {
      await saveInspectionOutcomes(updated);
      if (mounted) setState(() => _outcomes = updated);
    } catch (error) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('기록을 저장하지 못했습니다. 다시 시도해 주세요. ($error)'),
        ));
      }
    }
  }

  Future<void> _openCabinet(String cabinetUid) async {
    await context.push('/cabinet/$cabinetUid');
    if (!mounted) return;
    try {
      final saved = await loadInspectionOutcomes();
      if (mounted) setState(() => _outcomes = saved);
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('기기 기록을 다시 불러오지 못했습니다. ($error)'),
        ));
      }
    }
  }

  Widget _queueCount(String label, int count, _InspectionFilter filter) =>
      ActionChip(
          label: Text('$label $count'),
          onPressed: () => setState(() => _filter = filter));

  Widget _smallTag(String label) => Container(
      constraints: const BoxConstraints(minHeight: 30),
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
      decoration: BoxDecoration(
          color: const Color(0xFFE7EFED),
          borderRadius: BorderRadius.circular(7)),
      child: Text(label,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)));

  String _stageLabel(String stage) => switch (stage) {
        'remote_review' => '원격 확인',
        'field_review' => '현장 확인',
        'data_review' => '자료 확인',
        'observation' => '추적 관찰',
        _ => stage,
      };

  String _outcomeLabel(String code) => switch (code) {
        'fault_observed' => '고장 관찰',
        'normal' => '정상',
        'operational_exception' => '운영상 예외',
        'data_issue' => '자료 문제',
        'action_completed' => '조치 완료',
        _ => code,
      };

  String _nextAction(CabinetRecord cabinet, Map<String, String>? outcome) {
    if (outcome?['outcomeCode'] != null &&
        outcome!['outcomeCode']!.isNotEmpty) {
      return '기록 · ${_outcomeLabel(outcome['outcomeCode']!)}';
    }
    return switch (outcome?['stage']) {
      'remote_review' => '조치 · 제어기·동시간대 신호 원격 확인',
      'field_review' => '조치 · 제어기·배선·등기구 현장 확인',
      'data_review' => '조치 · 측정값·연결·시각 확인',
      'observation' => '조치 · 다음 주기 재확인',
      _ => cabinet.detectedSignals.isEmpty
          ? '조치 · 연결·점검 이력 확인'
          : '조치 · 제어기 원격 확인',
    };
  }

  String _datasetDate(DateTime timestamp) =>
      '${timestamp.year.toString().padLeft(4, '0')}-${timestamp.month.toString().padLeft(2, '0')}-${timestamp.day.toString().padLeft(2, '0')}';
}

enum _InspectionFilter {
  all,
  active,
  targeted,
  priority,
  recommended,
  observe,
  normal,
  scenario,
  municipalAsset,
  overdue,
  remoteReview,
  fieldReview,
  dataReview,
  completed,
}

class _InspectionOutcomeDialog extends StatefulWidget {
  const _InspectionOutcomeDialog(
      {required this.cabinet, required this.existing});

  final CabinetRecord cabinet;
  final Map<String, String>? existing;

  @override
  State<_InspectionOutcomeDialog> createState() =>
      _InspectionOutcomeDialogState();
}

class _InspectionOutcomeDialogState extends State<_InspectionOutcomeDialog> {
  late String _stage = widget.existing?['stage'] ?? 'remote_review';
  late String _outcomeCode = widget.existing?['outcomeCode'] ?? '';
  late String _dueDate = widget.existing?['dueDate'] ?? '';
  late final TextEditingController _noteController =
      TextEditingController(text: widget.existing?['note'] ?? '');
  late final TextEditingController _assigneeController =
      TextEditingController(text: widget.existing?['assignee'] ?? '');

  @override
  void dispose() {
    _noteController.dispose();
    _assigneeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AlertDialog(
        title: Text('${widget.cabinet.assetInfo.cabinetName} 확인 결과'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('기기 저장 · 서버 동기화 없음'),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _stage,
                decoration: const InputDecoration(
                    labelText: '진행 단계', border: OutlineInputBorder()),
                items: const [
                  DropdownMenuItem(
                      value: 'remote_review', child: Text('원격 확인')),
                  DropdownMenuItem(value: 'field_review', child: Text('현장 확인')),
                  DropdownMenuItem(value: 'data_review', child: Text('자료 확인')),
                  DropdownMenuItem(value: 'observation', child: Text('추적 관찰')),
                ],
                onChanged: (value) => setState(() => _stage = value ?? _stage),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _outcomeCode,
                decoration: const InputDecoration(
                  labelText: '기록 결과 (아직 미기록 가능)',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: '', child: Text('결과 미기록')),
                  DropdownMenuItem(
                      value: 'fault_observed', child: Text('고장 관찰')),
                  DropdownMenuItem(value: 'normal', child: Text('정상')),
                  DropdownMenuItem(
                      value: 'operational_exception', child: Text('운영상 예외')),
                  DropdownMenuItem(value: 'data_issue', child: Text('자료 문제')),
                  DropdownMenuItem(
                      value: 'action_completed', child: Text('조치 완료')),
                ],
                onChanged: (value) =>
                    setState(() => _outcomeCode = value ?? ''),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _assigneeController,
                decoration: const InputDecoration(
                    labelText: '담당자 (선택)', border: OutlineInputBorder()),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: _pickDueDate,
                icon: const Icon(Icons.calendar_today_outlined),
                label: Text(_dueDate.isEmpty ? '기한 선택 (선택)' : '기한 $_dueDate'),
              ),
              if (_dueDate.isNotEmpty)
                TextButton.icon(
                  key: const Key('clear-due-date'),
                  onPressed: () => setState(() => _dueDate = ''),
                  icon: const Icon(Icons.clear),
                  label: const Text('기한 지우기'),
                ),
              const SizedBox(height: 12),
              TextField(
                controller: _noteController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: '확인 메모',
                  hintText: '예: 제어기 상태 정상, 다음 운전 주기까지 관찰',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 8),
              const Text('원본 자료 변경 없음',
                  style: TextStyle(fontSize: 12)),
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
              'status': _outcomeCode.isEmpty
                  ? _dialogStageLabel(_stage)
                  : _dialogOutcomeLabel(_outcomeCode),
              'stage': _stage,
              'outcomeCode': _outcomeCode,
              'dueDate': _dueDate,
              'assignee': _assigneeController.text.trim(),
              'note': _noteController.text.trim(),
              'updatedAt': DateTime.now().toIso8601String(),
            }),
            child: const Text('저장'),
          ),
        ],
      );

  Future<void> _pickDueDate() async {
    final today = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime.tryParse(_dueDate) ?? today,
      firstDate: DateTime(today.year - 2),
      lastDate: DateTime(today.year + 10),
    );
    if (picked != null && mounted) {
      setState(() => _dueDate =
          '${picked.year.toString().padLeft(4, '0')}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}');
    }
  }
}

String _dialogStageLabel(String stage) => switch (stage) {
      'remote_review' => '원격 확인',
      'field_review' => '현장 확인',
      'data_review' => '자료 확인',
      'observation' => '추적 관찰',
      _ => stage,
    };

String _dialogOutcomeLabel(String code) => switch (code) {
      'fault_observed' => '고장 관찰',
      'normal' => '정상',
      'operational_exception' => '운영상 예외',
      'data_issue' => '자료 문제',
      'action_completed' => '조치 완료',
      _ => code,
    };
