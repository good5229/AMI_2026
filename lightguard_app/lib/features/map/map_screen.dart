import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/models/lightguard_models.dart';
import '../../data/repositories/lightguard_repository.dart';

class MapScreen extends ConsumerWidget {
  const MapScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dataAsync = ref.watch(lightguardDataProvider);
    return dataAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, s) => Scaffold(body: Center(child: Text('맵 데이터 로드 실패: $e'))),
      data: (data) {
        final points = data.objects
            .where((c) => c.assetInfo.latitude != null && c.assetInfo.longitude != null)
            .toList(growable: false);

        final center = points.isNotEmpty
            ? LatLng(points.first.assetInfo.latitude!, points.first.assetInfo.longitude!)
            : const LatLng(35.16, 129.12);

        return LightguardShell(
          title: '수영구 지도',
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
                bottom: 16,
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(10),
                    child: Wrap(
                      spacing: 8,
                      children: [
                        StatusBadge(type: BadgeType.inspect, label: '우선 점검'),
                        StatusBadge(type: BadgeType.scenario, label: '점검 권고/관찰'),
                        StatusBadge(type: BadgeType.normal, label: '정상'),
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

  static void _openCabinet(BuildContext context, String id) {
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
