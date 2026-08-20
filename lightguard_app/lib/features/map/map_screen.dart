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
  const MapScreen({super.key});

  @override
  ConsumerState<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends ConsumerState<MapScreen> {
  _MapFilter _filter = _MapFilter.all;

  @override
  Widget build(BuildContext context) {
    final dataAsync = ref.watch(lightguardDataProvider);
    return dataAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, s) => Scaffold(body: Center(child: Text('맵 데이터 로드 실패: $e'))),
      data: (data) {
        final region = ref.watch(selectedRegionProvider);
        final targetIds =
            _extractTargetCabinets(data.targetMode, region.targetModeField);

        final allPoints = data.objects
            .where((c) =>
                c.assetInfo.latitude != null && c.assetInfo.longitude != null)
            .toList(growable: false);
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

        final center = points.isNotEmpty
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
                options: MapOptions(
                  initialCenter: center,
                  initialZoom: 13,
                  minZoom: 10,
                  maxZoom: 18,
                ),
                children: [
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
                            onTap: () => _openCabinet(context, c.cabinetUid),
                            child: _statusMarker(c),
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
                                      '검증 시나리오 ($scenarioCount)'),
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
                            label: '우선점검 $priorityCount'),
                        StatusBadge(
                            type: BadgeType.scenario,
                            label: '점검권고 $recommendCount'),
                        StatusBadge(
                            type: BadgeType.validation,
                            label: '관찰 $observeCount'),
                        StatusBadge(
                            type: BadgeType.normal, label: '정상 $normalCount'),
                        if (supportsScenario && scenarioCount > 0)
                          StatusBadge(
                              type: BadgeType.scenario,
                              label: '시나리오 $scenarioCount'),
                        if (!supportsScenario && municipalCount > 0)
                          StatusBadge(
                              type: BadgeType.validation,
                              label: '실측 자산 $municipalCount'),
                      ],
                    ),
                  ),
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

  Widget _statusMarker(CabinetRecord c) {
    final color = switch (c.status) {
      InspectionStatus.normal => Colors.green,
      InspectionStatus.observe => Colors.blue,
      InspectionStatus.inspectionRecommended => Colors.orange,
      InspectionStatus.priorityInspection => Colors.red,
      InspectionStatus.dataCheckRequired => Colors.grey,
    };

    return CircleAvatar(
      radius: 12,
      backgroundColor: color,
      foregroundColor: Colors.white,
      child: const Icon(Icons.bolt, size: 14),
    );
  }
}
