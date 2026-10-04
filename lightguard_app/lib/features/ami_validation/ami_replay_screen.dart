import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/storage/inspection_outcome_storage.dart';
import '../../data/models/context_models.dart';
import '../../data/repositories/lightguard_repository.dart';

class AmiReplayScreen extends ConsumerWidget {
  const AmiReplayScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final events = ref.watch(competitionAmiEventsProvider);
    final windows = ref.watch(amiReplayWindowsProvider);
    return LightguardShell(
      title: '제공 AMI 기록 분석', compactTitle: 'AMI 기록 분석',
      child: events.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('AMI 후보 목록을 불러오지 못했습니다.')),
        data: (items) => windows.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (_, __) => const Center(child: Text('원본 관측 구간을 불러오지 못했습니다.')),
          data: (samples) => items.isEmpty
              ? const Center(child: Text('제공된 분석 후보가 없습니다.'))
              : _ReplayBody(events: items, windows: samples),
        ),
      ),
    );
  }
}

class _ReplayBody extends StatefulWidget {
  const _ReplayBody({required this.events, required this.windows});
  final List<ValidationEvent> events;
  final Map<String, List<AmiReplaySample>> windows;
  @override
  State<_ReplayBody> createState() => _ReplayBodyState();
}

class _ReplayBodyState extends State<_ReplayBody> {
  int selected = 0;
  int? cursor;
  Timer? timer;
  bool get playing => timer?.isActive ?? false;
  ValidationEvent get event => widget.events[selected];
  List<AmiReplaySample> get samples => widget.windows[
      '${event.meterId}_${event.firstSample.substring(0, 10)}.csv'] ?? const [];

  @override
  void dispose() { timer?.cancel(); super.dispose(); }

  void select(int value) {
    timer?.cancel();
    setState(() { selected = value; cursor = null; });
  }

