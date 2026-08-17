import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/widgets/app_scaffold.dart';
import '../../core/widgets/status_badges.dart';
import '../../data/repositories/lightguard_repository.dart';

class AmiValidationScreen extends ConsumerWidget {
  const AmiValidationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventsAsync = ref.watch(competitionAmiEventsProvider);
    return eventsAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, s) => Scaffold(body: Center(child: Text('실제 AMI 데이터 로드 실패: $e'))),
      data: (events) {
        return LightguardShell(
          title: '실제 AMI 검증 사례',
          child: ListView.separated(
            padding: const EdgeInsets.all(12),
            itemCount: events.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (_, idx) {
              final e = events[idx];
              return Card(
                child: ListTile(
                  title: Text(e.meterId),
                  subtitle: Text('${e.eventType} · ${e.firstSample} ~ ${e.lastSample}'),
                  leading: const StatusBadge(type: BadgeType.realAmi, label: '실제 AMI'),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text('duration: ${e.durationMin}분'),
                      Text('activation: ${(e.maxActivation * 100).toStringAsFixed(1)}%'),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }
}
