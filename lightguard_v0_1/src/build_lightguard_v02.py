#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import math
import os
import statistics
import zipfile
import json
import shutil
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path('/mnt/data')
if not ROOT.exists():
    ROOT = Path(__file__).resolve().parents[1]

OUT = Path(__file__).resolve().parents[1]
DATA_DIR = OUT / 'data'
SEED_DIR = OUT / 'app_seed'
REPORTS_DIR = OUT / 'reports'
SRC_DIR = OUT / 'src'
for d in (OUT, DATA_DIR, SEED_DIR, REPORTS_DIR, SRC_DIR):
    d.mkdir(parents=True, exist_ok=True)

SUYEONG_TARGET_RATING_W = 3400
SUYEONG_TARGET_TOLERANCE_W = 600
SCENARIO_DROP_PCT = 0.20
SCENARIO_DURATION_MIN = 90
SCENARIO_EVENT_MIN_GAP = 30


def detect_encoding(path: Path) -> str:
    with path.open('rb') as f:
        raw = f.read(4000)
    for enc in ('utf-8-sig', 'cp949', 'euc-kr', 'utf-8'):
        try:
            raw.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return 'utf-8'


def read_csv(path: Path):
    if not path.exists():
        return []
    enc = detect_encoding(path)
    with path.open(encoding=enc, newline='') as f:
        return list(csv.DictReader(f))


def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def write_csv(path: Path, rows: list[dict], fields=None):
    if not rows:
        path.write_text('', encoding='utf-8-sig')
        return
    if fields is None:
        fields = []
        seen = set()
        for row in rows:
            for key in row:
                if key not in seen:
                    fields.append(key)
                    seen.add(key)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def fnum(value):
    if value is None:
        return None
    s = str(value).strip().replace(',', '')
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def stable_id(prefix: str, *parts: str) -> str:
    raw = '|'.join('' if p is None else str(p).strip() for p in parts)
    h = hashlib.sha1(raw.encode('utf-8')).hexdigest()[:10]
    return f'{prefix}-{h}'


def find1(pattern: str, root: Path) -> Path:
    xs = sorted(root.glob(pattern))
    if len(xs) != 1:
        raise RuntimeError(f'{pattern}: expected 1 file in {root}, got {len(xs)} -> {xs}')
    return xs[0]


def find_any(patterns: list[str], root: Path):
    for p in patterns:
        found = sorted(root.glob(p))
        if found:
            return found[0]
    return None


def to_float_or_zero(value):
    return fnum(value) or 0.0


def km_distance_km(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    r = 6371.0088
    lat1r = math.radians(lat1)
    lat2r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1r) * math.cos(lat2r) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(h)))


# ---------------------------------------------------------------------------
# Sun/time helpers (civil + sunrise/sunset, local timezone assumed Asia/Seoul fixed +9)
# ---------------------------------------------------------------------------

def _sin_deg(d):
    return math.sin(math.radians(d))


def _cos_deg(d):
    return math.cos(math.radians(d))


def _tan_deg(d):
    return math.tan(math.radians(d))


def _asin(x):
    return math.degrees(math.asin(max(-1.0, min(1.0, x))))


def _acos(x):
    return math.degrees(math.acos(max(-1.0, min(1.0, x))))


def _normalize_angle(deg: float) -> float:
    return deg % 360

def calc_noon_event(date: datetime.date, lat: float, lon: float, zenith: float, is_rise: bool):
    day = date.timetuple().tm_yday
    lng_hour = lon / 15.0
    if is_rise:
        t = day + ((6 - lng_hour) / 24.0)
    else:
        t = day + ((18 - lng_hour) / 24.0)

    m = (0.9856 * t) - 3.289
    l = m + 1.916 * _sin_deg(m) + 0.020 * _sin_deg(2 * m) + 282.634
    l = _normalize_angle(l)

    ra = _atan2_deg(0.91764 * _tan_deg(l), 1.0)
    lq = math.floor(l / 90) * 90
    ra = _normalize_angle(ra + (lq - math.floor(ra / 90) * 90))
    ra /= 15.0

    sin_dec = 0.39782 * _sin_deg(l)
    cos_dec = math.cos(math.asin(sin_dec))
    cos_h = (_cos_deg(zenith) - sin_dec * _sin_deg(lat)) / (cos_dec * _cos_deg(lat))
    if cos_h < -1:
        cos_h = -1.0
    if cos_h > 1:
        return None

    if is_rise:
        h = 360 - _acos(cos_h)
    else:
        h = _acos(cos_h)
    h = h / 15.0
    t_local = h + ra - 0.06571 * t - 6.622
    ut = t_local - lng_hour
    # Local timezone fixed +9 (Seoul)
    local_hour = ut + 9
    base = datetime(date.year, date.month, date.day)
    dt = base + timedelta(hours=local_hour)
    return dt


