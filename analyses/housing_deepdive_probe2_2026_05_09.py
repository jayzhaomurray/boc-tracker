"""
Housing deep-dive probe part 2 — 2026-05-09

1. Fetch recent data from V80691335 and V122514 (mortgage rate candidates)
2. Fetch recent data from FVI_CREA_HOUSE_RESALE_INDEXED_CANADA and SNLR series
3. getCubeMetadata for Table 34-10-0158 with correct product ID (34100158)
4. Post-probe vectors near v52300157 for under-construction and CMA starts
"""

import json
import requests
import pandas as pd
from pathlib import Path

OUT = Path(__file__).parent / "housing_deepdive_probe2_results_2026_05_09.md"
lines = []

def log(s=""):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", errors="replace").decode("ascii"))
    lines.append(s)


# ── 1. Valet series data samples ───────────────────────────────────────────────

log("# Housing Deep-Dive Probe 2 -- 2026-05-09")
log()
log("## 1. Valet data samples for mortgage/CREA candidates")
log()

SAMPLE_KEYS = {
    "V80691335": "mortgage rate candidate (val ~6.09)",
    "V122514": "unknown (val ~2.24)",
    "BROKER_AVERAGE_5YR_VRM": "broker avg 5yr variable rate",
    "FVI_CREA_HOUSE_RESALE_INDEXED_CANADA": "CREA resales (indexed)",
    "FVI_CREA_HOUSE_SALES_TO_NEW_LISTINGS_CANADA": "CREA SNLR",
}

for key, desc in SAMPLE_KEYS.items():
    url = f"https://www.bankofcanada.ca/valet/observations/{key}/json"
    try:
        r = requests.get(url, params={"start_date": "2023-01-01"}, timeout=15)
        if r.status_code == 200:
            payload = r.json()
            obs = payload.get("observations", [])
            total = len(payload.get("observations", []))
            # Show last 5 data points
            recent = obs[-5:] if len(obs) >= 5 else obs
            log(f"  {key} ({desc}): {total} total obs since 2023")
            for o in recent:
                raw = o.get(key, {})
                val = raw.get("v", raw) if isinstance(raw, dict) else raw
                log(f"    {o.get('d','?')}: {val}")
        else:
            log(f"  {key}: HTTP {r.status_code}")
    except Exception as e:
        log(f"  {key}: ERROR {e}")
    log()


# ── 2. V80691335 full series label from Valet ──────────────────────────────────

log("## 2. V80691335 series metadata from Valet")
log()

try:
    r = requests.get("https://www.bankofcanada.ca/valet/series/V80691335/json", timeout=15)
    if r.status_code == 200:
        log(json.dumps(r.json(), indent=2)[:2000])
    else:
        log(f"HTTP {r.status_code}")
except Exception as e:
    log(f"ERROR: {e}")
log()

log("## 2b. V122514 series metadata from Valet")
log()
try:
    r = requests.get("https://www.bankofcanada.ca/valet/series/V122514/json", timeout=15)
    if r.status_code == 200:
        log(json.dumps(r.json(), indent=2)[:2000])
    else:
        log(f"HTTP {r.status_code}")
except Exception as e:
    log(f"ERROR: {e}")
log()


# ── 3. StatsCan Table 34-10-0158 -- correct product ID ─────────────────────────

log("## 3. StatsCan getCubeMetadata -- product ID 34100158")
log()

for pid in [34100158, 3410015801, 341001580, 34100158001]:
    try:
        url = f"https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata/{pid}"
        r = requests.get(url, timeout=30)
        log(f"  getCubeMetadata({pid}): HTTP {r.status_code}")
        if r.status_code == 200:
            meta = r.json()
            if meta.get("status") == "SUCCESS":
                cube_obj = meta.get("object", {})
                dims = cube_obj.get("dimension", [])
                log(f"  SUCCESS -- {len(dims)} dimensions")
                for i, dim in enumerate(dims):
                    dim_name = dim.get("dimensionNameEn", "?")
                    members = dim.get("member", [])
                    log(f"    Dim {i+1}: {dim_name} ({len(members)} members)")
                    for m in members[:30]:
                        log(f"      [{m.get('memberId','?')}] {m.get('memberNameEn','?')}")
                    if len(members) > 30:
                        log(f"      ... +{len(members)-30} more")
                break
            else:
                log(f"  status={meta.get('status')}")
    except Exception as e:
        log(f"  getCubeMetadata({pid}): ERROR {e}")
