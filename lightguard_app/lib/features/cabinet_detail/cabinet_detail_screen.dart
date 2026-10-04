import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../core/presentation/operational_copy.dart';
import '../../core/storage/inspection_outcome_storage.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/repositories/lightguard_repository.dart';

class CabinetDetailScreen extends ConsumerStatefulWidget {
  const CabinetDetailScreen({super.key, required this.cabinetUid});

  final String cabinetUid;

  @override
  ConsumerState<CabinetDetailScreen> createState() =>
      _CabinetDetailScreenState();
}

class _CabinetDetailScreenState extends ConsumerState<CabinetDetailScreen> {
  Map<String, Map<String, String>> _outcomes = {};

  @override
  void initState() {
    super.initState();
    loadInspectionOutcomes().then((value) {
      if (mounted) setState(() => _outcomes = {...value, ..._outcomes});
    });
  }

  @override
  Widget build(BuildContext context) {
    final dataAsync = ref.watch(lightguardDataProvider);
    return dataAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, s) => Scaffold(body: Center(child: Text('분전함 상세 실패: $e'))),
      data: (data) {
        final cabinet = data.objects.firstWhere(
            (c) => c.cabinetUid == widget.cabinetUid,
            orElse: () => data.objects.first);
        final signal = cabinet.detectedSignals.isNotEmpty
            ? cabinet.detectedSignals.first
            : null;
        final savedOutcome = _outcomes[cabinet.cabinetUid];
        final observations = cabinet.detectedSignals
            .take(3)
            .map((item) =>
                '${operationalSignalTitle(item)} (${item.estimatedDurationMin}분)')
            .join(' / ');
        final evidenceSummary = cabinet.detectedSignals.isEmpty
            ? 'AMI 미연결 · 자동 고장 판정 없음'
            : '$observations · 현장/정비 기록 없음';
        return LightguardShell(
          title: '분전함',
          bottomAction: SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              key: const Key('field-primary-result'),
              onPressed: () => _recordFieldResult(cabinet.cabinetUid),
              icon: const Icon(Icons.fact_check_outlined),
              label: Text(savedOutcome?['outcomeCode']?.isNotEmpty == true
                  ? '기록 결과 수정'
                  : '현장 확인 결과 기록'),
            ),
          ),
          child: ListView(
            padding: const EdgeInsets.all(12),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(children: [
                          Expanded(
                              child: Text(cabinet.assetInfo.cabinetName,
                                  style:
                                      Theme.of(context).textTheme.titleLarge)),
                          StatusBadge(
                              type: statusToBadge(cabinet.status),
                              label: statusToLabel(cabinet.status))
                        ]),
                        const SizedBox(height: 6),
                        Text('자산 ID · ${cabinet.cabinetUid}',
                            style: Theme.of(context).textTheme.labelLarge),
                        if (_displayLocation(cabinet) case final location?)
                          Text('주소 · $location'),
                        if (_displayLocation(cabinet) == null &&
                            cabinet.assetInfo.latitude != null &&
                            cabinet.assetInfo.longitude != null)
                          Text(
                              '좌표 · ${cabinet.assetInfo.latitude!.toStringAsFixed(6)}, ${cabinet.assetInfo.longitude!.toStringAsFixed(6)}'),
                        if (cabinet.assetInfo.latitude != null &&
                            cabinet.assetInfo.longitude != null)
                          OutlinedButton.icon(
                              key: const Key('cabinet-map-link'),
                              onPressed: () => context.go(
                                  '/map?cabinet=${Uri.encodeComponent(cabinet.cabinetUid)}'),
                              icon: const Icon(Icons.map_outlined),
                              label: const Text('지도에서 위치 보기')),
                        if (cabinet.assetInfo.latitude == null ||
                            cabinet.assetInfo.longitude == null)
                          const Text('좌표 없음'),
                        const Text(
                            '지도: 온라인 · 기록: 기기 저장',
                            style: TextStyle(fontSize: 12)),
                        const Divider(),
                        Text(
                            '핵심 신호 · ${cabinet.detectedSignals.isEmpty ? '미관측' : operationalSignalTitle(signal)}',
                            style: Theme.of(context).textTheme.titleSmall),
                        const SizedBox(height: 6),
                        const Text(
                            '확인 · 제어기 → 동시간대 자료 → 지속 시 현장'),
                        const SizedBox(height: 6),
                        Text(evidenceSummary,
                            style: Theme.of(context).textTheme.bodySmall),
                        const SizedBox(height: 8),
                        Text(
                            '다음 조치 · ${operationalRecommendedAction(cabinet.status)}'),
                        const SizedBox(height: 12),
                        if (savedOutcome != null)
                          Text(
                              '기록 · ${_outcomeLabel(savedOutcome['outcomeCode'] ?? savedOutcome['status'] ?? '')} · ${savedOutcome['updatedAt'] ?? ''}'),
                      ]),
                ),
              ),
              const SizedBox(height: 8),
              _section(
                  '자산 정보',
                  [
                    _kv('가로등', '${cabinet.assetInfo.fixtureCount}개'),
                    _kv('조명 규격', _fixtureLampType(cabinet)),
                    _kv('정격용량',
                        '${cabinet.expectedLoad.ratedPowerW.toStringAsFixed(1)} W'),
                    if (_displayLocation(cabinet) case final location?)
                      _kv('설치 위치', location),
                    _kv('자산 자료 출처', operationalAssetSourceLabel(cabinet)),
                    _kv('전력 신호 출처', operationalSignalSourceLabel(cabinet)),
                    _kv('정비 이력', '미연결'),
                  ],
                  keySuffix: 'cabinet-section-summary-a',
                  collapsed: true),
              const SizedBox(height: 8),
              _section('관측 상태', [
                const Text('AMI 미연결 · 현재 전력 상태 판단 불가'),
                const Text('공식 계량기·분전함 연결표와 해당 계량기 측정자료가 필요합니다.'),
              ], collapsed: true),
              const SizedBox(height: 8),
              _section(
                '전력 신호',
                [
                  const Text(
                    '연결된 계량기 관측이 있을 때만 표시',
                    key: Key('section-cabinet-section-summary-c-description'),
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  const SizedBox(height: 16),
                  if (signal == null)
                    const Text('AMI 미연결 · 현재 상태 판단 불가')
                  else ...[
                    LinearProgressIndicator(
                      minHeight: 18,
                      value: signal.maxActivation.clamp(0.0, 1.0),
                      color: const Color(0xFF0F766E),
                      backgroundColor: const Color(0xFFDDE7E4),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    const SizedBox(height: 8),
                    Text(
                        '신호 수준 · ${operationalSignalLevel(signal)}'),
                    const SizedBox(height: 10),
                    const _ActivationLegend(),
                  ],
                  _kv(
                      '신호',
                      signal == null
                          ? '관측 자료 없음'
                          : operationalSignalTitle(signal)),
                ],
                keySuffix: 'cabinet-section-summary-c',
              ),
              const SizedBox(height: 8),
              _section(
                '판단 근거',
                [
                  _kv('관측 내용', operationalPriorityReason(cabinet)),
                  _kv('적용 판정 기준', operationalCriteria(cabinet)),
                  _kv(
                      '기록 시각',
                      signal == null
                          ? '신호 시각 자료 없음'
                          : '${signal.firstSample} ~ ${signal.lastSample}'),
                  _kv('신뢰도', operationalConfidenceLabel(signal)),
                  _kv('범위', operationalEvidenceBoundary(cabinet)),
                ],
                keySuffix: 'summary-d',
                collapsed: true,
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _recordFieldResult(String uid) async {
    var result = _outcomes[uid]?['outcomeCode'] ?? '';
    final note = TextEditingController(text: _outcomes[uid]?['note'] ?? '');
    final selected = await showModalBottomSheet<String>(
        context: context,
        isScrollControlled: true,
        builder: (context) => SafeArea(
            child: Padding(
                padding: EdgeInsets.fromLTRB(
                    20, 20, 20, MediaQuery.viewInsetsOf(context).bottom + 20),
                child: SingleChildScrollView(
                    child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                      Text('현장 확인 결과',
                          style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 8),
                      const Text('운영자 기록 · 기기 저장'),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                          initialValue: result,
                          decoration: const InputDecoration(labelText: '결과'),
                          items: const [
                            DropdownMenuItem(value: '', child: Text('결과 미기록')),
                            DropdownMenuItem(
                                value: 'fault_observed', child: Text('고장 관찰')),
                            DropdownMenuItem(
                                value: 'normal', child: Text('정상')),
                            DropdownMenuItem(
                                value: 'operational_exception',
                                child: Text('운영상 예외')),
                            DropdownMenuItem(
                                value: 'data_issue', child: Text('자료 문제')),
                            DropdownMenuItem(
                                value: 'action_completed', child: Text('조치 완료'))
                          ],
                          onChanged: (value) => result = value ?? ''),
                      const SizedBox(height: 8),
                      TextField(
                          controller: note,
                          maxLines: 3,
                          decoration: const InputDecoration(
                              labelText: '짧은 메모 (선택)',
                              border: OutlineInputBorder())),
                      const SizedBox(height: 12),
                      SizedBox(
                          width: double.infinity,
                          child: FilledButton(
                              onPressed: () => Navigator.pop(context, result),
                              child: const Text('기기에 저장')))
                    ])))));
    if (selected != null && mounted) {
      final outcomes = Map<String, Map<String, String>>.from(_outcomes);
      outcomes[uid] = {
        ...?_outcomes[uid],
        'status': _outcomeLabel(selected),
        'outcomeCode': selected,
        'stage': 'field_review',
        'note': note.text.trim(),
        'updatedAt': DateTime.now().toIso8601String()
      };
      try {
        await saveInspectionOutcomes(outcomes);
        if (mounted) setState(() => _outcomes = outcomes);
      } catch (error) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text('기록을 저장하지 못했습니다. 다시 시도해 주세요. ($error)'),
          ));
        }
      }
    }
    note.dispose();
  }

  String _outcomeLabel(String code) => switch (code) {
        'fault_observed' => '고장 관찰',
        'normal' => '정상',
        'operational_exception' => '운영상 예외',
        'data_issue' => '자료 문제',
        'action_completed' => '조치 완료',
        _ => code.isEmpty ? '결과 미기록' : code,
      };

  String _fixtureLampType(CabinetRecord cabinet) {
    final wattages = cabinet.assetInfo.fixtures
        .map((fixture) => fixture.lampWatt)
        .whereType<double>()
        .where((value) => value > 0)
        .toSet()
        .toList(growable: false)
      ..sort();
    if (wattages.isEmpty) return '자료 미제공';
    return wattages.map((w) => '${w.toStringAsFixed(0)}W').join(', ');
  }

  String? _displayLocation(CabinetRecord cabinet) {
    final location = cabinet.assetInfo.location.trim();
    final coordinateOnly = RegExp(
      r'^-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?$',
    ).hasMatch(location);
    if (location.isEmpty || coordinateOnly) return null;
    return location;
  }

  Widget _section(String title, List<Widget> children,
      {String? keySuffix, bool collapsed = false}) {
    final key = Key(keySuffix == null ? 'section-$title' : 'section-$keySuffix');
    if (collapsed) {
      return Card(
        key: key,
        child: ExpansionTile(
          title: Text(title,
              style: const TextStyle(fontWeight: FontWeight.w800)),
          childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
          children: _layoutSectionChildren(children),
        ),
      );
    }
    return Card(
      key: key,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
            const Divider(height: 22),
            ..._layoutSectionChildren(children),
          ],
        ),
      ),
    );
  }

  List<Widget> _layoutSectionChildren(List<Widget> children) {
    final result = <Widget>[];
    final fields = <_InfoField>[];

    void flushFields() {
      if (fields.isEmpty) return;
      result.add(_InfoGrid(fields: List<_InfoField>.of(fields)));
      fields.clear();
    }

    for (final child in children) {
      if (child is _InfoField) {
        fields.add(child);
      } else {
        flushFields();
        result.add(child);
      }
    }
    flushFields();
    return result;
  }

  _InfoField _kv(String label, String value) =>
      _InfoField(label: label, value: value);
}

