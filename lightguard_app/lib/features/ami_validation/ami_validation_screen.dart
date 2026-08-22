import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/repositories/lightguard_repository.dart';

class AmiValidationScreen extends ConsumerWidget {
  const AmiValidationScreen({super.key});
  static const disclaimer = '이 화면은 지역 선택과 별도로 제공된 가명 전력계량 자료의 이상 신호를 보여줍니다. 실제 고장 여부는 정비 이력 또는 현장 확인으로 확정해야 합니다.';

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventsAsync = ref.watch(competitionAmiEventsProvider);
    return eventsAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (error, _) => const Scaffold(body: Center(child: Text('전력계량 자료를 불러오지 못했습니다.'))),
      data: (events) {
        final featured = events.where(_isFeatured).toList(growable: false);
        final excessKwh = events.fold<double>(0, (sum, event) => sum + event.estimatedExcessKwh);
        return LightguardShell(
          title: '전력계량 이상 신호 근거',
          child: ListView(
            padding: const EdgeInsets.all(12),
            children: [
              Card(
                color: const Color(0xFFEAF3F8),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    const Wrap(spacing: 8, runSpacing: 8, children: [
                      StatusBadge(type: BadgeType.realAmi, label: '가명 처리 전력계량 자료'),
                      StatusBadge(type: BadgeType.validation, label: '고장 여부 미확인 이상 신호'),
                    ]),
                    const SizedBox(height: 12),
                    Text('현장 확인 전 이상 신호 ${events.length}건', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 6),
                    Text('정상 비교값 대비 추정 초과 전력사용량 합계 ${excessKwh.toStringAsFixed(3)} kWh'),
                  ]),
                ),
              ),
              const SizedBox(height: 12),
              Text('대표 이상 신호 비교', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 4),
              const Text('정상 시간대와 실제 관측값의 차이를 비교합니다.'),
              const SizedBox(height: 10),
              LayoutBuilder(builder: (context, constraints) {
                final width = constraints.maxWidth >= 1080 ? (constraints.maxWidth - 24) / 3 : constraints.maxWidth >= 700 ? (constraints.maxWidth - 12) / 2 : constraints.maxWidth;
                return Wrap(spacing: 12, runSpacing: 12, children: [for (final event in featured) SizedBox(width: width, child: _CaseCard(event: event))]);
              }),
              const SizedBox(height: 20),
              Text('전체 이상 신호 ${events.length}건', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              for (final event in events) _EventCard(event: event),
              const SizedBox(height: 8),
              const Card(color: Color(0xFFFFF7E6), child: Padding(padding: EdgeInsets.all(14), child: Text(disclaimer, style: TextStyle(fontWeight: FontWeight.w600)))),
            ],
          ),
        );
      },
    );
  }

  bool _isFeatured(ValidationEvent event) =>
      (event.meterId == 'B-L-35' && event.firstSample.startsWith('2026-05-11')) ||
      (event.meterId == 'B-L-9' && event.firstSample.startsWith('2026-05-20')) ||
      (event.meterId == 'B-L-14' && event.firstSample.startsWith('2026-05-29'));
}

class _CaseCard extends StatelessWidget {
  const _CaseCard({required this.event});
  final ValidationEvent event;

  @override
  Widget build(BuildContext context) {
    final date = event.firstSample.split(' ').first;
    return Card(
      key: Key('ami-case-${event.meterId}-$date'),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [Expanded(child: Text(event.meterId, style: Theme.of(context).textTheme.titleLarge)), const StatusBadge(type: BadgeType.realAmi, label: '전력계량 자료')]),
          const SizedBox(height: 6),
          Text(_eventLabel(event.eventType), style: const TextStyle(fontWeight: FontWeight.w700)),
          Text('${event.firstSample} ~ ${event.lastSample} · ${event.durationMin}분'),
          const Divider(height: 24),
          _bar('소등 시간대 정상 비교값', event.offBaselineA, event.peakCurrentA, false),
          _bar('실제 관측 최대값', event.peakCurrentA, event.peakCurrentA, true),
          _bar('점등 시간대 정상 비교값', event.onBaselineA, event.peakCurrentA, false),
          const Divider(height: 24),
          _kv('탐지 기준 대비 최대 신호 비율', '${(event.maxActivation * 100).toStringAsFixed(1)}%'),
          _kv('신호가 확인된 전류선', _phaseLabel(event.activePhases)),
          _kv('정상 대비 추정 초과 전력사용량', '${event.estimatedExcessKwh.toStringAsFixed(3)} kWh'),
          _kv('이상 신호 형태 일치 수준', _confidenceLabel(event.patternConfidence)),
          _kv('고장 확인 여부', '현장 확인 전'),
        ]),
      ),
    );
  }
}

