#!/usr/bin/env python3
"""Census and download approval-free municipal lighting file data from Data.go.kr."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import certifi

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "official_docs" / "external_data" / "nationwide_v24"
DATA = ROOT / "lightguard_v0_1" / "data" / "validation" / "v24"
REPORT = ROOT / "lightguard_v0_1" / "reports" / "v24"
APP_DATA = ROOT / "lightguard_app" / "assets" / "data" / "context"
APP_GENERATED = ROOT / "lightguard_app" / "lib" / "generated"
SEARCH_URL = "https://www.data.go.kr/tcs/dss/selectDataSetList.do"
DETAIL = "https://www.data.go.kr/data/{dataset_id}/fileData.do"
QUERIES = ("가로등", "보안등", "도로조명", "스마트보안등", "가로등 분전함", "가로등 유지보수")
TITLE_INCLUDE = re.compile(r"가로등|보안등|도로조명|스마트보안등|조명시설|분전함")
TITLE_EXCLUDE = re.compile(r"교통신호|신호등|전광판|광고|채용|예산|계약현황")
TOP_LEVEL = (
    "서울특별시", "부산광역시", "대구광역시", "인천광역시",
    "대전광역시", "울산광역시", "세종특별자치시", "경기도", "강원특별자치도",
    "충청북도", "충청남도", "전북특별자치도", "전남광주통합특별시", "경상북도",
    "경상남도", "제주특별자치도",
)
SHORT_TOP = {
    "서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시",
    "인천": "인천광역시", "광주": "전남광주통합특별시", "전남": "전남광주통합특별시",
    "대전": "대전광역시",
    "울산": "울산광역시", "세종": "세종특별자치시", "제주": "제주특별자치도",
}
NON_MUNICIPAL_MARKERS = ("지식재산처", "한국도로공사", "한국수력원자력", "지방공사")
USER_AGENT = "LightGuard-Nationwide-Census/1.0 (public file-data research)"
TLS_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def fetch(url: str, timeout: int = 30, attempts: int = 3) -> bytes:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(
                request, timeout=timeout, context=TLS_CONTEXT
            ) as response:
                return response.read()
        except Exception as exc:  # pragma: no cover - network-dependent retry
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def search_url(query: str, page: int) -> str:
    return SEARCH_URL + "?" + urllib.parse.urlencode({
        "dType": "FILE", "keyword": query, "currentPage": page
    })


def clean_markup(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()


def parse_search(body: bytes) -> tuple[int, dict[str, str]]:
    text = body.decode("utf-8", errors="replace")
    count_match = re.search(r"파일데이터\s*<span>.*?\(([\d,]+)건\)", text, re.S)
    count = int(count_match.group(1).replace(",", "")) if count_match else 0
    entries = {}
    for dataset_id, title_html in re.findall(
        r'<a\s+href="/data/(\d+)/fileData\.do">(.*?)</a>', text, re.S
    ):
        title = clean_markup(title_html)
        if TITLE_INCLUDE.search(title) and not TITLE_EXCLUDE.search(title):
            entries[dataset_id] = title
    return count, entries


def discover() -> tuple[dict[str, str], dict[str, int]]:
    candidates: dict[str, str] = {}
    query_counts: dict[str, int] = {}
    for query in QUERIES:
        first = fetch(search_url(query, 1))
        total, first_entries = parse_search(first)
        query_counts[query] = total
        candidates.update(first_entries)
        pages = max(1, math.ceil(total / 10))
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(fetch, search_url(query, page)) for page in range(2, pages + 1)]
            for future in as_completed(futures):
                _, entries = parse_search(future.result())
                candidates.update(entries)
    return candidates, query_counts


def region_from_title(title: str) -> dict[str, str | None]:
    normalized = re.sub(r"[_·]", " ", title)
    normalized = normalized.replace("광주광역시", "전남광주통합특별시")
    normalized = normalized.replace("전라남도", "전남광주통합특별시")
    top = next((name for name in TOP_LEVEL if name in normalized), None)
    short_prefix = None
    if top is None:
        short_match = next(
            ((key, value) for key, value in SHORT_TOP.items() if normalized.startswith(key)),
            None,
        )
        if short_match:
            short_prefix, top = short_match

    # Accept only a standalone municipality immediately following its top-level
    # region. This recognizes one-syllable districts (남구, 중구, 동구, 북구,
    # 서구) without treating product words such as 도로조명시스템 as a city.
    if top and top in normalized:
        tail = normalized.split(top, 1)[1].strip()
    elif top and short_prefix:
        tail = normalized[len(short_prefix):].strip()
    else:
        tail = normalized.strip()
    local_match = re.match(r"([가-힣]+(?:시|군|구))(?:\s|$)", tail)
    local_matches = [local_match.group(1)] if local_match else []
    blocked = {"광역시", "특별시", "자치시", "도시", "관리시", "표시"}
    locals_clean = [value for value in local_matches if value not in blocked and value not in (top or "")]
    local = locals_clean[0] if locals_clean else None
    if top and local:
        label = f"{top} {local}"
    elif top:
        label = top
    elif local:
        label = local
    else:
        label = title.split("_")[0].strip()
    status = "NORMALIZED" if top or local else "NEEDS_REVIEW"
    return {"region": label, "top_level": top, "local": local, "region_status": status}


def is_municipal_scope(item: dict) -> bool:
    title = item.get("title", "")
    if any(marker in title for marker in NON_MUNICIPAL_MARKERS):
        return False
    return item.get("region_status") == "NORMALIZED"


def detail(dataset_id: str, fallback_title: str) -> dict:
    url = DETAIL.format(dataset_id=dataset_id)
    try:
        raw = fetch(url)
        text = raw.decode("utf-8", errors="replace")
        subject = re.search(r'const subject = "([^"]+)"', text)
        title = html.unescape(subject.group(1)).strip() if subject else fallback_title
        content = re.search(r'"contentUrl"\s*:\s*"([^"]+)"', text)
        encoding = re.search(r'"encodingFormat"\s*:\s*"([^"]+)"', text)
        modified = re.search(r'"dateModified"\s*:\s*"([^"]+)"', text)
        publisher = re.search(
            r'"publisher"\s*:\s*\{.*?"name"\s*:\s*"([^"]+)"', text, re.S
        )
        license_name = re.search(r'"license"\s*:\s*"([^"]+)"', text)
        external = re.search(r"제공데이터URL기재.*?URL.*?(https?://[^<\s]+)", text, re.S)
        return {
            "dataset_id": dataset_id,
            "title": title,
            "official_url": url,
            "content_url": html.unescape(content.group(1)) if content else None,
            "encoding_format": encoding.group(1).upper() if encoding else None,
            "date_modified": modified.group(1) if modified else None,
            "publisher": html.unescape(publisher.group(1)) if publisher else None,
            "license": html.unescape(license_name.group(1)) if license_name else None,
            "external_url": html.unescape(external.group(1)) if external else None,
            "detail_status": "OK",
            **region_from_title(title),
        }
    except Exception as exc:
        return {
            "dataset_id": dataset_id, "title": fallback_title, "official_url": url,
            "content_url": None, "encoding_format": None, "external_url": None,
            "detail_status": f"ERROR:{type(exc).__name__}", **region_from_title(fallback_title),
        }


def safe_filename(item: dict) -> str:
    return f"{item['dataset_id']}.csv"


def decode_csv(raw: bytes) -> tuple[list[str], int, str]:
    if raw.startswith(b"\xff\xd8\xff") or raw.startswith(b"\x89PNG") or raw.startswith(b"PK\x03\x04"):
        raise ValueError("NON_CSV_MAGIC")
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        reader = csv.reader(text.splitlines())
        try:
            header = [value.strip() for value in next(reader)]
        except StopIteration:
            raise ValueError("EMPTY_CSV")
        rows = sum(1 for row in reader if any(value.strip() for value in row))
        if not header or rows == 0:
            raise ValueError("EMPTY_CSV")
        return header, rows, encoding
    raise ValueError("UNKNOWN_ENCODING")


def roles(header: list[str]) -> list[str]:
    joined = "|".join(header).lower()
    found = []
    contracts = {
        "SIGNAL": r"전력|전류|전압|점등상태|소등상태|램프고장|누전|이상점등|깜빡",
        "OPERATIONS": r"접수일|처리일|고장|민원|유지보수|보수|수리|조치|작업시작",
        "CABINET": r"분전함|제어함|배전함",
        "LOAD": r"정격|용량|와트|watt|등용량",
        "SPATIAL": r"위도|경도|좌표|주소|소재지|설치위치",
        "ASSET": r"관리번호|가로등번호|보안등번호|표찰|등주|등수|등기구|광원|설치일",
    }
    for role, pattern in contracts.items():
        if re.search(pattern, joined, re.I):
            found.append(role)
    return found


def acquire(item: dict) -> dict:
    result = dict(item)
    result["municipal_scope"] = is_municipal_scope(item)
    content_url = item.get("content_url")
    fmt = item.get("encoding_format") or ""
    if not content_url:
        result["acquisition_status"] = "EXTERNAL_OR_NO_DIRECT_FILE"
        result["roles"] = []
        return result
    if "data.go.kr/cmm/cmm/fileDownload.do" not in content_url:
        result["acquisition_status"] = "NON_PORTAL_DIRECT_FILE"
        result["roles"] = []
        return result
    if "CSV" not in fmt:
        result["acquisition_status"] = f"NON_CSV:{fmt or 'UNKNOWN'}"
        result["roles"] = []
        return result
    try:
        path = RAW / safe_filename(item)
        raw = path.read_bytes() if path.exists() else fetch(content_url, timeout=60)
        header, rows, encoding = decode_csv(raw)
        RAW.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        result.update({
            "acquisition_status": "DOWNLOADED_ANALYZABLE",
            "raw_filename": path.name,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
            "encoding": encoding,
            "rows": rows,
            "column_count": len(header),
            "schema_fingerprint": hashlib.sha256("|".join(header).encode()).hexdigest(),
            "roles": roles(header),
            "tracked_in_git": False,
        })
        if not result["roles"]:
            result["acquisition_status"] = "DOWNLOADED_NOT_EVALUABLE_SCHEMA"
        return result
    except Exception as exc:
        result["acquisition_status"] = f"INVALID_FILE:{exc}"
        result["roles"] = []
        return result


def public_item(item: dict) -> dict:
    allowed = (
        "dataset_id", "title", "official_url", "encoding_format", "region", "top_level",
        "local", "region_status", "detail_status", "acquisition_status", "raw_filename",
        "sha256", "byte_size", "encoding", "rows", "column_count", "schema_fingerprint",
        "roles", "tracked_in_git", "municipal_scope", "date_modified", "publisher", "license",
    )
    return {key: item.get(key) for key in allowed if key in item}


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    candidates, query_counts = discover()
    with ThreadPoolExecutor(max_workers=8) as pool:
        details = list(pool.map(lambda pair: detail(*pair), candidates.items()))
    with ThreadPoolExecutor(max_workers=6) as pool:
        acquired = list(pool.map(acquire, details))
    acquired.sort(key=lambda item: (item.get("region") or "", item["dataset_id"]))

    public = [public_item(item) for item in acquired]
    analyzable = [item for item in public if item.get("acquisition_status") == "DOWNLOADED_ANALYZABLE"]
    municipal_analyzable = [item for item in analyzable if item.get("municipal_scope")]
    regions = sorted({item["region"] for item in municipal_analyzable})
    top_levels = sorted({item["top_level"] for item in municipal_analyzable if item.get("top_level")})
    role_counts = {role: sum(role in item.get("roles", []) for item in analyzable) for role in ("SIGNAL", "OPERATIONS", "CABINET", "LOAD", "SPATIAL", "ASSET")}
    status_counts = {}
    for item in public:
        status = item.get("acquisition_status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
    result = {
        "version": "0.24",
        "census_frame": "Data.go.kr public FILE search pages",
        "queries": list(QUERIES),
        "query_result_counts_before_deduplication": query_counts,
        "unique_candidates": len(public),
        "analyzable_datasets": len(analyzable),
        "municipal_analyzable_datasets": len(municipal_analyzable),
        "analyzable_region_labels": regions,
        "analyzable_region_count": len(regions),
        "represented_top_level_regions": top_levels,
        "current_top_level_region_count": len(TOP_LEVEL),
        "missing_top_level_regions": sorted(set(TOP_LEVEL) - set(top_levels)),
        "role_counts": role_counts,
        "status_counts": dict(sorted(status_counts.items())),
        "claim_boundary": "Nationwide public-file schema census, not nationwide AMI accuracy or field-fault truth.",
        "raw_values_exported": False,
        "new_predictive_tuning": 0,
        "datasets": public,
    }
    output = DATA / "v24_nationwide_file_census.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    APP_DATA.mkdir(parents=True, exist_ok=True)
    (APP_DATA / "v24_nationwide_file_census.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    APP_GENERATED.mkdir(parents=True, exist_ok=True)
    (APP_GENERATED / "v24_census_summary.dart").write_text(
        "// GENERATED CODE - DO NOT EDIT.\n"
        "// Generated by scripts/build_v24_nationwide_census.py.\n\n"
        "abstract final class V24CensusSummary {\n"
        f"  static const representedTopLevelCount = {len(top_levels)};\n"
        f"  static const currentTopLevelCount = {len(TOP_LEVEL)};\n"
        f"  static const analyzableRegionCount = {len(regions)};\n"
        f"  static const municipalDatasetCount = {len(municipal_analyzable)};\n"
        "}\n",
        encoding="utf-8",
    )

    rows_by_region = {}
    for item in municipal_analyzable:
        rows_by_region.setdefault(item["region"], []).append(item)
    lines = [
        "# LightGuard v0.24 Nationwide Municipal File-Data Census", "",
        "## Census result", "",
        f"- Unique file candidates: {len(public):,}",
        f"- Downloaded analyzable CSV datasets: {len(analyzable):,}",
        f"- Municipal-scope analyzable CSV datasets: {len(municipal_analyzable):,}",
        f"- Analyzable region labels: {len(regions):,}",
        f"- Represented top-level regions: {len(top_levels):,} / {len(TOP_LEVEL)}", "",
        "## Role counts", "",
    ]
    lines.extend(f"- {role}: {count:,}" for role, count in role_counts.items())
    lines.extend(["", "## Analyzable regions", ""])
    for region, items in sorted(rows_by_region.items()):
        combined_roles = sorted({role for item in items for role in item.get("roles", [])})
        total_rows = sum(item.get("rows", 0) for item in items)
        lines.append(f"- {region}: {len(items)} dataset(s), {total_rows:,} rows, {', '.join(combined_roles)}")
    lines.extend([
        "", "## Boundaries", "",
        "- The current 16 top-level frame reflects the Jeonnam-Gwangju Special Metropolitan City launched on 2026-07-01.",
        "- Central-government and public-corporation files remain in schema totals but are excluded from municipal coverage.",
        "- Portal search coverage is a reproducible public-file census, not proof that every municipality publishes a file.",
        "- External-link, non-CSV, invalid, and non-evaluable sources remain explicit gaps.",
        "- Raw identifiers, addresses, coordinates, and free text are not exported to tracked artifacts.",
        "- No result is municipal AMI ground truth, nationwide detector accuracy, or realized operational benefit.", "",
    ])
    (REPORT / "v24_nationwide_file_census.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "status": "BUILT", "candidates": len(public), "analyzable": len(analyzable),
        "municipal_analyzable": len(municipal_analyzable), "regions": len(regions),
        "top_levels": len(top_levels), "status_counts": result["status_counts"]
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"v24 census failed: {exc}", file=sys.stderr)
        raise
