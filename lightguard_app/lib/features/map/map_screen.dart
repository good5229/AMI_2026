import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/models/region_config.dart';
import '../../data/repositories/lightguard_repository.dart';

enum _MapFilter {
  all,
  targeted,
  normal,
  observe,
  recommended,
  priority,
  scenario,
  municipalAsset,
}

class MapScreen extends ConsumerStatefulWidget {
  const MapScreen({
    super.key,
    this.focusCabinetUid,
    this.showBaseMap = true,
  });

  final String? focusCabinetUid;
  final bool showBaseMap;

  @override
  ConsumerState<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends ConsumerState<MapScreen> {
  _MapFilter _filter = _MapFilter.all;
  final MapController _mapController = MapController();
  String? _selectedCabinetUid;

  @override
  void initState() {
    super.initState();
    _selectedCabinetUid = widget.focusCabinetUid;
  }

  @override
  void didUpdateWidget(covariant MapScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.focusCabinetUid != widget.focusCabinetUid) {
      _selectedCabinetUid = widget.focusCabinetUid;
    }
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final dataAsync = ref.watch(lightguardDataProvider);
    return dataAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, s) => const Scaffold(
        body: Center(child: Text('지도 자료를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.')),
      ),
      data: (data) {
        final region = ref.watch(selectedRegionProvider);
        final targetIds =
            _extractTargetCabinets(data.targetMode, region.targetModeField);

        final allPoints = data.objects
            .where((c) =>
                c.assetInfo.latitude != null && c.assetInfo.longitude != null)
            .toList(growable: false);
        final focusedCabinet = _selectedCabinetUid == null
            ? null
            : allPoints
                .where((c) => c.cabinetUid == _selectedCabinetUid)
                .firstOrNull;
        final isCompactMap = MediaQuery.sizeOf(context).width < 700;
        final targetPoints = targetIds.isEmpty
            ? allPoints
            : allPoints
                .where((c) => targetIds.contains(c.cabinetUid))
                .toList(growable: false);

        final totalCount = allPoints.length;
        final targetCount = targetPoints.length;
        final priorityCount = allPoints
            .where((c) => c.status == InspectionStatus.priorityInspection)
            .length;
        final recommendCount = allPoints
            .where((c) => c.status == InspectionStatus.inspectionRecommended)
            .length;
        final observeCount =
            allPoints.where((c) => c.status == InspectionStatus.observe).length;
        final normalCount =
            allPoints.where((c) => c.status == InspectionStatus.normal).length;
        final scenarioCount = allPoints
            .where((c) =>
                targetIds.contains(c.cabinetUid) &&
                c.evidenceSource == EvidenceSource.scenarioInjection)
            .length;
        final municipalCount = allPoints
            .where((c) => c.evidenceSource == EvidenceSource.realMunicipalAsset)
            .length;

        final supportsScenario = region.supportsScenarioInjection;
        final availableFilter = _resolveFilter(
          region: region,
          targetCount: targetCount,
          scenarioCount: scenarioCount,
          municipalCount: municipalCount,
          requested: _filter,
        );

        final points = switch (availableFilter) {
          _MapFilter.all => allPoints,
          _MapFilter.targeted => targetPoints,
          _MapFilter.normal => allPoints
              .where((c) => c.status == InspectionStatus.normal)
              .toList(growable: false),
          _MapFilter.observe => allPoints
              .where((c) => c.status == InspectionStatus.observe)
              .toList(growable: false),
          _MapFilter.recommended => allPoints
              .where((c) => c.status == InspectionStatus.inspectionRecommended)
              .toList(growable: false),
          _MapFilter.priority => allPoints
              .where((c) => c.status == InspectionStatus.priorityInspection)
              .toList(growable: false),
          _MapFilter.scenario => allPoints
              .where((c) =>
                  targetIds.contains(c.cabinetUid) &&
                  c.evidenceSource == EvidenceSource.scenarioInjection)
              .toList(growable: false),
          _MapFilter.municipalAsset => allPoints
              .where(
                  (c) => c.evidenceSource == EvidenceSource.realMunicipalAsset)
              .toList(growable: false),
        };

        final center = focusedCabinet != null
            ? LatLng(focusedCabinet.assetInfo.latitude!,
                focusedCabinet.assetInfo.longitude!)
            : points.isNotEmpty
            ? LatLng(points.first.assetInfo.latitude!,
                points.first.assetInfo.longitude!)
            : (allPoints.isNotEmpty
                ? LatLng(allPoints.first.assetInfo.latitude!,
                    allPoints.first.assetInfo.longitude!)
                : const LatLng(35.16, 129.12));

        return LightguardShell(
          title: '${region.label} 지도',
          child: Stack(
            children: [
              FlutterMap(
                mapController: _mapController,
                options: MapOptions(
                  initialCenter: center,
                  initialZoom: focusedCabinet == null ? 13 : 17,
                  minZoom: 10,
                  maxZoom: 18,
                ),
                children: [
                  if (widget.showBaseMap)
                    TileLayer(
                      urlTemplate:
                          'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'kr.example.lightguard',
                    ),
                  MarkerLayer(
                    key: const Key('map-marker-layer'),
                    markers: [
                      for (final c in points)
                        Marker(
                          width: 44,
                          height: 44,
                          point: LatLng(
                              c.assetInfo.latitude!, c.assetInfo.longitude!),
                          child: GestureDetector(
                            key: Key('map-marker-${c.cabinetUid}'),
                            onTap: () => _selectCabinet(c),
                            child: _statusMarker(
                              c,
                              isFocused: c.cabinetUid ==
                                  focusedCabinet?.cabinetUid,
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
              SafeArea(
                child: Align(
                  alignment: Alignment.topCenter,
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxHeight: 190),
                    child: Card(
                      margin: const EdgeInsets.all(12),
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.all(10),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              region.branchLabel,
                              style: Theme.of(context).textTheme.titleSmall,
                            ),
                            if (focusedCabinet != null) ...[
                              const SizedBox(height: 4),
                              Text(
                                '선택 위치 · ${focusedCabinet.assetInfo.cabinetName}',
                                key: const Key('map-focused-cabinet-label'),
                                style: const TextStyle(
                                    color: Color(0xFF0F766E),
                                    fontWeight: FontWeight.w700),
                              ),
                            ],
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: [
                                _buildFilterChip(availableFilter,
                                    _MapFilter.all, '전체 ($totalCount)'),
                                if (targetCount > 0)
                                  _buildFilterChip(
                                    availableFilter,
                                    _MapFilter.targeted,
                                    '검증/연계대상 ($targetCount)',
                                  ),
                                _buildFilterChip(
                                    availableFilter,
                                    _MapFilter.priority,
                                    '우선점검 ($priorityCount)'),
                                _buildFilterChip(
                                    availableFilter,
                                    _MapFilter.recommended,
                                    '점검권고 ($recommendCount)'),
                                _buildFilterChip(availableFilter,
                                    _MapFilter.observe, '관찰 ($observeCount)'),
                                _buildFilterChip(availableFilter,
                                    _MapFilter.normal, '정상 ($normalCount)'),
                                if (supportsScenario)
                                  _buildFilterChip(
                                      availableFilter,
                                      _MapFilter.scenario,
                                      '검증용 모의 신호 ($scenarioCount)'),
                                if (!supportsScenario && municipalCount > 0)
                                  _buildFilterChip(
                                      availableFilter,
                                      _MapFilter.municipalAsset,
                                      '실측 자산 ($municipalCount)'),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              Positioned(
                left: 12,
                right: 12,
                bottom: 16,
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(10),
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        StatusBadge(
                            type: BadgeType.inspect,
                            label: '우선 확인 $priorityCount'),
                        StatusBadge(
                            type: BadgeType.scenario,
                            label: '현장 확인 권고 $recommendCount'),
                        StatusBadge(
                            type: BadgeType.validation,
                            label: '관찰 $observeCount'),
                        StatusBadge(
                            type: BadgeType.normal, label: '정상 $normalCount'),
                        if (supportsScenario && scenarioCount > 0)
                          StatusBadge(
                              type: BadgeType.scenario,
                              label: '검증용 모의 신호 $scenarioCount'),
                        if (!supportsScenario && municipalCount > 0)
                          StatusBadge(
                              type: BadgeType.validation,
                              label: '지자체 시설정보 $municipalCount'),
                        if (widget.showBaseMap)
                          const Padding(
                            padding: EdgeInsets.symmetric(
                                horizontal: 4, vertical: 6),
                            child: Text(
                              '© OpenStreetMap contributors',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
              if (focusedCabinet != null)
                Positioned(
                  left: isCompactMap ? 12 : null,
                  right: 12,
                  bottom: 92,
                  width: isCompactMap ? null : 360,
                  child: _CabinetMapInfoCard(
                    cabinet: focusedCabinet,
                    onClose: _clearSelection,
                    onOpenDetail: () =>
                        _openCabinet(context, focusedCabinet.cabinetUid),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  _MapFilter _resolveFilter({
    required RegionId region,
    required int targetCount,
    required int scenarioCount,
    required int municipalCount,
    required _MapFilter requested,
  }) {
    if (region.supportsScenarioInjection == false &&
        requested == _MapFilter.scenario) {
      return _MapFilter.all;
    }
    if (requested == _MapFilter.targeted && targetCount <= 0) {
      return _MapFilter.all;
    }
    if (requested == _MapFilter.scenario && scenarioCount <= 0) {
      return _MapFilter.all;
    }
    if (requested == _MapFilter.municipalAsset && municipalCount <= 0) {
      return _MapFilter.all;
    }
    return requested;
  }

  Widget _buildFilterChip(
      _MapFilter activeFilter, _MapFilter filter, String label) {
    final selected = activeFilter == filter;
    return FilterChip(
      label: Text(label),
      selected: selected,
      selectedColor: Colors.blue.withValues(alpha: 0.2),
      onSelected: (_) {
        setState(() {
          _filter = filter;
        });
      },
    );
  }

  Set<String> _extractTargetCabinets(
      Map<String, dynamic> targetMode, String key) {
    final raw = targetMode[key];
    if (raw is List) return raw.map((value) => value.toString()).toSet();
    if (raw is String) return <String>{raw};
    return const <String>{};
  }

  void _openCabinet(BuildContext context, String id) {
    context.go('/cabinet/$id');
  }

  void _selectCabinet(CabinetRecord cabinet) {
    setState(() => _selectedCabinetUid = cabinet.cabinetUid);
    _mapController.move(
      LatLng(cabinet.assetInfo.latitude!, cabinet.assetInfo.longitude!),
      17,
    );
  }

  void _clearSelection() {
    setState(() => _selectedCabinetUid = null);
  }

  Widget _statusMarker(CabinetRecord c, {required bool isFocused}) {
    final color = switch (c.status) {
      InspectionStatus.normal => Colors.green,
      InspectionStatus.observe => Colors.blue,
      InspectionStatus.inspectionRecommended => Colors.orange,
      InspectionStatus.priorityInspection => Colors.red,
      InspectionStatus.dataCheckRequired => Colors.grey,
    };

    return Container(
      key: isFocused ? const Key('map-focused-cabinet-marker') : null,
      padding: EdgeInsets.all(isFocused ? 4 : 0),
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: isFocused ? Colors.white : Colors.transparent,
        border: isFocused
            ? Border.all(color: const Color(0xFF102A43), width: 3)
            : null,
        boxShadow: isFocused
            ? const [
                BoxShadow(
                    color: Color(0x40102A43), blurRadius: 10, spreadRadius: 2)
              ]
            : null,
      ),
      child: CircleAvatar(
        radius: 12,
        backgroundColor: color,
        foregroundColor: Colors.white,
        child: const Icon(Icons.bolt, size: 14),
      ),
    );
  }
}

class _CabinetMapInfoCard extends StatelessWidget {
  const _CabinetMapInfoCard({
    required this.cabinet,
    required this.onClose,
    required this.onOpenDetail,
  });

  final CabinetRecord cabinet;
  final VoidCallback onClose;
  final VoidCallback onOpenDetail;

  @override
  Widget build(BuildContext context) => Card(
        key: const Key('map-selected-cabinet-card'),
        margin: EdgeInsets.zero,
        elevation: 5,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(cabinet.assetInfo.cabinetName,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(context).textTheme.titleMedium),
                        Text(cabinet.cabinetUid,
                            style: Theme.of(context).textTheme.bodySmall),
                      ],
                    ),
                  ),
                  StatusBadge(
                    type: statusToBadge(cabinet.status),
                    label: statusToLabel(cabinet.status),
                  ),
                  IconButton(
                    key: const Key('map-selected-cabinet-close'),
                    tooltip: '선택 닫기',
                    onPressed: onClose,
                    icon: const Icon(Icons.close, size: 20),
                  ),
                ],
              ),
              const Divider(height: 18),
              Text(cabinet.assetInfo.location,
                  maxLines: 2, overflow: TextOverflow.ellipsis),
              const SizedBox(height: 4),
              Text(
                '${cabinet.assetInfo.latitude!.toStringAsFixed(6)}, ${cabinet.assetInfo.longitude!.toStringAsFixed(6)}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 10),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _MapInfoPill(
                      label: '연결 가로등',
                      value: '${cabinet.assetInfo.fixtureCount}개'),
                  _MapInfoPill(
                    label: '정격부하',
                    value:
                        '${cabinet.expectedLoad.expectedRatedLoadKw.toStringAsFixed(2)} kW',
                  ),
                ],
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  key: const Key('map-selected-cabinet-detail'),
                  onPressed: onOpenDetail,
                  icon: const Icon(Icons.open_in_new, size: 18),
                  label: const Text('분전함 상세 보기'),
                ),
              ),
            ],
          ),
        ),
      );
}

class _MapInfoPill extends StatelessWidget {
  const _MapInfoPill({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
        decoration: BoxDecoration(
          color: const Color(0xFFE7F2EF),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text('$label · $value',
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
      );
}
