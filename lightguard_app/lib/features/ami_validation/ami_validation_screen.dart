import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'v07_regional_seasonal_card.dart';
import 'v08_detector_card.dart';
import 'v09_specificity_card.dart';
import 'v10_real_background_card.dart';
import 'v11_anomaly_sign_card.dart';
import 'v12r_literature_card.dart';
import 'v13_external_validation_card.dart';
import 'v14_physical_external_card.dart';
import 'v15_target_mechanism_card.dart';
import 'v16_competition_utility_card.dart';
import 'municipal_operations_evidence_card.dart';
import 'nationwide_file_census_card.dart';
import 'submission_readiness_card.dart';

import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../core/presentation/plain_status.dart';
import '../../data/models/context_models.dart';
import '../../data/repositories/lightguard_repository.dart';

class AmiValidationScreen extends ConsumerWidget {
  const AmiValidationScreen({super.key});

  static const disclaimer =
      '공모전에서 제공한 가명 처리 전력계량 자료에서 찾은 확인 후보입니다. 실제 고장 여부는 정비 이력 또는 현장 확인이 필요합니다.';

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventsAsync = ref.watch(competitionAmiEventsProvider);
    final metrics = ref.watch(controlledMetricsProvider).asData?.value ??
        const <ControlledMetric>[];
    final v04Summary = ref.watch(v04ValidationSummaryProvider).asData?.value;
    final v05Summary = ref.watch(v05ValidationSummaryProvider).asData?.value;
    final v06Summary = ref.watch(v06EvidenceSummaryProvider).asData?.value;
    final replayWindows = ref.watch(amiReplayWindowsProvider).asData?.value ??
        const <String, List<AmiReplaySample>>{};
    return eventsAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (error, _) =>
          const Scaffold(
            body: Center(child: Text('공모전 전력계량 자료를 불러오지 못했습니다.')),
          ),
      data: (events) {
        final featured = events.where(_isFeatured).toList(growable: false);
        final excessKwh = events.fold<double>(
            0, (sum, event) => sum + event.estimatedExcessKwh);
        final representative = events.where((event) =>
            event.meterId == 'B-L-35' &&
            event.firstSample.startsWith('2026-05-11')).firstOrNull;

        return LightguardShell(
          title: '공모전 전력계량 자료 분석 근거',
          child: ListView(
            padding: const EdgeInsets.all(12),
            children: [
              _SummaryCard(eventCount: events.length, excessKwh: excessKwh),
              Text('대표 분석 사례 3건',
                  style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 4),
              const Text(
                  '측정값을 임의로 만들지 않고 파일에 기록된 소등 시간대 정상값, 관측 최대값, 점등 시간대 정상값을 비교합니다.'),
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
              const SizedBox(height: 12),
              _ControlledValidationSummary(
                  metrics: metrics, v04Summary: v04Summary),
              const SizedBox(height: 8),
              const _MetricReadingGuide(),
              if (v05Summary != null) ...[
                const SizedBox(height: 12),
                _V05TechnicalEvidence(summary: v05Summary),
              ],
              if (v06Summary != null) ...[
                const SizedBox(height: 12),
                _ResearchEvidenceSection(
                  child: _V06EvidenceHardening(summary: v06Summary),
                ),
              ],
              const SizedBox(height: 12),
              if (representative != null &&
                  replayWindows['B-L-35_2026-05-11.csv']?.isNotEmpty == true)
                _ActualReplayCard(
                  event: representative,
                  samples: replayWindows['B-L-35_2026-05-11.csv']!,
                  windowCount: replayWindows.length,
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

class _MetricReadingGuide extends StatelessWidget {
  const _MetricReadingGuide();

  @override
  Widget build(BuildContext context) {
    return const Card(
      color: Color(0xFFF5F7F8),
      child: Padding(
        padding: EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('수치 읽는 방법',
                style: TextStyle(fontWeight: FontWeight.w700)),
            SizedBox(height: 6),
            Text('• 탐지율: 검증용 이상 사례를 찾아낸 비율이며 높을수록 좋습니다.'),
            Text('• 정상 오분류율: 정상 상태를 이상으로 잘못 표시한 비율이며 낮을수록 좋습니다.'),
            Text('• 우선 확인 대상 일치율: 먼저 확인하도록 제시한 대상 중 검증 기준과 일치한 비율입니다.'),
            SizedBox(height: 6),
            Text('현장 고장 정답이 없는 결과는 실제 정확도로 해석하지 않습니다.',
                style: TextStyle(fontWeight: FontWeight.w700)),
          ],
        ),
      ),
    );
  }
}

class _ResearchEvidenceSection extends StatelessWidget {
  const _ResearchEvidenceSection({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ExpansionTile(
        key: const Key('research-evidence-expansion'),
        initiallyExpanded: false,
        leading: const Icon(Icons.science_outlined),
        title: const Text('상세 검증자료'),
        subtitle: const Text('연구 과정과 통계 검증이 필요할 때 펼쳐 봅니다.'),
        childrenPadding: const EdgeInsets.fromLTRB(8, 0, 8, 8),
        children: [child],
      ),
    );
  }
}

class _V06EvidenceHardening extends StatelessWidget {
  const _V06EvidenceHardening({required this.summary});

  final V06EvidenceSummary summary;

  @override
  Widget build(BuildContext context) {
    String percent(double value, [int digits = 1]) =>
        '${(value * 100).toStringAsFixed(digits)}%';
    return Card(
      key: const Key('v06-evidence-hardening'),
      color: const Color(0xFFF4F1E8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const V07RegionalSeasonalCard(),
            const SizedBox(height: 16),
            const V08DetectorCard(),
            const SizedBox(height: 16),
            const V09SpecificityCard(),
            const V10RealBackgroundCard(),
            const SizedBox(height: 16),
            const V11AnomalySignCard(),
            const SizedBox(height: 16),
            const V12RLiteratureCard(),
            const SizedBox(height: 16),
            const V13ExternalValidationCard(),
            const SizedBox(height: 16),
            const V14PhysicalExternalCard(),
            const SizedBox(height: 16),
            const V15TargetMechanismCard(),
            const SizedBox(height: 16),
            const V16CompetitionUtilityCard(),
            const SizedBox(height: 16),
            const SubmissionReadinessCard(),
            const SizedBox(height: 12),
            const MunicipalOperationsEvidenceCard(),
            const SizedBox(height: 16),
            const NationwideFileCensusCard(),
            const SizedBox(height: 16),
            Text('검증 근거와 불확실성',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 6),
            const Text(
              '6/6은 field recall이 아닙니다. 작은 표본의 불확실성과 판정 불가 조건을 함께 표시합니다.',
              style: TextStyle(fontSize: 12),
            ),
            const SizedBox(height: 12),
            Wrap(spacing: 10, runSpacing: 10, children: [
              _V05EvidenceTile(
                title: '알려진 이상 사례 탐지',
                value: percent(summary.coveragePoint),
                detail:
                    'Wilson 95% ${percent(summary.coverageLower)}–${percent(summary.coverageUpper)}',
              ),
              _V05EvidenceTile(
                title: '하루 평균 확인 후보 비율',
                value: percent(summary.candidateDensityPoint, 2),
                detail:
                    'Stationary bootstrap ${percent(summary.candidateDensityLower, 2)}–${percent(summary.candidateDensityUpper, 2)}',
              ),
              _V05EvidenceTile(
                title: '자료 부족 시 판정 보류 기준',
                value: '${summary.abstentionRuleCount} rules',
                detail: '120분 gap은 DATA_INSUFFICIENT',
              ),
            ]),
            const SizedBox(height: 10),
            Text(
              '두 조건이 동시에 바뀔 때 정상 오분류율의 최대 변화: ${summary.largestInteractionTerm} · ${(summary.largestInteractionEffect * 100).toStringAsFixed(2)}%p',
              style: const TextStyle(fontSize: 12),
            ),
            Text(
              summary.fieldTruthAvailable
                  ? 'Blinded field truth 연결됨'
                  : 'Blinded field truth 미확보 · schema만 준비됨',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
            ),
          ],
        ),
      ),
    );
  }
}

class _V05TechnicalEvidence extends StatelessWidget {
  const _V05TechnicalEvidence({required this.summary});

  final V05ValidationSummary summary;

  @override
  Widget build(BuildContext context) {
    String ratio(double value) => '${(value * 6).round()}/6';
    return Card(
      key: const Key('v05-technical-evidence'),
      color: const Color(0xFFEAF3F8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('실제 전력계량 자료 기술 검증',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 6),
            const Text('현장 고장 정답이 없는 상태에서, 기존에 확인된 이상 후보 구간을 다시 분석한 결과입니다.',
                style: TextStyle(fontSize: 12)),
            const SizedBox(height: 12),
            Wrap(spacing: 10, runSpacing: 10, children: [
              _V05EvidenceTile(
                title: '과거 자료만 사용한 재분석',
                value: ratio(summary.pastOnlyCoverage),
                detail: '과거 30일 정상 비교값 · 미래정보 미사용',
              ),
              _V05EvidenceTile(
                title: '측정값 20% 누락 시험',
                value: ratio(summary.missing20Coverage),
                detail: '고정 seed · random missing 20%',
              ),
              _V05EvidenceTile(
                title: '측정 간격 변경 시험',
                value: ratio(summary.downsample60Coverage),
                detail: '15분 → 60분 downsample',
              ),
            ]),
            const SizedBox(height: 10),
            Text('최대 전류 일치: 기존 계산 ${summary.legacyPeakConsistent}/6 · 세 전류 합계 기준 ${summary.adjudicatedPeakConsistent}/6'),
            const Text('기존 계산은 각 전류선의 최대값을, 개선 계산은 한 시점의 세 전류선 합계 최대값을 사용합니다.',
                style: TextStyle(fontSize: 12)),
            Text('120분 연속 측정 누락 시험 ${ratio(summary.gap120Coverage)} · ${plainSensitivityLabel(summary.sensitivityClassification)}',
                style: const TextStyle(fontSize: 12)),
            Text(
              '전력 사용 수준을 20% 높인 시험: 정상 오분류율 ${(summary.frozenBaselineFpr * 100).toStringAsFixed(2)}% → ${(summary.activationPlus20Fpr * 100).toStringAsFixed(2)}% · 판정 설정 변경 없음',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            ),
          ],
        ),
      ),
    );
  }
}

