#!/usr/bin/env python3
import csv, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"lightguard_v0_1/data/validation/v19"
def load(n): return json.loads((DATA/n).read_text(encoding="utf-8"))
def fail(x): raise RuntimeError(x)
raw=load("v19_buyeo_raw_manifest.json"); freeze=load("v18_freeze_manifest.json"); contract=load("v19_common_feature_contract.json"); result=load("v19_zero_shot_summary.json"); manifest=load("v19_artifact_manifest.json")
if raw["sha256"]!="9b42d1cee90202aec37e462718dd3b7ed3a00ae1d6a924b7d519cabc1ea3d4b0" or raw["rows"]!=3437 or raw["tracked_in_git"]: fail("RAW_CONTRACT")
if freeze["grade"]!="OU-B" or freeze["retuning_count"]!=0: fail("V18_FREEZE")
if contract["decision_timestamp_stage"]!="BEFORE_BUYEO_OUTCOME_CONSTRUCTION_AND_SCORING" or not contract["eligible"] or contract["buyeo_retuning_allowed"]: fail("ZERO_SHOT_GATE")
if result["external"]["buyeo_retuning_count"]!=0: fail("RETUNING")
with (DATA/"v19_buyeo_clean.csv").open(encoding="utf-8") as f: fields=next(csv.reader(f))
for blocked in ("민원인","고장신고위치","고장상세설명","처리내용","표찰번호","관리번호"):
    if blocked in fields: fail("PRIVACY_COLUMN:"+blocked)
for a in manifest["artifacts"]:
    p=ROOT/a["path"]
    if hashlib.sha256(p.read_bytes()).hexdigest()!=a["sha256"]: fail("HASH:"+a["path"])
text="\n".join((ROOT/a["path"]).read_text(encoding="utf-8",errors="ignore") for a in manifest["artifacts"] if (ROOT/a["path"]).suffix in {".md",".json",".csv",".dart"})
for forbidden in ("B-L-35는 실제 주간점등 고장","AMI daytime activation = confirmed","민원 감소율 입증","비용절감이 입증"):
    if forbidden in text: fail("CLAIM:"+forbidden)
tracked=subprocess.run(["git","ls-files",raw["local_path"]],cwd=ROOT,text=True,capture_output=True).stdout.strip()
if tracked: fail("RAW_TRACKED")
source=ROOT/raw["local_path"]
with source.open(encoding="utf-8-sig",newline="") as f: source_rows=list(csv.DictReader(f))
artifact_cells=set()
for a in manifest["artifacts"]:
    p=ROOT/a["path"]
    if p.suffix==".csv":
        with p.open(encoding="utf-8",newline="") as f:
            for row in csv.reader(f): artifact_cells.update(row)
safe_fault_labels={(r.get("고장상태") or "").strip() for r in source_rows}
for field in ("민원인","고장신고위치","고장상세설명"):
    for value in {(r.get(field) or "").strip() for r in source_rows}:
        if field=="고장상세설명" and value in safe_fault_labels: continue
        if value and value in artifact_cells: fail("RAW_PRIVACY_CELL:"+field)
        if len(value)>=6 and value in text: fail("RAW_PRIVACY_TEXT:"+field)
for value in {(r.get("처리내용") or "").strip() for r in source_rows}:
    if len(value)>=8 and value in text: fail("RAW_ACTION_TEXT")
print("v0.19 artifact contract PASS")
