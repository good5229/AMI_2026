import 'package:flutter_test/flutter_test.dart';
import 'package:lightguard_app/features/ami_validation/v17_municipal_operations_card.dart';

void main() {
  test('v0.17 exposes municipal workload with strict AMI boundary', () {
    expect(V17MunicipalOperationsContract.status,
        'OPERATIONAL_EVIDENCE_ON_A');
    expect(V17MunicipalOperationsContract.faultScope, contains('101,843'));
    expect(V17MunicipalOperationsContract.faultScope, contains('40,148'));
    expect(V17MunicipalOperationsContract.discovery, contains('일상점검'));
    expect(V17MunicipalOperationsContract.discovery, contains('민원신고'));
    expect(V17MunicipalOperationsContract.response, contains('p90 8일'));
    expect(V17MunicipalOperationsContract.repeat, contains('23,815'));
    expect(V17MunicipalOperationsContract.repeat, contains('10.3%'));
    expect(V17MunicipalOperationsContract.spatial, contains('PARTIAL_JOIN'));
    expect(V17MunicipalOperationsContract.spatial, contains('NO_SPATIAL_JOIN'));
    expect(V17MunicipalOperationsContract.spatial, contains('100,561'));
    expect(V17MunicipalOperationsContract.safety, contains('105,449'));
    expect(V17MunicipalOperationsContract.workflow,
        contains('FIELD_INSPECTION_CANDIDATE'));
    expect(V17MunicipalOperationsContract.boundary, contains('전력계량 자료와 직접 연결되지 않았습니다'));
    expect(V17MunicipalOperationsContract.boundary, contains('현장 정확도'));
    expect(V17MunicipalOperationsContract.boundary, contains('민원 예방'));
    expect(V17MunicipalOperationsContract.boundary, contains('비용절감'));
  });
}