def _atan2_deg(y, x):
    return math.degrees(math.atan2(y, x))


def calc_sun_schedule(date: datetime.date, lat: float, lon: float):
    sunrise = calc_noon_event(date, lat, lon, 90.833, True)
    sunset = calc_noon_event(date, lat, lon, 90.833, False)
    civil_start = calc_noon_event(date, lat, lon, 96.0, True)
    civil_end = calc_noon_event(date, lat, lon, 96.0, False)

    def to_same_day(ts: datetime):
        return ts if ts.date() == date else datetime(date.year, date.month, date.day, ts.hour, ts.minute, ts.second)

    # if no event, fallback hard values around Busan range
    if sunrise is None:
        sunrise = datetime(date.year, date.month, date.day, 6, 30)
    if sunset is None:
        sunset = datetime(date.year, date.month, date.day, 17, 45)
    else:
        sunrise = to_same_day(sunrise)
        sunset = to_same_day(sunset)
    if civil_start is None:
        civil_start = sunrise
    else:
        civil_start = to_same_day(civil_start)
    if civil_end is None:
        civil_end = sunset
    else:
        civil_end = to_same_day(civil_end)

    return {
        'date': date.isoformat(),
        'sunrise': sunrise.strftime('%H:%M'),
        'sunset': sunset.strftime('%H:%M'),
        'civil_twilight_start': civil_start.strftime('%H:%M'),
        'civil_twilight_end': civil_end.strftime('%H:%M'),
        'sunrise_dt': sunrise,
        'sunset_dt': sunset,
        'civil_start_dt': civil_start,
        'civil_end_dt': civil_end,
    }


def hhmm(dt):
    return dt.strftime('%H:%M')


# ---------------------------------------------------------------------------
# Data load (prefer normalized outputs, fallback to raw source if available)
# ---------------------------------------------------------------------------

def load_normalized_suyeong_assets():
    cabinets_csv = DATA_DIR / 'cabinets.csv'
    fixtures_csv = DATA_DIR / 'fixtures.csv'
    if not cabinets_csv.exists() or not fixtures_csv.exists():
        return None, None

    cabinet_rows = read_csv(cabinets_csv)
    fixture_rows = read_csv(fixtures_csv)
    suyeong_cabinets = [r for r in cabinet_rows if str(r.get('municipality_id', '')).strip() == 'suyeong']
    suyeong_fixtures = [r for r in fixture_rows if str(r.get('municipality_id', '')).strip() == 'suyeong']

    if not suyeong_cabinets:
        return None, None

    fixture_map = defaultdict(list)
    for r in suyeong_fixtures:
        fixture_map[r.get('cabinet_uid', '')].append(r)

    return suyeong_cabinets, fixture_map


