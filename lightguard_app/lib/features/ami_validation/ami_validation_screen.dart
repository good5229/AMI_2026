import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/repositories/lightguard_repository.dart';

class AmiValidationScreen extends ConsumerWidget {
  const AmiValidationScreen({super.key});

  static const disclaimer =
      '공모전 제공 가명화 AMI에서 탐지한 점검 후보이며, 실제 현장 고장 여부는 정비 이력/현장 확인이 필요합니다.';

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventsAsync = ref.watch(competitionAmiEventsProvider);
    return eventsAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (error, _) =>
          Scaffold(body: Center(child: Text('실제 공모전 AMI 데이터 로드 실패: $error'))),
      data: (events) {
        final featured = events.where(_isFeatured).toList(growable: false);
        final excessKwh = events.fold<double>(
            0, (sum, event) => sum + event.estimatedExcessKwh);

        return LightguardShell(
          title: '실제 공모전 AMI Case Study',
          child: ListView(
            padding: const EdgeInsets.all(12),
            children: [
              _SummaryCard(eventCount: events.length, excessKwh: excessKwh),
              const SizedBox(height: 12),
              Text('대표 Case Study 3건',
                  style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 4),
              const Text(
                  '원시 시계열을 임의 생성하지 않고 이벤트 CSV의 OFF baseline, 관측 peak, ON baseline을 비교합니다.'),
              const SizedBox(height: 10),
              LayoutBuilder(
                builder: (context, constraints) {
                  final cardWidth = constraints.maxWidth >= 1080
                      ? (constraints.maxWidth - 24) / 3
                      : constraints.maxWidth >= 700
                          ? (constraints.maxWidth - 12) / 2
                          : constraints.maxWidth;
                  return Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      for (final event in featured)
                        SizedBox(
                            width: cardWidth,
                            child: _CaseStudyCard(event: event)),
                    ],
                  );
                },
              ),
              const SizedBox(height: 20),
              Text('전체 점검 후보 ${events.length}건',
                  style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              for (final event in events) _EventSummaryCard(event: event),
              const SizedBox(height: 8),
              const Card(
                color: Color(0xFFFFF7E6),
                child: Padding(
                  padding: EdgeInsets.all(14),
                  child: Text(disclaimer,
                      style: TextStyle(fontWeight: FontWeight.w600)),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  bool _isFeatured(ValidationEvent event) {
    return (event.meterId == 'B-L-35' &&
            event.firstSample.startsWith('2026-05-11')) ||
        (event.meterId == 'B-L-9' &&
            event.firstSample.startsWith('2026-05-20')) ||
        (event.meterId == 'B-L-14' &&
            event.firstSample.startsWith('2026-05-29'));
  }
}

class _SummaryCard extends StatelessWidget {
  const _SummaryCard({required this.eventCount, required this.excessKwh});

  final int eventCount;
  final double excessKwh;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFFEAF3F8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Wrap(
              spacing: 8,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                StatusBadge(type: BadgeType.realAmi, label: '실제 공모전 AMI'),
                StatusBadge(type: BadgeType.validation, label: '현장 미확인 점검 후보'),
              ],
            ),
            const SizedBox(height: 12),
            Text('가명화 AMI에서 발견한 점검 후보 $eventCount건',
                style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 6),
            Text('후보 구간 추정 초과전력량 합계 ${excessKwh.toStringAsFixed(3)} kWh'),
            const SizedBox(height: 6),
            const Text('전기요금은 근거 단가가 없어 환산하지 않습니다.'),
          ],
        ),
      ),
    );
  }
}

class _CaseStudyCard extends StatelessWidget {
  const _CaseStudyCard({required this.event});

  final ValidationEvent event;

