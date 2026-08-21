# v0.12R Literature Search Protocol

Frozen before literature-result screening on 2026-08-21.

## Review questions

1. Are persistent meter-relative load departures used as anomaly indicators?
2. Are expected streetlight state versus current/light mismatches used to identify abnormal operation or inspection needs?
3. Are three-phase asymmetry and phase-selective deviations diagnostic signals?
4. What validation is required before an anomaly can be called a fault?
5. Which benchmark and measurement-process limitations constrain LightGuard's interpretation?

## Sources and queries

Search Crossref/DOI metadata, IEEE Xplore metadata, arXiv primary manuscripts, publisher full text, NIST and other government/standards sources. Query families are fixed as:

- smart meter load profile anomaly technical fault
- AMI anomaly detection utility operations
- electrical load profile abnormal consumption
- meter-specific time-of-day baseline anomaly
- persistent load deviation EWMA CUSUM anomaly
- streetlight daytime operation current sensor ambient light
- streetlight expected state current mismatch fault monitoring
- three phase current imbalance negative sequence diagnostics
- phase current asymmetry anomaly fault diagnosis
- time series anomaly benchmark leakage point adjustment
- blinded assessment anchoring bias inter-rater agreement

## Inclusion

- Peer-reviewed paper, government/public technical publication, standard, or official technical publication.
- Clear title, authorship, year, stable DOI or authoritative URL.
- Accessible method and result, not metadata-only evidence for a core claim.
- Explicit anomaly mechanism involving current, load, state mismatch, persistence, phase behavior, measurement process, or blinded review.
- Transfer boundary to LightGuard can be stated without treating literature as event-level truth.

## Exclusion

- Marketing, SEO, unsourced blog, duplicate, retracted work, or inaccessible claim.
- Anomaly and fault are conflated without outcome validation.
- Target, measurement, baseline, or label definition is not recoverable.
- Result is selected only because it agrees with H1, P1, P2, P3, or the canonical six.
- Long quotations or probability transfer unsupported by matching domain, label, measurement, field outcome, and calibration.

## Extraction and grading

Extract domain, data type, anomaly definition, label source, field validation, method, key result, limitations, directness, and allowed/prohibited claims.

- Quality A: peer-reviewed, government, or standard.
- Quality B: official technical publication with inspectable method.
- Quality C: secondary support only; never anchors a core claim.
- L3: direct streetlight/current/expected-state support.
- L2: direct electrical or AMI mechanism support.
- L1: general time-series or measurement support.
- L0: no support found.

## Independence and stopping

Literature grade is assigned without H1 score, proxy score, canonical membership, or human rating. Search aims for at least 8 core direct and 5 methodology sources, but stops rather than adding low-quality material. Conflicting and null evidence remains in the log.

No evidence grade is a fault probability. Literature cannot replace Gold or Silver operational labels.
