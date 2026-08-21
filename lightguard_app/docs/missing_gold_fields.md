# Missing Gold and Silver Fields

## Current blocking gaps

| priority | required data | minimum fields | why it matters |
|---:|---|---|---|
| 1 | cabinet to AMI mapping | immutable cabinet ID, meter ID, valid-from/to, mapping authority | resolves the target asset without name similarity |
| 2 | controller ON/OFF history | controller/cabinet ID, command, observed state, timestamp, acknowledgement | supports an independent operational-discrepancy label |
| 3 | maintenance and repair closeout | asset ID, inspection time, finding, action, cause, completion time | supports a scoped field-confirmed outcome |
| 4 | complaint and inspection log | asset ID/location, received time, visit time, disposition | supports independent corroboration and sampling |

## Acceptance contract

- IDs must map to the target AMI through a versioned, auditable chain.
- Timestamps must declare timezone and interval semantics.
- Missing paperwork is unknown, not a negative label.
- Reviewer or operator records must not be generated from the H1 decision or proxy score.
- Gold evaluation requires explicit positive, negative, unknown, duplicate, and exclusion rules.
- Raw/Office exports remain read-only and untracked; only aggregate provenance and hashes may enter Git.

## Next acquisition

Request the cabinet-meter mapping first, then controller state history, maintenance closeouts, and complaint/inspection dispositions. A prospective pilot should blind field reviewers to model group and score.
