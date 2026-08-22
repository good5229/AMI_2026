import 'package:flutter/material.dart';

class V18OperationalTriageContract {
  const V18OperationalTriageContract._();

  static const status = 'OU-B';
  static const title = 'v0.18 회고형 운영 우선검토 검증';
  static const split = '개발 71,162 · 검증 16,618 · 확인 9,145 asset-day episodes';
  static const primary = 'Primary · 30일 반복 기록 이벤트 · 확인기간 prevalence 7.3%';
  static const prediction = 'B2_LOGISTIC · AP 0.199 · Top 10% enrichment 3.12x';
  static const queue = 'C25=0 비검토 · C50=62 · C75=80 · C50 burden review difference -0.03일';
  static const workflow = 'DATA_QUALITY_REVIEW → REMOTE_REVIEW_CANDIDATE → FIELD_INSPECTION_CANDIDATE';
  static const decision = 'LIMITED_OPERATIONAL_PRIORITY_EVIDENCE';
  static const boundary = '접수일 시작 시점 이전의 고장 접수 이력만 사용한 사후 모의분석입니다. 고장 확률·전력자료 정확도·실제 수리시간 단축·민원 감소·비용절감 또는 대구 결과의 수영구 직접 적용을 뜻하지 않습니다.';
}

class V18OperationalTriageCard extends StatelessWidget {
  const V18OperationalTriageCard({super.key});

  @override
  Widget build(BuildContext context) => Card(
        key: const Key('v18-operational-triage-card'),
        color: const Color(0xFFE7F0F4),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              const Icon(Icons.low_priority, color: Color(0xFF175A70)),
              const SizedBox(width: 8),
              Expanded(child: Text(V18OperationalTriageContract.title, style: Theme.of(context).textTheme.titleLarge)),
              const Chip(label: Text(V18OperationalTriageContract.status)),
            ]),
            const SizedBox(height: 12),
            const Text(V18OperationalTriageContract.split),
            const Text(V18OperationalTriageContract.primary),
            const Text(V18OperationalTriageContract.prediction),
            const Text(V18OperationalTriageContract.queue),
            const Divider(height: 24),
            const Text(V18OperationalTriageContract.workflow, style: TextStyle(fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),
            const Text(V18OperationalTriageContract.decision),
            const SizedBox(height: 8),
            const Text(V18OperationalTriageContract.boundary, style: TextStyle(fontSize: 12, color: Color(0xFF174657))),
          ]),
        ),
      );
}
