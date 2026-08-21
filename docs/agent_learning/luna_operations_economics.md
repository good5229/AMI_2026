# Agent Learning Note

## Role

Public Operations & Economic Evidence Researcher for LightGuard v0.5. The task is to establish what a street-light cabinet can support operationally, identify public evidence for maintenance workflows and procurement scope, and define the boundary beyond which an economic claim would be unsupported.

## Model actually used

`gpt-5.6-luna` as assigned to Subagent C by the task runtime. The repository cannot independently inspect Codex model metadata, so this is recorded as the runtime assignment rather than a claim derived from shell output.

## Access date

2026-08-20 (Asia/Seoul). URLs below are the exact pages reviewed. Dynamic portal metadata may change after this date.

## Sources reviewed

### Required public-data portal sources

| URL | Institution | Key evidence | Applicability | Anti-pattern |
|---|---|---|---|---|
| https://www.data.go.kr/data/15032441/fileData.do | Gyeonggi-do Seongnam City, via data.go.kr | Cabinet name, address, pole count, lamp count; 826 rows; annual update. The page explicitly describes a cabinet as a power distribution/control and maintenance reference point. | Schema and operational-unit precedent only. It is not Suyeong data and does not provide a maintenance cost denominator. | Do not transplant Seongnam counts, locations, or costs into Suyeong. Treat blank fields as unknown, not zero. |
| https://www.data.go.kr/data/15059623/fileData.do | Incheon Yeonsu-gu, via data.go.kr | 681 rows; cabinet management number, installation count, address, coordinates, installation year, managing agency/contact, reference date; the page states uses including field confirmation, complaints, and budget planning. | Strong evidence that cabinet identity and asset metadata can support maintenance triage and GIS lookup. | Do not infer dispatch frequency, failure rate, or labor cost from a static asset file. |
| https://www.data.go.kr/data/15117413/fileData.do | Gangneung City, Gangwon State, via data.go.kr | 5,667 rows; lamp code and cabinet code, pole type, circuit branch, lamp type, rated lamp capacity, and partial-lighting fields. | Supports asset-to-cabinet grouping, rated-load estimation, branch/phase context, and a region selector schema. | Do not combine Gangneung asset quantities with Suyeong contract prices or AMI observations. |
| https://www.data.go.kr/data/15041822/fileData.do | Chungju City, Chungcheongbuk-do, via data.go.kr | 871 cabinet rows; cabinet ID/name, location, connected pole count, managing agency, coordinates, and reference date. The page ties the data to maintenance planning, budget, complaints, and fault response. | Supports a cabinet-first operational data contract and cross-region schema comparison. | Do not treat the portal description as proof of actual work volume or local cost. |

### Additional authoritative public sources

| URL | Institution | Key evidence | Applicability | Anti-pattern |
|---|---|---|---|---|
| https://www.suyeong.go.kr/index.suyeong?menuCd=DOM_000000119001001000 | Suyeong-gu Office | 2026 base-budget portal with general and departmental budget documents. | Entry point for locating the Suyeong-specific line item and its budget period. | A budget landing page is not a contract scope, asset denominator, or dispatch count. |
| https://www.busan.go.kr/bhtelinfo02/?curPage=2254 | Busan Metropolitan City organization/contact directory, Suyeong-gu entry | Suyeong-gu Safety Management Office lists street-light unit-price maintenance and material management responsibilities. | Direct operational ownership evidence for the target municipality. | A staff-duty listing does not prove staffing time, contractor rates, or event volume. |
| https://www.gn.go.kr/www/selectEmployeeList.do?key=735&pageIndex=2&searchDeptCode=42010160000&searchKrwd= | Gangneung City | The energy department listing includes unit-price maintenance, remote-control-system maintenance, and street-light civil-complaint handling. | Independent official evidence that maintenance, remote control, and complaints are connected workflow concerns. | This is a different municipality; use as workflow precedent only, never as a Suyeong cost proxy. |
| https://www.g2b.go.kr/pn/pnp/pnpe/UntyAtchFile/downloadFile.do?bidPbancNo=R26BK01450767&bidPbancOrd=000&fileSeq=6&fileType=&prcmBsneSeCd=07 | Korea ON-line E-Procurement System (G2B), bid by Gwangju Seo-gu | 2026 street-light underground-line maintenance unit-cost estimate. The schedule includes cabinet labels, leakage-circuit exploration by cabinet, cabinet installation/removal, poles, lamps, and cable work. | Procurement vocabulary and scope decomposition; useful for asking Suyeong for equivalent BOQ/contract fields. | It has no LightGuard event/dispatch denominator and is not a Suyeong contract. Do not derive per-dispatch cost. |
| https://www.jeonju.go.kr/planweb/board/view.9is?boardUid=ff8080818990c349018b1dbaa78e4b41&contentUid=ff8080818990c349018b041a87373953&dataUid=8eba577186a04f6abab704d3cdee0d17&page=794&tmpField14= | Jeonju City | Official remote-control-system announcement: two-way control for 725 cabinets, with a reported total project cost of KRW 1.34 billion for that project. | Source-local evidence that a remote-control project can be stated with both total scope and cabinet denominator. | It is a 2014 Jeonju deployment, not maintenance dispatch cost and not a Suyeong benchmark. No cross-city unit-cost transfer. |

## Risks / Anti-patterns

- A cabinet inventory proves an operational reference key, not the frequency or cost of field work.
- A unit-price maintenance schedule is not a per-dispatch tariff unless the contract explicitly defines dispatches as the denominator.
- A remote-control deployment total is a capital/project scope figure, not a recurring maintenance saving.
- Do not merge Suyeong, Gangneung, Chungju, Seongnam, Yeonsu-gu, Gwangju Seo-gu, and Jeonju into a synthetic average.
- Do not call a detector candidate a confirmed failure; the v0.5 prompt explicitly treats canonical events as known candidates, not truth labels.
- Do not present a staff directory or budget landing page as proof of actual AMI availability, dispatch count, or contractor performance.
- Keep the anonymized competition AMI separate from Busan/Suyeong geographic context.

## Concrete execution rules adopted

1. Use the cabinet as the operational join key: cabinet ID, location, connected lamp/pole count, rated-load fields, control/branch metadata, signal provenance, and maintenance status.
2. Label each claim with its institution, exact URL, access date, municipality, date/version, and denominator.
3. Use LEVEL A only when the same official project or contract supplies both the numerator and a matching denominator.
4. Use LEVEL B for official context that informs workflow or procurement questions but cannot support a direct cost calculation.
5. Use LEVEL C for advertisements, third-party mirrors, ambiguous scope, missing denominator, or cross-municipality extrapolation; exclude it from claims.
6. Ask neutral interview questions before requesting internal identifiers, dispatch counts, or maintenance outcomes. No outreach is performed by this agent.
