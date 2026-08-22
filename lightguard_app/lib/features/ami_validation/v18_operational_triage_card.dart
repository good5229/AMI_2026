import 'package:flutter/material.dart';

class V18OperationalTriageContract {
  const V18OperationalTriageContract._();

  static const status = '운영 우선순위 근거 제한';
  static const title = '과거 운영기록 기반 우선검토 검증';
  static const split = '개발 71,162건 · 검증 16,618건 · 확인 9,145건의 자산·일 단위 기록';
  static const primary = '주요 판정 대상 · 30일 반복 기록 · 확인기간 발생 비율 7.3%';
  static const prediction = '로지스틱 분석 · 평균 정밀도 0.199 · 상위 10% 대상의 반복 기록 밀도 3.12배';
  static const queue = '검토 기준별 후보 수: 하위 기준 0건 · 중앙 기준 62건 · 상위 기준 80건 · 중앙 기준 업무부담 차이 -0.03일';
  static const workflow = '자료 품질 확인 → 원격 확인 후보 → 현장점검 후보';
  static const decision = '운영 우선순위에 참고할 수 있으나 제한적으로 해석';
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
