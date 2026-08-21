import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/repositories/lightguard_repository.dart';

class CabinetDetailScreen extends ConsumerWidget {
  const CabinetDetailScreen({super.key, required this.cabinetUid});

  final String cabinetUid;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dataAsync = ref.watch(lightguardDataProvider);
    final officialContext = ref.watch(officialContextProvider).asData?.value;
    return dataAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, s) => Scaffold(body: Center(child: Text('분전함 상세 실패: $e'))),
      data: (data) {
        final cabinet = data.objects.firstWhere(
            (c) => c.cabinetUid == cabinetUid,
            orElse: () => data.objects.first);
        final signal = cabinet.detectedSignals.isNotEmpty
            ? cabinet.detectedSignals.first
            : null;
        return LightguardShell(
          title: '분전함 상세',
          child: ListView(
            padding: const EdgeInsets.all(12),
            children: [
              Card(
                child: ListTile(
                  title: Text(cabinet.cabinetUid),
                  subtitle: Text(cabinet.assetInfo.cabinetName),
                  trailing: StatusBadge(
                      type: statusToBadge(cabinet.status),
                      label: statusToLabel(cabinet.status)),
                ),
              ),
              const SizedBox(height: 8),
              _section(
                  'Section A — 자산 정보',
                  [
                    _kv('연결 가로등 수', '${cabinet.assetInfo.fixtureCount}개'),
                    _kv('램프 정격', _fixtureLampType(cabinet)),
                    _kv('총 정격용량',
                        '${cabinet.expectedLoad.ratedPowerW.toStringAsFixed(1)} W'),
                    _kv('주소/위치', cabinet.assetInfo.location),
                    _kv('데이터 유형', cabinet.modeLabel),
                  ],
                  keySuffix: 'cabinet-section-summary-a'),
              const SizedBox(height: 8),
              _section('Section B — 예상 운전', [
                _kv('일출', cabinet.expectedSchedule.sunrise),
                _kv('일몰', cabinet.expectedSchedule.sunset),
                _kv('시민박명 시작', cabinet.expectedSchedule.civilTwilightStart),
                _kv('시민박명 종료', cabinet.expectedSchedule.civilTwilightEnd),
                _kv(
                    '예상 점등시간',
                    cabinet.expectedSchedule.expectedOnWindow['on_start']
                            ?.toString() ??
                        ''),
                _kv(
                    '예상 소등시간',
                    cabinet.expectedSchedule.expectedOnWindow['on_end']
                            ?.toString() ??
                        ''),
                _kv('기상 기준점', cabinet.weatherContext.stationName),
                _kv('운영 기상 정책', '기상청 관측자료만 operational context'),
                _kv(
                    '공식 천문 Context',
                    officialContext?.firstOfficialSolar == null
                        ? 'KASI 미수집 · 내부 계산값으로 대체하지 않음'
                        : 'KASI ${officialContext!.firstOfficialSolar!['date']} · 일출 ${officialContext.firstOfficialSolar!['sunrise']} / 일몰 ${officialContext.firstOfficialSolar!['sunset']}'),
                _kv(
                    '공식 기상 Context',
                    officialContext?.firstOfficialWeather == null
                        ? 'KMA ASOS 부산 159 미수집'
                        : 'KMA ASOS 부산 159 · ${officialContext!.firstOfficialWeather!['timestamp']}'),
              ]),
              const SizedBox(height: 8),
              _section(
                'Section C — 이벤트 활성도 요약',
                [
                  const Text(
                    '탐지 이벤트의 최대 활성도 요약이며 원시 15분 AMI 시계열이 아닙니다.',
                    key: Key('section-cabinet-section-summary-c-description'),
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  const SizedBox(height: 16),
                  if (signal == null)
                    const Text('탐지 이벤트 없음')
                  else ...[
                    LinearProgressIndicator(
                      minHeight: 18,
                      value: signal.maxActivation.clamp(0.0, 1.0),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    const SizedBox(height: 8),
                    Text(
                        '관측 최대 activation ${(signal.maxActivation * 100).toStringAsFixed(1)}%'),
                  ],
                  _kv(
                      '탐지 유형',
                      signal == null
                          ? '없음'
                          : '${signal.eventType} / ${signal.patternConfidence}'),
                ],
                keySuffix: 'cabinet-section-summary-c',
              ),
              const SizedBox(height: 8),
              _section(
                'Section D — 이상 근거',
                [
                  _kv('이상 룰', cabinet.anomalyEvidence.ruleIds.join(', ')),
                  _kv('근거 요약', cabinet.anomalyEvidence.summary),
                  if (signal != null)
                    _kv('최대 activation',
                        '${(signal.maxActivation * 100).toStringAsFixed(1)}%'),
                ],
                keySuffix: 'summary-d',
              ),
              const SizedBox(height: 8),
              _section(
                'Section E — 점검 우선순위',
                [
                  _kv('우선순위 점수',
                      cabinet.inspectionPriority.score.toStringAsFixed(1)),
                  _kv('심각도', cabinet.inspectionPriority.severity),
                  _kv('승인 이유', cabinet.inspectionPriority.reason),
                  const SizedBox(height: 6),
                  const Text('권장 확인사항: AMI 시그널 지속시간, 분전함 제어이력, 조도 이슈 동시 점검'),
                ],
                keySuffix: 'priority',
              ),
            ],
          ),
        );
      },
    );
  }

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

  Widget _section(String title, List<Widget> children, {String? keySuffix}) {
    return Card(
      key: Key(keySuffix == null ? 'section-$title' : 'section-$keySuffix'),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
            const Divider(),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _kv(String label, String value) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 3),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final labelText = Text(label,
                style: const TextStyle(fontWeight: FontWeight.w600));
            if (constraints.maxWidth < 420) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [labelText, const SizedBox(height: 2), Text(value)],
              );
            }
            return Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(width: 140, child: labelText),
                Expanded(child: Text(value)),
              ],
            );
          },
        ),
      );
}