log()


# ── 4. POST probe: data for candidate under-construction and CMA starts vectors ─

log("## 4. POST probe: candidate under-construction and CMA starts vectors")
log()
log("Using getDataFromVectorsAndLatestNPeriods (POST) to fetch 3 data points each.")
log()

BASE_URL = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"

# Try batches of candidate vectors
# v52300157 = Canada total starts
# Under construction likely in a different range within the same table
# Try some other candidate ranges known from CMHC/StatsCan housing data
CANDIDATE_BATCHES = [
    # batch: list of vector IDs to try
    list(range(52300157, 52300180)),  # sequential from housing_starts
    # Try the CMHC housing data vectors around housing_starts predecessor tables
    [2054553, 2054554, 2054555, 2054556, 2054557, 2054558, 2054559, 2054560, 2054561, 2054562,
     2054563, 2054564, 2054565, 2054566, 2054567, 2054568, 2054569, 2054570],
    # Try vectors in the 35M range often used for building permits / construction
    [35012345, 35012346, 35012347, 35012348, 35012349, 35012350],
]

# Actually, let me try a known approach: search the Valet series list for housing starts
log("First checking BoC Valet for housing-under-construction series...")
try:
    r = requests.get("https://www.bankofcanada.ca/valet/lists/series/json", timeout=30)
    r.raise_for_status()
    series_dict = r.json().get("series", {})
    # Search for housing/construction in FVI or housing series
    housing_keys = {k: v for k, v in series_dict.items()
                    if "CONSTRUCTION" in k.upper() or "UNDER_CONS" in k.upper()
                    or ("HOUS" in k.upper() and "UNDER" in str(v).upper())
                    or "FVI_HOUS" in k.upper()}
    log(f"  Housing/construction keys ({len(housing_keys)} found):")
    for k in sorted(housing_keys.keys()):
        v = housing_keys[k]
        label = v.get("label", str(v)[:80]) if isinstance(v, dict) else str(v)[:80]
        log(f"    {k}: {label}")
    log()
except Exception as e:
    log(f"  ERROR: {e}")

# Now try the POST batch for the sequential range near v52300157
log("Trying sequential vectors near v52300157 via POST...")
for vid in range(52300157, 52300200, 10):
    batch = list(range(vid, min(vid + 10, 52300200)))
    body = [{"vectorId": v, "latestN": 2} for v in batch]
    try:
        r = requests.post(BASE_URL, json=body, timeout=20)
        if r.status_code == 200:
            results = r.json()
            for item in results:
                status = item.get("status", "?")
                if status == "SUCCESS":
                    obj = item.get("object", {})
                    vid2 = obj.get("vectorId") or obj.get("VectorId")
                    pts = obj.get("vectorDataPoint", [])
                    latest = pts[-1] if pts else {}
                    val = latest.get("value", "?")
                    ref = latest.get("refPer", "?")
                    # Try to get series info from within the response
                    series_name = obj.get("SeriesTitleEn") or obj.get("seriesTitleEn") or ""
                    log(f"  v{vid2}: {series_name[:60]} latest={ref} val={val}")
                # else silently skip failures
        else:
            log(f"  Batch {vid}-{vid+9}: HTTP {r.status_code}")
    except Exception as e:
        log(f"  Batch {vid}-{vid+9}: ERROR {e}")
log()


# ── 5. Try getSeriesInfoFromVector with POST (not GET) ─────────────────────────

log("## 5. getSeriesInfoFromVector via POST")
log()

# Some StatsCan endpoints accept POST with a JSON array
try:
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromVector"
    body = [52300157, 52300158, 52300159, 52300160, 52300161]
    r = requests.post(url, json=body, timeout=20)
    log(f"POST getSeriesInfoFromVector: HTTP {r.status_code}")
    if r.status_code == 200:
        resp = r.json()
        log(json.dumps(resp, indent=2)[:3000])
except Exception as e:
    log(f"ERROR: {e}")
log()


# ── Write report ───────────────────────────────────────────────────────────────

report = "\n".join(lines)
OUT.write_text(report, encoding="utf-8")
print(f"\nReport written to {OUT}")