  void toggleReplay() {
    if (playing) {
      timer?.cancel();
      setState(() {});
      return;
    }
    setState(() { cursor = 0; });
    timer = Timer.periodic(const Duration(milliseconds: 800), (_) {
      if (!mounted) return;
      setState(() {
        if ((cursor ?? 0) >= samples.length - 1) {
          timer?.cancel();
        } else {
          cursor = (cursor ?? 0) + 1;
        }
      });
    });
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final rows = samples;
    final start = DateTime.parse(event.firstSample);
    final end = DateTime.parse(event.lastSample);
    final candidate = rows.where((r) => !r.timestamp.isBefore(start) && !r.timestamp.isAfter(end));
    final sums = candidate.map((r) => [r.i1, r.i2, r.i3].whereType<double>().toList())
        .where((values) => values.isNotEmpty).map((values) => values.reduce((a, b) => a + b));
    final peak = sums.isEmpty ? null : sums.reduce(math.max);
    final current = rows.isEmpty ? null : rows[(cursor ?? rows.length - 1).clamp(0, rows.length - 1)];
    return ListView(padding: const EdgeInsets.all(16), children: [
      Container(
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          gradient: const LinearGradient(colors: [Color(0xFF102A43), Color(0xFF0F5D59)]),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('실제 공모전 제공 자료', style: TextStyle(color: Color(0xFFAED4CD), fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Text('전류 변화에서 확인 후보를 찾습니다', style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: Colors.white)),
          const SizedBox(height: 10),
          Text('가로등형 계량기 5개 분석 · 기존 후보 ${widget.events.length}건', style: const TextStyle(color: Colors.white)),
          const SizedBox(height: 8),
          const Text('2026년 4~6월 제공 기록의 후보 구간 재생\n실시간 수신 아님 · 지역 연결 없음 · 고장 여부 미확인', style: TextStyle(color: Color(0xFFD5E4E4))),
        ]),
      ),
      const SizedBox(height: 18),
      DropdownButtonFormField<int>(
        key: const Key('ami-event-selector'), initialValue: selected, isExpanded: true,
        decoration: const InputDecoration(labelText: '분석할 후보 구간', border: OutlineInputBorder()),
        items: [for (var i = 0; i < widget.events.length; i++) DropdownMenuItem(value: i,
          child: Text('${widget.events[i].meterId} · ${widget.events[i].firstSample}', overflow: TextOverflow.ellipsis))],
        onChanged: (value) { if (value != null) select(value); },
      ),
      const SizedBox(height: 14),
      if (rows.isEmpty) const Card(child: Padding(padding: EdgeInsets.all(18), child: Text('원본 관측 구간 없음 · 그래프를 만들 수 없습니다.')))
      else Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(
        crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('${event.meterId} 전류 관측 기록', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 6),
        Text('${_stamp(rows.first.timestamp)} ~ ${_stamp(rows.last.timestamp)}'),
        const Text('점은 원본 관측값입니다. 빈 값은 미수집으로 유지하며 연결선으로 보간하지 않습니다.'),
        const SizedBox(height: 10),
        const Wrap(spacing: 18, runSpacing: 8, children: [
          Text('● I1', style: TextStyle(color: Color(0xFF0F766E), fontWeight: FontWeight.w700)),
          Text('● I2', style: TextStyle(color: Color(0xFF1D4ED8), fontWeight: FontWeight.w700)),
          Text('● I3', style: TextStyle(color: Color(0xFFB45309), fontWeight: FontWeight.w700)),
          Text('배경 강조: 기존 탐지 후보 구간'),
        ]),
        const SizedBox(height: 10),
        SizedBox(height: 240, width: double.infinity, child: Semantics(
          label: '실제 전류 관측 그래프. 수치는 아래 원본 관측 표에서도 확인할 수 있습니다.',
          child: CustomPaint(key: const Key('ami-measured-chart'), painter: _SamplePainter(
            rows, cursor ?? rows.length - 1, start, end,
          )),
        )),
        Wrap(spacing: 10, runSpacing: 10, crossAxisAlignment: WrapCrossAlignment.center, children: [
          FilledButton.icon(key: const Key('ami-play'), onPressed: toggleReplay,
            icon: Icon(playing ? Icons.pause : Icons.play_arrow), label: Text(playing ? '일시 정지' : '기록 재생')),
          OutlinedButton(onPressed: () { timer?.cancel(); setState(() => cursor = null); }, child: const Text('전체 기록')),
          Text('${(cursor ?? rows.length - 1) + 1} / ${rows.length} 관측점'),
        ]),
        if (rows.length > 1) Slider(key: const Key('ami-time-slider'),
          value: (cursor ?? rows.length - 1).toDouble(), min: 0, max: (rows.length - 1).toDouble(), divisions: rows.length - 1,
          label: current == null ? null : _stamp(current.timestamp),
          onChanged: (value) { timer?.cancel(); setState(() => cursor = value.round()); }),
        if (current != null) Text('${_stamp(current.timestamp)}\nI1 ${_amp(current.i1)}  /  I2 ${_amp(current.i2)}  /  I3 ${_amp(current.i3)}', key: const Key('ami-current-sample')),
      ]))),
      const SizedBox(height: 12),
      Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('이 구간을 확인하는 이유', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        Text('기존 탐지 후보의 관측 시각: ${event.firstSample} ~ ${event.lastSample}'),
        Text('후보 구간 관측 ${candidate.length}점 · 15분 표본 기준 추정 ${candidate.length * 15}분'),
        Text('관측된 상 전류 합의 구간 최대 ${peak == null ? '계산 불가' : '${peak.toStringAsFixed(3)} A'}'),
        const SizedBox(height: 8),
        const Text('분석 기준: 09~16시대 전류를 계량기별 비교 수준과 대조한 기존 후보입니다. 위치를 알 수 없어 지역 일출·일몰은 적용하지 않습니다.'),
        const SizedBox(height: 8),
        const Text('현재 화면은 원본값과 후보 구간을 재생합니다. 고장 확정, 탐지 정확도, 실현 절감량을 뜻하지 않습니다. 전류 시각의 구간 시작/끝 정의는 미확인으로 원본 시각을 유지합니다.'),
      ]))),
      _AmiReview(key: ValueKey(event.eventId), eventId: event.eventId),
      ExpansionTile(title: const Text('원본 관측 표'), subtitle: const Text('추출 파일의 원본 행 번호 포함'), children: [
        SingleChildScrollView(scrollDirection: Axis.horizontal, child: DataTable(
          columns: const [DataColumn(label: Text('원본 시각')), DataColumn(label: Text('I1 (A)')), DataColumn(label: Text('I2 (A)')), DataColumn(label: Text('I3 (A)')), DataColumn(label: Text('원본 행'))],
          rows: [for (final r in rows) DataRow(cells: [DataCell(Text(_stamp(r.timestamp))), DataCell(Text(_number(r.i1))), DataCell(Text(_number(r.i2))), DataCell(Text(_number(r.i3))), DataCell(Text('${r.sourceRow}'))])],
        )),
      ]),
      const SizedBox(height: 12),
      Wrap(spacing: 12, runSpacing: 10, children: [
        OutlinedButton(onPressed: () => context.go('/'), child: const Text('지역 공개자산 보기')),
        TextButton(onPressed: () => context.go('/evidence'), child: const Text('기술 검증 세부 자료')),
      ]),
    ]);
  }
}

class _AmiReview extends StatefulWidget {
  const _AmiReview({super.key, required this.eventId});
  final String eventId;
  @override
  State<_AmiReview> createState() => _AmiReviewState();
}