def load_suyeong_from_raw():
    try:
        src = find1('*20260114.csv', ROOT)
    except RuntimeError as e:
        return None, None

    rows = read_csv(src)
    if not rows:
        return None, None

    cabinet_rows = []
    fixture_rows = defaultdict(list)
    cabinet_map = {}

    for idx, r in enumerate(rows, start=2):
        source_cab = r.get('소속분전함', '').strip()
        if not source_cab:
            continue
        cab_uid = stable_id('SY-CAB', 'suyeong', source_cab)
        source_fixture = r.get('관리번호', '').strip()
        source_sub = r.get('등기구ID', '').strip()
        fixture_lamp_count = fnum(r.get('등 수'))
        lamp_count = int(round(fixture_lamp_count)) if fixture_lamp_count is not None else 0
        lamp_w = fnum(r.get('램프용량(W)'))
        rated = (lamp_count * lamp_w) if lamp_w is not None else None

        fx_uid = stable_id('SY-FIX', 'suyeong', source_fixture, source_sub, source_cab)
        fixture_rows[cab_uid].append({
            'fixture_uid': fx_uid,
            'municipality_id': 'suyeong',
            'cabinet_uid': cab_uid,
            'source_fixture_id': source_fixture,
            'source_sub_id': source_sub,
            'source_cabinet_key': source_cab,
            'administrative_dong': r.get('행정동', '').strip(),
            'road_name': r.get('노선명', '').strip(),
            'address': '',
            'latitude': fnum(r.get('위도')),
            'longitude': fnum(r.get('경도')),
            'lamp_type': r.get('램프종류', '').strip(),
            'lamp_count': lamp_count,
            'lamp_watt': lamp_w,
            'rated_power_w': rated,
            'purpose': r.get('용도', '').strip(),
            'pole_type': r.get('등주종류', '').strip(),
            'pole_shape': r.get('등주형태', '').strip(),
            'controller_type': r.get('점멸기종류', '').strip(),
            'branch_no': r.get('분기번호', '').strip(),
            'source_file': src.name,
            'source_row': idx,
        })

        if source_cab not in cabinet_map:
            lat = fnum(r.get('위도'))
            lon = fnum(r.get('경도'))
            cabinet_map[source_cab] = {
                'cabinet_uid': cab_uid,
                'municipality_id': 'suyeong',
                'source_cabinet_key': source_cab,
                'cabinet_name': source_cab,
                'latitude': lat,
                'longitude': lon,
                'fixture_rows': 0,
                'lamp_count': 0,
                'rated_power_w': 0.0,
                'controller_type': r.get('점멸기종류', '').strip(),
                'controller_link_status': 'asset_only',
                'address': '',
                'source_file': src.name,
            }

        if cabinet_map[source_cab]['latitude'] is None:
            cabinet_map[source_cab]['latitude'] = fnum(r.get('위도'))
            cabinet_map[source_cab]['longitude'] = fnum(r.get('경도'))
        cabinet_map[source_cab]['fixture_rows'] += 1
        cabinet_map[source_cab]['lamp_count'] += lamp_count
        if rated:
            cabinet_map[source_cab]['rated_power_w'] += rated

    for k, cab in cabinet_map.items():
        # keep integer-like output, keep None fallback to 0 for sortability
        cab['fixture_rows'] = int(cab['fixture_rows'])
        cab['lamp_count'] = int(cab['lamp_count'])

    return list(cabinet_map.values()), fixture_rows


def choose_suyeong_assets():
    cab_rows, fixture_map = load_normalized_suyeong_assets()
    if cab_rows is not None:
        return cab_rows, fixture_map
    return load_suyeong_from_raw()


def load_ami_profiles():
    profile_path = DATA_DIR / 'ami_meter_profiles.csv'
    if profile_path.exists():
        return read_csv(profile_path)
    return []