  @override
  Widget build(BuildContext context) {
    final date = event.firstSample.split(' ').first;
    return Card(
      key: Key('ami-case-${event.meterId}-$date'),
      clipBehavior: Clip.antiAlias,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                    child: Text(event.meterId,
                        style: Theme.of(context).textTheme.titleLarge)),
                const StatusBadge(type: BadgeType.realAmi, label: '실제 공모전 AMI'),
              ],
            ),
            const SizedBox(height: 6),
            Text(_eventLabel(event.eventType),
                style: const TextStyle(fontWeight: FontWeight.w700)),
            Text(
                '${event.firstSample} ~ ${event.lastSample} · ${event.durationMin}분'),
            const Divider(height: 24),
            _EvidenceBars(event: event),
            const Divider(height: 24),
            _kv('Max activation',
                '${(event.maxActivation * 100).toStringAsFixed(1)}%'),
            _kv('Active phases', event.activePhases),
            _kv('Estimated excess',
                '${event.estimatedExcessKwh.toStringAsFixed(3)} kWh'),
            _kv('Pattern confidence', event.patternConfidence),
            _kv('Fault status', '현장 미확인 점검 후보'),
            _kv('Source mode', '가명화 공모전 AMI 검증'),
            const SizedBox(height: 10),
            const Text(AmiValidationScreen.disclaimer,
                style: TextStyle(fontSize: 12, color: Color(0xFF6B4D00))),
          ],
        ),
      ),
    );
  }
}

class _EvidenceBars extends StatelessWidget {
  const _EvidenceBars({required this.event});

  final ValidationEvent event;

  @override
  Widget build(BuildContext context) {
    final maxValue = <double>[
      event.offBaselineA,
      event.peakCurrentA,
      event.onBaselineA
    ].reduce((a, b) => a > b ? a : b);
    return Column(
      children: [
        _EvidenceBar(
            label: 'OFF baseline',
            value: event.offBaselineA,
            maxValue: maxValue),
        _EvidenceBar(
            label: 'Observed peak',
            value: event.peakCurrentA,
            maxValue: maxValue),
        _EvidenceBar(
            label: 'ON baseline', value: event.onBaselineA, maxValue: maxValue),
      ],
    );
  }
}

class _EvidenceBar extends StatelessWidget {
  const _EvidenceBar(
      {required this.label, required this.value, required this.maxValue});

  final String label;
  final double value;
  final double maxValue;

  @override
  Widget build(BuildContext context) {
    final ratio = maxValue <= 0 ? 0.0 : (value / maxValue).clamp(0.0, 1.0);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
              width: 92,
              child: Text(label, style: const TextStyle(fontSize: 12))),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(5),
              child: SizedBox(
                height: 12,
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: FractionallySizedBox(
                    widthFactor: ratio,
                    child: ColoredBox(
                      color: label == 'Observed peak'
                          ? const Color(0xFFE76F51)
                          : const Color(0xFF2A6F97),
                    ),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
              width: 58,
              child: Text('${value.toStringAsFixed(2)}A',
                  textAlign: TextAlign.end)),
        ],
      ),
    );
  }
}

class _EventSummaryCard extends StatelessWidget {
  const _EventSummaryCard({required this.event});

  final ValidationEvent event;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ExpansionTile(
        leading: const Icon(Icons.bolt_outlined),
        title: Text('${event.meterId} · ${_eventLabel(event.eventType)}'),
        subtitle: Text(
            '${event.firstSample} · ${event.durationMin}분 · ${(event.maxActivation * 100).toStringAsFixed(1)}%'),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _kv('Event ID', event.eventId),
          _kv('Active phases', event.activePhases),
          _kv('Estimated excess',
              '${event.estimatedExcessKwh.toStringAsFixed(3)} kWh'),
          _kv('Pattern confidence', event.patternConfidence),
          _kv('Fault status', '현장 미확인 점검 후보'),
          _kv('Source mode', '가명화 공모전 AMI 검증'),
        ],
      ),
    );
  }
}

Widget _kv(String label, String value) {
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 3),
    child: Wrap(
      spacing: 8,
      runSpacing: 2,
      children: [
        SizedBox(
            width: 118,
            child: Text(label,
                style: const TextStyle(fontWeight: FontWeight.w600))),
        Text(value.isEmpty ? '미제공' : value),
      ],
    ),
  );
}

String _eventLabel(String eventType) {
  return switch (eventType) {
    'daytime_full_activation' => '주간 전체 활성 의심',
    'daytime_partial_activation' => '주간 부분 활성 의심',
    'daytime_phase_selective_activation' => '주간 상 선택 활성 의심',
    _ => eventType,
  };
}