class _V05EvidenceTile extends StatelessWidget {
  const _V05EvidenceTile({
    required this.title,
    required this.value,
    required this.detail,
  });

  final String title;
  final String value;
  final String detail;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 210,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFFB8CEDB)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              Text(value, style: Theme.of(context).textTheme.titleLarge),
              Text(detail, style: const TextStyle(fontSize: 11)),
            ],
          ),
        ),
      ),
    );
  }
}

class _ControlledValidationSummary extends StatelessWidget {
  const _ControlledValidationSummary({
    required this.metrics,
    required this.v04Summary,
  });

  final List<ControlledMetric> metrics;
  final V04ValidationSummary? v04Summary;

  @override
  Widget build(BuildContext context) {
    final m0 = metrics.where((row) => row.model == 'M0').firstOrNull;
    final m3 = metrics.where((row) => row.model == 'M3').firstOrNull;
    String rate(double? value) =>
        value == null ? 'unavailable' : '${(value * 100).toStringAsFixed(1)}%';
    return Card(
      key: const Key('controlled-validation-summary'),
      color: const Color(0xFFF0F6F1),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('동일 조건 비교 검증 요약',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            if (v04Summary == null) ...[
              Text('전력자료만 사용한 정상 오분류율 ${rate(m0?.normalFpr)}'),
              Text('운영정보를 함께 사용한 정상 오분류율 ${rate(m3?.normalFpr)}'),
              Text('우선 확인 20건의 일치율 ${rate(m3?.precisionAt20)}'),
            ] else ...[
              Text('점검 후보 ${v04Summary!.baselineCandidateCount} → ${v04Summary!.bestCandidateCount}'),
              Text('정상 오분류율 ${rate(v04Summary!.normalFpr)}'),
              Text('우선 확인 10건 일치율 ${rate(v04Summary!.precisionAt10)} · 20건 일치율 ${rate(v04Summary!.precisionAt20)}'),
              Text(v04Summary!.weatherLabel),
            ],
            const SizedBox(height: 6),
            Text(
              v04Summary != null
                  ? '판정 기준을 정하는 자료와 최종 확인 자료를 분리한 비교 검증 결과입니다.'
                  : m3?.status == 'available'
                  ? '동일 frozen set의 M0-M3 비교 결과입니다.'
                  : '공식 KASI/KMA snapshot 미수집으로 M1-M3를 계산하지 않았습니다.',
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}

class _ActualReplayCard extends StatelessWidget {
  const _ActualReplayCard({
    required this.event,
    required this.samples,
    required this.windowCount,
  });

  final ValidationEvent event;
  final List<AmiReplaySample> samples;
  final int windowCount;

  @override
  Widget build(BuildContext context) {
    return Card(
      key: const Key('actual-ami-replay-chart'),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('가명 처리된 공모전 전력계량 자료 · 실제 시간대별 측정값',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 4),
            Text('실제 측정 구간 $windowCount개 · 계량기 ${event.meterId} 대표 구간'),
            const SizedBox(height: 12),
            SizedBox(
              height: 220,
              child: CustomPaint(
                painter: _ReplayPainter(samples: samples, event: event),
                child: const SizedBox.expand(),
              ),
            ),
            const SizedBox(height: 8),
            const Wrap(spacing: 12, runSpacing: 4, children: [
              Text('1번 전류선', style: TextStyle(color: Color(0xFF0077B6))),
              Text('2번 전류선', style: TextStyle(color: Color(0xFFE76F51))),
              Text('3번 전류선', style: TextStyle(color: Color(0xFF2A9D8F))),
              Text('사용 전력량', style: TextStyle(color: Color(0xFFE9C46A))),
              Text('이벤트 구간 음영'),
            ]),
            const SizedBox(height: 6),
            const Text('원본 측정값만 사용하며 누락값과 중복 측정 시각도 임의로 고치지 않습니다.',
                style: TextStyle(fontSize: 12)),
          ],
        ),
      ),
    );
  }
}

class _ReplayPainter extends CustomPainter {
  _ReplayPainter({required this.samples, required this.event});