def make_weather_stations(fixtures: dict[str, list[dict]]):
    all_rows = [r for rows in fixtures.values() for r in rows]
    with_coord = [r for r in all_rows if fnum(r.get('latitude')) is not None and fnum(r.get('longitude')) is not None]

    stations = []
    if with_coord:
        buckets = defaultdict(list)
        for r in with_coord:
            lat = fnum(r.get('latitude'))
            lon = fnum(r.get('longitude'))
            if lat is None or lon is None:
                continue
            key = (round(lat, 2), round(lon, 2))
            buckets[key].append((lat, lon))

        # derive up to 4 synthetic station points from coarse buckets
        top_items = sorted(((len(v), k, v) for k, v in buckets.items()), reverse=True)
        for _, key, vals in top_items[:4]:
            lat = sum(v[0] for v in vals) / len(vals)
            lon = sum(v[1] for v in vals) / len(vals)
            stations.append({
                'station_id': stable_id('STN', f'{lat:.4f}', f'{lon:.4f}'),
                'station_name': f'수영구 {key[0]:.2f}_{key[1]:.2f}',
                'latitude': round(lat, 6),
                'longitude': round(lon, 6),
                'station_type': 'synthetic_cluster',
            })

        if not stations:
            lat = sum(fnum(r.get('latitude')) for r in with_coord if fnum(r.get('latitude')) is not None) / len(with_coord)
            lon = sum(fnum(r.get('longitude')) for r in with_coord if fnum(r.get('longitude')) is not None) / len(with_coord)
            stations.append({
                'station_id': stable_id('STN', 'suyeong_center'),
                'station_name': '수영구 중심',
                'latitude': round(lat, 6),
                'longitude': round(lon, 6),
                'station_type': 'synthetic_center',
            })
    else:
        stations.append({
            'station_id': 'SUY-MOCK-0001',
            'station_name': '수영구 미정 위치',
            'latitude': 35.16,
            'longitude': 129.12,
            'station_type': 'synthetic_default',
        })

    return stations


def nearest_station(cab: dict, stations: list[dict]):
    cab_lat = fnum(cab.get('latitude'))
    cab_lon = fnum(cab.get('longitude'))
    if cab_lat is None or cab_lon is None:
        return stations[0], None

    best = None
    best_d = 1e12
    for s in stations:
        d = km_distance_km(cab_lat, cab_lon, fnum(s.get('latitude')), fnum(s.get('longitude')))
        if d is None:
            continue
        if d < best_d:
            best_d = d
            best = s
    return best, best_d


def generate_synthetic_weather_series(date: datetime.date, station: dict):
    base = datetime(date.year, date.month, date.day)
    rows = []
    for hour in range(24):
        dt = base + timedelta(hours=hour)
        t = 13 + 8 * math.sin((hour - 13) / 24 * 2 * math.pi)
        c = 45 + 20 * math.cos((hour - 16) / 24 * 2 * math.pi)
        wind = 1.5 + 1.0 * abs(math.sin(hour / 24 * 2 * math.pi))
        rows.append({
            'time': dt.strftime('%Y-%m-%d %H:%M'),
            'temperature_c': round(t, 1),
            'cloud_pct': int(round(max(0, min(100, c)))),
            'wind_ms': round(wind, 2),
            'station_id': station['station_id'],
            'station_name': station['station_name'],
        })
    return rows


def to_detection_sample_series(scenario_start: datetime, scenario_end: datetime, off_current: float, on_current: float, cadence_min=15):
    start = scenario_start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    rows = []
    t = start
    while t < end:
        in_window = (scenario_start <= t <= scenario_end)
        current = off_current + (on_current - off_current) * SCENARIO_DROP_PCT if in_window else off_current
        rows.append({
            'time': t.strftime('%Y-%m-%d %H:%M'),
            'current_total': round(current, 6),
            'i1': round(current / 3, 6),
            'i2': round(current / 3, 6),
            'i3': round(current / 3, 6),
        })
        t += timedelta(minutes=cadence_min)

    return rows


