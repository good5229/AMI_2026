#!/usr/bin/env python3
from __future__ import annotations
import csv, json, os, re, glob, hashlib, sqlite3, statistics, math, shutil, zipfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path('/mnt/data')
OUT = ROOT / 'lightguard_v0_1'
DATA = OUT / 'data'
SEED = OUT / 'app_seed'
REPORTS = OUT / 'reports'
SRC = OUT / 'src'
for d in (OUT, DATA, SEED, REPORTS, SRC): d.mkdir(parents=True, exist_ok=True)


def find1(pattern: str) -> Path:
    xs = list(ROOT.glob(pattern))
    if len(xs) != 1:
        raise RuntimeError(f'{pattern}: expected 1, got {len(xs)}: {xs}')
    return xs[0]

SUYEONG = find1('*20260114.csv')
GANG_LIGHT = find1('*20230818.csv')
GANG_CAB = find1('*20230820.csv')
CHUNGJU = find1('*20260630.csv')
SMART = find1('*스마트*csv') if list(ROOT.glob('*스마트*csv')) else [p for p in ROOT.glob('*.csv') if '2026' not in p.name and '2023' not in p.name][0]
AMI_JSON = ROOT / 'ami_streetlights.json'
META_XLSX = find1('1-1_*.xlsx')


def detect_encoding(p: Path) -> str:
    with p.open('rb') as f:
        raw=f.readline()
    for e in ('utf-8-sig','cp949','euc-kr','utf-8'):
        try:
            raw.decode(e); return e
        except UnicodeDecodeError: pass
    return 'cp949'

def read_csv(p: Path):
    enc=detect_encoding(p)
    with p.open(encoding=enc,newline='') as f:
        return list(csv.DictReader(f)), enc

def fnum(x):
    if x is None: return None
    s=str(x).strip().replace(',','')
    if not s: return None
    try: return float(s)
    except ValueError: return None

def inum(x, default=0):
    v=fnum(x)
    return int(v) if v is not None else default

def stable_id(prefix: str, *parts: str) -> str:
    s='|'.join('' if p is None else str(p).strip() for p in parts)
    return f'{prefix}-{hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]}'

def median_or_none(xs):
    xs=[x for x in xs if x is not None]
    return statistics.median(xs) if xs else None

def write_csv(path: Path, rows: list[dict], fields=None):
    if fields is None:
        fields=[]
        seen=set()
        for r in rows:
            for k in r:
                if k not in seen: fields.append(k);seen.add(k)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
        w.writeheader(); w.writerows(rows)

