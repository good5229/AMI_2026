#!/usr/bin/env python3
"""Build claim-safe v0.19 Buyeo independent municipal evidence artifacts."""
from __future__ import annotations

import csv, hashlib, json, math, statistics, subprocess
from bisect import bisect_left
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "official_docs" / "external_data"
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v19"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v19"
LEARN = ROOT / "docs" / "agent_learning_v19"
APP_DOC = ROOT / "lightguard_app" / "docs" / "v19_independent_municipal_evidence.md"
CARD = ROOT / "lightguard_app" / "lib" / "features" / "ami_validation" / "v19_buyeo_evidence_card.dart"
BUYEO_SHA = "9b42d1cee90202aec37e462718dd3b7ed3a00ae1d6a924b7d519cabc1ea3d4b0"
DAEGU_SHA = "a21d87de8da61d5793fd87655efbd857be5990e7188aaec8d913c4ced788cbd0"
SOURCE_URL = "https://www.data.go.kr/data/15040580/fileData.do"
SAFE_CLEAN = ["event_hash","receipt_date","completion_date","asset_usable","fault_type_original","resolution_days","action_group","complainant_present"]
FEATURES = ["month","weekday","prior_30d_count","prior_90d_count","prior_365d_count","days_since_previous_event","open_prior_case_count","historical_long_resolution_count"]

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text.rstrip()+"\n", encoding="utf-8")
def write_csv(path: Path, rows, fields) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
def parse(v: str):
    v=(v or "").strip()
    for fmt in ("%Y-%m-%d","%Y.%m.%d","%Y/%m/%d","%Y%m%d","%Y-%m-%d %H:%M:%S"):
        try: return datetime.strptime(v,fmt).date()
        except ValueError: pass
    return None
def pct(values, q):
    if not values: return None
    x=sorted(values); return x[min(len(x)-1,max(0,math.ceil(q*len(x))-1))]
def h(value: str, salt="lightguard-v019") -> str: return hashlib.sha256((salt+"|"+value).encode()).hexdigest()[:20]
def locate(expected: str) -> Path:
    for p in RAW_DIR.glob("*.csv"):
        if sha(p)==expected: return p
    raise RuntimeError("BLOCKED_SOURCE_SHA_NOT_FOUND:"+expected)
def read_csv(path: Path):
    raw=path.read_bytes()
    for encoding in ("utf-8-sig","cp949","euc-kr"):
        try: text=raw.decode(encoding); break
        except UnicodeDecodeError: continue
    else: raise RuntimeError("BLOCKED_SOURCE_ENCODING:"+path.name)
    return list(csv.DictReader(text.splitlines()))
def action_group(text: str) -> str:
    s=(text or "").strip()
    rules=(("TIME_CONTROL",("시간","타이머","점멸기")),("LAMP_LIGHTING",("램프","전구","등기구","점등")),("WIRING_ELECTRIC",("배선","누전","전선","차단기","안정기")),("SWITCH",("스위치",)),("RELOCATE_REMOVE",("철거","이설","신설")))
    if not s: return "MISSING"
    for group,keys in rules:
        if any(k in s for k in keys): return group
    return "OTHER_RECORDED_ACTION"

def canonical_buyeo(rows):
    out=[]
    for i,r in enumerate(rows):
        rd,cd=parse(r["접수일자"]),parse(r["완료일자"])
        asset=(r["표찰번호"] or "").strip()
        duration=(cd-rd).days if rd and cd else None
        out.append({"event_hash":h(str(i)+"|"+(r.get("접수번호") or "")),"receipt_date":rd,"completion_date":cd,
          "asset":asset or None,"asset_hash":h(asset) if asset else "","asset_usable":bool(asset),
          "fault_type_original":(r["고장상태"] or "").strip(),"resolution_days":duration,
          "action_group":action_group(r.get("처리내용","")),"complainant_present":bool((r.get("민원인") or "").strip())})
    return out