def detect_daytime_events(rows: list[dict], off_base: float, on_base: float):
    if not rows:
        return []
    valid = []
    for r in rows:
        dts = datetime.strptime(r['time'], '%Y-%m-%d %H:%M')
        total = fnum(r.get('current_total'))
        if total is None:
            continue
        valid.append({'dt': dts, 'current': total})

    if not valid:
        return []

    valid.sort(key=lambda x: x['dt'])
    denom = on_base - off_base
    if denom <= 0:
        return []

    candidates = []
    for r in valid:
        if r['dt'].hour < 9 or r['dt'].hour > 16:
            continue
        act = (r['current'] - off_base) / denom
        if act >= max(0.10, SCENARIO_DROP_PCT - 0.01):
            candidates.append((r, act))

    if not candidates:
        return []

    groups = []
    for sample, act in candidates:
        if not groups or (sample['dt'] - groups[-1][-1]['dt']).total_seconds() > 60 * max(30, 2 * 15):
            groups.append([{'dt': sample['dt'], 'act': act, 'current': sample['current']}])
        else:
            groups[-1].append({'dt': sample['dt'], 'act': act, 'current': sample['current']})

    events = []
    for gi, g in enumerate(groups):
        maxa = max(x['act'] for x in g)
        duration_min = max(1, int((g[-1]['dt'] - g[0]['dt']).total_seconds() / 60) + 15)
        keep = maxa >= max(0.10, SCENARIO_DROP_PCT * 0.75)
        if not keep:
            continue

        etype = 'daytime_partial_activation'
        if maxa >= 0.80:
            etype = 'daytime_full_activation'
        elif len(g) >= 2 and (g[0]['act'] > 0.2 and g[-1]['act'] > 0.2):
            etype = 'daytime_phase_selective_activation'

        conf = 'low'
        if maxa >= 0.80 and duration_min >= 30:
            conf = 'high'
        elif maxa >= 0.40 and duration_min >= 30:
            conf = 'medium_high'
        else:
            conf = 'medium'

        events.append({
            'event_id': stable_id('AMI-EVT-SIM', g[0]['dt'].isoformat(), g[-1]['dt'].isoformat()),
            'event_type': etype,
            'first_sample': g[0]['dt'].strftime('%Y-%m-%d %H:%M'),
            'last_sample': g[-1]['dt'].strftime('%Y-%m-%d %H:%M'),
            'estimated_duration_min': duration_min,
            'max_activation': round(maxa, 4),
            'peak_current_a': max(x['current'] for x in g),
            'off_baseline_a': round(off_base, 4),
            'on_baseline_a': round(on_base, 4),
            'active_phases': 'i1,i2,i3',
            'pattern_confidence': conf,
            'estimated_excess_kwh': None,
            'energy_method': 'synthetic_injection',
            'fault_status': 'validation_candidate',
            'source_mode': 'scenario_injection',
            'scenario_group': gi,
        })

    return events


def make_priority(score: float):
    if score >= 85:
        return 'critical'
    if score >= 70:
        return 'high'
    if score >= 50:
        return 'medium'
    return 'low'


