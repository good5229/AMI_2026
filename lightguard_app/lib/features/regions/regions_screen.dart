import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/widgets/app_scaffold.dart';
import '../../data/models/region_config.dart';
import '../../data/repositories/lightguard_repository.dart';

class RegionsScreen extends ConsumerStatefulWidget {
  const RegionsScreen({super.key});

  @override
  ConsumerState<RegionsScreen> createState() => _RegionsScreenState();
}

class _RegionsScreenState extends ConsumerState<RegionsScreen> {
  late final Future<List<_RegionDatasetSummary>> _catalog = _loadCatalog();
  String _query = '';
  String _topLevel = '전체';
  String _role = '전체';
  String _readiness = '전체';
  int _visibleCount = 20;
  String? _selectedCatalogRegion;
  final Set<String> _comparisonKeys = {};

  @override
  Widget build(BuildContext context) {
    final currentRegion = ref.watch(selectedRegionProvider);
    final dataAsync = ref.watch(lightguardDataProvider);

    return LightguardShell(
      title: '지역별 데이터 확인',
      child: dataAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => const Center(
          child: Text('지역 자료를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.'),
        ),
        data: (data) => FutureBuilder<List<_RegionDatasetSummary>>(
          future: _catalog,
          builder: (context, snapshot) {
            final catalog = snapshot.data ?? const <_RegionDatasetSummary>[];
            final topLevels = <String>{
              '전체',
              for (final region in catalog) region.topLevel,
            }.toList()
              ..sort((a, b) => a == '전체' ? -1 : a.compareTo(b));
            final filtered = catalog.where((region) {
              final topMatches =
                  _topLevel == '전체' || region.topLevel == _topLevel;
              final queryMatches = _query.isEmpty ||
                  region.name.toLowerCase().contains(_query.toLowerCase());
              final roleMatches =
                  _role == '전체' || region.roles.contains(_role);
              final readinessMatches = _readiness == '전체' ||
                  region.readinessLabel == _readiness;
              return topMatches &&
                  queryMatches &&
                  roleMatches &&
                  readinessMatches;
            }).toList(growable: false);

            return ListView(
              padding: const EdgeInsets.all(12),
              children: [
                _CurrentOperationalRegion(
                  region: currentRegion,
                  cabinetCount: data.objects.length,
                  lampCount: data.totalLampCount,
                ),
                const SizedBox(height: 12),
                Text(
                  '운영 화면을 바로 볼 수 있는 지역',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 4),
                const Text(
                  '분전함 단위 예시 데이터가 준비된 3개 지역입니다. 지역을 선택하면 현황·지도·점검 화면이 함께 바뀝니다.',
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    for (final meta in RegionMetadata.all)
                      _OperationalRegionCard(
                        meta: meta,
                        selected: currentRegion == meta.id,
                        onSelect: () => ref
                            .read(selectedRegionProvider.notifier)
                            .state = meta.id,
                      ),
                  ],
                ),
                const SizedBox(height: 22),
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        '전국 공개데이터 확인 지역',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                    ),
                    if (snapshot.hasData) Text('전체 ${catalog.length}개 지역'),
                  ],
                ),
                const SizedBox(height: 4),
                const Text(
                  '가로등·보안등 공개파일에서 분석에 필요한 항목을 확인한 지역입니다. 아직 LightGuard 운영 화면과 직접 연결됐다는 의미는 아닙니다.',
                ),
                const SizedBox(height: 12),
                LayoutBuilder(
                  builder: (context, constraints) {
                    final width = constraints.maxWidth >= 680
                        ? (constraints.maxWidth - 12) / 2
                        : constraints.maxWidth;
                    return Wrap(
                      spacing: 12,
                      runSpacing: 10,
                      children: [
                        SizedBox(
                          width: width,
                          child: TextField(
                            decoration: const InputDecoration(
                              labelText: '시·군·구 이름 검색',
                              hintText: '예: 순천시, 남구, 통영시',
                              prefixIcon: Icon(Icons.search),
                              border: OutlineInputBorder(),
                            ),
                            onChanged: (value) => setState(() {
                              _query = value.trim();
                              _visibleCount = 20;
                            }),
                          ),
                        ),
                        SizedBox(
                          width: width,
                          child: DropdownButtonFormField<String>(
                            initialValue: topLevels.contains(_topLevel)
                                ? _topLevel
                                : '전체',
                            decoration: const InputDecoration(
                              labelText: '광역단위로 좁혀 보기',
                              border: OutlineInputBorder(),
                            ),
                            items: [
                              for (final value in topLevels)
                                DropdownMenuItem(
                                  value: value,
                                  child: Text(value),
                                ),
                            ],
                            onChanged: (value) => setState(() {
                              _topLevel = value ?? '전체';
                              _visibleCount = 20;
                            }),
                          ),
                        ),
                      ],
                    );
                  },
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 12,
                  runSpacing: 10,
                  children: [
                    SizedBox(
                      width: 280,
                      child: DropdownButtonFormField<String>(
                        initialValue: _role,
                        decoration: const InputDecoration(
                          labelText: '확인 가능한 자료로 좁혀 보기',
                          border: OutlineInputBorder(),
                        ),
                        items: const [
                          DropdownMenuItem(value: '전체', child: Text('모든 자료 유형')),
                          DropdownMenuItem(value: 'SIGNAL', child: Text('전력·점등 상태')),
                          DropdownMenuItem(value: 'OPERATIONS', child: Text('고장 접수·처리 이력')),
                          DropdownMenuItem(value: 'CABINET', child: Text('분전함 정보')),
                          DropdownMenuItem(value: 'LOAD', child: Text('설비용량 정보')),
                          DropdownMenuItem(value: 'SPATIAL', child: Text('설치 위치')),
                          DropdownMenuItem(value: 'ASSET', child: Text('가로등 시설정보')),
                        ],
                        onChanged: (value) => setState(() {
                          _role = value ?? '전체';
                          _visibleCount = 20;
                        }),
                      ),
                    ),
                    SizedBox(
                      width: 280,
                      child: DropdownButtonFormField<String>(
                        initialValue: _readiness,
                        decoration: const InputDecoration(
                          labelText: '분석 준비수준으로 좁혀 보기',
                          border: OutlineInputBorder(),
                        ),
                        items: const [
                          DropdownMenuItem(value: '전체', child: Text('모든 준비수준')),
                          DropdownMenuItem(value: '복합자료 구조 확인', child: Text('복합자료 구조 확인')),
                          DropdownMenuItem(value: '전력 신호 구조 확인', child: Text('전력 신호 구조 확인')),
                          DropdownMenuItem(value: '운영 이력 구조 확인', child: Text('운영 이력 구조 확인')),
                          DropdownMenuItem(value: '시설·위치 구조 확인', child: Text('시설·위치 구조 확인')),
                          DropdownMenuItem(value: '기본 공개정보 확인', child: Text('기본 공개정보 확인')),
                        ],
                        onChanged: (value) => setState(() {
                          _readiness = value ?? '전체';
                          _visibleCount = 20;
                        }),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                if (_comparisonKeys.isNotEmpty) ...[
                  _ComparisonPanel(
                    regions: catalog
                        .where((region) =>
                            _comparisonKeys.contains(region.regionKey))
                        .toList(growable: false),
                    onClear: () => setState(_comparisonKeys.clear),
                  ),
                  const SizedBox(height: 10),
                ],
                if (snapshot.connectionState == ConnectionState.waiting)
                  const Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: CircularProgressIndicator()),
                  )
                else if (snapshot.hasError)
                  const _NoticeCard(
                    text: '전국 공개데이터 목록을 불러오지 못했습니다.',
                  )
                else if (filtered.isEmpty)
                  const _NoticeCard(text: '조건에 맞는 지역이 없습니다.')
                else
                  for (final region in filtered.take(_visibleCount))
                    _CatalogRegionCard(
                      region: region,
                      expanded: _selectedCatalogRegion == region.name,
                      compared: _comparisonKeys.contains(region.regionKey),
                      onCompare: () => setState(() {
                        if (_comparisonKeys.contains(region.regionKey)) {
                          _comparisonKeys.remove(region.regionKey);
                        } else if (_comparisonKeys.length < 3) {
                          _comparisonKeys.add(region.regionKey);
                        } else {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('지역 비교는 최대 3개까지 선택할 수 있습니다.'),
                            ),
                          );
                        }
                      }),
                      onTap: () => setState(() {
                        _selectedCatalogRegion =
                            _selectedCatalogRegion == region.name
                                ? null
                                : region.name;
                      }),
                    ),
                if (filtered.length > _visibleCount)
                  Padding(
                    padding: const EdgeInsets.only(top: 4, bottom: 16),
                    child: OutlinedButton.icon(
                      onPressed: () => setState(() => _visibleCount += 20),
                      icon: const Icon(Icons.expand_more),
                      label: Text(
                        '지역 더 보기 · ${filtered.length - _visibleCount}개 남음',
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
      ),
    );
  }

  Future<List<_RegionDatasetSummary>> _loadCatalog() async {
    final text = await rootBundle.loadString(
      'assets/data/context/v24_nationwide_file_census.json',
    );
    final root = jsonDecode(text) as Map<String, dynamic>;
    final datasets = root['datasets'] as List<dynamic>? ?? const [];
    final grouped = <String, _MutableRegionSummary>{};
    for (final raw in datasets.whereType<Map<String, dynamic>>()) {
      if (raw['municipal_scope'] != true ||
          raw['acquisition_status'] != 'DOWNLOADED_ANALYZABLE') {
        continue;
      }
      final name = raw['region']?.toString() ?? '';
      final topLevel = raw['top_level']?.toString() ?? '광역단위 미분류';
      if (name.isEmpty) continue;
      final item = grouped.putIfAbsent(
        name,
        () => _MutableRegionSummary(name: name, topLevel: topLevel),
      );
      item.datasetCount += 1;
      item.rowCount += (raw['rows'] as num?)?.toInt() ?? 0;
      item.roles.addAll(
        (raw['roles'] as List<dynamic>? ?? const []).map((e) => e.toString()),
      );
      item.sources.add(_RegionSource(
        title: raw['title']?.toString() ?? '제목 미제공',
        publisher: raw['publisher']?.toString(),
        modified: raw['date_modified']?.toString(),
        license: raw['license']?.toString(),
        officialUrl: raw['official_url']?.toString() ?? '',
      ));
    }
    return grouped.values
        .map((item) => item.freeze())
        .toList(growable: false)
      ..sort((a, b) => a.name.compareTo(b.name));
  }
}

class _CurrentOperationalRegion extends StatelessWidget {
  const _CurrentOperationalRegion({
    required this.region,
    required this.cabinetCount,
    required this.lampCount,
  });

  final RegionId region;
  final int cabinetCount;
  final int lampCount;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFFF0F6F1),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '현재 운영 화면: ${region.label}',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 6),
            Text(region.branchLabel),
            const SizedBox(height: 4),
            Text('분전함 $cabinetCount개 · 가로등 $lampCount개'),
            const SizedBox(height: 6),
            const Text(
              '지자체 전력계량 자료는 아직 직접 연결되지 않았습니다. 표시된 이상 신호는 검증자료 또는 자산정보에 따른 결과입니다.',
              style: TextStyle(fontSize: 12, height: 1.45),
            ),
          ],
        ),
      ),
    );
  }
}

