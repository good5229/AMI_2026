import 'dart:convert';

import 'package:flutter/material.dart';

const _evidenceAsset =
    'assets/data/evidence/v27_evidence_strengthening.json';
const _ink = Color(0xFF163632);
const _teal = Color(0xFF0F766E);
const _paleTeal = Color(0xFFEAF5F2);
const _yellow = Color(0xFFF2C14E);
const _paleYellow = Color(0xFFFFF7DD);

class EvidenceStrengtheningPanel extends StatefulWidget {
  const EvidenceStrengtheningPanel({super.key});

  @override
  State<EvidenceStrengtheningPanel> createState() =>
      _EvidenceStrengtheningPanelState();
}

class _EvidenceStrengtheningPanelState
    extends State<EvidenceStrengtheningPanel> {
  AssetBundle? _bundle;
  Future<_EvidencePackage>? _evidence;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final bundle = DefaultAssetBundle.of(context);
    if (!identical(bundle, _bundle)) {
      _bundle = bundle;
      _evidence = _loadEvidence(bundle);
    }
  }

  Future<_EvidencePackage> _loadEvidence(AssetBundle bundle) async {
    final raw = await bundle.loadString(_evidenceAsset);
    final decoded = jsonDecode(raw);
    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('v0.27 evidence asset must be an object');
    }
    return _EvidencePackage.fromJson(decoded);
  }

  void _retry() {
    setState(() {
      _evidence = _loadEvidence(DefaultAssetBundle.of(context));
    });
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<_EvidencePackage>(
      future: _evidence,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const _PanelStateCard(
            key: Key('v27-evidence-loading'),
            child: Row(
              children: [
                SizedBox(
                  width: 22,
                  height: 22,
                  child: CircularProgressIndicator(strokeWidth: 2.5),
                ),
                SizedBox(width: 12),
                Expanded(child: Text('근거와 적용 준비 자료를 불러오는 중입니다.')),
              ],
            ),
          );
        }
        if (snapshot.hasError || !snapshot.hasData) {
          return _PanelStateCard(
            key: const Key('v27-evidence-error'),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '근거 자료를 불러오지 못했습니다.',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 4),
                const Text('후보 자료는 계속 볼 수 있습니다. 잠시 후 다시 시도해 주세요.'),
                const SizedBox(height: 10),
                OutlinedButton.icon(
                  onPressed: _retry,
                  icon: const Icon(Icons.refresh),
                  label: const Text('다시 시도'),
                ),
              ],
            ),
          );
        }
        return _EvidenceBody(evidence: snapshot.requireData);
      },
    );
  }
}

class _PanelStateCard extends StatelessWidget {
  const _PanelStateCard({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) => Card(
        color: _paleTeal,
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: child,
        ),
      );
}

class _EvidenceBody extends StatelessWidget {
  const _EvidenceBody({required this.evidence});

  final _EvidencePackage evidence;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      container: true,
      label: 'v0.27 근거 강화',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            key: const Key('v27-evidence-positioning'),
            decoration: BoxDecoration(
              color: _ink,
              borderRadius: BorderRadius.circular(18),
            ),
            clipBehavior: Clip.antiAlias,
            child: IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(width: 7, child: ColoredBox(color: _yellow)),
                  Expanded(
                    child: Padding(
                    padding: const EdgeInsets.fromLTRB(18, 20, 18, 20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          evidence.title,
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.w800,
                              ),
                        ),
                        if (evidence.positioning.isNotEmpty) ...[
                          const SizedBox(height: 10),
                          for (final paragraph in evidence.positioning)
                            Padding(
                              padding: const EdgeInsets.only(bottom: 6),
                              child: Text(
                                paragraph,
                                style: const TextStyle(
                                  color: Color(0xFFE4F1EE),
                                  height: 1.45,
                                ),
                              ),
                            ),
                        ],
                        const SizedBox(height: 8),
                        const Text(
                          '현장 고장 정확도와 실현 절감 효과는 현장 연결 전까지 입증 범위가 아닙니다.',
                          key: Key('v27-scope-boundary'),
                          style: TextStyle(
                            color: Color(0xFFFFE49B),
                            fontWeight: FontWeight.w700,
                            height: 1.4,
                          ),
                        ),
                      ],
                    ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (evidence.claimBoundaries.isNotEmpty) ...[
            const SizedBox(height: 12),
            _BoundaryBox(
              title: '공통 주장 경계',
              paragraphs: evidence.claimBoundaries,
            ),
          ],
          const SizedBox(height: 16),
          for (var index = 0; index < evidence.stages.length; index++) ...[
            _EvidenceStageCard(stage: evidence.stages[index]),
            if (index != evidence.stages.length - 1)
              const SizedBox(height: 10),
          ],
        ],
      ),
    );
  }
}