def build_inventory_and_scenarios():
    suyeong_cabinets, cabinet_fixture_map = choose_suyeong_assets()
    if not suyeong_cabinets:
        raise RuntimeError('수영구 자산 데이터를 읽지 못했습니다.')

    weather_stations = make_weather_stations(cabinet_fixture_map)
    stations_map = {s['station_id']: s for s in weather_stations}

    # scenario candidates: 3.4 kW 주변 분전함
    targets = []
    for c in suyeong_cabinets:
        rp = fnum(c.get('rated_power_w'))
        if rp is None:
            continue
        if abs(rp - SUYEONG_TARGET_RATING_W) <= SUYEONG_TARGET_TOLERANCE_W:
            targets.append(c)

    if not targets:
        # no exact 3.4kW cabinet, pick nearest 3 and flag fallback
        ranked = sorted(
            [c for c in suyeong_cabinets if fnum(c.get('rated_power_w')) is not None],
            key=lambda x: abs(fnum(x.get('rated_power_w')) - SUYEONG_TARGET_RATING_W),
        )
        targets = ranked[:3]

    base_date = datetime(2026, 1, 14)
    scenarios = []
    scenario_records = []
    v02_objects = []

    for c in suyeong_cabinets:
        cab_uid = c['cabinet_uid']
        fixtures = cabinet_fixture_map.get(cab_uid, [])
        lat = fnum(c.get('latitude'))
        lon = fnum(c.get('longitude'))
        if lat is None or lon is None:
            # fallback to fixture mean
            lats = [fnum(x.get('latitude')) for x in fixtures if fnum(x.get('latitude')) is not None]
            lons = [fnum(x.get('longitude')) for x in fixtures if fnum(x.get('longitude')) is not None]
            lat = (sum(lats) / len(lats)) if lats else None
            lon = (sum(lons) / len(lons)) if lons else None

        sun = calc_sun_schedule(base_date.date(), lat or 35.16, lon or 129.12)

        station, dist_km = nearest_station(c, weather_stations)
        station = station or stations_map[weather_stations[0]['station_id']]
        weather_ctx = {
            'station_id': station['station_id'],
            'station_name': station.get('station_name'),
            'station_type': station.get('station_type'),
            'distance_km_to_station': round(dist_km, 3) if dist_km is not None else None,
            'forecast_hourly': generate_synthetic_weather_series(base_date.date(), station),
            'observation_at': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        }

        expected_schedule = {
            'date': base_date.date().isoformat(),
            'sunrise': sun['sunrise'],
            'sunset': sun['sunset'],
            'civil_twilight_start': sun['civil_twilight_start'],
            'civil_twilight_end': sun['civil_twilight_end'],
            'expected_on_window': {
                'start_mode': 'sunset_to_next_sunrise',
                'on_start': sun['sunset'],
                'on_end': sun['sunrise'],
            }
        }

        rated = fnum(c.get('rated_power_w')) or 0.0
        fixture_count = int(c.get('fixture_rows') or len(fixtures) or 0)
        lamp_count = int(c.get('lamp_count') or sum(int(fnum(x.get('lamp_count')) or 0) for x in fixtures))

        asset_info = {
            'cabinet_uid': cab_uid,
            'cabinet_name': c.get('cabinet_name') or c.get('source_cabinet_key'),
            'source_cabinet_key': c.get('source_cabinet_key'),
            'municipality_id': 'suyeong',
            'spatial': {
                'latitude': lat,
                'longitude': lon,
            },
            'fixture_count': fixture_count,
            'lamp_count': lamp_count,
            'rated_power_w': rated,
            'fixtures': [
                {
                    'fixture_uid': x.get('fixture_uid'),
                    'source_fixture_id': x.get('source_fixture_id'),
                    'road_name': x.get('road_name'),
                    'lamp_count': x.get('lamp_count'),
                    'lamp_watt': x.get('lamp_watt'),
                    'rated_power_w': x.get('rated_power_w'),
                    'latitude': x.get('latitude'),
                    'longitude': x.get('longitude'),
                }
                for x in fixtures
            ],
            'metadata': {
                'controller_type': c.get('controller_type'),
                'controller_link_status': c.get('controller_link_status', 'asset_only'),
                'address': c.get('address', ''),
            },
        }

        has_real_ami = False
        ami_payload = {
            'has_real_ami': has_real_ami,
            'ami_state': 'unlinked',
            'virtual_link_mode': 'scenario_injection',
            'ami_meter_id': None,
            'mapping_visibility': {
                'reason': '수영구 실제 AMI-분전함 공식 매핑 부재',
                'created_by': 'v0.2 scenario injection layer',
            },
        }

        detected = []
        anomaly_evidence = {
            'rule_ids': [],
            'payload': {
                'expected_drop_pct': None,
                'observed_max_activation': None,
                'deviation': None,
                'sunrise': expected_schedule['sunrise'],
            }
        }

        priority_score = 0.0
        priority_sev = 'low'

        if any(x.get('cabinet_uid') == cab_uid for x in targets):
            on_current = max(1.0, rated / 300.0)  # synthetic 전류 기반의 expected on current
            off_current = max(0.05, rated / 68000.0)
            on_anchor = (sun['sunrise_dt'] + timedelta(minutes=20))
            if on_anchor < base_date.replace(hour=9, minute=30):
                on_anchor = base_date.replace(hour=9, minute=30)
            scenario_start = on_anchor
            scenario_end = on_anchor + timedelta(minutes=SCENARIO_DURATION_MIN)
            scenario_id = stable_id('SCN', cab_uid, base_date.date().isoformat())

            injection_meter_id = stable_id('MI-V2', cab_uid)
            series = to_detection_sample_series(scenario_start, scenario_end, off_current, on_current)
            events = detect_daytime_events(series, off_current, on_current)
            for ev in events:
                ev['scenario_id'] = scenario_id
                ev['meter_id'] = injection_meter_id
            detected = events

            # expected/observed alignment check
            matched = bool(events)
            expected = {
                'expected_drop_pct': SCENARIO_DROP_PCT,
                'expected_start': scenario_start.strftime('%Y-%m-%d %H:%M'),
                'expected_end': scenario_end.strftime('%Y-%m-%d %H:%M'),
                'expected_duration_min': SCENARIO_DURATION_MIN,
            }
            if events:
                d = events[0]
                start_delta = abs((datetime.strptime(d['first_sample'], '%Y-%m-%d %H:%M') - scenario_start).total_seconds() / 60)
                end_delta = abs((datetime.strptime(d['last_sample'], '%Y-%m-%d %H:%M') - scenario_end).total_seconds() / 60)
                observed = {
                    'first_sample': d['first_sample'],
                    'last_sample': d['last_sample'],
                    'duration_min': d['estimated_duration_min'],
                    'max_activation': d['max_activation'],
                }
                priority_score = min(100.0, 22 + d['estimated_duration_min'] * 0.3 + 220 * d['max_activation'] + min(30.0, rated / 200.0))
                priority_sev = make_priority(priority_score)
                anomaly_evidence['rule_ids'] = ['daytime_partial_activation', 'post_sunrise_persistence_90m', 'scenario_injection']
                anomaly_evidence['payload'] = {
                    'expected': expected,
                    'observed': observed,
                    'start_delta_min': round(start_delta, 2),
                    'end_delta_min': round(end_delta, 2),
                }

            scenario_records.append({
                'scenario_id': scenario_id,
                'scenario_date': base_date.date().isoformat(),
                'cabinet_uid': cab_uid,
                'target_expected_drop_pct': SCENARIO_DROP_PCT,
                'target_duration_min': SCENARIO_DURATION_MIN,
                'target_start': expected['expected_start'],
                'target_end': expected['expected_end'],
                'detected_event_count': len(events),
                'detect_matched': matched,
            })

            scenarios.append({
                'scenario_id': scenario_id,
                'cabinet_uid': cab_uid,
                'cable': on_current,
                'injection_meter_id': injection_meter_id,
                'target_current_on': round(on_current * SCENARIO_DROP_PCT, 5),
                'simulated_series_len': len(series),
                'expected_start': expected['expected_start'],
                'expected_end': expected['expected_end'],
            })

        v02_objects.append({
            'cabinet_uid': cab_uid,
            'asset_info': asset_info,
            'expected_schedule': expected_schedule,
            'expected_load': {
                'rated_power_w': rated,
                'expected_rated_load_kW': round(rated / 1000.0, 3),
                'lamp_count': lamp_count,
                'fixture_rows': fixture_count,
            },
            'weather_context': weather_ctx,
            'ami': ami_payload,
            'detected_signals': detected,
            'anomaly_evidence': anomaly_evidence,
            'inspection_priority': {
                'score': round(priority_score, 2),
                'severity': priority_sev,
                'rank': None,
                'reason': '실제 AMI 없음: 시뮬레이션 주입 기반 검증' if has_real_ami is False else '실측 AMI 연동 대기',
            },
        })

    # ranking: higher priority score first
    ranked = sorted(v02_objects, key=lambda x: x['inspection_priority']['score'], reverse=True)
    for idx, v in enumerate(ranked, start=1):
        v['inspection_priority']['rank'] = idx

    return {
        'objects': ranked,
        'targets': sorted(x['cabinet_uid'] for x in targets),
        'stations': weather_stations,
        'stations_map': stations_map,
        'scenarios': scenarios,
        'scenario_records': scenario_records,
    }