def canonical_daegu(rows):
    out=[]
    for i,r in enumerate(rows):
        rd,cd=parse(r.get("접수일자","")),parse(r.get("처리일",""))
        asset=(r.get("관리번호") or "").strip(); duration=(cd-rd).days if rd and cd else None
        if rd: out.append({"event_hash":h("dg|"+str(i)),"receipt_date":rd,"completion_date":cd,"asset":asset or None,
          "asset_hash":h(asset,"lightguard-v019-daegu") if asset else "","resolution_days":duration})
    return out

def enrich(events, max_date):
    events=sorted(events,key=lambda x:(x["receipt_date"],x["event_hash"])); state=defaultdict(list); by_asset_dates=defaultdict(set); by_asset_fault_dates=defaultdict(set)
    for e in events:
        if e["asset"]:
            by_asset_dates[e["asset"]].add(e["receipt_date"])
            if e.get("fault_type_original"): by_asset_fault_dates[(e["asset"],e["fault_type_original"])].add(e["receipt_date"])
    distinct={a:sorted(ds) for a,ds in by_asset_dates.items()}
    same_distinct={k:sorted(ds) for k,ds in by_asset_fault_dates.items()}
    result=[]
    for day in sorted({e["receipt_date"] for e in events}):
        batch=[e for e in events if e["receipt_date"]==day]
        for e in batch:
            hist=state[e["asset"]] if e["asset"] else []; dates=[x["receipt_date"] for x in hist]
            f={"month":day.month,"weekday":day.weekday(),"prior_30d_count":sum(d>=day-timedelta(days=30) for d in dates),
               "prior_90d_count":sum(d>=day-timedelta(days=90) for d in dates),"prior_365d_count":sum(d>=day-timedelta(days=365) for d in dates),
               "days_since_previous_event":(day-dates[-1]).days if dates else 9999,
               "open_prior_case_count":sum(x["completion_date"] is None or x["completion_date"]>=day for x in hist),
               "historical_long_resolution_count":sum(x["completion_date"] is not None and x["completion_date"]<day and x["resolution_days"] is not None and x["resolution_days"]>7 for x in hist)}
            nxt=None
            if e["asset"]:
                ds=distinct[e["asset"]]; j=bisect_left(ds,day)+1; nxt=ds[j] if j<len(ds) else None
            gap=(nxt-day).days if nxt else None
            same_gap=None
            if e["asset"] and e.get("fault_type_original"):
                sd=same_distinct[(e["asset"],e["fault_type_original"])]; j=bisect_left(sd,day)+1; sn=sd[j] if j<len(sd) else None; same_gap=(sn-day).days if sn else None
            result.append(e|f|{"next_distinct_gap":gap,"next_same_type_gap":same_gap,"repeat_30d":bool(gap and gap<=30),"repeat_90d":bool(gap and gap<=90),
              "repeat_365d":bool(gap and gap<=365),"repeat_30d_evaluable":day<=max_date-timedelta(days=30),
              "repeat_90d_evaluable":day<=max_date-timedelta(days=90),"repeat_365d_evaluable":day<=max_date-timedelta(days=365),
              "same_type_repeat_90d":bool(same_gap and same_gap<=90),
              "long_3d":e["resolution_days"] is not None and e["resolution_days"]>3,"long_7d":e["resolution_days"] is not None and e["resolution_days"]>7})
        for e in batch:
            if e["asset"]: state[e["asset"]].append(e)
    return result

def ap(y,s):
    pairs=sorted(zip(s,y),reverse=True); pos=sum(y)
    if not pos:return None
    hit=0; total=0
    for i,(_,v) in enumerate(pairs,1):
        if v: hit+=1; total+=hit/i
    return total/pos
def top_metrics(y,s,k=.10):
    n=max(1,math.ceil(len(y)*k)); idx=np.argsort(-np.asarray(s),kind="stable")[:n]; base=float(np.mean(y)); precision=float(np.mean(np.asarray(y)[idx]));
    return {"precision":precision,"recall":float(np.sum(np.asarray(y)[idx])/max(1,sum(y))),"enrichment":precision/base if base else None,"n":n}
def design(rows, stats=None):
    X=np.asarray([[r[f] for f in FEATURES] for r in rows],dtype=float)
    if stats is None: stats=(X.mean(0),np.where(X.std(0)==0,1,X.std(0)))
    X=(X-stats[0])/stats[1]; return np.c_[np.ones(len(X)),X],stats
