"""
Final comprehensive probe for 6 StatsCan tables.
Uses getCubeMetadata (8-digit PIDs) + getSeriesInfoFromVector + getDataFromVectors.
"""

import requests
import time
import json

OUTPUT = "analyses/statcan_probe_results_2026_05_10.md"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
}
BASE = "https://www150.statcan.gc.ca/t1/wds/rest"


def cube_meta(pid):
    r = requests.post(
        f"{BASE}/getCubeMetadata",
        json=[{"productId": pid}],
        headers=headers,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()[0]


def series_info(vid):
    r = requests.post(
        f"{BASE}/getSeriesInfoFromVector",
        json=[{"vectorId": vid}],
        headers=headers,
        timeout=20,
    )
    r.raise_for_status()
    return r.json()[0]


def fetch_pts(vid, n=3):
    r = requests.post(
        f"{BASE}/getDataFromVectorsAndLatestNPeriods",
        json=[{"vectorId": vid, "latestN": n}],
        headers=headers,
        timeout=20,
    )
    r.raise_for_status()
    item = r.json()[0]
    if item.get("status") != "SUCCESS":
        return []
    return [(p["refPer"], p["value"]) for p in item["object"]["vectorDataPoint"]]


def get_all_vectors_from_cube(pid):
    """Use getAllSeriesInfoFromCube endpoint to get all vectors in a table."""
    r = requests.get(
        f"{BASE}/getAllSeriesInfoFromCube/{pid}",
        headers=headers,
        timeout=60,
    )
    if r.status_code != 200:
        return None
    try:
        return r.json()
    except Exception:
        return None


lines = []


def w(s=""):
    lines.append(s + "\n")


# Header
w("# StatsCan 6-Table Probe Results")
w("**Date:** 2026-05-10")
w()
w("API: WDS REST — getCubeMetadata, getSeriesInfoFromVector, getDataFromVectorsAndLatestNPeriods")
w()

confirmed_all = []

# =============================================================
# Helper: scan vector range and return matches by keyword
# =============================================================
def scan_vectors(start, end, keywords, table_id, label, step=1):
    found = []
    for vid in range(start, end + 1, step):
        try:
            info = series_info(vid)
            if info.get("status") == "SUCCESS":
                obj = info["object"]
                title = obj.get("SeriesTitleEn") or ""
                pid_found = obj.get("productId")
                freq = obj.get("frequencyCode")
                tl = title.lower()
                if any(k.lower() in tl for k in keywords):
                    pts = fetch_pts(vid, 3)
                    recent = pts and pts[-1][0] >= "2024"
                    print(f"  V{vid}: {title[:70]} | recent={recent}")
                    if recent:
                        found.append({
                            "vid": vid,
                            "title": title,
                            "freq": freq,
                            "pts": pts,
                            "table": table_id,
                            "label": label,
                        })
                    time.sleep(0.1)
        except Exception:
            pass
        time.sleep(0.05)
    return found


# =============================================================
# TABLE 1: Capacity utilization — 34-10-0035-01
# Best matching product: 16100109 (Industrial cap util, quarterly)
#   Dim1: Geography (Canada=1), Dim2: NAICS industries
#   Total industrial = member 1, Manufacturing = member 8
# Also: 16100012 (Manufacturing cap util by NAICS, quarterly)
#   Dim1: Geography (Canada=1), Dim2: NAICS, Dim3: Principal stats (CU rate=1)
#   Manufacturing = member 1
# =============================================================
w("---")
w()
w("## Table 1: 34-10-0035-01 — Capacity Utilization, Total Manufacturing, Canada")
w()
print("TABLE 1: Capacity utilization")

# getCubeMetadata
for pid, name in [(16100109, "Industrial cap util"), (16100012, "Manufacturing cap util")]:
    try:
        meta = cube_meta(pid)
        if meta.get("status") == "SUCCESS":
            obj = meta["object"]
            w(f"### getCubeMetadata pid={pid}: **SUCCESS**")
            w(f"Title: {obj.get('cubeTitleEn', 'N/A')}")
            w(f"Freq: {obj.get('freq', 'N/A')}")
            dims = obj.get("dimension", [])
            for di, dim in enumerate(dims, 1):
                dname = dim.get("dimensionNameEn", "")
                members = [(m.get("memberId"), m.get("memberNameEn", "")) for m in dim.get("member", [])]
                w(f"**Dim{di}: {dname}**")
                for mid, mname in members[:30]:
                    w(f"  [{mid}] {mname}")
                w()
    except Exception as e:
        w(f"getCubeMetadata pid={pid}: ERROR — {e}")
    time.sleep(0.3)

# For capacity utilization, use getAllSeriesInfoFromCube on 16100109
w("### Vector scan (getAllSeriesInfoFromCube on pid=16100109)")
print("  Trying getAllSeriesInfoFromCube on 16100109...")
all_series_16100109 = get_all_vectors_from_cube(16100109)
cu_confirmed = []
if all_series_16100109 and isinstance(all_series_16100109, list):
    w(f"getAllSeriesInfoFromCube returned {len(all_series_16100109)} series")
    for item in all_series_16100109:
        s = item.get("status", "?")
        if s == "SUCCESS":
            obj = item.get("object", {})
            title = obj.get("SeriesTitleEn") or ""
            vid = obj.get("vectorId")
            freq = obj.get("frequencyCode")
            tl = title.lower()
            if "canada" in tl and ("total industrial" in tl or "manufacturing" in tl):
                pts = fetch_pts(int(vid), 3)
                print(f"  V{vid}: {title[:70]} pts={pts}")
                w(f"**V{vid}**: {title}")
                w(f"  Freq: {freq}")
                w(f"  Latest 3: {pts}")
                if pts and pts[-1][0] >= "2024":
                    w("  **CONFIRMED — recent data**")
                    cu_confirmed.append({
                        "vid": int(vid), "title": title, "freq": freq,
                        "pts": pts, "table": "34-10-0035-01",
                        "label": "Capacity utilization, " + title
                    })
                time.sleep(0.2)
        w()
else:
    w(f"getAllSeriesInfoFromCube: failed or empty (type={type(all_series_16100109)})")
    # Fallback: scan vector range
    w("Fallback: scanning vector range for capacity utilization keywords...")
    print("  Scanning vector range 81819-81870 for capacity utilization...")
    cu_confirmed = scan_vectors(81819, 81870, ["canada", "capacity", "manufactur"], "34-10-0035-01", "capacity utilization")

# Also try for 16100012
w("### Vector scan (getAllSeriesInfoFromCube on pid=16100012)")
print("  Trying getAllSeriesInfoFromCube on 16100012...")
all_series_16100012 = get_all_vectors_from_cube(16100012)
if all_series_16100012 and isinstance(all_series_16100012, list):
    w(f"getAllSeriesInfoFromCube returned {len(all_series_16100012)} series")
    for item in all_series_16100012:
        s = item.get("status", "?")
        if s == "SUCCESS":
            obj = item.get("object", {})
            title = obj.get("SeriesTitleEn") or ""
            vid = obj.get("vectorId")
            freq = obj.get("frequencyCode")
            tl = title.lower()
            if "canada" in tl and "manufactur" in tl:
                pts = fetch_pts(int(vid), 3)
                print(f"  V{vid}: {title[:70]} pts={pts}")
                w(f"**V{vid}**: {title}")
                w(f"  Freq: {freq}")
                w(f"  Latest 3: {pts}")
                if pts and pts[-1][0] >= "2024":
                    w("  **CONFIRMED — recent data**")
                    cu_confirmed.append({
                        "vid": int(vid), "title": title, "freq": freq,
                        "pts": pts, "table": "34-10-0035-01",
                        "label": "Capacity utilization, " + title
                    })
                time.sleep(0.2)
        w()
else:
    w(f"getAllSeriesInfoFromCube pid=16100012: failed")

confirmed_all.extend(cu_confirmed)

# =============================================================
# TABLE 2: EI regular beneficiaries — 14-10-0022-01
# Best matching product: 14100011 (EI regular benefits, province, monthly SA)
# Dim1=Geography(Canada=1), Dim2=Beneficiary detail(Regular=2), Dim3=Sex(Both=1), Dim4=Age(15+=1)
# =============================================================
w("---")
w()
w("## Table 2: 14-10-0022-01 — EI Regular Beneficiaries, Canada, Monthly SA")
w()
print("\nTABLE 2: EI regular beneficiaries")

try:
    meta = cube_meta(14100011)
    if meta.get("status") == "SUCCESS":
        obj = meta["object"]
        w(f"### getCubeMetadata pid=14100011: **SUCCESS**")
        w(f"Title: {obj.get('cubeTitleEn', 'N/A')}")
        dims = obj.get("dimension", [])
        for di, dim in enumerate(dims, 1):
            dname = dim.get("dimensionNameEn", "")
            members = [(m.get("memberId"), m.get("memberNameEn", "")) for m in dim.get("member", [])]
            w(f"**Dim{di}: {dname}**")
            for mid, mname in members:
                w(f"  [{mid}] {mname}")
            w()
except Exception as e:
    w(f"getCubeMetadata pid=14100011: ERROR — {e}")
time.sleep(0.3)

w("### Vector scan (getAllSeriesInfoFromCube on pid=14100011)")
print("  Trying getAllSeriesInfoFromCube on 14100011...")
all_series_ei = get_all_vectors_from_cube(14100011)
ei_confirmed = []
if all_series_ei and isinstance(all_series_ei, list):
    w(f"getAllSeriesInfoFromCube returned {len(all_series_ei)} series")
    for item in all_series_ei:
        s = item.get("status", "?")
        if s == "SUCCESS":
            obj = item.get("object", {})
            title = obj.get("SeriesTitleEn") or ""
            vid = obj.get("vectorId")
            freq = obj.get("frequencyCode")
            tl = title.lower()
            # Canada + regular benefits + both sexes + 15+
            if ("canada" in tl and "regular" in tl and
                    ("both sexes" in tl or "15 years" in tl)):
                pts = fetch_pts(int(vid), 3)
                print(f"  V{vid}: {title[:70]} pts={pts}")
                w(f"**V{vid}**: {title}")
                w(f"  Freq: {freq}")
                w(f"  Latest 3: {pts}")
                if pts and pts[-1][0] >= "2024":
                    w("  **CONFIRMED — recent data**")
                    ei_confirmed.append({
                        "vid": int(vid), "title": title, "freq": freq,
                        "pts": pts, "table": "14-10-0022-01",
                        "label": "EI regular beneficiaries, Canada, Both sexes, 15+, SA"
                    })
                time.sleep(0.2)
        w()
else:
    w(f"getAllSeriesInfoFromCube: failed — {type(all_series_ei)}")
    # Fallback: known vectors from similar EI probes
    w("Fallback: probe known EI vector ranges...")
    print("  Probing EI vector candidates directly...")
    ei_candidates = list(range(1406516, 1406530)) + list(range(1800695, 1800710))
    for vid in ei_candidates:
        try:
            info = series_info(vid)
            if info.get("status") == "SUCCESS":
                obj = info["object"]
                title = obj.get("SeriesTitleEn") or ""
                freq = obj.get("frequencyCode")
                tl = title.lower()
                w(f"V{vid}: {title}")
                if "canada" in tl and "regular" in tl:
                    pts = fetch_pts(vid, 3)
                    w(f"  Latest 3: {pts}")
                    if pts and pts[-1][0] >= "2024":
                        w("  **CONFIRMED**")
                        ei_confirmed.append({
                            "vid": vid, "title": title, "freq": freq,
                            "pts": pts, "table": "14-10-0022-01",
                            "label": "EI regular beneficiaries"
                        })
                    time.sleep(0.15)
        except Exception:
            pass
        time.sleep(0.05)
        w()

confirmed_all.extend(ei_confirmed)

# =============================================================
# TABLE 3: Merchandise trade — 12-10-0011-01
# Product: 12100011 (confirmed working, monthly)
# Dim1=Geography(Canada=1), Dim2=Trade(Import=1,Export=2,Balance=3)
# Dim3=Basis(Customs=1), Dim4=SeasonalAdj(SA=2), Dim5=Partner(All=1,US=2)
# =============================================================
w("---")
w()
w("## Table 3: 12-10-0011-01 — Merchandise Trade, Canada-US Bilateral")
w()
print("\nTABLE 3: Merchandise trade")

try:
    meta = cube_meta(12100011)
    if meta.get("status") == "SUCCESS":
        obj = meta["object"]
        w(f"### getCubeMetadata pid=12100011: **SUCCESS**")
        w(f"Title: {obj.get('cubeTitleEn', 'N/A')}")
        dims = obj.get("dimension", [])
        for di, dim in enumerate(dims, 1):
            dname = dim.get("dimensionNameEn", "")
            members = [(m.get("memberId"), m.get("memberNameEn", "")) for m in dim.get("member", [])]
            w(f"**Dim{di}: {dname}**")
            for mid, mname in members[:15]:
                w(f"  [{mid}] {mname}")
            w()
except Exception as e:
    w(f"getCubeMetadata pid=12100011: ERROR — {e}")
time.sleep(0.3)

w("### Vector scan (getAllSeriesInfoFromCube on pid=12100011)")
print("  Trying getAllSeriesInfoFromCube on 12100011...")
all_series_trade = get_all_vectors_from_cube(12100011)
trade_confirmed = []
if all_series_trade and isinstance(all_series_trade, list):
    w(f"getAllSeriesInfoFromCube returned {len(all_series_trade)} series")
    target_patterns = [
        ("canada;export;customs;seasonally adjusted;united states", "Canada, Exports, Customs, SA, US"),
        ("canada;import;customs;seasonally adjusted;united states", "Canada, Imports, Customs, SA, US"),
        ("canada;trade balance;customs;seasonally adjusted;united states", "Canada, Balance, Customs, SA, US"),
        ("canada;export;customs;seasonally adjusted;all countries", "Canada, Exports, Customs, SA, All"),
        ("canada;import;customs;seasonally adjusted;all countries", "Canada, Imports, Customs, SA, All"),
        ("canada;trade balance;customs;seasonally adjusted;all countries", "Canada, Balance, Customs, SA, All"),
    ]
    for item in all_series_trade:
        s = item.get("status", "?")
        if s == "SUCCESS":
            obj = item.get("object", {})
            title = obj.get("SeriesTitleEn") or ""
            vid = obj.get("vectorId")
            freq = obj.get("frequencyCode")
            tl = title.lower()
            matched_label = None
            for pattern, label in target_patterns:
                parts = pattern.split(";")
                if all(p in tl for p in parts):
                    matched_label = label
                    break
            if not matched_label:
                # Simpler check: SA + US + Canada
                if ("canada" in tl and "united states" in tl and
                        "seasonally adjusted" in tl and "customs" in tl):
                    matched_label = "Canada-US trade, SA, Customs: " + title[:40]
            if matched_label:
                pts = fetch_pts(int(vid), 3)
                print(f"  V{vid}: {title[:70]} pts={pts}")
                w(f"**V{vid}**: {title}")
                w(f"  Label: {matched_label}")
                w(f"  Freq: {freq}")
                w(f"  Latest 3: {pts}")
                if pts and pts[-1][0] >= "2024":
                    w("  **CONFIRMED — recent data**")
                    trade_confirmed.append({
                        "vid": int(vid), "title": title, "freq": freq,
                        "pts": pts, "table": "12-10-0011-01",
                        "label": matched_label
                    })
                time.sleep(0.15)
        w()
else:
    w(f"getAllSeriesInfoFromCube: failed — {type(all_series_trade)}")

confirmed_all.extend(trade_confirmed)

# =============================================================
# TABLE 4: Population components — 17-10-0040-01
# Product: 17100040 (International migration components, quarterly)
# Dim1=Geography(Canada=1), Dim2=Components(Immigrants=1, Net emigration=6, NPR=5)
# NOTE: "natural increase" is NOT in this table — this table has immigration/emigration
# Natural increase (births - deaths) is in 17100008 (annual) or would need separate table
# =============================================================
w("---")
w()
w("## Table 4: 17-10-0040-01 — Population Components (International Migration)")
w()
w("*Note: Table 17-10-0040-01 covers international migration components.*")
w("*Natural increase (births minus deaths) is NOT in this table — it is in 17-10-0008-01 (annual only).*")
w()
print("\nTABLE 4: Population components (international migration)")

try:
    meta = cube_meta(17100040)
    if meta.get("status") == "SUCCESS":
        obj = meta["object"]
        w(f"### getCubeMetadata pid=17100040: **SUCCESS**")
        w(f"Title: {obj.get('cubeTitleEn', 'N/A')}")
        dims = obj.get("dimension", [])
        for di, dim in enumerate(dims, 1):
            dname = dim.get("dimensionNameEn", "")
            members = [(m.get("memberId"), m.get("memberNameEn", "")) for m in dim.get("member", [])]
            w(f"**Dim{di}: {dname}**")
            for mid, mname in members:
                w(f"  [{mid}] {mname}")
            w()
except Exception as e:
    w(f"getCubeMetadata pid=17100040: ERROR — {e}")
time.sleep(0.3)

w("### Vector scan (getAllSeriesInfoFromCube on pid=17100040)")
print("  Trying getAllSeriesInfoFromCube on 17100040...")
all_series_pop_comp = get_all_vectors_from_cube(17100040)
pop_comp_confirmed = []
if all_series_pop_comp and isinstance(all_series_pop_comp, list):
    w(f"getAllSeriesInfoFromCube returned {len(all_series_pop_comp)} series")
    target_components = [
        "immigrants", "net emigration", "emigrants", "returning emigrants",
        "net temporary emigration", "net non-permanent residents",
        "non-permanent residents, inflows", "non-permanent residents, outflows"
    ]
    for item in all_series_pop_comp:
        s = item.get("status", "?")
        if s == "SUCCESS":
            obj = item.get("object", {})
            title = obj.get("SeriesTitleEn") or ""
            vid = obj.get("vectorId")
            freq = obj.get("frequencyCode")
            tl = title.lower()
            if "canada" in tl:
                matched = next((c for c in target_components if c in tl), None)
                if matched:
                    pts = fetch_pts(int(vid), 3)
                    print(f"  V{vid}: {title[:70]} pts={pts}")
                    w(f"**V{vid}**: {title}")
                    w(f"  Component: {matched}")
                    w(f"  Freq: {freq}")
                    w(f"  Latest 3: {pts}")
                    if pts and pts[-1][0] >= "2024":
                        w("  **CONFIRMED — recent data**")
                        pop_comp_confirmed.append({
                            "vid": int(vid), "title": title, "freq": freq,
                            "pts": pts, "table": "17-10-0040-01",
                            "label": matched.title()
                        })
                    time.sleep(0.15)
        w()
else:
    w(f"getAllSeriesInfoFromCube: failed — {type(all_series_pop_comp)}")

confirmed_all.extend(pop_comp_confirmed)

# =============================================================
# TABLE 5: Population stock by age group — 17-10-0009-01
# Product: 17100009 (Population estimates, quarterly)
# Dim1=Geography only (Canada=1) — possibly no age dim in this table
# From prior probe: vector 1 = Canada total = 41.5M (2026-Q1)
# =============================================================
w("---")
w()
w("## Table 5: 17-10-0009-01 — Population Stock, Canada (Quarterly)")
w()
print("\nTABLE 5: Population stock (17100009)")

try:
    meta = cube_meta(17100009)
    if meta.get("status") == "SUCCESS":
        obj = meta["object"]
        w(f"### getCubeMetadata pid=17100009: **SUCCESS**")
        w(f"Title: {obj.get('cubeTitleEn', 'N/A')}")
        dims = obj.get("dimension", [])
        for di, dim in enumerate(dims, 1):
            dname = dim.get("dimensionNameEn", "")
            members = [(m.get("memberId"), m.get("memberNameEn", "")) for m in dim.get("member", [])]
            w(f"**Dim{di}: {dname}**")
            for mid, mname in members[:20]:
                w(f"  [{mid}] {mname}")
            w()
except Exception as e:
    w(f"getCubeMetadata pid=17100009: ERROR — {e}")
time.sleep(0.3)

w("### Vector scan (getAllSeriesInfoFromCube on pid=17100009)")
print("  Trying getAllSeriesInfoFromCube on 17100009...")
all_series_pop = get_all_vectors_from_cube(17100009)
pop_confirmed = []
if all_series_pop and isinstance(all_series_pop, list):
    w(f"getAllSeriesInfoFromCube returned {len(all_series_pop)} series")
    for item in all_series_pop:
        s = item.get("status", "?")
        if s == "SUCCESS":
            obj = item.get("object", {})
            title = obj.get("SeriesTitleEn") or ""
            vid = obj.get("vectorId")
            freq = obj.get("frequencyCode")
            tl = title.lower()
            if "canada" in tl:
                pts = fetch_pts(int(vid), 3)
                print(f"  V{vid}: {title[:70]} pts={pts}")
                w(f"**V{vid}**: {title}")
                w(f"  Freq: {freq}")
                w(f"  Latest 3: {pts}")
                if pts and pts[-1][0] >= "2024":
                    w("  **CONFIRMED — recent data**")
                    pop_confirmed.append({
                        "vid": int(vid), "title": title, "freq": freq,
                        "pts": pts, "table": "17-10-0009-01",
                        "label": "Population, Canada: " + title
                    })
                time.sleep(0.15)
        w()
else:
    w(f"getAllSeriesInfoFromCube: failed — {type(all_series_pop)}")
    # Fallback: from prior probe vector 1 = Canada total
    w("Fallback: probing low vector IDs (known from prior probe: V1 = Canada total)")
    for vid in range(1, 20):
        try:
            info = series_info(vid)
            if info.get("status") == "SUCCESS":
                obj = info["object"]
                title = obj.get("SeriesTitleEn") or ""
                pid_f = obj.get("productId")
                freq = obj.get("frequencyCode")
                w(f"V{vid}: pid={pid_f} {title}")
                if pid_f == 17100009 or "canada" in title.lower():
                    pts = fetch_pts(vid, 3)
                    w(f"  Latest 3: {pts}")
                    if pts and pts[-1][0] >= "2024":
                        w("  **CONFIRMED**")
                        pop_confirmed.append({
                            "vid": vid, "title": title, "freq": freq,
                            "pts": pts, "table": "17-10-0009-01",
                            "label": "Population stock, Canada"
                        })
                    time.sleep(0.15)
        except Exception:
            pass
        time.sleep(0.05)

confirmed_all.extend(pop_confirmed)

# =============================================================
# TABLE 6: Labour force by age/sex — 14-10-0027-01
# Best matching product: 14100287 (Labour force char, monthly SA + trend-cycle)
# Dim1=Geography(Canada=1), Dim2=Characteristics(8=Participation,9=Employment)
# Dim3=Gender(Total=1), Dim4=AgeGroup(15+=1, 25-54=6, 15-24=2)
# Dim5=Statistics(Estimate=1), Dim6=DataType(SA=1)
# =============================================================
w("---")
w()
w("## Table 6: 14-10-0027-01 — Labour Force, Participation + Employment Rate, Canada, Monthly SA")
w()
w("*Note: Table 14-10-0027-01 maps to product 14100287 (Labour force characteristics, monthly SA)*")
w()
print("\nTABLE 6: Labour force characteristics (14100287)")

try:
    meta = cube_meta(14100287)
    if meta.get("status") == "SUCCESS":
        obj = meta["object"]
        w(f"### getCubeMetadata pid=14100287: **SUCCESS**")
        w(f"Title: {obj.get('cubeTitleEn', 'N/A')}")
        dims = obj.get("dimension", [])
        for di, dim in enumerate(dims, 1):
            dname = dim.get("dimensionNameEn", "")
            members = [(m.get("memberId"), m.get("memberNameEn", "")) for m in dim.get("member", [])]
            w(f"**Dim{di}: {dname}**")
            for mid, mname in members:
                w(f"  [{mid}] {mname}")
            w()
except Exception as e:
    w(f"getCubeMetadata pid=14100287: ERROR — {e}")
time.sleep(0.3)

w("### Vector scan (getAllSeriesInfoFromCube on pid=14100287)")
print("  Trying getAllSeriesInfoFromCube on 14100287...")
all_series_lf = get_all_vectors_from_cube(14100287)
lf_confirmed = []
if all_series_lf and isinstance(all_series_lf, list):
    w(f"getAllSeriesInfoFromCube returned {len(all_series_lf)} series")
    lf_targets = [
        ("canada", "participation rate", "total", "15 years and over", "estimate", "seasonally adjusted"),
        ("canada", "employment rate", "total", "15 years and over", "estimate", "seasonally adjusted"),
        ("canada", "unemployment rate", "total", "15 years and over", "estimate", "seasonally adjusted"),
        ("canada", "participation rate", "total", "25 to 54 years", "estimate", "seasonally adjusted"),
        ("canada", "employment rate", "total", "25 to 54 years", "estimate", "seasonally adjusted"),
        ("canada", "participation rate", "total", "15 to 24 years", "estimate", "seasonally adjusted"),
        ("canada", "employment rate", "total", "15 to 24 years", "estimate", "seasonally adjusted"),
    ]
    for item in all_series_lf:
        s = item.get("status", "?")
        if s == "SUCCESS":
            obj = item.get("object", {})
            title = obj.get("SeriesTitleEn") or ""
            vid = obj.get("vectorId")
            freq = obj.get("frequencyCode")
            tl = title.lower()
            matched_label = None
            for target in lf_targets:
                if all(t in tl for t in target):
                    matched_label = f"{target[1].title()}, {target[3].title()}, SA"
                    break
            if matched_label:
                pts = fetch_pts(int(vid), 3)
                print(f"  V{vid}: {title[:70]} pts={pts}")
                w(f"**V{vid}**: {title}")
                w(f"  Label: {matched_label}")
                w(f"  Freq: {freq}")
                w(f"  Latest 3: {pts}")
                if pts and pts[-1][0] >= "2024":
                    w("  **CONFIRMED — recent data**")
                    lf_confirmed.append({
                        "vid": int(vid), "title": title, "freq": freq,
                        "pts": pts, "table": "14-10-0027-01",
                        "label": matched_label
                    })
                time.sleep(0.15)
        w()
else:
    w(f"getAllSeriesInfoFromCube: failed — {type(all_series_lf)}")
    # Fallback: known working vectors
    w("Fallback: probing known LFS vector range...")
    print("  Probing known LFS vector range 2062809-2062850...")
    for vid in range(2062809, 2062851):
        try:
            info = series_info(vid)
            if info.get("status") == "SUCCESS":
                obj = info["object"]
                title = obj.get("SeriesTitleEn") or ""
                freq = obj.get("frequencyCode")
                tl = title.lower()
                targets_lf = [
                    "participation rate", "employment rate", "unemployment rate"
                ]
                if ("canada" in tl and "15 years and over" in tl and
                        "seasonally adjusted" in tl and
                        any(t in tl for t in targets_lf) and
                        "total - gender" in tl):
                    pts = fetch_pts(vid, 3)
                    print(f"  V{vid}: {title[:70]} pts={pts}")
                    w(f"**V{vid}**: {title}")
                    w(f"  Freq: {freq}")
                    w(f"  Latest 3: {pts}")
                    if pts and pts[-1][0] >= "2024":
                        w("  **CONFIRMED**")
                        lf_confirmed.append({
                            "vid": vid, "title": title, "freq": freq,
                            "pts": pts, "table": "14-10-0027-01",
                            "label": title
                        })
                    time.sleep(0.15)
        except Exception:
            pass
        time.sleep(0.05)

confirmed_all.extend(lf_confirmed)

# =============================================================
# CONFIRMED VECTORS SUMMARY TABLE
# =============================================================
w("---")
w()
w("## CONFIRMED VECTORS")
w()

freq_label = {6: "Quarterly", 9: "Monthly", 12: "Annual", 6: "Quarterly"}
freq_map = {6: "Monthly", 9: "Quarterly", 12: "Annual"}

# Frequency codes: StatsCan uses 6=Monthly, 9=Quarterly, 12=Annual
# But getCubeMetadata may return different codes

if confirmed_all:
    w("| Series | Table | Vector ID | Frequency | Latest date | Latest value | CSV name |")
    w("|--------|-------|-----------|-----------|-------------|--------------|----------|")
    csv_map = {
        "34-10-0035-01": "capacity_util_mfg_sa",
        "14-10-0022-01": "ei_regular_beneficiaries_sa",
        "12-10-0011-01": "trade_canada_us",
        "17-10-0040-01": "pop_intl_migration",
        "17-10-0009-01": "pop_stock_quarterly",
        "14-10-0027-01": "lf_participation_employment_sa",
    }
    for c in confirmed_all:
        freq_str = freq_map.get(c.get("freq", 0), str(c.get("freq")))
        pts = c.get("pts", [])
        latest_date = pts[-1][0] if pts else "N/A"
        latest_val = pts[-1][1] if pts else "N/A"
        csv = csv_map.get(c["table"], "tbd")
        short_title = (c.get("title") or c.get("label", ""))[:55]
        w(f"| {short_title} | {c['table']} | {c['vid']} | {freq_str} | {latest_date} | {latest_val} | {csv} |")
    w()
else:
    w("**No vectors confirmed via getAllSeriesInfoFromCube.** See raw results above.")
    w()

w("## Per-Table Status")
w()
table_groups = {
    "34-10-0035-01": cu_confirmed,
    "14-10-0022-01": ei_confirmed,
    "12-10-0011-01": trade_confirmed,
    "17-10-0040-01": pop_comp_confirmed,
    "17-10-0009-01": pop_confirmed,
    "14-10-0027-01": lf_confirmed,
}
table_descs = {
    "34-10-0035-01": "Capacity utilization, total manufacturing, SA",
    "14-10-0022-01": "EI regular beneficiaries, Canada, monthly SA",
    "12-10-0011-01": "Merchandise trade, Canada-US bilateral",
    "17-10-0040-01": "Population components (international migration)",
    "17-10-0009-01": "Population stock quarterly",
    "14-10-0027-01": "Labour force participation + employment rate, monthly SA",
}
for tid, group in table_groups.items():
    status = "CONFIRMED" if group else "NOT CONFIRMED"
    w(f"- **{tid}** ({table_descs[tid]}): **{status}** — {len(group)} vector(s)")

# Save output
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("".join(lines))

print(f"\nResults written to {OUTPUT}")
print(f"Total confirmed: {len(confirmed_all)}")
for c in confirmed_all:
    pts = c.get("pts", [])
    last = pts[-1] if pts else ("N/A", "N/A")
    print(f"  V{c['vid']}: {c['title'][:65]} | latest={last[0]} {last[1]}")
