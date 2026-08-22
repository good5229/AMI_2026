import 'package:flutter/material.dart';

class V17MunicipalOperationsContract {
  const V17MunicipalOperationsContract._();

  static const status = 'OPERATIONAL_EVIDENCE_ON_A';
  static const title = 'v0.17 실제 지자체 운영부담 · 대구 공개데이터';
  static const faultScope =
      '고장관리 101,843건 · 관리번호 40,148개 · 2020-01-02~2025-08-09';
  static const discovery =
      '일상점검 92.0% · 민원신고 5.2% · 민원+직원 신고 7.3%';
  static const response = '처리기간 중앙값 0일 · p90 8일 · 음수 기간 품질검토 4건';
  static const repeat =
      '서로 다른 날짜의 반복 기록 자산 23,815개 · 30일 재기록 10.3% (완전 관측 episode 기준)';
  static const spatial =
      'PARTIAL_JOIN · NO_SPATIAL_JOIN · 좌표 후보 100,561건도 ID 의미 검증 전 hotspot 보류';
  static const safety =
      '안전점검 105,449건 · 현장조치 분류 제공 · 전기값은 단위/공식 기준 미확인으로 분포만 사용';
  static const workflow =
      'DATA_QUALITY_REVIEW → REMOTE_MONITOR → FIELD_INSPECTION_CANDIDATE 업무 queue에 연결';
  static const boundary =
      '대구 운영사례는 LightGuard 전력계량 자료와 직접 연결되지 않았습니다. 일부 자료는 행 수가 맞지 않아 사용을 보류했으며, 현장 정확도·민원 예방·처리시간 개선·비용절감을 입증하지 않습니다.';
}

class V17MunicipalOperationsCard extends StatelessWidget {
  const V17MunicipalOperationsCard({super.key});

  @override
  Widget build(BuildContext context) => Card(
        key: const Key('v17-municipal-operations-card'),
        color: const Color(0xFFE8F3EE),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.streetview_outlined,
                      color: Color(0xFF176B4D)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(V17MunicipalOperationsContract.title,
                        style: Theme.of(context).textTheme.titleLarge),
                  ),
                  const Chip(
                      label: Text(V17MunicipalOperationsContract.status)),
                ],
              ),
              const SizedBox(height: 12),
              const _EvidenceLine(
                  label: '운영 규모',
                  value: V17MunicipalOperationsContract.faultScope),
              const _EvidenceLine(
                  label: '발견 경로',
                  value: V17MunicipalOperationsContract.discovery),
              const _EvidenceLine(
                  label: '처리시간',
                  value: V17MunicipalOperationsContract.response),
              const _EvidenceLine(
                  label: '반복 기록',
                  value: V17MunicipalOperationsContract.repeat),
              const _EvidenceLine(
                  label: '공간 결합',
                  value: V17MunicipalOperationsContract.spatial),
              const _EvidenceLine(
                  label: '안전점검',
                  value: V17MunicipalOperationsContract.safety),
              const Divider(height: 24),
              const Text(V17MunicipalOperationsContract.workflow,
                  style: TextStyle(fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              const Text(V17MunicipalOperationsContract.boundary,
                  style: TextStyle(fontSize: 12, color: Color(0xFF14513B))),
            ],
          ),
        ),
      );
}

class _EvidenceLine extends StatelessWidget {
  const _EvidenceLine({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 3),
        child: Text('$label · $value'),
      );
}