def write_json(path: Path, obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

# ---- AMI metadata from tiny XLSX, read-only XML parsing (no workbook mutation) ----
def extract_xlsx_rows(path: Path):
    import xml.etree.ElementTree as ET
    NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    with zipfile.ZipFile(path) as z:
        ss=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            root=ET.fromstring(z.read('xl/sharedStrings.xml'))
            ss=[''.join((t.text or '') for t in si.iter(NS+'t')) for si in root.findall(NS+'si')]
        root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        records=[]
        headers={}
        for row in root.findall('.//'+NS+'row'):
            rno=int(row.attrib.get('r','0'))
            vals={}
            for c in row.findall(NS+'c'):
                ref=c.attrib.get('r','')
                col=re.match(r'([A-Z]+)',ref).group(1)
                v=c.find(NS+'v'); val=None if v is None else v.text
                if c.attrib.get('t')=='s' and val is not None: val=ss[int(val)]
                vals[col]=val
            if rno==2:
                headers=vals
            elif rno>2 and headers:
                rec={headers.get(col,col): vals.get(col) for col in headers}
                records.append(rec)
        return records

meta_rows=extract_xlsx_rows(META_XLSX)
street_meta=[]
for r in meta_rows:
    if '가로등' in str(r.get('계약종별','')) or '가로등' in str(r.get('사용용도','')):
        street_meta.append({
            'meter_id':r.get('순번(계기번호)'), 'line':r.get('선로명'), 'section_no':r.get('구간번호'),
            'multiplier':fnum(r.get('배수')), 'supply_type':r.get('공급방식'), 'contract_power_kw':fnum(r.get('수전전력')),
            'contract_type':r.get('계약종별'), 'usage':r.get('사용용도'), 'production':r.get('주생산품'), 'industry':r.get('산업분류')
        })
meta_by_meter={r['meter_id']:r for r in street_meta}

# ---- Municipal normalization ----
suy, suy_enc = read_csv(SUYEONG)
gl, gl_enc = read_csv(GANG_LIGHT)
gc, gc_enc = read_csv(GANG_CAB)
ch, ch_enc = read_csv(CHUNGJU)
sm, sm_enc = read_csv(SMART)

municipalities=[]; cabinets=[]; fixtures=[]; controllers=[]

# Suyeong
suy_by_cab=defaultdict(list)
for idx,r in enumerate(suy, start=2):
    source_cab=r.get('소속분전함','').strip()
    cab_uid=stable_id('SY-CAB','suyeong',source_cab)
    fix_uid=stable_id('SY-FIX','suyeong',r.get('관리번호',''),r.get('등기구ID',''))
    lamp_count=inum(r.get('등 수'),0); lamp_w=fnum(r.get('램프용량(W)'))
    rated=(lamp_count*lamp_w) if lamp_w is not None else None
    fx={
        'fixture_uid':fix_uid,'municipality_id':'suyeong','cabinet_uid':cab_uid,
        'source_fixture_id':r.get('관리번호','').strip(),'source_sub_id':r.get('등기구ID','').strip(),
        'source_cabinet_key':source_cab,'administrative_dong':r.get('행정동','').strip(),
        'road_name':r.get('노선명','').strip(),'address':'','latitude':fnum(r.get('위도')),'longitude':fnum(r.get('경도')),
        'lamp_type':r.get('램프종류','').strip(),'lamp_count':lamp_count,'lamp_watt':lamp_w,'rated_power_w':rated,
        'purpose':r.get('용도','').strip(),'pole_type':r.get('등주종류','').strip(),'pole_shape':r.get('등주형태','').strip(),
        'controller_type':r.get('점멸기종류','').strip(),'branch_no':r.get('분기번호','').strip(),
        'source_file':SUYEONG.name,'source_row':idx
    }
    fixtures.append(fx); suy_by_cab[source_cab].append(fx)
for source_cab,rr in suy_by_cab.items():
    lat=median_or_none([x['latitude'] for x in rr]);lon=median_or_none([x['longitude'] for x in rr])
    pwr=sum(x['rated_power_w'] or 0 for x in rr); lamps=sum(x['lamp_count'] or 0 for x in rr)
    cabinets.append({
        'cabinet_uid':rr[0]['cabinet_uid'],'municipality_id':'suyeong','source_cabinet_key':source_cab,
        'cabinet_name':source_cab,'latitude':lat,'longitude':lon,'fixture_rows':len(rr),'lamp_count':lamps,
        'rated_power_w':pwr,'controller_type':'양방향식' if all(x['controller_type']=='양방향식' for x in rr) else 'mixed',
        'controller_link_status':'asset_only','address':'','source_file':SUYEONG.name
    })
municipalities.append({'municipality_id':'suyeong','municipality_name':'부산광역시 수영구','asset_mode':'full_asset','data_date':'2026-01-14',
                       'fixture_rows':len(suy),'cabinet_count':len(suy_by_cab),'source_file':SUYEONG.name})

# Gangneung controller index
ctrl_idx={}
for idx,r in enumerate(gc,start=2):
    key=(r.get('회사코드','').strip(),r.get('분전함코드','').strip(),r.get('분전함SEQ','').strip())
    cab_uid=stable_id('GN-CAB','gangneung',*key)
    ctrl={
        'controller_uid':stable_id('GN-CTL','gangneung',*key),'municipality_id':'gangneung','cabinet_uid':cab_uid,
        'company_code':key[0],'cabinet_code':key[1],'cabinet_seq':key[2], 'operation_mode':r.get('운영모드','').strip(),
        'switch_model':r.get('점멸기','').strip(),'modem_type':r.get('모뎀타입','').strip(),'modem_id':r.get('모뎀ID','').strip(),
        'on_offset_min':fnum(r.get('점등편차')),'off_offset_min':fnum(r.get('소등편차')),'voltage_setting':fnum(r.get('전압')),
        'sequential_control':r.get('순차제어','').strip(),'forced_time':r.get('강제시간','').strip(),
        'latitude':fnum(r.get('좌표(위도)')),'longitude':fnum(r.get('좌표(경도)')),'address':r.get('주소','').strip(),
        'source_file':GANG_CAB.name,'source_row':idx
    }
    controllers.append(ctrl); ctrl_idx[key]=ctrl

gang_by_cab=defaultdict(list); gang_unmatched=[]
for idx,r in enumerate(gl,start=2):
    key=(r.get('제조사코드','').strip(),r.get('분전함코드','').strip(),r.get('분전함순번(SEQ)','').strip())
    cab_uid=stable_id('GN-CAB','gangneung',*key)
    powers=[fnum(r.get('등용량1')),fnum(r.get('등용량2'))]
    types=[r.get('등종류1','').strip(),r.get('등종류2','').strip()]
    valid_lamps=[(t,p) for t,p in zip(types,powers) if t or p is not None]
    rated=sum(p or 0 for _,p in valid_lamps) if valid_lamps else None
    fx={
        'fixture_uid':stable_id('GN-FIX','gangneung',r.get('제조사코드',''),r.get('가로등코드',''),r.get('가로등순번(SEQ)','')),
        'municipality_id':'gangneung','cabinet_uid':cab_uid,'source_fixture_id':f"{r.get('제조사코드','')}|{r.get('가로등코드','')}|{r.get('가로등순번(SEQ)','')}",
        'source_sub_id':'','source_cabinet_key':'|'.join(key),'administrative_dong':'','road_name':'','address':r.get('주소','').strip(),
        'latitude':fnum(r.get('좌표(위도)')),'longitude':fnum(r.get('좌표(경도)')),
        'lamp_type':' + '.join(t for t in types if t),'lamp_count':len(valid_lamps),'lamp_watt':None,'rated_power_w':rated,
        'purpose':'','pole_type':r.get('등주종류','').strip(),'pole_shape':r.get('등주타입','').strip(),
        'controller_type':ctrl_idx.get(key,{}).get('switch_model',''),'branch_no':'/'.join(x for x in [r.get('분기1','').strip(),r.get('분기2','').strip()] if x),
        'source_file':GANG_LIGHT.name,'source_row':idx
    }
    fixtures.append(fx); gang_by_cab[key].append(fx)
    if key not in ctrl_idx: gang_unmatched.append(fx)
for key,rr in gang_by_cab.items():
    ctrl=ctrl_idx.get(key)
    lat=(ctrl.get('latitude') if ctrl else None) or median_or_none([x['latitude'] for x in rr])
    lon=(ctrl.get('longitude') if ctrl else None) or median_or_none([x['longitude'] for x in rr])
    cabinets.append({
        'cabinet_uid':rr[0]['cabinet_uid'],'municipality_id':'gangneung','source_cabinet_key':'|'.join(key),
        'cabinet_name':'|'.join(key),'latitude':lat,'longitude':lon,'fixture_rows':len(rr),'lamp_count':sum(x['lamp_count'] or 0 for x in rr),
        'rated_power_w':sum(x['rated_power_w'] or 0 for x in rr),'controller_type':ctrl.get('switch_model','') if ctrl else '',
        'controller_link_status':'linked' if ctrl else 'unmatched','address':ctrl.get('address','') if ctrl else '',
        'source_file':GANG_CAB.name if ctrl else GANG_LIGHT.name
    })
municipalities.append({'municipality_id':'gangneung','municipality_name':'강원특별자치도 강릉시','asset_mode':'controller_linked','data_date':'2023-08-20',
                       'fixture_rows':len(gl),'cabinet_count':len(gang_by_cab),'source_file':f'{GANG_LIGHT.name}; {GANG_CAB.name}'})

# Chungju cabinet-only
for idx,r in enumerate(ch,start=2):
    key=r.get('분전함 번호 ',r.get('분전함 번호','')).strip()
    cab_uid=stable_id('CJ-CAB','chungju',key)
    cabinets.append({
        'cabinet_uid':cab_uid,'municipality_id':'chungju','source_cabinet_key':key,
        'cabinet_name':r.get('분전함 이름 ',r.get('분전함 이름','')).strip(),'latitude':fnum(r.get('위도')),'longitude':fnum(r.get('경도')),
        'fixture_rows':None,'lamp_count':inum(r.get('등주수량 ',r.get('등주수량','')),0),'rated_power_w':None,'controller_type':'',
        'controller_link_status':'cabinet_only','address':r.get('설치위치 ',r.get('설치위치','')).strip(),'source_file':CHUNGJU.name
    })
municipalities.append({'municipality_id':'chungju','municipality_name':'충청북도 충주시','asset_mode':'minimal_asset','data_date':'2026-06-30',
                       'fixture_rows':None,'cabinet_count':len(ch),'source_file':CHUNGJU.name})

# Smart streetlights reference normalize lightly
smart_ref=[]
for idx,r in enumerate(sm,start=2):
    smart_ref.append({
        'smart_uid':stable_id('SMART',r.get('시도명',''),r.get('시군구명',''),r.get('도로명',''),r.get('위도',''),r.get('경도',''),str(idx)),
        'province':r.get('시도명','').strip(),'municipality':r.get('시군구명','').strip(),'road_name':r.get('도로명','').strip(),
        'address_road':r.get('소재지도로명주소','').strip(),'address_lot':r.get('소재지지번주소','').strip(),
        'latitude':fnum(r.get('위도')),'longitude':fnum(r.get('경도')),'lighting_control':r.get('조명제어여부','').strip(),
        'sensor_type':r.get('센서종류','').strip(),'manager':r.get('관리기관명','').strip(),'manager_phone':r.get('관리기관전화번호','').strip(),
        'data_date':r.get('데이터기준일자','').strip(),'source_file':SMART.name
    })

# ---- AMI Detector v0.1 ----
ami=json.loads(AMI_JSON.read_text(encoding='utf-8'))
profiles=[]; events=[]; dq=[]; transition_rows=[]

def total_current(r):
    xs=[r.get(k) for k in ('i1','i2','i3') if r.get(k) is not None]
    return sum(xs) if xs else None

def median_gap_minutes(dts):
    gaps=[int((b-a).total_seconds()/60) for a,b in zip(dts,dts[1:]) if b>a]
    return int(statistics.median(gaps)) if gaps else None

def cv(xs):
    xs=[x for x in xs if x is not None]
    if len(xs)<2:return None
    mu=statistics.mean(xs)
    return statistics.pstdev(xs)/mu if mu else None

for meter,raw in ami.items():
    rows=[]
    for r in raw:
        rr=dict(r); rr['_dt']=datetime.strptime(r['time'],'%Y-%m-%d %H:%M');rr['_current']=total_current(r)
        rows.append(rr)
    rows.sort(key=lambda r:r['_dt'])
    valid=[r for r in rows if r['_current'] is not None]
    off_vals=[r['_current'] for r in valid if 10<=r['_dt'].hour<15]
    on_vals=[r['_current'] for r in valid if r['_dt'].hour>=22 or r['_dt'].hour<4]
    off=statistics.median(off_vals); on=statistics.median(on_vals)
    denom=on-off
    if denom<=0: continue
    cadence=median_gap_minutes([r['_dt'] for r in valid]) or 15
    # per phase baselines
    phase_base={}
    for k in ('i1','i2','i3'):
        dv=[r.get(k) for r in valid if 10<=r['_dt'].hour<15 and r.get(k) is not None]
        nv=[r.get(k) for r in valid if (r['_dt'].hour>=22 or r['_dt'].hour<4) and r.get(k) is not None]
        phase_base[k]=(median_or_none(dv),median_or_none(nv))
    # daily night median CV
    byday=defaultdict(list)
    for r in valid:
        if r['_dt'].hour>=22 or r['_dt'].hour<4:byday[r['_dt'].date()].append(r['_current'])
    daily_night=[statistics.median(v) for v in byday.values() if v]
    # energy cadence and TOD baseline
    erows=[r for r in rows if r.get('recv_active') is not None]
    energy_cad=median_gap_minutes([r['_dt'] for r in erows]) if erows else None
    e_tod=defaultdict(list)
    for r in erows:e_tod[(r['_dt'].hour,r['_dt'].minute)].append(float(r['recv_active']))
    e_base={k:statistics.median(v) for k,v in e_tod.items() if v}
    # monthly transitions via activation 0.5
    day_map=defaultdict(list)
    for r in valid:
        r['_activation']=(r['_current']-off)/denom
        day_map[r['_dt'].date()].append(r)
    transitions=defaultdict(lambda:{'morning':[],'evening':[]})
    for d,dr in day_map.items():
        dr=sorted(dr,key=lambda x:x['_dt'])
        morning=[x for x in dr if 4<=x['_dt'].hour<9]
        # first low sample after a high sample during morning window
        mt=None
        for prev,cur in zip(morning,morning[1:]):
            if prev['_activation']>=0.5 and cur['_activation']<0.5:
                mt=cur['_dt'];break
        evening=[x for x in dr if 17<=x['_dt'].hour<23]
        et=None
        for prev,cur in zip(evening,evening[1:]):
            if prev['_activation']<0.5 and cur['_activation']>=0.5:
                et=cur['_dt'];break
        month=f'{d.year}-{d.month:02d}'
        if mt: transitions[month]['morning'].append(mt.hour*60+mt.minute)
        if et: transitions[month]['evening'].append(et.hour*60+et.minute)
    def mm_str(v):
        if v is None:return None
        v=int(round(v/15)*15);return f'{v//60:02d}:{v%60:02d}'
    for mon,v in sorted(transitions.items()):
        transition_rows.append({'meter_id':meter,'month':mon,'morning_off_median':mm_str(median_or_none(v['morning'])),
                                'evening_on_median':mm_str(median_or_none(v['evening'])),'days_morning':len(v['morning']),'days_evening':len(v['evening'])})
    # core day candidate points
    candidates=[]
    for r in valid:
        if 9<=r['_dt'].hour<17 and r['_activation']>=0.20:
            candidates.append(r)
    groups=[]
    for r in candidates:
        if not groups or (r['_dt']-groups[-1][-1]['_dt']).total_seconds()/60 > max(30,cadence*2): groups.append([r])
        else: groups[-1].append(r)
    for g in groups:
        maxa=max(x['_activation'] for x in g); duration=len(g)*cadence
        keep=(maxa>=0.80) or (maxa>=0.40 and duration>=15) or (maxa>=0.20 and duration>=30)
        if not keep: continue
        # phase selective evidence
        phase_max={}
        for k,(poff,pon) in phase_base.items():
            if poff is None or pon is None or pon<=poff: continue
            vals=[(x.get(k)-poff)/(pon-poff) for x in g if x.get(k) is not None]
            if vals:phase_max[k]=max(vals)
        active_phases=[k for k,a in phase_max.items() if a>=0.20]
        all_measured=[k for k,(a,b) in phase_base.items() if a is not None and b is not None and b>a]
        if maxa>=0.80: etype='daytime_full_activation'
        elif len(all_measured)>=2 and 0<len(active_phases)<len(all_measured): etype='daytime_phase_selective_activation'
        else: etype='daytime_partial_activation'
        if maxa>=0.8 and duration>=30: conf='high'
        elif maxa>=0.8 or (maxa>=0.4 and duration>=30) or duration>=60: conf='medium_high'
        else: conf='medium'
        start=g[0]['_dt']; last=g[-1]['_dt']; est_end=last+timedelta(minutes=cadence)
        # energy interval overlap, assuming each sample reports the interval ending at timestamp
        excess=0.0;n_energy=0
        if energy_cad:
            for er in erows:
                interval_start=er['_dt']-timedelta(minutes=energy_cad); interval_end=er['_dt']
                if interval_end<=start or interval_start>=est_end: continue
                base=e_base.get((er['_dt'].hour,er['_dt'].minute))
                if base is not None:
                    excess += max(0.0,float(er['recv_active'])-base); n_energy+=1
        events.append({
            'event_id':stable_id('AMI-EVT',meter,start.isoformat(),last.isoformat()),'meter_id':meter,'event_type':etype,
            'first_sample':start.isoformat(' '),'last_sample':last.isoformat(' '),'estimated_duration_min':duration,
            'max_activation':round(maxa,4),'peak_current_a':round(max(x['_current'] for x in g),4),
            'off_baseline_a':round(off,4),'on_baseline_a':round(on,4),'active_phases':','.join(active_phases),
            'pattern_confidence':conf,'estimated_excess_kwh':round(excess,4) if n_energy else None,
            'energy_method':'interval-end overlap + median by time-of-day' if n_energy else 'unavailable',
            'fault_status':'unverified inspection candidate','source_mode':'anonymized AMI validation'
        })
    # valid night underactivation (measurement-missing rows excluded)
    night_candidates=[r for r in valid if (r['_dt'].hour>=22 or r['_dt'].hour<4) and r['_activation']<0.5]
    # intentionally report count; no events unless >=2 consecutive samples
    ngroups=[]
    for r in night_candidates:
        if not ngroups or (r['_dt']-ngroups[-1][-1]['_dt']).total_seconds()/60 > max(30,cadence*2):ngroups.append([r])
        else:ngroups[-1].append(r)
    night_persistent=sum(1 for g in ngroups if len(g)*cadence>=30)
    # current/voltage channel missing rows
    missing_current=[r for r in rows if all(r.get(k) is None for k in ('i1','i2','i3'))]
    missing_voltage=[r for r in rows if all(r.get(k) is None for k in ('v1','v2','v3'))]
    profiles.append({
        **meta_by_meter.get(meter,{'meter_id':meter}), 'rows':len(rows),'valid_current_rows':len(valid),'cadence_min':cadence,
        'off_baseline_a':round(off,4),'on_baseline_a':round(on,4),'on_off_ratio':round(on/off,2) if off else None,
        'night_daily_cv_pct':round((cv(daily_night) or 0)*100,3),'energy_cadence_min':energy_cad,
        'day_event_count':sum(1 for e in events if e['meter_id']==meter),'persistent_night_underactivation_count':night_persistent
    })
    dq.append({'meter_id':meter,'total_rows':len(rows),'current_channel_missing_rows':len(missing_current),
               'voltage_channel_missing_rows':len(missing_voltage),'current_missing_rate_pct':round(len(missing_current)/len(rows)*100,3),
               'note':'Rows with missing current/voltage are treated as measurement-channel gaps, not zero-current outages.'})

# Sort events by strength then time
events.sort(key=lambda e:(e['first_sample'],e['meter_id']))

# ---- Data quality / stats ----
suy_comp=len(set((r.get('관리번호',''),r.get('등기구ID','')) for r in suy))
suy_lamps=sum(inum(r.get('등 수')) for r in suy)
suy_power=sum((fnum(r.get('램프용량(W)')) or 0)*inum(r.get('등 수')) for r in suy)
gang_ref_keys=set((r.get('제조사코드','').strip(),r.get('분전함코드','').strip(),r.get('분전함순번(SEQ)','').strip()) for r in gl)
gang_ctrl_keys=set(ctrl_idx)
gang_match_rows=sum(1 for r in gl if (r.get('제조사코드','').strip(),r.get('분전함코드','').strip(),r.get('분전함순번(SEQ)','').strip()) in gang_ctrl_keys)
smart_suyeong=sum(1 for r in sm if r.get('시도명','').strip()=='부산광역시' and r.get('시군구명','').strip()=='수영구')
smart_busan=sum(1 for r in sm if r.get('시도명','').strip()=='부산광역시')
summary={
 'suyeong':{'fixture_rows':len(suy),'unique_fixture_composite':suy_comp,'cabinet_count':len(suy_by_cab),'lamp_count':suy_lamps,
            'rated_power_kw':round(suy_power/1000,3),'all_controller_type_bidirectional':all(r.get('점멸기종류','').strip()=='양방향식' for r in suy),
            'latlon_complete_pct':round(sum(1 for r in suy if fnum(r.get('위도')) is not None and fnum(r.get('경도')) is not None)/len(suy)*100,2)},
 'gangneung':{'fixture_rows':len(gl),'referenced_cabinets':len(gang_ref_keys),'controller_rows':len(gc),'matched_referenced_cabinets':len(gang_ref_keys&gang_ctrl_keys),
               'unmatched_referenced_cabinets':len(gang_ref_keys-gang_ctrl_keys),'matched_fixture_rows':gang_match_rows,'fixture_join_rate_pct':round(gang_match_rows/len(gl)*100,3)},
 'chungju':{'cabinet_rows':len(ch),'lamp_pole_count':sum(inum(r.get('등주수량 ',r.get('등주수량',''))) for r in ch),
            'latlon_complete_pct':round(sum(1 for r in ch if fnum(r.get('위도')) is not None and fnum(r.get('경도')) is not None)/len(ch)*100,2)},
 'smart_reference':{'rows':len(sm),'busan_rows':smart_busan,'suyeong_rows':smart_suyeong},
 'ami':{'streetlight_meter_count':len(profiles),'detected_daytime_events':len(events),'meters':[p['meter_id'] for p in profiles]}
}

# ---- Export normalized data ----
write_csv(DATA/'municipalities.csv',municipalities)
write_csv(DATA/'cabinets.csv',cabinets)
write_csv(DATA/'fixtures.csv',fixtures)
write_csv(DATA/'controllers.csv',controllers)
write_csv(DATA/'smart_streetlight_reference.csv',smart_ref)
write_csv(DATA/'ami_meter_profiles.csv',profiles)
write_csv(DATA/'ami_events.csv',events)
write_csv(DATA/'ami_data_quality.csv',dq)
write_csv(DATA/'ami_monthly_transitions.csv',transition_rows)
write_json(DATA/'data_summary.json',summary)
write_json(SEED/'municipalities.json',municipalities)
write_json(SEED/'suyeong_cabinets.json',[x for x in cabinets if x['municipality_id']=='suyeong'])
write_json(SEED/'suyeong_fixtures.json',[x for x in fixtures if x['municipality_id']=='suyeong'])
write_json(SEED/'gangneung_cabinets.json',[x for x in cabinets if x['municipality_id']=='gangneung'])
write_json(SEED/'gangneung_fixtures.json',[x for x in fixtures if x['municipality_id']=='gangneung'])
write_json(SEED/'gangneung_controllers.json',controllers)
write_json(SEED/'chungju_cabinets.json',[x for x in cabinets if x['municipality_id']=='chungju'])
write_json(SEED/'demo_ami_meters.json',profiles)
write_json(SEED/'demo_ami_events.json',events)

# Empty mapping table is intentional: never fabricate AMI-to-municipal mapping.
mapping_fields=['mapping_id','meter_id','cabinet_uid','municipality_id','mapping_status','evidence','verified_at']
write_csv(DATA/'ami_cabinet_mappings.csv',[],mapping_fields)
write_json(SEED/'ami_cabinet_mappings.json',[])

# ---- SQLite ----
db=OUT/'lightguard_v0_1.sqlite'
if db.exists():db.unlink()
conn=sqlite3.connect(db)
conn.execute('PRAGMA foreign_keys=ON')
conn.execute('CREATE TABLE municipalities (municipality_id TEXT PRIMARY KEY, municipality_name TEXT, asset_mode TEXT, data_date TEXT, fixture_rows INTEGER, cabinet_count INTEGER, source_file TEXT)')
conn.execute('''CREATE TABLE cabinets (cabinet_uid TEXT PRIMARY KEY, municipality_id TEXT, source_cabinet_key TEXT, cabinet_name TEXT,
 latitude REAL, longitude REAL, fixture_rows INTEGER, lamp_count INTEGER, rated_power_w REAL, controller_type TEXT, controller_link_status TEXT, address TEXT, source_file TEXT)''')
conn.execute('''CREATE TABLE fixtures (fixture_uid TEXT PRIMARY KEY, municipality_id TEXT, cabinet_uid TEXT, source_fixture_id TEXT, source_sub_id TEXT,
 source_cabinet_key TEXT, administrative_dong TEXT, road_name TEXT, address TEXT, latitude REAL, longitude REAL, lamp_type TEXT, lamp_count INTEGER,
 lamp_watt REAL, rated_power_w REAL, purpose TEXT, pole_type TEXT, pole_shape TEXT, controller_type TEXT, branch_no TEXT, source_file TEXT, source_row INTEGER)''')
conn.execute('''CREATE TABLE controllers (controller_uid TEXT PRIMARY KEY, municipality_id TEXT, cabinet_uid TEXT, company_code TEXT, cabinet_code TEXT, cabinet_seq TEXT,
 operation_mode TEXT, switch_model TEXT, modem_type TEXT, modem_id TEXT, on_offset_min REAL, off_offset_min REAL, voltage_setting REAL, sequential_control TEXT,
 forced_time TEXT, latitude REAL, longitude REAL, address TEXT, source_file TEXT, source_row INTEGER)''')
conn.execute('''CREATE TABLE ami_meter_profiles (meter_id TEXT PRIMARY KEY, line TEXT, section_no TEXT, multiplier REAL, supply_type TEXT, contract_power_kw REAL,
 contract_type TEXT, usage TEXT, production TEXT, industry TEXT, rows INTEGER, valid_current_rows INTEGER, cadence_min INTEGER, off_baseline_a REAL,
 on_baseline_a REAL, on_off_ratio REAL, night_daily_cv_pct REAL, energy_cadence_min INTEGER, day_event_count INTEGER, persistent_night_underactivation_count INTEGER)''')
conn.execute('''CREATE TABLE ami_events (event_id TEXT PRIMARY KEY, meter_id TEXT, event_type TEXT, first_sample TEXT, last_sample TEXT, estimated_duration_min INTEGER,
 max_activation REAL, peak_current_a REAL, off_baseline_a REAL, on_baseline_a REAL, active_phases TEXT, pattern_confidence TEXT, estimated_excess_kwh REAL,
 energy_method TEXT, fault_status TEXT, source_mode TEXT)''')
conn.execute('''CREATE TABLE ami_cabinet_mappings (mapping_id TEXT PRIMARY KEY, meter_id TEXT, cabinet_uid TEXT, municipality_id TEXT, mapping_status TEXT, evidence TEXT, verified_at TEXT)''')

def ins(table, rows):
    if not rows:return
    cols=list(rows[0].keys()); qs=','.join('?' for _ in cols)
    conn.executemany(f'INSERT INTO {table} ({",".join(cols)}) VALUES ({qs})',[[r.get(c) for c in cols] for r in rows])
ins('municipalities',municipalities);ins('cabinets',cabinets);ins('fixtures',fixtures);ins('controllers',controllers);ins('ami_meter_profiles',profiles);ins('ami_events',events)
conn.execute('CREATE INDEX idx_cabinets_muni ON cabinets(municipality_id)')
conn.execute('CREATE INDEX idx_fixtures_cab ON fixtures(cabinet_uid)')
conn.execute('CREATE INDEX idx_events_meter_time ON ami_events(meter_id, first_sample)')
conn.commit();conn.close()

# ---- Source manifest ----
source_files=[SUYEONG,GANG_LIGHT,GANG_CAB,CHUNGJU,SMART,AMI_JSON,META_XLSX]
manifest=[]
for p in source_files:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    manifest.append({'file':p.name,'size_bytes':p.stat().st_size,'sha256':h.hexdigest(),'encoding':detect_encoding(p) if p.suffix.lower()=='.csv' else None})
write_json(OUT/'source_manifest.json',manifest)

# ---- Detector source standalone ----
shutil.copy2(Path(__file__), SRC/'build_lightguard_v01.py')

# ---- Reports ----
# top events
lines=['# LightGuard v0.1 데이터 검증 리포트','',
'## 1. 이번 단계에서 한 일','',
'- 부산 수영구·강릉시·충주시 가로등/분전함 파일을 하나의 공통 데이터 모델로 정규화했습니다.',
'- 공모전 AMI 가로등 5개 계량기에 대해 설명 가능한 규칙 기반 Detector v0.1을 구현했습니다.',
'- 실제 지자체 자산과 가명화 AMI 사이의 공식 연결키가 없으므로 `ami_cabinet_mappings`는 의도적으로 비워 두었습니다.',
'- 앱이 바로 읽을 수 있는 JSON seed와 SQLite DB를 함께 생성했습니다.','',
'## 2. 지자체 데이터 결과','',
f"- 수영구: {summary['suyeong']['fixture_rows']:,}개 행, {summary['suyeong']['cabinet_count']:,}개 분전함, {summary['suyeong']['lamp_count']:,}등, 계산 가능한 정격용량 약 {summary['suyeong']['rated_power_kw']:.3f} kW.",
f"- 수영구 복합키(관리번호+등기구ID)는 {summary['suyeong']['unique_fixture_composite']:,}/{summary['suyeong']['fixture_rows']:,}로 중복이 없습니다.",
f"- 수영구의 점멸기종류는 전 행에서 양방향식입니다.",
f"- 강릉: 가로등 {summary['gangneung']['fixture_rows']:,}행이 {summary['gangneung']['referenced_cabinets']}개 분전함을 참조하며, 제어기 데이터와 {summary['gangneung']['fixture_join_rate_pct']:.3f}% 조인됩니다. 미매칭은 1개 분전함/8개 가로등 행입니다.",
f"- 충주: 분전함 {summary['chungju']['cabinet_rows']:,}개, 등주수량 합계 {summary['chungju']['lamp_pole_count']:,}개입니다.",
f"- 전국 스마트가로등 표준데이터: {summary['smart_reference']['rows']:,}행이며, 부산 데이터는 {summary['smart_reference']['busan_rows']}행, 수영구 명시 레코드는 {summary['smart_reference']['suyeong_rows']}행입니다. 이 표준데이터의 부재를 스마트화 부재로 해석하면 안 됩니다.",'',
'## 3. AMI Detector v0.1 결과','',
'- 상태판정의 주 신호는 전류(i1+i2+i3)입니다. 전류 채널이 모두 결측인 행은 0A로 처리하지 않고 계측결측으로 제외합니다.',
'- 익명 AMI에는 실제 위치가 없으므로 일출·일몰을 억지로 적용하지 않고 09:00~16:59를 보수적인 핵심 주간 검증창으로 사용했습니다.',
'- 각 계량기별 10:00~14:59 전류 중앙값을 OFF baseline, 22:00~03:59 중앙값을 ON baseline으로 사용해 activation을 계산했습니다.',
'- 탐지 결과는 고장 확정이 아니라 `unverified inspection candidate`입니다.','',
'### 탐지 이벤트','',
'|계량기|시작|마지막 샘플|추정 지속|유형|최대 활성도|최대전류(A)|초과 kWh 추정|신뢰도|','|---|---|---|---:|---|---:|---:|---:|---|']
for e in events:
    excess_text = '' if e['estimated_excess_kwh'] is None else format(e['estimated_excess_kwh'], '.3f')
    lines.append(f"|{e['meter_id']}|{e['first_sample']}|{e['last_sample']}|{e['estimated_duration_min']}분|{e['event_type']}|{e['max_activation']*100:.1f}%|{e['peak_current_a']:.3f}|{excess_text}|{e['pattern_confidence']}|")
lines += ['', '## 4. 중요한 데이터 품질 발견','']
for q in dq:
    lines.append(f"- {q['meter_id']}: 전류/전압 채널 결측 {q['current_channel_missing_rows']}행 ({q['current_missing_rate_pct']:.3f}%). 이 행들은 전력량 값이 존재할 수 있으므로 미점등으로 판정하면 안 됩니다.")
lines += ['', '## 5. 앱에 연결할 때의 원칙','',
'1. **AMI 검증 모드**: 공모전 가명화 AMI에서 실제 탐지된 이벤트를 그대로 표시합니다.',
'2. **수영구 자산 모드**: 204개 실제 분전함과 4,076개 자산행을 지도/목록에 표시합니다.',
'3. **Mapping 전에는 두 모드를 결합하지 않습니다.** 실제 계량기↔분전함 연결키를 기관에서 받기 전에는 특정 수영구 분전함에 AMI 이상을 붙이지 않습니다.',
'4. **강릉은 Controller-linked 검증**에 사용합니다. 제어기 설정과 자산의 조인구조가 이미 존재합니다.',
'5. **충주는 Minimal mode**로 사용합니다. 개별 램프 정격이 없어도 분전함/등주수/위치 수준에서 서비스가 열리도록 설계합니다.','',
'## 6. 다음 구현 단계','',
'- Flutter Web/Android 공통 프로젝트에서 SQLite 또는 JSON seed를 읽는 Data Repository를 먼저 구현합니다.',
'- 첫 화면은 `수영구 관제지도`, 두 번째는 `AMI 검증 이벤트`, 세 번째는 `분전함 상세`, 네 번째는 `데이터/Mapping 상태`가 적절합니다.',
'- 이후 부산 일출·일몰/시민박명과 기상데이터를 `context` 레이어로 추가해 지역운영 Detector를 구현합니다.',
'- 마지막으로 강릉/충주 adapter를 켜 동일 UI가 데이터 수준에 따라 기능을 축소/확장하는지 검증합니다.']
(REPORTS/'validation_report.md').write_text('\n'.join(lines),encoding='utf-8')

readme=f'''# AMI LightGuard v0.1\n\n공모전 제공 AMI와 지자체 공개 가로등 데이터를 이용한 **독립 검증·점검 후보 생성**용 데이터 레이어입니다.\n\n## 핵심 원칙\n- 실제 AMI↔지자체 분전함 매핑은 제공되지 않았습니다. `ami_cabinet_mappings`는 비어 있으며 임의 매핑을 만들지 않습니다.\n- AMI 이벤트는 고장 확정이 아니라 점검 후보입니다.\n- 수영구는 Full Asset, 강릉은 Controller-linked, 충주는 Minimal Asset mode로 정규화합니다.\n\n## 주요 파일\n- `lightguard_v0_1.sqlite`: 앱/백엔드가 바로 읽을 수 있는 DB\n- `app_seed/*.json`: Flutter/Web 데모용 seed\n- `data/ami_events.csv`: Detector v0.1 실제 탐지 이벤트\n- `data/ami_meter_profiles.csv`: 5개 가로등 AMI baseline/profile\n- `data/cabinets.csv`, `data/fixtures.csv`, `data/controllers.csv`: 공통 자산 모델\n- `reports/validation_report.md`: 분석 결과와 구현 원칙\n\n## 현재 범위\n- 수영구: {len(suy):,} fixture rows / {len(suy_by_cab):,} cabinets\n- 강릉: {len(gl):,} fixture rows / {len(gang_by_cab):,} referenced cabinets\n- 충주: {len(ch):,} cabinet rows\n- AMI: {len(profiles)} streetlight meters / {len(events)} daytime inspection candidates\n'''
(OUT/'README.md').write_text(readme,encoding='utf-8')

# Zip package
zip_path=ROOT/'lightguard_v0_1_package.zip'
if zip_path.exists():zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in OUT.rglob('*'):
        if p.is_file(): z.write(p,p.relative_to(ROOT))

print(json.dumps({'out':str(OUT),'zip':str(zip_path),'summary':summary,'events':events},ensure_ascii=False,indent=2))