class _OperationalRegionCard extends StatelessWidget {
  const _OperationalRegionCard({
    required this.meta,
    required this.selected,
    required this.onSelect,
  });

  final RegionMetadata meta;
  final bool selected;
  final VoidCallback onSelect;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 330,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(meta.id.label,
                  style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 4),
              Text(meta.id.modeDescription),
              const SizedBox(height: 8),
              for (final note in meta.modeNotes)
                Padding(
                  padding: const EdgeInsets.only(bottom: 3),
                  child: Text('• $note', style: const TextStyle(fontSize: 12)),
                ),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: selected
                    ? const FilledButton(
                        onPressed: null,
                        child: Text('현재 선택된 지역'),
                      )
                    : OutlinedButton(
                        onPressed: onSelect,
                        child: const Text('운영 화면에서 보기'),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CatalogRegionCard extends StatelessWidget {
  const _CatalogRegionCard({
    required this.region,
    required this.expanded,
    required this.compared,
    required this.onCompare,
    required this.onTap,
  });

  final _RegionDatasetSummary region;
  final bool expanded;
  final bool compared;
  final VoidCallback onCompare;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final roleLabels = region.roles.map(_roleLabel).toList(growable: false);
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.location_on_outlined),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(region.name,
                        style: Theme.of(context).textTheme.titleMedium),
                  ),
                  Chip(label: Text(region.readinessLabel)),
                  const SizedBox(width: 6),
                  Text('공개파일 ${region.datasetCount}개'),
                  IconButton(
                    tooltip: compared ? '지역 비교에서 제외' : '지역 비교에 추가',
                    onPressed: onCompare,
                    icon: Icon(
                      compared
                          ? Icons.compare_arrows
                          : Icons.add_chart_outlined,
                    ),
                  ),
                  Icon(expanded ? Icons.expand_less : Icons.expand_more),
                ],
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: [
                  for (final label in roleLabels) Chip(label: Text(label)),
                ],
              ),
              if (expanded) ...[
                const Divider(height: 22),
                Text('확인된 데이터 행: ${region.rowCount}개'),
                Text('지역 식별키: ${region.regionKey}'),
                const SizedBox(height: 5),
                const _CapabilityFlow(),
                const SizedBox(height: 8),
                const Text(
                  '활용 가능성: 공개파일의 항목 구성을 LightGuard 입력 구조와 비교할 수 있습니다. 시설물 연결번호와 실제 전력자료가 확보되면 지역 맞춤 분석으로 확장할 수 있습니다.',
                  style: TextStyle(fontSize: 12, height: 1.45),
                ),
                const SizedBox(height: 5),
                Text(
                  region.missingRoleLabels.isEmpty
                      ? '추가 필요자료: 실제 전력계량 자료와 현장 확인 결과'
                      : '추가 필요자료: ${region.missingRoleLabels.join(' · ')} · 실제 전력계량 자료 · 현장 확인 결과',
                  style: const TextStyle(fontSize: 12),
                ),
                const SizedBox(height: 8),
                const Text('공식 데이터 출처',
                    style: TextStyle(fontWeight: FontWeight.w700)),
                for (final source in region.sources.take(5))
                  Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(source.title,
                            style: const TextStyle(fontSize: 12)),
                        Text(
                          '${source.publisher ?? '제공기관 미표기'} · 갱신일 ${source.modified ?? '미표기'} · 이용조건 ${source.license ?? '포털 상세페이지 확인'}',
                          style: const TextStyle(fontSize: 11),
                        ),
                        SelectableText(source.officialUrl,
                            style: const TextStyle(fontSize: 10)),
                      ],
                    ),
                  ),
                const SizedBox(height: 5),
                const Text(
                  '현재 제한: 이 지역의 실시간 전력계량 자료와 현장 고장 정답은 연결되지 않았습니다.',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  static String _roleLabel(String role) => switch (role) {
        'SIGNAL' => '전력·점등 상태',
        'OPERATIONS' => '고장 접수·처리 이력',
        'CABINET' => '분전함 정보',
        'LOAD' => '설비용량 정보',
        'SPATIAL' => '설치 위치',
        'ASSET' => '가로등 시설정보',
        _ => '기타 공개정보',
      };
}

