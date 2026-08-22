import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../core/presentation/operational_copy.dart';
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
                  '자산 정보',
                  [
                    _kv('연결 가로등 수', '${cabinet.assetInfo.fixtureCount}개'),
                    _kv('램프 정격', _fixtureLampType(cabinet)),
                    _kv('총 정격용량',
                        '${cabinet.expectedLoad.ratedPowerW.toStringAsFixed(1)} W'),
                    _kv('설치 위치', cabinet.assetInfo.location),
                    if (cabinet.assetInfo.latitude != null &&
                        cabinet.assetInfo.longitude != null) ...[
                      Align(
                        alignment: Alignment.centerLeft,
                        child: OutlinedButton.icon(
                          key: const Key('cabinet-map-link'),
                          onPressed: () => context.go(
                            '/map?cabinet=${Uri.encodeComponent(cabinet.cabinetUid)}',
                          ),
                          icon: const Icon(Icons.map_outlined),
                          label: const Text('지도에서 위치 보기'),
                        ),
                      ),
                    ],
                    _kv('자료 구분', operationalEvidenceSourceLabel(cabinet)),
                  ],
                  keySuffix: 'cabinet-section-summary-a'),
              const SizedBox(height: 8),
              _section('예상 운전 기준', [
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
                _kv('기상자료 적용 원칙', '기상청 공식 관측자료만 운전 판단의 참고정보로 사용'),
                _kv(
                    '공식 천문자료',
                    officialContext?.firstOfficialSolar == null
                        ? '한국천문연구원 자료 미수집 · 내부 추정값으로 대체하지 않음'
                        : '한국천문연구원 ${officialContext!.firstOfficialSolar!['date']} · 일출 ${officialContext.firstOfficialSolar!['sunrise']} / 일몰 ${officialContext.firstOfficialSolar!['sunset']}'),
                _kv(
                    '공식 기상 관측자료',
                    officialContext?.firstOfficialWeather == null
                        ? '기상청 ASOS 부산관측소(159) 자료 미수집'
                        : '기상청 ASOS 부산관측소(159) · ${officialContext!.firstOfficialWeather!['timestamp']}'),
              ]),
              const SizedBox(height: 8),
              _section(
                '관측 신호 요약',
                [
                  const Text(
                    '관측 구간에서 확인된 전력 사용 신호의 최대 수준이며 원시 15분 AMI 시계열은 아닙니다.',
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
                      color: const Color(0xFF0F766E),
                      backgroundColor: const Color(0xFFDDE7E4),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    const SizedBox(height: 8),
                    Text('최대 신호 수준 · ${operationalSignalLevel(signal)}'),
                    const SizedBox(height: 10),
                    const _ActivationLegend(),
                  ],
                  _kv(
                      '관측 항목',
                      signal == null
                          ? '우선 확인이 필요한 지속 신호 없음'
                          : operationalSignalTitle(signal)),
                ],
                keySuffix: 'cabinet-section-summary-c',
              ),
              const SizedBox(height: 8),
              _section(
                '우선 확인 사유',
                [
                  _kv('관측 내용', operationalPriorityReason(cabinet)),
                  _kv('적용 판정 기준', operationalCriteria(cabinet)),
                  _kv('자료 구분', operationalEvidenceSourceLabel(cabinet)),
                  _kv('판정 신뢰도', operationalConfidenceLabel(signal)),
                  _kv('해석 범위', operationalEvidenceBoundary(cabinet)),
                ],
                keySuffix: 'summary-d',
              ),
              const SizedBox(height: 8),
              _section(
                '확인 우선순위 및 조치 안내',
                [
                  _kv('확인 순위', '${cabinet.inspectionPriority.rank}번'),
                  _kv('운영 상태', operationalStatusLabel(cabinet.status)),
                  _kv('분류 사유', operationalPriorityReason(cabinet)),
                  _kv('권장 확인 절차',
                      operationalRecommendedAction(cabinet.status)),
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
            label: '관측 신호 수준',
            detail: '탐지 기준 대비 확인된 최대 비율',
          ),
          _LegendItem(
            color: Color(0xFFDDE7E4),
            label: '기준 잔여 구간',
            detail: '전체 탐지 기준에서 남은 비율',
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