class _EvidenceStageCard extends StatelessWidget {
  const _EvidenceStageCard({required this.stage});

  final _EvidenceStage stage;

  bool get _isTechnical => stage.id == 'technical' ||
      stage.id == 'technical_evidence' ||
      stage.id.contains('technical');

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      elevation: 0,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Color(0xFFBCD5CF)),
      ),
      child: ExpansionTile(
        key: Key('v27-stage-${stage.id}'),
        initiallyExpanded: _isTechnical,
        tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 18),
        expandedCrossAxisAlignment: CrossAxisAlignment.stretch,
        iconColor: _teal,
        collapsedIconColor: _ink,
        backgroundColor: Colors.white,
        collapsedBackgroundColor: Colors.white,
        shape: const Border(),
        collapsedShape: const Border(),
        title: Text(
          '${stage.order}. ${stage.title}',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: _ink,
                fontWeight: FontWeight.w800,
              ),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 7),
          child: Align(
            alignment: Alignment.centerLeft,
            child: DecoratedBox(
              decoration: BoxDecoration(
                color: _paleTeal,
                borderRadius: BorderRadius.circular(999),
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
                child: Text(
                  stage.statusLabel,
                  style: const TextStyle(
                    color: _teal,
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ),
          ),
        ),
        children: [
          Container(
            key: Key('v27-stage-body-${stage.id}'),
            padding: const EdgeInsets.only(top: 4),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(stage.summary, style: const TextStyle(height: 1.5)),
                if (stage.id == 'external_context') ...[
                  const SizedBox(height: 12),
                  const _ExternalContextNotice(),
                ],
                if (stage.metrics.isNotEmpty) ...[
                  const SizedBox(height: 14),
                  LayoutBuilder(
                    builder: (context, constraints) {
                      final itemWidth = constraints.maxWidth >= 680
                          ? (constraints.maxWidth - 10) / 2
                          : constraints.maxWidth;
                      return Wrap(
                        spacing: 10,
                        runSpacing: 10,
                        children: [
                          for (final metric in stage.metrics)
                            SizedBox(
                              width: itemWidth,
                              child: _MetricCard(metric: metric),
                            ),
                        ],
                      );
                    },
                  ),
                ],
                if (stage.joinChain.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Text(
                    '현장 데이터 연결 순서',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: _ink,
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                  const SizedBox(height: 7),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: _paleTeal,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: SelectableText(
                      stage.joinChain,
                      key: const Key('v27-field-join-chain'),
                      style: const TextStyle(
                        color: _ink,
                        fontWeight: FontWeight.w700,
                        height: 1.5,
                      ),
                    ),
                  ),
                ],
                if (stage.requiredData.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Text(
                    '현장 검증에 필요한 자료',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: _ink,
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                  const SizedBox(height: 6),
                  for (final item in stage.requiredData)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 5),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Padding(
                            padding: EdgeInsets.only(top: 8),
                            child: SizedBox(
                              width: 6,
                              height: 6,
                              child: DecoratedBox(
                                decoration: BoxDecoration(
                                  color: _teal,
                                  shape: BoxShape.circle,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 9),
                          Expanded(child: Text(item, style: const TextStyle(height: 1.4))),
                        ],
                      ),
                    ),
                ],
                if (stage.boundary.isNotEmpty) ...[
                  const SizedBox(height: 14),
                  _BoundaryBox(
                    title: '이 단계의 해석 범위',
                    paragraphs: [stage.boundary],
                  ),
                ],
                const SizedBox(height: 12),
                Row(
                  children: [
                    const Icon(Icons.verified_outlined, size: 17, color: _teal),
                    const SizedBox(width: 6),
                    Text(
                      '근거 자료 ${stage.sourceCount}개',
                      key: Key('v27-source-count-${stage.id}'),
                      style: const TextStyle(
                        color: Color(0xFF46645F),
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ExternalContextNotice extends StatelessWidget {
  const _ExternalContextNotice();

  @override
  Widget build(BuildContext context) => Container(
        key: const Key('v27-external-context-notice'),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: _paleYellow,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFFE8CB72)),
        ),
        child: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '실제 AMI 미연결 · 기상자료는 참고용',
              style: TextStyle(color: _ink, fontWeight: FontWeight.w800),
            ),
            SizedBox(height: 4),
            Text(
              '현재 자료는 외부요인을 설명하는 맥락이며, 보정 효과나 오탐 감소를 입증한 결과가 아닙니다.',
              style: TextStyle(height: 1.4),
            ),
          ],
        ),
      );
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({required this.metric});

  final _EvidenceMetric metric;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(13),
        decoration: BoxDecoration(
          color: const Color(0xFFF4F8F6),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFD4E3DF)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              metric.label,
              style: const TextStyle(
                color: Color(0xFF46645F),
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              metric.value,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: _ink,
                    fontWeight: FontWeight.w900,
                  ),
            ),
            if (metric.qualification.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(
                metric.qualification,
                style: const TextStyle(fontSize: 12, height: 1.4),
              ),
            ],
          ],
        ),
      );
}