class _InfoGrid extends StatelessWidget {
  const _InfoGrid({required this.fields});

  final List<_InfoField> fields;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
        builder: (context, constraints) {
          final columns = constraints.maxWidth >= 980
              ? 3
              : constraints.maxWidth >= 620
                  ? 2
                  : 1;
          const gap = 10.0;
          final width = (constraints.maxWidth - (columns - 1) * gap) / columns;
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Wrap(
              spacing: gap,
              runSpacing: gap,
              children: [
                for (final field in fields)
                  SizedBox(width: width, child: field),
              ],
            ),
          );
        },
      );
}

class _InfoField extends StatelessWidget {
  const _InfoField({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Container(
        constraints: const BoxConstraints(minHeight: 76),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFFF5F7F6),
          border: Border.all(color: const Color(0xFFDDE5E2)),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: const TextStyle(
                color: Color(0xFF5C6B73),
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 6),
            Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
          ],
        ),
      );
}

class _ActivationLegend extends StatelessWidget {
  const _ActivationLegend();

  @override
  Widget build(BuildContext context) => const Wrap(
        key: Key('activation-chart-legend'),
        spacing: 14,
        runSpacing: 8,
        children: [
          _LegendItem(
            color: Color(0xFF0F766E),
            label: '신호 수준',
            detail: '관측 최대치',
          ),
          _LegendItem(
            color: Color(0xFFDDE7E4),
            label: '남은 구간',
            detail: '기준 미충족',
          ),
        ],
      );
}

class _LegendItem extends StatelessWidget {
  const _LegendItem({
    required this.color,
    required this.label,
    required this.detail,
  });

  final Color color;
  final String label;
  final String detail;

  @override
  Widget build(BuildContext context) => Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 6),
          Text('$label · $detail',
              style: Theme.of(context).textTheme.bodySmall),
        ],
      );
}
