# LightGuard v0.10 Real-Background Transport Final Summary

## 1. Repository / Freeze
- branch: `codex/context-aware-validation`
- git SHA: `38fda2a26c5f55eee7ce0317d98f18df45ff1ac2`
- v0.9 H1: frozen; no Track-A retuning
- H1 config SHA: `b536f8ca68222662c717cd27a6af4c3c64a3330782b0545503df6e4aff3e6232`

## 2. Actual AMI Source
- source: `2-2_MDMS자료(AMI 데이터)_B선로_가명화_★.xlsx` (ignored/untracked)
- SHA-256: `c18b49022d1c7dee2117a8d65a07d71351fb1aea8538751b7032867e4081b7d0`
- rows/meters: `280836` / `33`
- target: 5 meters, 2026-04-01 through 2026-06-30, 15-minute interval-end

## 3. Background Pool
- eligible frozen units: `200`; 40 per meter
- pool SHA: `b59120e8580ce0502ea5001b3f12d2c932b1b6fde65abb063d87e12d84049282`
- source-only selection; canonical +/-4h buffers excluded; H1 output unused

## 4. Counterfactual Injection
- constructable/pool: `182/200`
- current-only identity residual graft; energy unchanged; raw values uncommitted

## 5. Frozen H1 Transport
- informative pairs: `149`
- IRR: `0.97315436`
- worst-meter/operator IRR: `0.85714286` / `0.78947368`
- benign escalation: `0.0`
- median score uplift: `0.25`
- gate: `PASS`; R1 triggered: `False`

## 6. Causal Shadow Replay
- meter-days/evaluable: `455/305`
- inspect/observe: `0/6`
- canonical six are replay coverage only, never actual recall

## 7. Evidence Availability
- solar/load/policy: unavailable
- persistence: current-derived
- phase: native measured phases only

## 8. Claims Allowed
- Real-background counterfactual transport validation passed for frozen H1 on the defined semi-synthetic protocol.
- Past-only shadow replay describes candidate density and meter drift.

## 9. Claims Prohibited
- Field accuracy, actual fault recall, real-background FPR/specificity, municipal performance, and production readiness.

## 10. Remaining Gap
- cabinet-linked municipal AMI, maintenance labels, cabinet-meter mapping, and prospective field shadow pilot.
