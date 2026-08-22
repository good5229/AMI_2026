# v0.21 Evidence Traceability

| Claim | Level | Evidence type | Source | Metric | Qualification |
| --- | --- | --- | --- | --- | --- |
| C001 | GREEN | PRODUCT | lightguard_v0_1/data/data_summary.json | M001 | 현장 확인이 최종 판정 단계다. |
| C002 | YELLOW | ACTUAL_AMI | lightguard_v0_1/data/data_summary.json | M001 | 가명 AMI이며 지자체 분전함 직접 매핑과 현장 정답은 없다. |
| C003 | YELLOW | CONTROLLED | lightguard_app/assets/data/simulation_validation_results_v02.csv | M002 | 46/46은 controlled 재현 결과이며 현장 성능지표가 아니다. |
| C004 | GREEN | NEGATIVE_EXTERNAL | lightguard_v0_1/reports/v14/v14_final_summary.md | - | v0.13/v0.14 negative evidence를 유지한다. |
| C005 | GREEN | MUNICIPAL_DAEGU | lightguard_v0_1/data/validation/v17/v17_operational_summary.json | M003 | 공모전 AMI 또는 현장 고장 정답과 직접 연결되지 않는다. |
| C006 | YELLOW | MUNICIPAL_BUYEO | lightguard_v0_1/data/validation/v19/v19_zero_shot_summary.json | M006 | 운영 우선순위 전이이며 AMI 정확도가 아니다. |
| C007 | YELLOW | MUNICIPAL_ULSAN | lightguard_v0_1/data/validation/v20/v20_zero_shot_summary.json | M011 | 현장 지연 감소의 인과효과나 실제 staffing capacity가 아니다. |
| C008 | YELLOW | MUNICIPAL_ULSAN_ASSET | lightguard_v0_1/data/validation/v20/v20_u1_u2_join_summary.json | M008 | 13개 ambiguous와 48개 unmatched를 제외하며 historical coverage는 UNKNOWN이다. |
| C009 | GREEN | GENERALIZABILITY | lightguard_v0_1/data/validation/v19/v19_common_feature_contract.json | - | 동일 모델이 모든 지자체에 그대로 적용된다는 뜻이 아니다. |
| C010 | GREEN | ARCHITECTURE | lightguard_app/README.md | - | 실제 장비비 절감액·ROI·payback은 산정하지 않았다. |
| C011 | RED | PROHIBITED | lightguard_v0_1/data/validation/v20/v20_feature_availability_contract.json | - | 사용 금지 |
| C012 | RED | PROHIBITED | lightguard_v0_1/data/validation/v20/v20_queue_replay_summary.json | - | 실제 dispatch, unit cost, avoidable dispatch가 없어 사용 금지 |