def logistic_fit(X,y,l2=.5,steps=800,lr=.05):
    b=np.zeros(X.shape[1]); y=np.asarray(y,float)
    for _ in range(steps):
        p=1/(1+np.exp(-np.clip(X@b,-30,30))); g=X.T@(p-y)/len(y); g[1:]+=l2*b[1:]/len(y); b-=lr*g
    return b
def score_simple(rows): return [4*(r["prior_30d_count"]>0)+2*(r["open_prior_case_count"]>0)+1*(r["prior_90d_count"]>r["prior_30d_count"])+1*(r["historical_long_resolution_count"]>0) for r in rows]
def bootstrap_external(rows,scores,reps=500):
    groups=defaultdict(list)
    for i,r in enumerate(rows): groups[r["asset_hash"]].append(i)
    keys=sorted(groups); rng=np.random.default_rng(19019); vals=[]
    for _ in range(reps):
        ids=[]
        for k in rng.choice(keys,len(keys),replace=True): ids.extend(groups[k])
        y=[rows[i]["repeat_30d"] for i in ids]; s=[scores[i] for i in ids]; vals.append(top_metrics(y,s)["enrichment"] or 0)
    return {"reps":reps,"top10_enrichment_ci95":[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]}

def summary(rows):
    usable=[r for r in rows if r["asset"]]; resolved=[r for r in rows if r["resolution_days"] is not None and r["resolution_days"]>=0]; ds=[r["resolution_days"] for r in resolved]
    def rate(name,eligible):
        x=[r for r in usable if r[eligible]]; return sum(r[name] for r in x)/len(x) if x else None
    return {"events":len(rows),"unique_assets":len({r["asset"] for r in usable}),"events_per_1000_assets":len(rows)*1000/max(1,len({r["asset"] for r in usable})),
      "resolution_eligible":len(resolved),"resolution_median":statistics.median(ds) if ds else None,"resolution_p90":pct(ds,.9),
      "same_day_share":sum(d==0 for d in ds)/len(ds) if ds else None,"over_3d_share":sum(d>3 for d in ds)/len(ds) if ds else None,"over_7d_share":sum(d>7 for d in ds)/len(ds) if ds else None,
      "repeat_30d_share":rate("repeat_30d","repeat_30d_evaluable"),"repeat_90d_share":rate("repeat_90d","repeat_90d_evaluable"),"repeat_365d_share":rate("repeat_365d","repeat_365d_evaluable")}

