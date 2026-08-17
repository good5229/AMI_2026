# LightGuard v0.2 Validation (수영구 우선 v0.2 Flow)

- 생성 시각: 2026-08-17T22:02:10Z
- 대상 지자체: 수영구
- 분전함: 204개
- 3.4kW 기반 시나리오 주입 대상: 46개
- 시나리오 검출 이벤트: 46개
- 주입-검출 정합 성공: 46/46

## 이벤트 객체 형식(요약)
- 구조: 분전함 → 자산정보(asset_info) → 예상점등시간(expected_schedule) → 정격부하(expected_load) → AMI(ami) → 근거(anomaly_evidence) → 점검우선순위(inspection_priority)
- AMI는 현재 실제 매핑이 없으므로 모든 항목에서 `has_real_ami = false`로 명시
- 시나리오 주입은 `scenario_injection` 모드로 추적됨

## 점검우선순위 분포
- critical: 46
- low: 158

## Scenario 검증

- SCN-350451a801: cabinet=SY-CAB-1cd2be8800, match=True (1 events)
- SCN-e41dcc6f3a: cabinet=SY-CAB-69005e730c, match=True (1 events)
- SCN-69d2d11b92: cabinet=SY-CAB-987a63343c, match=True (1 events)
- SCN-a6ab8e646d: cabinet=SY-CAB-082c6a7345, match=True (1 events)
- SCN-6dad945f75: cabinet=SY-CAB-4dd2e815cc, match=True (1 events)
- SCN-0e79e93e66: cabinet=SY-CAB-0ff5c26f27, match=True (1 events)
- SCN-d530d229da: cabinet=SY-CAB-e2da04e0e2, match=True (1 events)
- SCN-58743a3b54: cabinet=SY-CAB-715b5f5216, match=True (1 events)
- SCN-96c377f80b: cabinet=SY-CAB-63d66e1877, match=True (1 events)
- SCN-f4cbf61148: cabinet=SY-CAB-66c30ac282, match=True (1 events)
- SCN-477ce7a013: cabinet=SY-CAB-502375414c, match=True (1 events)
- SCN-73fe007f6a: cabinet=SY-CAB-84f0d25e33, match=True (1 events)
- SCN-f9115b4acd: cabinet=SY-CAB-7b2542c2bd, match=True (1 events)
- SCN-f18cd0f98f: cabinet=SY-CAB-2aa1ae2a5f, match=True (1 events)
- SCN-61533d070e: cabinet=SY-CAB-6dc9777a03, match=True (1 events)
- SCN-f752955ae0: cabinet=SY-CAB-5712016b2e, match=True (1 events)
- SCN-55ddb58462: cabinet=SY-CAB-4701a959c6, match=True (1 events)
- SCN-5bfe75e6e1: cabinet=SY-CAB-aac150345f, match=True (1 events)
- SCN-1216e8ab2c: cabinet=SY-CAB-ba3d522445, match=True (1 events)
- SCN-a073bdf790: cabinet=SY-CAB-4b02a9e27b, match=True (1 events)
- SCN-fee494f2e0: cabinet=SY-CAB-cdf9b98e1d, match=True (1 events)
- SCN-8df8a4590a: cabinet=SY-CAB-6760905c21, match=True (1 events)
- SCN-e5a13a9852: cabinet=SY-CAB-9e585a96e3, match=True (1 events)
- SCN-7a3d1b2b03: cabinet=SY-CAB-b411ece2df, match=True (1 events)
- SCN-68c2c6f5c7: cabinet=SY-CAB-5e5e2e417b, match=True (1 events)
- SCN-1369745427: cabinet=SY-CAB-50177e52f5, match=True (1 events)
- SCN-89a5cb03d4: cabinet=SY-CAB-a0094f6a60, match=True (1 events)
- SCN-e84e767af2: cabinet=SY-CAB-d70c07505f, match=True (1 events)
- SCN-ce35c2650b: cabinet=SY-CAB-1e5575ef40, match=True (1 events)
- SCN-a12e772151: cabinet=SY-CAB-2665e30f6b, match=True (1 events)
- SCN-942c64a67c: cabinet=SY-CAB-8389649fa3, match=True (1 events)
- SCN-63dbf2ebf3: cabinet=SY-CAB-248450b7b0, match=True (1 events)
- SCN-f60f9847ba: cabinet=SY-CAB-245507b8f2, match=True (1 events)
- SCN-94c4742469: cabinet=SY-CAB-37f3f2b32b, match=True (1 events)
- SCN-97c0d19692: cabinet=SY-CAB-ff01b34d1f, match=True (1 events)
- SCN-f2d614eb14: cabinet=SY-CAB-5643046ecf, match=True (1 events)
- SCN-dfc02e7e3f: cabinet=SY-CAB-50da942b62, match=True (1 events)
- SCN-b48b075218: cabinet=SY-CAB-16bce2a1c0, match=True (1 events)
- SCN-2a8a61c459: cabinet=SY-CAB-d5d4f36cc5, match=True (1 events)
- SCN-ea447d3132: cabinet=SY-CAB-dd85b9a3b7, match=True (1 events)
- SCN-b1533c9b3e: cabinet=SY-CAB-11a030806b, match=True (1 events)
- SCN-3bfd6c6000: cabinet=SY-CAB-bc9ff352d9, match=True (1 events)
- SCN-32431ee6e7: cabinet=SY-CAB-fca94bf3bb, match=True (1 events)
- SCN-2cd9aec154: cabinet=SY-CAB-0c940c7f31, match=True (1 events)
- SCN-b0c9ac9e41: cabinet=SY-CAB-d6a63b2385, match=True (1 events)
- SCN-9951e84728: cabinet=SY-CAB-3c6861d396, match=True (1 events)