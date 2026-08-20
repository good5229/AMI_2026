# LightGuard v0.9 episode-separated validation protocol

## Decision boundary

This is a pre-outcome protocol. It does not inspect detector scores, labels, candidate performance, calibration performance, or confirmatory performance. The frozen v0.8 calibration and confirmatory artifacts may be consulted only as failure-analysis or regression evidence. They cannot contribute candidate parameters, thresholds, episode allocation, or promotion claims in v0.9.

## Experimental units and context provenance

The indivisible unit is an official-context episode: one region, one season, one 2025 calendar date, its KMA ASOS station-date group of 24 hourly observations, and its KASI sunrise/sunset/civil-twilight response.

| Region | KMA ASOS station | KASI area |
| --- | ---: | --- |
| Suyeong, Busan | 159 | 부산 |
| Gangneung | 105 | 강릉 |
| Chungju | 127 | 충주 |

There are twelve region-season cells. Each selects four distinct dates from its existing frozen v0.7 seven-day KMA window around the 2025 anchor. The anchor is retained, and the other three dates and split are selected through SHA-256 ordering with fixed seed `20260901`. Every cell has exactly two calibration and two confirmatory episodes, for 24 calibration and 24 confirmatory episodes (48 total).

The manifest asserts that all dates are in 2025, each cell has four unique dates and two rows per split, every KMA group has 24 unique official hours, and no KMA station-date group can occur twice. Thus calibration and confirmatory have zero episode, date-within-cell, and KMA-observation overlap.

## Official-data completion gate

The frozen v0.7 context has official KMA ASOS observations for all 48 selected station-date groups. It stores normalized official KASI values only for the twelve original anchor dates; it has neither raw KASI response hashes nor the remaining 36 date values.

The initial manifest consequently marks those 36 episodes `blocked_pending_official_kasi`. This is not a synthetic fallback and is not an availability claim. Scenario generation stays blocked until every episode has verified official KMA and KASI context.

The only permitted completion path is:

```bash
KASI_SERVICE_KEY=... python3 scripts/fetch_v09_context_episodes.py --fetch
python3 scripts/build_v09_episode_manifest.py
```

The fetcher reads a process environment variable only; it does not read or modify `.env`. It calls KASI's area rise/set endpoint with the manifest date and area, stores normalized values plus a raw-response SHA-256, and serializes failure rather than substituting calculated solar times.

If the public-data key is not registered for KASI, the permitted official fallback is `python3 scripts/fetch_v09_context_episodes.py --fetch --official-web`. It executes KASI's own public `algorithms.js` and `delta_t.js` from the official sunrise/sunset calculator in an isolated JavaScript context, records both official source URLs and SHA-256 hashes, and uses the fixed regional asset centroids. This is not the LightGuard internal solar formula, interpolation, or synthetic fallback.

## Downstream locking rules

Only after the manifest gate is open may scenario construction create 16 calibration cases per calibration episode (384 total, eight normal/eight abnormal) and 24 confirmatory cases per confirmatory episode (576 total, twelve normal/twelve abnormal). Candidate selection must finish on calibration and be frozen before confirmatory scoring. No episode reassignment, date substitution, context refresh, or retuning is allowed after confirmatory outcomes are viewed.

## References

- KMA quality/statistics guidance: <https://data.kma.go.kr/resources/images/publication/%EA%B8%B0%EC%83%81%EA%B4%80%EC%B8%A1%EB%8D%B0%EC%9D%B4%ED%84%B0%20%ED%92%88%EC%A7%88%20%ED%86%B5%EA%B3%84%20%EA%B4%80%EB%A6%AC%20%EC%A7%80%EC%B9%A8%282025.9%29.pdf>
- KASI Area sunrise/sunset API: <https://www.data.go.kr/data/15012688/openapi.do>
- Held-out evaluation guidance: <https://scikit-learn.org/stable/modules/cross_validation.html>
