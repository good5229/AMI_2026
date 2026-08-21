# v0.5 Operational Evidence Summary

Research date: 2026-08-20 (Asia/Seoul). Research role: Subagent C, Public Operations & Economic Evidence Researcher. Runtime assignment: `gpt-5.6-luna`; independent model metadata is not exposed by the repository.

## Finding

Public evidence supports a cabinet-first maintenance data model. Official inventories consistently expose some combination of cabinet identifier/name, location, connected lamp or pole count, rated lamp capacity, branch/circuit, managing agency, and reference date. Official local-government pages also show that street-light maintenance, complaints, materials, and remote-control maintenance can be separate but related operational responsibilities.

The evidence does not establish Suyeong's actual AMI availability, work-order process, remote-control coverage, dispatch count, or failure rate. The current LightGuard data contract must therefore distinguish official public asset context, scenario injection, and anonymized competition AMI replay.

## Required public-data URLs

| Institution / dataset | Exact URL | Operational use | Economic status |
|---|---|---|---|
| Gyeonggi-do Seongnam City cabinet inventory | https://www.data.go.kr/data/15032441/fileData.do | Cabinet/pole/lamp schema and cabinet-as-maintenance-reference precedent | Not an economic source |
| Incheon Yeonsu-gu cabinet information | https://www.data.go.kr/data/15059623/fileData.do | Stable management number, location, agency/contact, installation-year and reference-date precedent | Not an economic source |
| Gangneung City street-light inventory | https://www.data.go.kr/data/15117413/fileData.do | Cabinet-to-lamp mapping, branch, lamp type, rated capacity, partial-lighting fields | Not an economic source |
| Chungju City cabinet information | https://www.data.go.kr/data/15041822/fileData.do | Cabinet ID, location, connected pole count, managing agency and maintenance-planning precedent | Not an economic source |

## Additional authoritative sources

| Source | Exact URL | Evidence | Level |
|---|---|---|---|
| Suyeong-gu 2026 budget portal | https://www.suyeong.go.kr/index.suyeong?menuCd=DOM_000000119001001000 | Official budget-document entry point; no matching asset or dispatch denominator on the landing page | B |
| Busan organization directory, Suyeong entry | https://www.busan.go.kr/bhtelinfo02/?curPage=2254 | Suyeong municipal street-light unit-price maintenance and materials responsibility | B |
| Gangneung energy department duties | https://www.gn.go.kr/www/selectEmployeeList.do?key=735&pageIndex=2&searchDeptCode=42010160000&searchKrwd= | Official workflow precedent linking maintenance, remote-control-system maintenance, and complaints | B |
| G2B 2026 Gwangju Seo-gu maintenance cost schedule | https://www.g2b.go.kr/pn/pnp/pnpe/UntyAtchFile/downloadFile.do?bidPbancNo=R26BK01450767&bidPbancOrd=000&fileSeq=6&fileType=&prcmBsneSeCd=07 | Official BOQ/unit-cost categories including cabinet and leakage-circuit work; no LightGuard dispatch denominator | B |
| Jeonju remote-control announcement | https://www.jeonju.go.kr/planweb/board/view.9is?boardUid=ff8080818990c349018b1dbaa78e4b41&contentUid=ff8080818990c349018b041a87373953&dataUid=8eba577186a04f6abab704d3cdee0d17&page=794&tmpField14= | Historical official project with total project cost and 725-cabinet scope; source-local project evidence only | A |

## Economic boundary

LEVEL A is allowed only for a same-project, source-local statement with a matching numerator and denominator. The Jeonju material meets that narrow condition for its own remote-control deployment scope, not for Suyeong and not for per-dispatch maintenance.

LEVEL B is background evidence for workflow, budget discovery, and procurement vocabulary. It must not be converted into currency claims in the app.

LEVEL C includes private/vendor pricing, third-party tender mirrors, missing-denominator totals, cross-municipality averages, and any invented dispatch denominator. It is excluded.

**Cost conversion for LightGuard/Suyeong: not allowed.** A future conversion requires an official Suyeong contract or expenditure record with matching scope and period plus an explicit work-order/dispatch denominator. No such denominator was found in the reviewed public pages, so no blocker URL is fabricated. The remaining gap is recorded for interview/data request.

## Product and interview implications

- Show cabinet-level asset context and inspection priority as a decision-support hypothesis.
- Keep “official public asset data,” “scenario injection,” and “anonymized competition AMI replay” visibly separate.
- Do not show per-alert savings, avoided dispatch cost, or ROI.
- Ask the neutral questions in `lightguard_app/docs/interview_readiness.md` only after user approval for contact.
