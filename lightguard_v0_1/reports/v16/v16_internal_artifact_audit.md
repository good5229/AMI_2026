# LightGuard v0.16 internal artifact audit

## Verdicts

- Artifact and build contract: `PASS`
- Official competition alignment: `PASS`
- Official streetlight asset coverage: `PASS`, 5/5
- Experimental prospective targets: `FAIL`
- Independent validation: `NO`
- Promotion to field-performance claim: `BLOCKED`

## Evidence checks

- Official scope registry contains 129 assets, 5 streetlight eligible assets,
  and 124 out-of-scope assets.
- v0.10 and canonical overlap counts are zero for the B-L-12 extension.
- The corpus contains 71 explicitly post-hoc v0.15 replay pairs and 9 B-L-12
  exploratory extension pairs.
- H1 threshold is unchanged.
- P0 is labeled as collapsed non-normal endpoint semantics, not a deployed
  operational policy.
- P1 separates QA, remote monitoring, and field candidates.
- Natural shadow contains target-side lanes and no truth, recovery, accuracy,
  FPR, specificity, or fault-probability fields.
- Flutter disclosure reports both failed targets and the independent-validation
  prohibition.

## Experimental findings

- R: P1 4.88%, P0 26.83%, RD -21.95 percentage points.
- B: P1 2.56%, P0 5.13%, RD -2.56 percentage points.
- Both frozen prospective targets were missed.
- The guarded policy must not be promoted or tuned again on this corpus.

## Residual risks

- No actual fault or maintenance labels exist.
- The 71 replay pairs informed earlier mechanism analysis.
- The B-L-12 extension has only nine pairs and became exploratory during the
  action-vocabulary audit.
- April-June covers one limited seasonal window.
- A/C meters are not streetlight assets and cannot establish LightGuard field
  generality.

## Build evidence

- Artifact contract: PASS
- Flutter analyze: no issues
- Flutter tests: 29 passed
- Web release: built
- Android release: built
