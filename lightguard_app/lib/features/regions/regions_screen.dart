import 'package:flutter/material.dart';
import '../../core/widgets/app_scaffold.dart';

class RegionInfo {
  const RegionInfo({
    required this.name,
    required this.mode,
    required this.notes,
  });

  final String name;
  final String mode;
  final List<String> notes;
}

class RegionsScreen extends StatelessWidget {
  const RegionsScreen({super.key});

  static const regions = [
    RegionInfo(
      name: '부산 수영구',
      mode: 'Full Asset Mode',
      notes: [
        '개별 가로등/분전함 연결 가능',
        '총 정격용량, 좌표 기반 분석',
        '분전함 204개 · 가로등 4,076개',
      ],
    ),
    RegionInfo(
      name: '강릉시',
      mode: 'Controller-linked Mode',
      notes: [
        '제어 설정 메타데이터 존재',
        '분전함·제어기 조인율 높음',
        '가로등 5,667개 · 분전함 339개',
      ],
    ),
    RegionInfo(
      name: '충주시',
      mode: 'Minimal Asset Mode',
      notes: [
        '분전함 중심',
        '제한적 자산 스펙',
        '분전함 871개 · 등주수 16,121개',
      ],
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return LightguardShell(
      title: '지역 전환',
      child: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          for (final r in regions)
            Card(
              child: ListTile(
                title: Text(r.name, style: const TextStyle(fontWeight: FontWeight.w700)),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(r.mode),
                    const SizedBox(height: 6),
                    for (final n in r.notes)
                      Text('• $n', style: const TextStyle(fontSize: 13)),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