class _CapabilityFlow extends StatelessWidget {
  const _CapabilityFlow();

  @override
  Widget build(BuildContext context) {
    return const Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('지역 적용 흐름', style: TextStyle(fontWeight: FontWeight.w700)),
        SizedBox(height: 6),
        _FlowRow(
          number: '1',
          title: '현재 가능',
          detail: '공개파일의 시설물 분포와 항목 구성을 확인할 수 있습니다.',
        ),
        _FlowRow(
          number: '2',
          title: '전력계량 자료 추가 시',
          detail: '예상 점등시간과 실제 전력 사용을 비교해 이상 신호 후보를 찾을 수 있습니다.',
        ),
        _FlowRow(
          number: '3',
          title: '현장 확인 결과 연결 시',
          detail: '지역별 탐지율과 정상 오분류율을 검증하고 점검 우선순위를 개선할 수 있습니다.',
        ),
      ],
    );
  }
}

class _FlowRow extends StatelessWidget {
  const _FlowRow({required this.number, required this.title, required this.detail});

  final String number;
  final String title;
  final String detail;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(radius: 12, child: Text(number)),
          const SizedBox(width: 8),
          Expanded(
            child: Text('$title · $detail', style: const TextStyle(fontSize: 12)),
          ),
        ],
      ),
    );
  }
}

