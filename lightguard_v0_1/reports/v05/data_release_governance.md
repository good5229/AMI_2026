# v0.5 Data Release Governance

## Decision

- `lightguard_v0_1.sqlite` is a generated local integration artifact and is **not approved for public redistribution**.
- The database combines municipal asset coordinates and addresses with controller metadata, including modem identifiers. Even when source rows originate from competition or public-sector material, that combined operational view is more sensitive than the product-facing aggregate evidence.
- The database is removed from Git tracking and covered by `*.sqlite` / `*.sqlite3` ignore rules. Local regeneration remains possible from the excluded source workbooks through the existing build pipeline.

## Public release boundary

- Allowed: anonymized B-line meter IDs, six detector-candidate summaries, aggregate robustness metrics, frozen configuration hashes, non-sensitive app seed data already reviewed for the demo.
- Prohibited: raw source workbooks, API credentials, controller modem identifiers, combined cabinet/controller operational database, and any direct AMI-to-municipal-asset mapping.
- The Flutter application does not depend on the SQLite file; it consumes reviewed JSON/CSV assets.

## Review performed

- Schema review covered `municipalities`, `cabinets`, `fixtures`, `controllers`, `ami_meter_profiles`, `ami_events`, and `ami_cabinet_mappings`.
- No person-name, phone, email, password, token, or private-key column was identified.
- Operational sensitivity remains because `controllers` contains `modem_id` and the asset tables contain precise locations and addresses. Exclusion is therefore the conservative release decision.
- `ami_cabinet_mappings` remains logically separate; no unverified actual AMI-to-Suyeong cabinet mapping may be published.

## Re-entry gate

The database may be reconsidered only after a named data owner documents source licensing, field-level minimization, modem-ID removal, location precision policy, mapping verification policy, and a fresh secret/privacy scan.
