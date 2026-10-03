# LightGuard field workflow: competition-final scope

## Purpose and evidence boundary

This release helps an operator decide what to review, why, and what to record on a compact phone. It does not diagnose a fault or claim live telemetry, central dispatch, synchronization, savings, or measured accuracy. Existing seed/validation data retain their original provenance. JEV is outside this feature.

## Functional contract

1. **Today's work queue.** The first screen leads with actionable candidates, a one-sentence reason, next action, and filters/counts for overdue, remote review, field review, and data-quality review. Candidate ordering uses existing priority only; a case becomes overdue only when a user-entered due date exists and is past. Completed cases leave the active queue but remain accessible. Show the dataset timestamp so “today” never implies a live feed. Preserve existing region and inspection routes.
2. **Progressive explanation.** A cabinet opens with a ten-second summary and action. A second level shows up to three concrete observations plus counterevidence/unknowns. A third level exposes criteria, source and timestamp, input/provenance, and the existing detailed asset/signal/context facts. Never convert a simulated signal into a real AMI observation.
3. **Local case loop.** A user can move a candidate through remote review, field review, observation, and a recorded outcome. Capture structured outcome code (fault observed, normal, operational exception, data issue, action completed), short note, optional assignee and due date, and update time. Keep previously saved v1 outcome data readable where practical. Persist on web and Android device across restart; indicate that the state is device-only and has no server sync. No fabricated completion verification.
4. **Field mode.** The phone detail view makes asset ID, available address/coordinates, map link, reason, a short check sequence, and one primary result action easy to reach. Keep that action above system/navigation insets and keyboard. Targets are at least 48 dp. If position or online map tiles are unavailable, say so; the local inspection queue, asset identity/status, coordinates, selection, and detail navigation remain usable without tiles. Map tiles are online-only; do not imply that offline tiles are available. At desktop widths (1024 px and above), use a queue-and-summary dashboard and a map with a selectable asset list alongside it.
5. **Observed impact.** Count only locally recorded outcomes (for example completed, normal, fault observed, data issue) and show the denominator and device-only scope. Do not present detector success, money/time saved, or model accuracy as observed benefit.
6. **Source labels.** Distinguish municipal asset records, actual AMI when present, validation/scenario signal, and maintenance history. For absent maintenance history say “not linked”; locally entered outcomes are labeled as operator records, not source maintenance history. Source type remains visible in queue and each explanation level.

## Interface direction

Retain LightGuard dark teal and amber as navigation and attention roles. Use restrained public-infrastructure signage: strong Korean type hierarchy, ruled sections, compact status tags with text, and obvious action labels. Avoid decorative gradients and synthetic illustrations. Compact phones use a single reading column and bottom navigation; wider layouts may show list and supporting detail with a rail. Respect safe insets, text scaling, contrast, and 48 dp touch targets.

Reference principles: [Material 3 canonical layouts](https://m3.material.io/foundations/layout/canonical-examples/overview) for adaptive panes; [GOV.UK task list](https://design-system.service.gov.uk/components/task-list/) and [status tags](https://design-system.service.gov.uk/components/tag/) for explicit task/status text; [ArcGIS Field Maps offline maps](https://doc.arcgis.com/en/field-maps/android/use-maps/download-maps.htm) and [tool reference](https://doc.arcgis.com/en/field-maps/android/use-maps/quick-reference.htm) for clear on-device/offline affordances. These are interaction references, not visual templates or a claim that LightGuard downloads maps.

## Acceptance checklist

- On a compact Android-sized viewport, the first actionable item and its next action are readable without horizontal scrolling; bottom navigation and the primary action remain reachable with safe insets.
- Queue filters reflect case state and user due dates; an item without a due date is never marked overdue. Dataset age is visible.
- Each cabinet offers summary, evidence/counterevidence, and provenance/details in that order. Missing evidence is explicitly unknown.
- Save a structured case result, reopen it, and see the same state after restart on web and Android. The UI consistently says device-only/no sync.
- Local outcome counts change with real local saves, never seed/scenario counts, and show their denominator.
- Source chips/copy correctly distinguish actual AMI, municipal asset, scenario signal, absent history, and local operator entry.
- Existing dashboard, inspections, cabinet, map, and evidence routes remain usable.
- Focused widget/storage tests and Flutter analysis pass; review at compact and expanded widths, with larger text where practical.