class _EventCard extends StatelessWidget {
  const _EventCard({required this.event});
  final ValidationEvent event;
  @override
  Widget build(BuildContext context) => Card(
    child: ExpansionTile(
      leading: const Icon(Icons.bolt_outlined),
      title: Text('${event.meterId} · ${_eventLabel(event.eventType)}'),
      subtitle: Text('${event.firstSample} · 지속 ${event.durationMin}분 · 최대 신호 ${(event.maxActivation * 100).toStringAsFixed(1)}%'),
      childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      expandedCrossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _kv('신호가 확인된 전류선', _phaseLabel(event.activePhases)),
        _kv('정상 대비 추정 초과 전력사용량', '${event.estimatedExcessKwh.toStringAsFixed(3)} kWh'),
        _kv('이상 신호 형태 일치 수준', _confidenceLabel(event.patternConfidence)),
        _kv('고장 확인 여부', '현장 확인 전'),
      ],
    ),
  );
}

Widget _bar(String label, double value, double maxValue, bool emphasized) {
  final ratio = maxValue <= 0 ? 0.0 : (value / maxValue).clamp(0.0, 1.0);
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 4),
    child: Row(children: [
      SizedBox(width: 96, child: Text(label, style: const TextStyle(fontSize: 12))),
      Expanded(child: ClipRRect(borderRadius: BorderRadius.circular(4), child: ColoredBox(color: const Color(0xFFE4EBE8), child: SizedBox(height: 12, child: Align(alignment: Alignment.centerLeft, child: FractionallySizedBox(widthFactor: ratio, child: ColoredBox(color: emphasized ? const Color(0xFF0F766E) : const Color(0xFF9FB7B3)))))))),
      const SizedBox(width: 8),
      SizedBox(width: 58, child: Text('${value.toStringAsFixed(2)}A', textAlign: TextAlign.end)),
    ]),
  );
}

Widget _kv(String label, String value) => Padding(
  padding: const EdgeInsets.symmetric(vertical: 3),
  child: Wrap(spacing: 8, runSpacing: 2, children: [
    SizedBox(width: 118, child: Text(label, style: const TextStyle(fontWeight: FontWeight.w600))),
    Text(value.isEmpty ? '미제공' : value, style: const TextStyle(fontWeight: FontWeight.w500)),
  ]),
);

String _phaseLabel(String value) {
  if (value.trim().isEmpty) return '정보 없음';
  const labels = {'i1': '1번 전류선(i1)', 'i2': '2번 전류선(i2)', 'i3': '3번 전류선(i3)'};
  return value.split(',').map((phase) => phase.trim().toLowerCase()).map((phase) => labels[phase] ?? phase).join(' · ');
}

String _confidenceLabel(String value) => switch (value.toLowerCase()) {
  'high' => '높음',
  'medium_high' || 'high_medium' => '보통 이상',
  'medium' => '보통',
  'low' => '낮음',
  _ => value.isEmpty ? '평가 정보 없음' : value,
};

String _eventLabel(String type) => switch (type) {
  'daytime_full_activation' => '주간 전체 활성 의심',
  'daytime_partial_activation' => '주간 부분 활성 의심',
  'daytime_phase_selective_activation' => '주간 상 선택 활성 의심',
  _ => type,
};