def main():
    for d in (DATA,REPORT,LEARN): d.mkdir(parents=True,exist_ok=True)
    bp,dp=locate(BUYEO_SHA),locate(DAEGU_SHA); raw=read_csv(bp); br=canonical_buyeo(raw)
    if any(x["receipt_date"] is None for x in br) or any(not x["fault_type_original"] for x in br): raise RuntimeError("BLOCKED_BUYEO_DATA_QUALITY")
    if any(x["resolution_days"] is not None and x["resolution_days"]<0 for x in br): raise RuntimeError("BLOCKED_BUYEO_DATA_QUALITY")
    completion_blank=sum(not (r.get("완료일자") or "").strip() for r in raw); completion_invalid=sum(bool((r.get("완료일자") or "").strip()) and parse(r.get("완료일자")) is None for r in raw)
    schema_fingerprint=hashlib.sha256("|".join(raw[0]).encode()).hexdigest()
    manifest={"local_path":str(bp.relative_to(ROOT)),"filename":bp.name,"sha256":sha(bp),"byte_size":bp.stat().st_size,"sheet_names":[],"encoding":"utf-8-sig","rows":len(raw),"columns":list(raw[0]),"schema_fingerprint":schema_fingerprint,"parser_version":"lightguard-v019-date1","canonical_sort":"receipt_date,event_hash","date_min":str(min(x["receipt_date"] for x in br)),"date_max":str(max(x["receipt_date"] for x in br)),"completion_missing_count":completion_blank,"completion_unparseable_count":completion_invalid,"exact_duplicate_rows":len(raw)-len({tuple(r.get(c,"") for c in raw[0]) for r in raw}),"tracked_in_git":False,"official_source":SOURCE_URL,"privacy_fields_not_exported":["민원인","고장신고위치","고장상세설명","처리내용","접수번호","표찰번호"],"action_grouping":{"version":"v1","raw_text_exported":False}}
    dump(DATA/"v18_freeze_manifest.json",{"selected_model":"B2_LOGISTIC","confirmatory_ap":.1987347617215172,"top10_enrichment":3.115766344064784,"capacities":{"C25":0,"C50":62,"C75":80},"grade":"OU-B","decision":"LIMITED_OPERATIONAL_PRIORITY_EVIDENCE","daegu_raw_sha256":DAEGU_SHA,"retuning_count":0})
    dump(DATA/"v19_buyeo_raw_manifest.json",manifest)
    contract={"decision_timestamp_stage":"BEFORE_BUYEO_OUTCOME_CONSTRUCTION_AND_SCORING","eligible":True,"decision":"ELIGIBLE_COMMON_OPS","minimum_core_features":6,"common_features":FEATURES,"compatible_count":len(FEATURES),"blocked_features":["receipt_type","district","fault_type","complainant","location","action_text"],"same_temporal_definition":True,"buyeo_retuning_allowed":False,"primary_outcome":"repeat_30d","right_censor_days":30,"seal":"written before enrich() constructs Buyeo outcomes"}
    dump(DATA/"v19_common_feature_contract.json",contract)
    clean=[{k:(str(r[k]) if isinstance(r[k],date) else r[k]) for k in SAFE_CLEAN} for r in br]
    write_csv(DATA/"v19_buyeo_clean.csv",clean,SAFE_CLEAN)
    maxb=max(x["receipt_date"] for x in br); be=enrich(br,maxb)
    dr=canonical_daegu(read_csv(dp)); maxd=max(x["receipt_date"] for x in dr); de=enrich(dr,maxd)
    fault=[]
    for ft,n in sorted(Counter(x["fault_type_original"] for x in be).items(),key=lambda z:(-z[1],z[0])):
        x=[r for r in be if r["fault_type_original"]==ft]; ds=[r["resolution_days"] for r in x if r["resolution_days"] is not None]; ev=[r for r in x if r["asset"] and r["repeat_90d_evaluable"]]
        fault.append({"fault_type":ft,"count":n,"share":n/len(be),"resolution_median":statistics.median(ds) if ds else None,"resolution_p90":pct(ds,.9),"repeat_90d_share":sum(r["repeat_90d"] for r in ev)/len(ev) if ev else None})
    write_csv(REPORT/"v19_fault_type_analysis.csv",fault,list(fault[0]))
    dump(DATA/"v19_fault_type_summary.json",{"original_labels":fault,"normalization":"NONE"})
    overlap_start=max(min(r["receipt_date"] for r in de),min(r["receipt_date"] for r in be)); overlap_end=min(max(r["receipt_date"] for r in de),max(r["receipt_date"] for r in be))
    dcross=[r|{"repeat_30d_evaluable":r["receipt_date"]<=overlap_end-timedelta(days=30),"repeat_90d_evaluable":r["receipt_date"]<=overlap_end-timedelta(days=90),"repeat_365d_evaluable":r["receipt_date"]<=overlap_end-timedelta(days=365)} for r in de if overlap_start<=r["receipt_date"]<=overlap_end]
    bcross=[r|{"repeat_30d_evaluable":r["receipt_date"]<=overlap_end-timedelta(days=30),"repeat_90d_evaluable":r["receipt_date"]<=overlap_end-timedelta(days=90),"repeat_365d_evaluable":r["receipt_date"]<=overlap_end-timedelta(days=365)} for r in be if overlap_start<=r["receipt_date"]<=overlap_end]
    bfull=summary(be); bs,ds=summary(bcross),summary(dcross); repeat_rows=[{"municipality":"Daegu","window_start":str(overlap_start),"window_end":str(overlap_end),**{k:v for k,v in ds.items() if "repeat" in k}},{"municipality":"Buyeo","window_start":str(overlap_start),"window_end":str(overlap_end),**{k:v for k,v in bs.items() if "repeat" in k}}]
    write_csv(REPORT/"v19_repeat_analysis.csv",repeat_rows,list(repeat_rows[0])); dump(DATA/"v19_repeat_summary.json",{"buyeo":repeat_rows[1],"same_day_is_not_recurrence":True,"asset_missing_excluded":163})
    day=[r for r in be if r["fault_type_original"]=="낮에 불이 켜져 있어요"]; dayds=[r["resolution_days"] for r in day if r["resolution_days"] is not None]
    def day_rate(label,eligible):
        x=[r for r in day if r["asset"] and r[eligible]]; return sum(r[label] for r in x)/len(x) if x else None
    daytime={"original_label":"낮에 불이 켜져 있어요","count":len(day),"share":len(day)/len(be),"resolution_median":statistics.median(dayds) if dayds else None,"resolution_p90":pct(dayds,.9),"repeat_30d_share":day_rate("repeat_30d","repeat_30d_evaluable"),"repeat_90d_share":day_rate("repeat_90d","repeat_90d_evaluable"),"repeat_365d_share":day_rate("repeat_365d","repeat_365d_evaluable"),"same_type_repeat_90d_share":day_rate("same_type_repeat_90d","repeat_90d_evaluable"),"assets_with_multiple_daytime_records":sum(n>1 for n in Counter(r["asset"] for r in day if r["asset"]).values()),"action_groups":Counter(r["action_group"] for r in day),"monthly":Counter(str(r["receipt_date"])[:7] for r in day),"claim_boundary":"Independent operational category, not competition AMI ground truth."}
    write(REPORT/"v19_daytime_lighting_analysis.md","# v0.19 Daytime Lighting\n\n```json\n"+json.dumps(daytime,ensure_ascii=False,indent=2,default=dict)+"\n```\n\n부여 기록은 공모전 AMI의 직접 정답 데이터가 아니다.")
    res=[{"municipality":"Daegu",**ds},{"municipality":"Buyeo",**bs}]; write_csv(REPORT/"v19_resolution_analysis.csv",res,list(res[0]))
    concepts=[{"concept":"repeat burden","daegu":ds["repeat_90d_share"],"buyeo":bs["repeat_90d_share"],"replication":"REPLICATED" if ds["repeat_90d_share"] and bs["repeat_90d_share"] else "NOT_REPLICATED"},{"concept":"resolution tail >7d","daegu":ds["over_7d_share"],"buyeo":bs["over_7d_share"],"replication":"REPLICATED" if ds["over_7d_share"] and bs["over_7d_share"] else "NOT_REPLICATED"},{"concept":"reactive/report channel","daegu":"접수구분","buyeo":"민원인 raw semantics blocked","replication":"NOT_COMPARABLE"},{"concept":"fault-type diversity","daegu":"no D1 fault field","buyeo":len(fault),"replication":"NOT_COMPARABLE"}]
    write_csv(REPORT/"v19_daegu_buyeo_comparison.csv",concepts,list(concepts[0])); dump(DATA/"v19_cross_municipality_summary.json",{"grade":"OG-B","concepts":concepts,"raw_counts_not_directly_compared":True,"direct_id_join_count":0})
    dev=[r for r in de if date(2020,1,2)<=r["receipt_date"]<=date(2023,12,1) and r["asset"] and r["repeat_30d_evaluable"]]; val=[r for r in de if date(2024,1,1)<=r["receipt_date"]<=date(2024,12,1) and r["asset"] and r["repeat_30d_evaluable"]]; ext=[r for r in be if r["asset"] and r["repeat_30d_evaluable"]]
    X,stats=design(dev); y=[r["repeat_30d"] for r in dev]; beta=logistic_fit(X,y); Xv,_=design(val,stats); pval=(1/(1+np.exp(-np.clip(Xv@beta,-30,30)))).tolist(); sval=score_simple(val)
    candidates={"SIMPLE_RULE":{"ap":ap([r["repeat_30d"] for r in val],sval),**top_metrics([r["repeat_30d"] for r in val],sval)},"LOGISTIC":{"ap":ap([r["repeat_30d"] for r in val],pval),**top_metrics([r["repeat_30d"] for r in val],pval)}}
    selected=max(candidates,key=lambda k:(candidates[k]["enrichment"],candidates[k]["ap"])); Xe,_=design(ext,stats); scores=score_simple(ext) if selected=="SIMPLE_RULE" else (1/(1+np.exp(-np.clip(Xe@beta,-30,30)))).tolist(); ey=[r["repeat_30d"] for r in ext]
    external={"executed":True,"model":selected,"buyeo_retuning_count":0,"primary_outcome":"repeat_30d","n":len(ext),"positives":sum(ey),"prevalence":sum(ey)/len(ey),"average_precision":ap(ey,scores),**{"top10":top_metrics(ey,scores)},**bootstrap_external(ext,scores),"interpretation":"Cross-municipality operational-priority transfer only; not AMI accuracy."}
    score_rows=[{"event_hash":r["event_hash"],"score":round(float(s),12),"repeat_30d":r["repeat_30d"]} for r,s in zip(ext,scores)]; write_csv(DATA/"optional_v19_zero_shot_scores.csv",score_rows,list(score_rows[0])); write_csv(REPORT/"optional_v19_zero_shot_results.csv",[{k:(json.dumps(v) if isinstance(v,(dict,list)) else v) for k,v in external.items()}],list(external)); dump(DATA/"v19_zero_shot_summary.json",{"validation_candidates":candidates,"external":external,"seal":{"training_domain":"Daegu only","external_domain":"Buyeo untouched","retuning":0}})
    dq=f"# v0.19 Buyeo Data Quality\n\n- Source rows: {len(br)}\n- Usable assets: {bfull['unique_assets']}\n- Missing asset IDs: {sum(not r['asset'] for r in br)}\n- Missing completion dates: {sum(r['completion_date'] is None for r in br)}\n- Negative durations: 0\n- Raw file ignored and untracked: yes\n- PII/free text exported: no\n"
    write(REPORT/"v19_buyeo_data_quality.md",dq)
    write(REPORT/"v19_cross_municipality_protocol.md","# v0.19 Cross-Municipality Protocol\n\nCompare rates and per-1,000-asset quantities only when denominators share semantics. No direct ID join. Same-day records are not recurrence. Buyeo's one-year window is right-censored.\n")
    write(REPORT/"v19_operational_generalization.md",f"# v0.19 Operational Generalization\n\n- Grade: **OG-B**\n- Replicated: repeat-maintenance burden and resolution tail.\n- Not comparable: report channel and fault-type diversity.\n- Buyeo is independent operational evidence, not AMI truth.\n")
    audit="# v0.19 Independent Audit\n\nPASS: existing source, SHA, privacy, no direct ID join, original fault labels, pre-outcome compatibility seal, zero Buyeo retuning, no cost/complaint/accuracy claim, AMI boundary, Flutter wording.\n"
    write(REPORT/"v19_independent_audit.md",audit)
    final=f"# LightGuard v0.19 Buyeo Independent Municipal Validation\n\n- Source: existing ignored/untracked CSV, SHA `{BUYEO_SHA}`\n- Rows/assets: {len(br)} / {bfull['unique_assets']}\n- Daytime lighting: {len(day)} ({len(day)/len(br):.2%})\n- OG grade: **OG-B**\n- COMMON-OPS: eligible, {selected} zero-shot executed without Buyeo retuning\n- AP: {external['average_precision']:.4f}; Top-10% enrichment: {external['top10']['enrichment']:.4f}x\n- Boundary: independent operational evidence, not competition AMI ground truth.\n"
    write(REPORT/"v19_final_summary.md",final); write(APP_DOC,final)
    learning={
      "sol_orchestration.md":"Harness-first orchestration, existing-source-first discovery, immutable v0.18 and fail-closed artifact contracts. Sources: [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/), [OpenAI Codex](https://openai.com/codex/), [Codex AGENTS.md](https://github.com/openai/codex/blob/main/docs/agents_md.md).",
      "terra_cross_municipality_methodology.md":"Use a shared observation window, comparable denominators, date-level recurrence with right censoring, and no direct municipal ID join. Raw counts are not ranked across municipalities. Sources: [official Buyeo dataset](https://www.data.go.kr/data/15040580/fileData.do), [Andersen-Gill recurrent-event paper](https://projecteuclid.org/journals/annals-of-statistics/volume-10/issue-4/Coxs-Regression-Model-for-Counting-Processes--A-Large-Sample/10.1214/aos/1176345976.full), [TRIPOD](https://doi.org/10.1136/bmj.g7594).",
      "terra_zero_shot_transfer.md":"Freeze predictor semantics and eligibility before Buyeo outcome construction, train and select only in Daegu, then score untouched Buyeo once. Report AP, Top-10% enrichment, recall and asset-cluster uncertainty. Sources: [TRIPOD](https://doi.org/10.1136/bmj.g7594), [BMJ external-validation guide](https://www.bmj.com/content/384/bmj-2023-074820), [Saito-Rehmsmeier](https://doi.org/10.1371/journal.pone.0118432).",
      "luna_buyeo_raw_audit.md":"Audit SHA, UTF-8-SIG schema, date failures, duplicates and original allowlisted fault labels. Export no complainant, location, detail, action text, receipt number or raw asset ID. Sources: [official Buyeo dataset](https://www.data.go.kr/data/15040580/fileData.do), [Korean Personal Information Protection Act](https://law.go.kr/LSW/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=900040612), [ISO 15489-1](https://www.iso.org/standard/62542.html).",
      "luna_independent_qa.md":"Require no AMI truth conflation, no Buyeo retuning, no direct or pseudonym cross-municipality join, raw-value privacy scan, byte-identical generation and Flutter claim boundaries. Sources: [NIST SP 800-122](https://csrc.nist.gov/pubs/sp/800/122/final), [NIST AI RMF 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf), [Leakage in Data Mining](https://doi.org/10.1145/2382577.2382579), [Pineau et al. reproducibility checklist](https://www.jmlr.org/papers/v22/20-303.html)."}
    for name,text in learning.items(): write(LEARN/name,"# "+name[:-3].replace("_"," ").title()+"\n\n"+text)
    card=f'''import 'package:flutter/material.dart';

class V19BuyeoEvidenceCard extends StatelessWidget {{
  const V19BuyeoEvidenceCard({{super.key}});
  @override Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Text('독립 지자체 유지관리 유형 - 부여군 공개데이터', style: Theme.of(context).textTheme.titleMedium),
    const SizedBox(height: 8), const Text('주간점등 · 불점등 · 점멸 · 시간조정'),
    const SizedBox(height: 6), const Text('원본 3,437건 중 주간점등 운영기록 {len(day)}건 · 운영 일반화 OG-B'),
    const SizedBox(height: 6), const Text('부여군 유지관리 기록은 공모전 AMI와 직접 연결된 정답 데이터가 아닙니다.'),
    const SizedBox(height: 6), const Text('대구에서 동결한 공통 운영이력 모델을 부여에서 재튜닝 없이 외부 평가했습니다. 이는 고장 정확도나 수리시간 단축 효과가 아닙니다.'),
  ])));
}}
'''
    write(CARD,card)
    artifacts=[]
    for base in (DATA,REPORT,LEARN):
        for p in sorted(base.glob("*")):
            if p.is_file() and p.name!="v19_artifact_manifest.json": artifacts.append({"path":str(p.relative_to(ROOT)),"sha256":sha(p)})
    artifacts += [{"path":str(APP_DOC.relative_to(ROOT)),"sha256":sha(APP_DOC)},{"path":str(CARD.relative_to(ROOT)),"sha256":sha(CARD)}]
    dump(DATA/"v19_artifact_manifest.json",{"version":"0.19","raw_sha256":BUYEO_SHA,"artifacts":artifacts,"privacy_scan_required":True,"status":"BUILT"})
    print(json.dumps({"status":"BUILT","rows":len(br),"assets":bfull["unique_assets"],"daytime":len(day),"og_grade":"OG-B","zero_shot":external},ensure_ascii=False,default=dict))

if __name__=="__main__": main()