  final List<AmiReplaySample> samples;
  final ValidationEvent event;

  @override
  void paint(Canvas canvas, Size size) {
    if (samples.length < 2) return;
    const inset = 12.0;
    final area = Rect.fromLTWH(inset, inset, size.width - inset * 2,
        size.height - inset * 2);
    final start = samples.first.timestamp.millisecondsSinceEpoch.toDouble();
    final end = samples.last.timestamp.millisecondsSinceEpoch.toDouble();
    final span = end == start ? 1.0 : end - start;
    double x(DateTime time) =>
        area.left + (time.millisecondsSinceEpoch - start) / span * area.width;

    final eventStart = DateTime.parse(event.firstSample);
    final eventEnd = DateTime.parse(event.lastSample);
    canvas.drawRect(area, Paint()..color = const Color(0xFFF8FAFC));
    canvas.drawRect(
      Rect.fromLTRB(x(eventStart).clamp(area.left, area.right), area.top,
          x(eventEnd).clamp(area.left, area.right), area.bottom),
      Paint()..color = const Color(0x33E76F51),
    );

    final currents = <double>[
      for (final sample in samples)
        ...[sample.i1, sample.i2, sample.i3].whereType<double>(),
      event.offBaselineA,
      event.onBaselineA,
    ];
    final maxCurrent = currents.isEmpty
        ? 1.0
        : currents.reduce((a, b) => a > b ? a : b).clamp(1.0, double.infinity);
    double currentY(double value) =>
        area.bottom - (value / maxCurrent).clamp(0.0, 1.0) * area.height;

    void baseline(double value, Color color) {
      canvas.drawLine(Offset(area.left, currentY(value)),
          Offset(area.right, currentY(value)), Paint()..color = color..strokeWidth = 1);
    }
    baseline(event.offBaselineA, const Color(0xFF94A3B8));
    baseline(event.onBaselineA, const Color(0xFF475569));

    void series(double? Function(AmiReplaySample) value, Color color,
        double Function(double) y) {
      final paint = Paint()
        ..color = color
        ..strokeWidth = 1.6
        ..style = PaintingStyle.stroke;
      Path? path;
      for (final sample in samples) {
        final point = value(sample);
        if (point == null) {
          if (path != null) canvas.drawPath(path, paint);
          path = null;
          continue;
        }
        final offset = Offset(x(sample.timestamp), y(point));
        if (path == null) {
          path = Path()..moveTo(offset.dx, offset.dy);
        } else {
          path.lineTo(offset.dx, offset.dy);
        }
      }
      if (path != null) canvas.drawPath(path, paint);
    }

    series((sample) => sample.i1, const Color(0xFF0077B6), currentY);
    series((sample) => sample.i2, const Color(0xFFE76F51), currentY);
    series((sample) => sample.i3, const Color(0xFF2A9D8F), currentY);
    final energy = samples.map((row) => row.activeEnergyKwh).whereType<double>().toList();
    if (energy.isNotEmpty) {
      final minEnergy = energy.reduce((a, b) => a < b ? a : b);
      final maxEnergy = energy.reduce((a, b) => a > b ? a : b);
      final energySpan = maxEnergy == minEnergy ? 1.0 : maxEnergy - minEnergy;
      series((sample) => sample.activeEnergyKwh, const Color(0xFFE9C46A),
          (value) => area.bottom - ((value - minEnergy) / energySpan).clamp(0.0, 1.0) * area.height);
    }
  }

  @override
  bool shouldRepaint(covariant _ReplayPainter oldDelegate) =>
      oldDelegate.samples != samples || oldDelegate.event != event;
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
                StatusBadge(type: BadgeType.realAmi, label: '실제 공모전 전력계량 자료'),
                StatusBadge(type: BadgeType.validation, label: '현장 미확인 점검 후보'),
              ],
            ),
            const SizedBox(height: 12),
            Text('가명 처리된 전력계량 자료에서 발견한 확인 후보 $eventCount건',
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
                const StatusBadge(type: BadgeType.realAmi, label: '실제 공모전 전력계량 자료'),
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
            _kv('자료 구분', '가명 처리된 공모전 전력계량 자료 검증'),
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
            label: '소등 시간대 정상 비교값',
            value: event.offBaselineA,
            maxValue: maxValue),
        _EvidenceBar(
            label: '실제 관측 최대값',
            value: event.peakCurrentA,
            maxValue: maxValue),
        _EvidenceBar(
            label: '점등 시간대 정상 비교값', value: event.onBaselineA, maxValue: maxValue),
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
          _kv('자료 구분', '가명 처리된 공모전 전력계량 자료 검증'),
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