class _BoundaryBox extends StatelessWidget {
  const _BoundaryBox({required this.title, required this.paragraphs});

  final String title;
  final List<String> paragraphs;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(13),
        decoration: BoxDecoration(
          color: _paleYellow,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE8CB72)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.info_outline, size: 18, color: Color(0xFF765C08)),
                const SizedBox(width: 7),
                Expanded(
                  child: Text(
                    title,
                    style: const TextStyle(
                      color: _ink,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            for (final paragraph in paragraphs)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(paragraph, style: const TextStyle(height: 1.4)),
              ),
          ],
        ),
      );
}

class _EvidencePackage {
  const _EvidencePackage({
    required this.title,
    required this.positioning,
    required this.stages,
    required this.claimBoundaries,
  });

  factory _EvidencePackage.fromJson(Map<String, dynamic> json) {
    final stages = _mapList(json['ordered_stages'])
        .map(_EvidenceStage.fromJson)
        .toList(growable: false)
      ..sort((a, b) => a.order.compareTo(b.order));
    if (stages.length != 5) {
      throw FormatException(
        'v0.27 evidence asset must contain five stages; found ${stages.length}',
      );
    }
    return _EvidencePackage(
      title: _string(json['title'], fallback: '근거와 적용 준비'),
      positioning: _textItems(json['positioning']),
      stages: stages,
      claimBoundaries: _textItems(json['claim_boundaries']),
    );
  }

  final String title;
  final List<String> positioning;
  final List<_EvidenceStage> stages;
  final List<String> claimBoundaries;
}

class _EvidenceStage {
  const _EvidenceStage({
    required this.order,
    required this.id,
    required this.title,
    required this.statusLabel,
    required this.summary,
    required this.metrics,
    required this.boundary,
    required this.sourceCount,
    required this.joinChain,
    required this.requiredData,
  });

  factory _EvidenceStage.fromJson(Map<String, dynamic> json) {
    final orderValue = json['order'];
    final order = orderValue is num
        ? orderValue.toInt()
        : int.tryParse(orderValue?.toString() ?? '') ?? 0;
    return _EvidenceStage(
      order: order,
      id: _string(json['id'], fallback: 'stage-$order'),
      title: _string(json['title'], fallback: '근거 단계'),
      statusLabel: _string(json['status_label'], fallback: '상태 확인 필요'),
      summary: _string(json['summary']),
      metrics: _mapList(json['metrics'])
          .map(_EvidenceMetric.fromJson)
          .toList(growable: false),
      boundary: _textItems(json['boundary']).join('\n'),
      sourceCount: _itemCount(json['sources']),
      joinChain: _joinChain(json['join_chain']),
      requiredData: _textItems(json['required_data']),
    );
  }

  final int order;
  final String id;
  final String title;
  final String statusLabel;
  final String summary;
  final List<_EvidenceMetric> metrics;
  final String boundary;
  final int sourceCount;
  final String joinChain;
  final List<String> requiredData;
}

class _EvidenceMetric {
  const _EvidenceMetric({
    required this.label,
    required this.value,
    required this.qualification,
  });

  factory _EvidenceMetric.fromJson(Map<String, dynamic> json) =>
      _EvidenceMetric(
        label: _string(json['label'], fallback: '지표'),
        value: _string(json['value'], fallback: '미제공'),
        qualification: _string(json['qualification']),
      );

  final String label;
  final String value;
  final String qualification;
}

List<Map<String, dynamic>> _mapList(Object? value) {
  if (value is! List) return const [];
  return value
      .whereType<Map<Object?, Object?>>()
      .map((item) => item.map((key, value) => MapEntry(key.toString(), value)))
      .toList(growable: false);
}

String _string(Object? value, {String fallback = ''}) {
  final text = value?.toString().trim() ?? '';
  return text.isEmpty ? fallback : text;
}

List<String> _textItems(Object? value) {
  if (value == null) return const [];
  if (value is String || value is num || value is bool) {
    final text = value.toString().trim();
    return text.isEmpty ? const [] : [text];
  }
  if (value is List) {
    return value.expand(_textItems).toList(growable: false);
  }
  if (value is Map) {
    return value.values.expand(_textItems).toList(growable: false);
  }
  return const [];
}

int _itemCount(Object? value) {
  if (value is List) return value.length;
  if (value is Map) return value.length;
  return value == null || value.toString().trim().isEmpty ? 0 : 1;
}

String _joinChain(Object? value) {
  if (value is List) return _textItems(value).join(' → ');
  return _textItems(value).join(' → ');
}
