import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../data/models/region_config.dart';
import '../../data/repositories/lightguard_repository.dart';

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
        error: (error, _) => const Center(child: Text('지역 자료를 불러오지 못했습니다.')),
        data: (data) => ListView(
          padding: const EdgeInsets.all(12),
          children: [
            Card(
              color: const Color(0xFFF0F6F1),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text('현재 지역 · ${currentRegion.label}', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 6),
                  Text('분전함 ${data.objects.length}개 · 가로등 ${data.totalLampCount}개'),
                  const SizedBox(height: 6),
                  const Text('지자체 전력계량 자료는 아직 직접 연결되지 않았습니다.', style: TextStyle(fontSize: 12)),
                ]),
              ),
            ),
            const SizedBox(height: 16),
            Text('운영 화면을 전환할 지역', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 4),
            const Text('지역을 선택하면 현황·지도·점검 화면이 함께 바뀝니다.'),
            const SizedBox(height: 10),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                for (final meta in RegionMetadata.all)
                  _RegionCard(meta: meta, selected: currentRegion == meta.id, onSelect: () => ref.read(selectedRegionProvider.notifier).state = meta.id),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _RegionCard extends StatelessWidget {
  const _RegionCard({required this.meta, required this.selected, required this.onSelect});
  final RegionMetadata meta;
  final bool selected;
  final VoidCallback onSelect;

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 330,
    child: Card(
      color: selected ? const Color(0xFFF0F7F4) : null,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Expanded(child: Text(meta.id.label, style: Theme.of(context).textTheme.titleMedium)),
            if (selected) const Icon(Icons.check_circle, color: Color(0xFF0F766E), size: 20),
          ]),
          const SizedBox(height: 6),
          Text(meta.id.modeDescription),
          const SizedBox(height: 10),
          for (final note in meta.modeNotes) Padding(padding: const EdgeInsets.only(bottom: 4), child: Text('• $note', style: const TextStyle(fontSize: 12))),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: selected
                ? const FilledButton(onPressed: null, child: Text('현재 지역'))
                : OutlinedButton(onPressed: onSelect, child: const Text('이 지역으로 전환')),
          ),
        ]),
      ),
    ),
  );
}
