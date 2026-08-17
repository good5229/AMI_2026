import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/models/region_config.dart';
import '../../data/repositories/lightguard_repository.dart';

enum _MapFilter {
  all,
  normal,
  observe,
  recommended,
  priority,
  scenario,
  realAmi,
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
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, s) => Scaffold(body: Center(child: Text('맵 데이터 로드 실패: $e'))),
      data: (data) {
        final region = ref.watch(selectedRegionProvider);

        final allPoints = data.objects
            .where((c) => c.assetInfo.latitude != null && c.assetInfo.longitude != null)
            .toList(growable: false);
        final totalCount = allPoints.length;
        final priorityCount = allPoints.where((c) => c.status == InspectionStatus.priorityInspection).length;
        final recommendCount = allPoints.where((c) => c.status == InspectionStatus.inspectionRecommended).length;
        final observeCount = allPoints.where((c) => c.status == InspectionStatus.observe).length;
        final normalCount = allPoints.where((c) => c.status == InspectionStatus.normal).length;
        final scenarioCount = allPoints.where((c) => c.evidenceSource == EvidenceSource.scenarioInjection).length;
        final realAmiCount = allPoints.where((c) => c.evidenceSource == EvidenceSource.realCompetitionAmi).length;

        final points = switch (_filter) {
          _MapFilter.all => allPoints,
          _MapFilter.normal => allPoints.where((c) => c.status == InspectionStatus.normal).toList(growable: false),
          _MapFilter.observe => allPoints.where((c) => c.status == InspectionStatus.observe).toList(growable: false),
          _MapFilter.recommended =>
            allPoints.where((c) => c.status == InspectionStatus.inspectionRecommended).toList(growable: false),
          _MapFilter.priority =>
            allPoints.where((c) => c.status == InspectionStatus.priorityInspection).toList(growable: false),
          _MapFilter.scenario =>
            allPoints.where((c) => c.evidenceSource == EvidenceSource.scenarioInjection).toList(growable: false),
          _MapFilter.realAmi =>
            allPoints.where((c) => c.evidenceSource == EvidenceSource.realCompetitionAmi).toList(growable: false),
        };

        final center = points.isNotEmpty
            ? LatLng(points.first.assetInfo.latitude!, points.first.assetInfo.longitude!)
            : (allPoints.isNotEmpty
                ? LatLng(allPoints.first.assetInfo.latitude!, allPoints.first.assetInfo.longitude!)
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
                    urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    userAgentPackageName: 'kr.example.lightguard',
                  ),
                  MarkerLayer(
                    markers: [
                      for (final c in points)
                        Marker(
                          width: 44,
                          height: 44,
                          point: LatLng(c.assetInfo.latitude!, c.assetInfo.longitude!),
                          child: GestureDetector(
                            onTap: () => _openCabinet(context, c.cabinetUid),
                            child: _statusMarker(c),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
              Positioned(
                left: 12,
                right: 12,
                top: 12,
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(10),
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _buildFilterChip(_MapFilter.all, '전체 ($totalCount)'),
                        _buildFilterChip(_MapFilter.priority, '우선점검 ($priorityCount)'),
                        _buildFilterChip(_MapFilter.recommended, '점검권고 ($recommendCount)'),
                        _buildFilterChip(_MapFilter.observe, '관찰 ($observeCount)'),
                        _buildFilterChip(_MapFilter.normal, '정상 ($normalCount)'),
                        _buildFilterChip(_MapFilter.scenario, '시나리오 ($scenarioCount)'),
                        _buildFilterChip(_MapFilter.realAmi, '실제AMI ($realAmiCount)'),
                      ],
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
                  children: [
                        StatusBadge(type: BadgeType.inspect, label: '우선점검 $priorityCount'),
                        StatusBadge(type: BadgeType.scenario, label: '점검권고 $recommendCount'),
                        StatusBadge(type: BadgeType.validation, label: '관찰 $observeCount'),
                        StatusBadge(type: BadgeType.normal, label: '정상 $normalCount'),
                        StatusBadge(type: BadgeType.scenario, label: '시나리오 $scenarioCount'),
                        StatusBadge(type: BadgeType.validation, label: '실제AMI $realAmiCount'),
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

  Widget _buildFilterChip(_MapFilter filter, String label) {
    final active = _filter == filter;
    return FilterChip(
      label: Text(label),
      selected: active,
      selectedColor: Colors.blue.withValues(alpha: 0.2),
      onSelected: (selected) {
        setState(() {
          _filter = filter;
        });
      },
    );
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

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        CircleAvatar(radius: 12, backgroundColor: color, foregroundColor: Colors.white, child: const Icon(Icons.bolt, size: 14)),
      ],
    );
  }
}
