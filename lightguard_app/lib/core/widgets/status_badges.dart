import 'package:flutter/material.dart';
import '../../data/models/lightguard_models.dart';

enum BadgeType { normal, realAmi, scenario, validation, inspect }

class StatusBadge extends StatelessWidget {
  const StatusBadge({super.key, required this.type, required this.label});

  final BadgeType type;
  final String label;

  @override
  Widget build(BuildContext context) {
    final color = switch (type) {
      BadgeType.normal => Colors.green,
      BadgeType.realAmi => const Color(0xFF007C78),
      BadgeType.scenario => Colors.orange,
      BadgeType.validation => Colors.indigo,
      BadgeType.inspect => Colors.red,
    };

    return Container(
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      child: Text(
        label,
        style:
            TextStyle(color: color, fontWeight: FontWeight.w700, fontSize: 12),
      ),
    );
  }
}

String statusToLabel(InspectionStatus status) => switch (status) {
      InspectionStatus.normal => '정상',
      InspectionStatus.observe => '관찰',
      InspectionStatus.inspectionRecommended => '점검 권고',
      InspectionStatus.priorityInspection => '우선 점검',
      InspectionStatus.dataCheckRequired => '데이터 확인 필요',
    };

BadgeType statusToBadge(InspectionStatus status) => switch (status) {
      InspectionStatus.normal => BadgeType.normal,
      InspectionStatus.observe => BadgeType.validation,
      InspectionStatus.inspectionRecommended => BadgeType.scenario,
      InspectionStatus.priorityInspection => BadgeType.inspect,
      InspectionStatus.dataCheckRequired => BadgeType.validation,
    };
