# Operational Evidence

Access date for every source below: 2026-08-20 (Asia/Seoul).

## What the public evidence supports

The public evidence supports a narrow, defensible statement: a street-light distribution cabinet is a practical operational reference point because it groups lamps, power/control equipment, location, and maintenance responsibility. It does not establish that Suyeong-gu has public AMI data, a particular remote-control platform, a particular dispatch process, or a known failure rate.

LightGuard can therefore present the following workflow as an operational hypothesis to validate with the municipality:

`cabinet -> asset scope -> expected lighting/load context -> measured signal -> anomaly evidence -> inspection priority`

The current MVP must label the public asset information as official reference data and label the AMI replay as anonymized validation data. The two must not be presented as one municipality's measured system.

## Source register

| Source | Institution | Observed operational fields or statement | Use in LightGuard | Limitation / anti-pattern |
|---|---|---|---|---|
| [Seongnam cabinet inventory](https://www.data.go.kr/data/15032441/fileData.do) | Gyeonggi-do Seongnam City | Cabinet name/address, pole count, lamp count; annual update; page describes cabinet as distribution/control and maintenance reference point. | Public precedent for cabinet-first asset schema and map/list views. | Different city; static inventory; blank fields are unknown. |
| [Yeonsu-gu cabinet information](https://www.data.go.kr/data/15059623/fileData.do) | Incheon Yeonsu-gu | Management number, installation count, address, latitude/longitude, installation year, managing agency/contact, reference date; stated uses include field confirmation, complaints, and budget planning. | Evidence for stable asset ID, field navigation, contact/agency metadata, and lifecycle context. | Does not include work orders, dispatch counts, or AMI readings. |
| [Gangneung street-light inventory](https://www.data.go.kr/data/15117413/fileData.do) | Gangneung City | Street-light code and cabinet code, branch fields, lamp type, rated lamp capacity, partial-lighting fields. | Reference for expected load and cabinet-to-lamp grouping in the region selector. | One-time 2023 asset snapshot; not Suyeong evidence. |
| [Chungju cabinet inventory](https://www.data.go.kr/data/15041822/fileData.do) | Chungju City | Cabinet ID/name, location, connected pole count, managing agency, coordinates, reference date; page links the data to maintenance, budget, complaints, and fault response. | Cross-check for cabinet-centric data contract and operations vocabulary. | Different city; page narrative is not an observed work-order dataset. |
| [Suyeong 2026 budget portal](https://www.suyeong.go.kr/index.suyeong?menuCd=DOM_000000119001001000) | Suyeong-gu Office | Official entry point for the 2026 base budget and departmental documents. | Starting point for locating the target department's official budget line and period. | A landing page does not identify a matching asset denominator or dispatch denominator. |
| [Busan organization directory, Suyeong entry](https://www.busan.go.kr/bhtelinfo02/?curPage=2254) | Busan Metropolitan City | Suyeong-gu Safety Management Office lists street-light unit-price maintenance and material management duties. | Direct evidence of a responsible municipal function to validate in interviews. | Duty assignment is not proof of actual workflow timing or cost. |
| [Gangneung energy department duties](https://www.gn.go.kr/www/selectEmployeeList.do?key=735&pageIndex=2&searchDeptCode=42010160000&searchKrwd=) | Gangneung City | Official listing connects unit-price maintenance, remote-control-system maintenance, and civil complaints. | Workflow precedent for separating complaint intake, remote-control monitoring, and field maintenance. | Different municipality; cannot be used as Suyeong performance or cost evidence. |
| [G2B 2026 maintenance cost schedule](https://www.g2b.go.kr/pn/pnp/pnpe/UntyAtchFile/downloadFile.do?bidPbancNo=R26BK01450767&bidPbancOrd=000&fileSeq=6&fileType=&prcmBsneSeCd=07) | Korea ON-line E-Procurement System / Gwangju Seo-gu bid | Itemized scope includes cabinet labels, cabinet-based leakage-circuit exploration, cabinet installation/removal, lighting equipment, and underground cable work. | Defines the procurement questions and work categories to request for Suyeong. | No LightGuard event count or dispatch denominator; not a Suyeong contract. |
| [Jeonju remote-control announcement](https://www.jeonju.go.kr/planweb/board/view.9is?boardUid=ff8080818990c349018b1dbaa78e4b41&contentUid=ff8080818990c349018b041a87373953&dataUid=8eba577186a04f6abab704d3cdee0d17&page=794&tmpField14=) | Jeonju City | Official announcement reports two-way remote control and cabinet-level status/defect visibility for 725 cabinets. | Supports the product hypothesis that remote-control status can reduce blind field confirmation when such a system exists. | 2014 capital deployment in another city; cannot prove current Suyeong capability or savings. |

## Operational interpretation

- `Cabinet ID`: candidate operational join key, pending confirmation that Suyeong's maintenance system uses the same identifier.
- `Asset scope`: lamp count, rated load, branches, coordinates, managing agency, and reference date.
- `Expected context`: KASI/KMA context and asset-derived expected load are contextual signals; they are not maintenance records.
- `Measured signal`: current AMI is absent for the 204 Suyeong municipal assets in the current MVP. The six AMI windows are anonymized competition validation data.
- `Anomaly evidence`: a detector score and evidence fields support triage, not a confirmed failure diagnosis.
- `Inspection priority`: a proposed queue that requires a human or municipal workflow to validate before operational adoption.

## Evidence gaps

The public sources do not answer whether Suyeong has: cabinet-level work-order history, a complaint-to-dispatch timestamp chain, remote ON versus actual-light confirmation, AMI-to-cabinet mapping, repair-cause codes, or a dispatch denominator. These are interview/data-request items, not facts to infer from the public pages.