class _AmiReviewState extends State<_AmiReview> {
  final note = TextEditingController();
  String status = 'unreviewed';
  String? error;
  bool loading = true;
  bool saving = false;
  String get recordKey => 'ami-review:${widget.eventId}';
  @override
  void initState() {
    super.initState();
    loadInspectionOutcomes().then((records) {
      if (!mounted) return;
      setState(() { note.text = records[recordKey]?['note'] ?? ''; status = records[recordKey]?['reviewStatus'] ?? 'unreviewed'; loading = false; });
    }).catchError((Object _) { if (mounted) setState(() { error = '저장된 검토 기록을 불러오지 못했습니다.'; loading = false; }); });
  }
  @override
  void dispose() { note.dispose(); super.dispose(); }
  Future<void> save() async {
    setState(() { saving = true; error = null; });
    try {
      final records = await loadInspectionOutcomes();
      records[recordKey] = {'note': note.text.trim(), 'reviewStatus': status,
        'recordType': 'ami_analysis_review', 'updatedAt': DateTime.now().toIso8601String()};
      await saveInspectionOutcomes(records);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('AMI 검토 기록을 기기에 저장했습니다.')));
    } catch (_) {
      if (mounted) setState(() => error = '저장 실패 · 다시 시도해 주세요.');
    } finally { if (mounted) setState(() => saving = false); }
  }
  @override
  Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Text('분석 검토 기록', style: Theme.of(context).textTheme.titleLarge),
    const Text('가명 계량기 후보 검토용 · 현장 고장 확인이나 지역 점검 실적으로 집계하지 않습니다.'),
    const SizedBox(height: 12),
    if (loading) const LinearProgressIndicator() else ...[
      DropdownButtonFormField<String>(key: ValueKey('$recordKey-$status'), initialValue: status, isExpanded: true,
        decoration: const InputDecoration(labelText: '검토 상태', border: OutlineInputBorder()),
        items: const [DropdownMenuItem(value: 'unreviewed', child: Text('미검토')), DropdownMenuItem(value: 'reviewed', child: Text('측정 구간 검토 완료')), DropdownMenuItem(value: 'mapping_needed', child: Text('기관 연결자료 확인 필요'))],
        onChanged: (value) { if (value != null) setState(() => status = value); }),
      const SizedBox(height: 12),
      TextField(key: const Key('ami-review-note'), controller: note, maxLines: 2, decoration: const InputDecoration(labelText: '검토 메모', border: OutlineInputBorder())),
      const SizedBox(height: 12),
      FilledButton(key: const Key('ami-review-save'), onPressed: saving ? null : save, child: Text(saving ? '저장 중' : '검토 기록 저장')),
    ],
    if (error != null) Text(error!, style: const TextStyle(color: Colors.red)),
  ])));
}

String _stamp(DateTime value) => value.toIso8601String().replaceFirst('T', ' ').substring(0, 16);
String _number(double? value) => value?.toStringAsFixed(3) ?? '미수집';
String _amp(double? value) => value == null ? '미수집' : '${value.toStringAsFixed(3)} A';

class _SamplePainter extends CustomPainter {
  _SamplePainter(this.samples, this.last, this.start, this.end);
  final List<AmiReplaySample> samples;
  final int last;
  final DateTime start;
  final DateTime end;

  @override
  void paint(Canvas canvas, Size size) {
    if (samples.isEmpty) return;
    const left = 48.0, top = 22.0, bottom = 34.0;
    final right = size.width - 12;
    final height = size.height - top - bottom;
    final values = samples.expand((r) => [r.i1, r.i2, r.i3]).whereType<double>();
    final maxValue = math.max(1.0, values.isEmpty ? 1.0 : values.reduce(math.max) * 1.15);
    final minTime = samples.first.timestamp.millisecondsSinceEpoch;
    final duration = math.max(1, samples.last.timestamp.millisecondsSinceEpoch - minTime);
    double x(DateTime time) => left + (time.millisecondsSinceEpoch - minTime) / duration * (right - left);
    double y(double value) => top + height * (1 - value / maxValue);
    void text(String value, Offset offset) {
      final painter = TextPainter(text: TextSpan(text: value, style: const TextStyle(fontSize: 11, color: Color(0xFF526471))), textDirection: TextDirection.ltr)..layout();
      painter.paint(canvas, offset);
    }
    final rect = Rect.fromLTRB(math.max(left, x(start) - 4), top, math.min(right, x(end) + 4), top + height);
    canvas.drawRect(rect, Paint()..color = const Color(0xFFFFF0CD));
    for (var i = 0; i <= 4; i++) {
      final value = maxValue * i / 4;
      canvas.drawLine(Offset(left, y(value)), Offset(right, y(value)), Paint()..color = const Color(0xFFDDE5E2));
      text(value.toStringAsFixed(1), Offset(0, y(value) - 6));
    }
    text('전류 A', const Offset(0, 0));
    text(_stamp(samples.first.timestamp).substring(11), Offset(left, size.height - 22));
    text(_stamp(samples.last.timestamp).substring(11), Offset(right - 36, size.height - 22));
    const colors = [Color(0xFF0F766E), Color(0xFF1D4ED8), Color(0xFFB45309)];
    for (final r in samples.take(last + 1)) {
      final channels = [r.i1, r.i2, r.i3];
      for (var phase = 0; phase < channels.length; phase++) {
        final value = channels[phase];
        if (value != null) canvas.drawCircle(Offset(x(r.timestamp), y(value)), 3.4, Paint()..color = colors[phase]);
      }
    }
    final current = samples[last.clamp(0, samples.length - 1)];
    canvas.drawLine(Offset(x(current.timestamp), top), Offset(x(current.timestamp), top + height), Paint()..color = const Color(0x66526471)..strokeWidth = 1);
  }

  @override
  bool shouldRepaint(covariant _SamplePainter old) => old.samples != samples || old.last != last || old.start != start || old.end != end;
}
