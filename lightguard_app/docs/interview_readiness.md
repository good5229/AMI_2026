# Interview Readiness

No outreach or contact has been performed. The questions below are neutral prompts for a future user-approved interview with the Suyeong-gu responsible office or maintenance contractor.

## Current workflow

1. How is a street-light issue first reported or detected, and which systems record that first signal?
2. What information is recorded when an issue is associated with a distribution cabinet?
3. How are citizen complaints, automated alarms, patrol observations, and contractor reports distinguished in the work record?
4. Which steps occur between initial detection, field confirmation, repair assignment, and closure?
5. What determines the priority or order of field inspections?

## Cabinet, control, and measured data

6. Is the distribution cabinet the unit used for maintenance planning or dispatch assignment? If another unit is used, what is it?
7. What identifier links a cabinet inventory record to a work order, remote-control record, or asset-management record?
8. Is remote ON/OFF status recorded, and how is actual illumination confirmation performed when the two differ?
9. Are partial-outage events recorded separately from whole-circuit or whole-cabinet outages?
10. Is electrical measurement data available at cabinet, circuit, meter, or lamp level, and what is its sampling interval?
11. Can an AMI meter identifier be linked to a cabinet management number through an internal key? If so, which fields and governance rules apply?

## Outcomes and economics

12. Are work orders coded with cause, repair action, parts, labor time, travel time, and completion status?
13. Which official contract or budget document defines the covered assets, work categories, period, and payment basis for street-light maintenance?
14. Is there an official count of dispatches, visits, or completed work orders for the same contract scope and period?
15. Which operational outcome would be considered useful: earlier detection, fewer repeat visits, shorter confirmation time, different priority ordering, or another measure?
16. What limitations or approval requirements apply before an automated ranking could be used by staff?

## Data-request checklist

- Cabinet master data with stable identifier, coordinates, connected lamp/pole count, rated load, branch/circuit, control mode, and reference date.
- Work-order history with detection source, timestamps, status, cause, repair action, and cabinet identifier.
- Remote-control command/status history, if available, with command time and observed result.
- AMI mapping and interval data, if available, with timestamp semantics and missing-data rules.
- Contract/BOQ and payment records with matching scope, period, and denominator.
