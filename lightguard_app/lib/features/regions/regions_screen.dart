import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../data/models/region_config.dart';
import '../../data/repositories/lightguard_repository.dart';
import '../../core/widgets/status_badges.dart';

class RegionsScreen extends ConsumerWidget {
  const RegionsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentRegion = ref.watch(selectedRegionProvider);
    final dataAsync = ref.watch(lightguardDataProvider);

    return LightguardShell(
      title: '지역 전환',
      child: dataAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('지역 데이터 실패: $error')),
        data: (data) {
          return ListView(
            padding: const EdgeInsets.all(12),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.location_city_outlined),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              '현재 표시 지역: ${currentRegion.label}',
                              style:
                                  const TextStyle(fontWeight: FontWeight.w700),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          StatusBadge(
                              type: BadgeType.validation,
                              label: currentRegion.branchLabel),
                          const StatusBadge(
                              type: BadgeType.validation,
                              label: '실제 지자체 AMI 0개'),
                          StatusBadge(
                            type: currentRegion.supportsScenarioInjection
                                ? BadgeType.scenario
                                : BadgeType.validation,
                            label: currentRegion.supportsScenarioInjection
                                ? 'Controlled scenario'
                                : currentRegion.supportsControllerData
                                    ? 'Controller-linked'
                                    : 'Asset-only',
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                          '${data.objects.length}개 분전함 · 가로등 ${data.totalLampCount}등'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text(currentRegion.regionalFilterHint,
                      style: const TextStyle(fontSize: 13)),
                ),
              ),
              const SizedBox(height: 8),
              for (final meta in RegionMetadata.all)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                currentRegion == meta.id
                                    ? Icons.toggle_on
                                    : Icons.location_city_outlined,
                                color: currentRegion == meta.id
                                    ? Colors.blue
                                    : Colors.grey,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(meta.id.label,
                                    style: const TextStyle(
                                        fontWeight: FontWeight.w700)),
                              ),
                              if (currentRegion == meta.id)
                                const Text('현재')
                              else
                                ElevatedButton(
                                  onPressed: () {
                                    ref
                                        .read(selectedRegionProvider.notifier)
                                        .state = meta.id;
                                  },
                                  child: const Text('선택'),
                                ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: [
                              StatusBadge(
                                  type: BadgeType.validation,
                                  label: meta.id.modeDescription),
                              const StatusBadge(
                                  type: BadgeType.validation,
                                  label: '실제 AMI 연결 없음'),
                            ],
                          ),
                          const SizedBox(height: 8),
                          for (final note in meta.modeNotes)
                            Text('• $note',
                                style: const TextStyle(fontSize: 13)),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}
