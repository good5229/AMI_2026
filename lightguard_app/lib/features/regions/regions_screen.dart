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
                  child: Row(
                    children: [
                      const Icon(Icons.location_city_outlined),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          '현재 표시 지역: ${currentRegion.label} (${data.objects.length}개 분전함, 유효 등주수 ${data.totalLampCount}개)',
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                      ),
                      StatusBadge(type: BadgeType.validation, label: currentRegion.modeDescription),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 8),
              for (final meta in RegionMetadata.all)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Card(
                    child: ListTile(
                      leading: Icon(
                        currentRegion == meta.id ? Icons.toggle_on : Icons.location_city_outlined,
                        color: currentRegion == meta.id ? Colors.blue : Colors.grey,
                      ),
                      title: Text(meta.id.label, style: const TextStyle(fontWeight: FontWeight.w700)),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(meta.id.modeDescription),
                          const SizedBox(height: 6),
                          for (final note in meta.modeNotes) Text('• $note', style: const TextStyle(fontSize: 13)),
                        ],
                      ),
                      trailing: currentRegion == meta.id
                          ? const Text('현재')
                          : ElevatedButton(
                              onPressed: () {
                                ref.read(selectedRegionProvider.notifier).state = meta.id;
                              },
                              child: const Text('선택'),
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