def write_outputs(bundle):
    objects = bundle['objects']
    generated_at = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

    write_json(OUT / 'data' / 'suyeong_v02_objects.json', objects)
    write_json(OUT / 'data' / 'simulation_scenarios_v02.json', bundle['scenarios'])
    write_csv(OUT / 'data' / 'simulation_validation_results_v02.csv', bundle['scenario_records'])
    write_json(OUT / 'app_seed' / 'suyeong_v02_seed.json', {
        'generated_at': generated_at,
        'schema_version': 'lightguard-v0.2',
        'municipality': 'suyeong',
        'asset_count': len(objects),
        'target_mode': {
            'title': '수영구 AMI 미연결 + scenario injection',
            'description': '실제 AMI 연결 전제 미존재. 주입 시나리오로 Detector v0.2 동작 검증',
            'target_cabinets_3_4kw_like': bundle['targets'],
        },
        'objects': objects,
    })

    # station lookup table for app/debug
    station_rows = []
    for s in bundle['stations']:
        station_rows.append({
            'station_id': s['station_id'],
            'station_name': s['station_name'],
            'latitude': s['latitude'],
            'longitude': s['longitude'],
            'station_type': s.get('station_type', ''),
        })
    write_csv(OUT / 'data' / 'suyeong_weather_stations_v02.csv', station_rows)

    # keep light summary report
    detected = sum(1 for x in objects for y in x['detected_signals'])
    total_targets = len(bundle['targets'])
    success = sum(1 for r in bundle['scenario_records'] if r['detect_matched'])
    lines = [
        '# LightGuard v0.2 Validation (수영구 우선 v0.2 Flow)',
        '',
        f"- 생성 시각: {datetime.utcnow().replace(microsecond=0).isoformat()}Z",
        f"- 대상 지자체: 수영구",
        f"- 분전함: {len(objects)}개",
        f"- 3.4kW 기반 시나리오 주입 대상: {total_targets}개",
        f"- 시나리오 검출 이벤트: {detected}개",
        f"- 주입-검출 정합 성공: {success}/{len(bundle['scenario_records'])}",
        '',
        '## 이벤트 객체 형식(요약)',
        '- 구조: 분전함 → 자산정보(asset_info) → 예상점등시간(expected_schedule) → 정격부하(expected_load) → AMI(ami) → 근거(anomaly_evidence) → 점검우선순위(inspection_priority)',
        '- AMI는 현재 실제 매핑이 없으므로 모든 항목에서 `has_real_ami = false`로 명시',
        '- 시나리오 주입은 `scenario_injection` 모드로 추적됨',
        '',
        '## 점검우선순위 분포',
    ]

    sev_count = defaultdict(int)
    for o in objects:
        sev_count[o['inspection_priority']['severity']] += 1
    lines += [f"- {k}: {v}" for k, v in sorted(sev_count.items())]
    lines += ['','## Scenario 검증', '']

    for r in bundle['scenario_records']:
        lines.append(
            f"- {r['scenario_id']}: cabinet={r['cabinet_uid']}, "
            f"match={r['detect_matched']} ({r['detected_event_count']} events)"
        )

    (OUT / 'reports' / 'validation_report_v02.md').write_text('\n'.join(lines), encoding='utf-8')

    # zip package for easy delivery
    zip_path = ROOT / 'lightguard_v0_1_package_v02.zip'
    if zip_path.exists():
        zip_path.unlink()
    package_files = [
        OUT / 'data' / 'suyeong_v02_objects.json',
        OUT / 'data' / 'simulation_scenarios_v02.json',
        OUT / 'data' / 'simulation_validation_results_v02.csv',
        OUT / 'data' / 'suyeong_weather_stations_v02.csv',
        OUT / 'app_seed' / 'suyeong_v02_seed.json',
        OUT / 'reports' / 'validation_report_v02.md',
        OUT / 'README.md',
        OUT / 'source_manifest.json',
    ]
    with zipfile.ZipFile(
        zip_path,
        'w',
        compression=zipfile.ZIP_DEFLATED,
        allowZip64=True,
    ) as zf:
        for p in package_files:
            if p.exists() and p.is_file():
                zf.write(p, p.relative_to(OUT))

    # source manifest: lightweight track
    manifest = []
    for p in [OUT / 'data' / 'suyeong_v02_objects.json', OUT / 'data' / 'simulation_scenarios_v02.json', OUT / 'app_seed' / 'suyeong_v02_seed.json']:
        if not p.exists():
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        manifest.append({
            'file': p.name,
            'size_bytes': p.stat().st_size,
            'sha256': h,
            'purpose': 'v0.2_output',
        })
    write_json(OUT / 'source_manifest.json', manifest)


def main():
    inventory = build_inventory_and_scenarios()
    write_outputs(inventory)


if __name__ == '__main__':
    main()
