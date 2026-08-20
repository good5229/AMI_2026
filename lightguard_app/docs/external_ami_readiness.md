# External AMI Readiness

## Scope

This note records whether public evidence can support actual cabinet-linked AMI
validation outside Busan. It does not treat residential, photovoltaic, training,
or unrelated utility AMI datasets as municipal street-light cabinet data.

## Gangneung

- Status: `REQUEST_REQUIRED`
- Public asset evidence: the official public-data portal provides a Gangneung
  distribution-cabinet dataset with controller and operating metadata.
- Missing evidence: no public interval current/power series linked to those
  cabinet identifiers was found.
- Required acquisition: request cabinet-to-meter/controller mapping, timestamped
  phase current or active-power data, quality flags, maintenance labels, and the
  governing access/retention terms from Gangneung's lighting-facility operator.
- Official starting point:
  https://www.data.go.kr/data/15117418/fileData.do

## Chungju

- Status: `REQUEST_REQUIRED`
- Public asset evidence: the official cabinet file exposes identifiers, names,
  coordinates, management fields, and lamp-pole counts.
- Missing evidence: no public AMI/meter identifier or interval electric series is
  linked to the 871 cabinet rows; per-cabinet rated load is also unavailable.
- Required acquisition: request circuit ledger, completion drawings, material
  approval records, cabinet-to-meter mapping, and interval phase/current data from
  Chungju and the relevant meter/operator organization.
- Official starting point:
  https://www.data.go.kr/data/15041822/fileData.do

## Search boundary and decision

Public-data searches also return residential photovoltaic AMI and unrelated AMI
education or technology records. They cannot validate LightGuard's municipal
cabinet detector because neither asset identity nor operating policy matches.

Current classification:

| Region | Public cabinet-linked interval AMI | Decision |
|---|---|---|
| Gangneung | Not found | `REQUEST_REQUIRED` |
| Chungju | Not found | `REQUEST_REQUIRED` |

Until an authorized mapping and interval series are supplied, all v0.8 outcomes
remain controlled scenario evidence and the product must not claim actual regional
AMI accuracy, outage detection rate, or field generalization.
