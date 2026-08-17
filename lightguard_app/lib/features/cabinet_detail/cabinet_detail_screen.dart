import 'package:fl_chart/fl_chart.dart';
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
    return dataAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, s) => Scaffold(body: Center(child: Text('분전함 상세 실패: $e'))),
      data: (data) {
        final cabinet = data.objects.firstWhere((c) => c.cabinetUid == cabinetUid, orElse: () => data.objects.first);
        final signal = cabinet.detectedSignals.isNotEmpty ? cabinet.detectedSignals.first : null;
        return LightguardShell(
          title: '분전함 상세',
          child: ListView(
            padding: const EdgeInsets.all(12),
            children: [
              Card(
                child: ListTile(
                  title: Text(cabinet.cabinetUid),
                  subtitle: Text(cabinet.assetInfo.cabinetName),
                  trailing: StatusBadge(type: statusToBadge(cabinet.status), label: statusToLabel(cabinet.status)),
                ),
              ),
              const SizedBox(height: 8),
              _section('Section A — 자산 정보', [
                _kv('연결 가로등 수', '${cabinet.assetInfo.fixtureCount}개'),
                _kv('램프 종류', 'LED'),
                _kv('총 정격용량', '${cabinet.expectedLoad.ratedPowerW.toStringAsFixed(1)} W'),
                _kv('주소/위치', cabinet.assetInfo.location),
                _kv('데이터 유형', cabinet.modeLabel),
              ]),
              const SizedBox(height: 8),
              _section('Section B — 예상 운전', [
                _kv('일출', cabinet.expectedSchedule.sunrise),
                _kv('일몰', cabinet.expectedSchedule.sunset),
                _kv('시민박명 시작', cabinet.expectedSchedule.civilTwilightStart),
                _kv('시민박명 종료', cabinet.expectedSchedule.civilTwilightEnd),
                _kv('예상 점등시간', cabinet.expectedSchedule.expectedOnWindow['on_start']?.toString() ?? ''),
                _kv('예상 소등시간', cabinet.expectedSchedule.expectedOnWindow['on_end']?.toString() ?? ''),
                _kv('기상 기준점', cabinet.weatherContext.stationName),
              ]),
              const SizedBox(height: 8),
              _section('Section C — AMI/시나리오 시계열', [
                SizedBox(
                  height: 240,
                  child: signal == null
                      ? const Center(child: Text('시계열 이벤트 없음'))
                      : Padding(
                          padding: const EdgeInsets.all(8),
                          child: LineChart(
                            LineChartData(
                              minX: 0,
                              maxX: 2,
                              minY: 0,
                              maxY: signal.maxActivation,
                              lineBarsData: [
                                LineChartBarData(
                                  spots: [
                                    const FlSpot(0, 0),
                                    const FlSpot(1, signal.maxActivation),
                                    const FlSpot(2, 0),
                                  ],
                                  isCurved: false,
                                  barWidth: 3,
                                  color: Colors.blueAccent,
                                ),
                              ],
                            ),
                          ),
                        ),
                ),
                if (signal != null)
                  _kv('탐지 유형', '${signal.eventType} / ${signal.patternConfidence}'),
              ]),
              const SizedBox(height: 8),
              _section('Section D — 이상 근거', [
                _kv('이상 룰', cabinet.anomalyEvidence.ruleIds.join(', ')),
                _kv('근거 요약', cabinet.anomalyEvidence.summary),
                if (signal != null)
                  _kv('최대 activation', '${(signal.maxActivation * 100).toStringAsFixed(1)}%'),
              ]),
              const SizedBox(height: 8),
              _section('Section E — 점검 우선순위', [
                _kv('우선순위 점수', cabinet.inspectionPriority.score.toStringAsFixed(1)),
                _kv('심각도', cabinet.inspectionPriority.severity),
                _kv('승인 이유', cabinet.inspectionPriority.reason),
                const SizedBox(height: 6),
                const Text('권장 확인사항: AMI 시그널 지속시간, 분전함 제어이력, 조도 이슈 동시 점검'),
              ]),
            ],
          ),
        );
      },
    );
  }

  Widget _section(String title, List<Widget> children) {
    return Card(
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
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(width: 140, child: Text(label, style: const TextStyle(fontWeight: FontWeight.w600))),
        Expanded(child: Text(value)),
      ],
    ),
  );
}
