import 'package:flutter/material.dart';
import '../presentation/operational_copy.dart';
import '../../data/models/lightguard_models.dart';

enum BadgeType { normal, realAmi, scenario, validation, inspect }

class StatusBadge extends StatelessWidget {
  const StatusBadge({super.key, required this.type, required this.label});

  final BadgeType type;
  final String label;

  @override
  Widget build(BuildContext context) {
    final color = switch (type) {
      BadgeType.normal => const Color(0xFF347149),
      BadgeType.realAmi => const Color(0xFF007C78),
      BadgeType.scenario => const Color(0xFF9A5B00),
      BadgeType.validation => const Color(0xFF405D73),
      BadgeType.inspect => const Color(0xFFB42318),
    };

    return Container(
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.32)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w700,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

String statusToLabel(InspectionStatus status) => operationalStatusLabel(status);

BadgeType statusToBadge(InspectionStatus status) => switch (status) {
      InspectionStatus.normal => BadgeType.normal,
      InspectionStatus.observe => BadgeType.validation,
      InspectionStatus.inspectionRecommended => BadgeType.scenario,
      InspectionStatus.priorityInspection => BadgeType.inspect,
      InspectionStatus.dataCheckRequired => BadgeType.validation,
    };