class _ComparisonPanel extends StatelessWidget {
  const _ComparisonPanel({required this.regions, required this.onClear});

  final List<_RegionDatasetSummary> regions;
  final VoidCallback onClear;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFFFFF8E7),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text('지역 데이터 비교',
                      style: Theme.of(context).textTheme.titleMedium),
                ),
                TextButton(onPressed: onClear, child: const Text('비교 초기화')),
              ],
            ),
            const Text('공개자료 규모는 지역의 관리 성과나 서비스 품질 순위가 아닙니다.',
                style: TextStyle(fontSize: 12)),
            const SizedBox(height: 10),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                for (final region in regions)
                  SizedBox(
                    width: 280,
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(region.name,
                                style: const TextStyle(fontWeight: FontWeight.w700)),
                            Text(region.readinessLabel),
                            Text('공개파일 ${region.datasetCount}개 · 데이터 행 ${region.rowCount}개'),
                            Text('확인자료: ${region.roles.map(_CatalogRegionCard._roleLabel).join(' · ')}',
                                style: const TextStyle(fontSize: 12)),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _NoticeCard extends StatelessWidget {
  const _NoticeCard({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(padding: const EdgeInsets.all(18), child: Text(text)),
    );
  }
}

class _MutableRegionSummary {
  _MutableRegionSummary({required this.name, required this.topLevel});

  final String name;
  final String topLevel;
  int datasetCount = 0;
  int rowCount = 0;
  final Set<String> roles = {};
  final List<_RegionSource> sources = [];

  _RegionDatasetSummary freeze() => _RegionDatasetSummary(
        name: name,
        topLevel: topLevel,
        datasetCount: datasetCount,
        rowCount: rowCount,
        roles: roles.toList()..sort(),
        sources: sources,
      );
}

class _RegionDatasetSummary {
  const _RegionDatasetSummary({
    required this.name,
    required this.topLevel,
    required this.datasetCount,
    required this.rowCount,
    required this.roles,
    required this.sources,
  });

  final String name;
  final String topLevel;
  final int datasetCount;
  final int rowCount;
  final List<String> roles;
  final List<_RegionSource> sources;

  String get regionKey => '$topLevel|$name';

  String get readinessLabel {
    if (roles.length >= 4) return '복합자료 구조 확인';
    if (roles.contains('SIGNAL')) return '전력 신호 구조 확인';
    if (roles.contains('OPERATIONS')) return '운영 이력 구조 확인';
    if (roles.contains('ASSET') && roles.contains('SPATIAL')) {
      return '시설·위치 구조 확인';
    }
    return '기본 공개정보 확인';
  }

  List<String> get missingRoleLabels {
    const required = <String>{'SIGNAL', 'OPERATIONS', 'CABINET', 'LOAD', 'SPATIAL', 'ASSET'};
    return (required.difference(roles.toSet()).map(_CatalogRegionCard._roleLabel).toList()
      ..sort());
  }
}

class _RegionSource {
  const _RegionSource({
    required this.title,
    required this.publisher,
    required this.modified,
    required this.license,
    required this.officialUrl,
  });

  final String title;
  final String? publisher;
  final String? modified;
  final String? license;
  final String officialUrl;
}
