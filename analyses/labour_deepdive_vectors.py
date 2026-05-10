"""
Probe B: Labour-related StatsCan vectors.
 - LFS reason for unemployment — job losers: Table 14-10-0125-01
 - Youth unemployment rate (15-24): Table 14-10-0287-01
 - Prime-age unemployment rate (25-54): Table 14-10-0287-01
 - EI regular beneficiaries: Table 14-10-0005-01

Run: python analyses/labour_deepdive_vectors.py
Output: analyses/labour_deepdive_vectors_results.md
"""

import requests
from pathlib import Path

OUTPUT = Path("analyses/labour_deepdive_vectors_results.md")


def get_series_info(vector_id: int) -> dict:
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromVector"
    r = requests.post(url, json=[{"vectorId": vector_id}], timeout=30)
    r.raise_for_status()
    return r.json()[0]


def get_cube_metadata(product_id: str) -> dict:
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata"
    r = requests.post(url, json=[{"productId": int(product_id)}], timeout=30)
    r.raise_for_status()
    return r.json()[0]


def fetch_vector_sample(vector_id: int, n: int = 3) -> list:
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
    r = requests.post(url, json=[{"vectorId": vector_id, "latestN": n}], timeout=30)
    r.raise_for_status()
    payload = r.json()
    item = payload[0]
    if item.get("status") != "SUCCESS":
        return []
    pts = item["object"]["vectorDataPoint"]
    return [(p["refPer"], p["value"]) for p in pts]


results = []
results.append("# Labour Deep-Dive Vector Probe Results\n")
results.append(f"Date: 2026-05-09\n\n")

# ── LFS reason for unemployment: Table 14-10-0125-01 ─────────────────────────
results.append("## LFS Reason for Unemployment — Table 14-10-0125-01\n\n")
print("Fetching cube metadata for 14-10-0125-01...")
try:
    meta = get_cube_metadata("14100125")
    status = meta.get("status", "?")
    results.append(f"getCubeMetadata status: {status}\n\n")
    if status == "SUCCESS":
        obj = meta.get("object", {})
        dims = obj.get("dimension", [])
        results.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
        results.append(f"Frequency: {obj.get('freq', 'N/A')}\n\n")
        for dim in dims:
            results.append(f"### Dimension: {dim.get('dimensionNameEn', 'N/A')}\n")
            for m in dim.get("member", [])[:40]:
                results.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
            results.append("\n")
except Exception as e:
    results.append(f"ERROR: {e}\n\n")

# Probe candidate vectors for job losers
print("Probing job losers vectors...")
results.append("## LFS Reason — Direct Vector Probes (Job Losers)\n\n")
job_loser_candidates = [2062849, 2062850, 2062851, 2062852, 80691, 80692, 80693,
                        2062856, 2062857, 41704532, 41704533]
for vid in job_loser_candidates:
    try:
        info = get_series_info(vid)
        s = info.get("status", "?")
        if s == "SUCCESS":
            obj = info.get("object", {})
            title = obj.get("SeriesTitleEn", "N/A")
            if any(kw in title.lower() for kw in ["job loser", "layoff", "dismiss", "reason"]):
                results.append(f"** Vector {vid}: CANDIDATE **\n")
                results.append(f"  Title: {title}\n")
                results.append(f"  Freq: {obj.get('frequencyCode')}\n")
                pts = fetch_vector_sample(vid, 3)
                if pts:
                    results.append(f"  Latest 3: {pts}\n")
                results.append("\n")
            else:
                results.append(f"Vector {vid}: {title}\n")
        else:
            results.append(f"Vector {vid}: {s}\n")
    except Exception as e:
        results.append(f"Vector {vid}: ERROR — {e}\n")

results.append("\n")

# ── Youth & Prime-age unemployment: Table 14-10-0287-01 ──────────────────────
results.append("## Youth & Prime-Age Unemployment — Table 14-10-0287-01\n\n")
print("Fetching cube metadata for 14-10-0287-01...")
try:
    meta = get_cube_metadata("14100287")
    status = meta.get("status", "?")
    results.append(f"getCubeMetadata status: {status}\n\n")
    if status == "SUCCESS":
        obj = meta.get("object", {})
        dims = obj.get("dimension", [])
        results.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
        results.append(f"Frequency: {obj.get('freq', 'N/A')}\n\n")
        for dim in dims:
            results.append(f"### Dimension: {dim.get('dimensionNameEn', 'N/A')}\n")
            for m in dim.get("member", [])[:50]:
                results.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
            results.append("\n")
except Exception as e:
    results.append(f"ERROR: {e}\n\n")

print("Probing youth/prime-age unemployment vectors...")
results.append("## Youth/Prime-Age Unemployment — Direct Vector Probes\n\n")
# Known: 2062815 is total unemployment rate. Youth and prime-age will be nearby.
# Try vectors around 2062815.
age_group_candidates = [2062825, 2062826, 2062827, 2062828, 2062829, 2062830,
                        2062831, 2062832, 2062833, 2062834, 2062835,
                        2062836, 2062837, 2062838, 2062839, 2062840]
for vid in age_group_candidates:
    try:
        info = get_series_info(vid)
        s = info.get("status", "?")
        if s == "SUCCESS":
            obj = info.get("object", {})
            title = obj.get("SeriesTitleEn", "N/A")
            results.append(f"Vector {vid}: {title}\n")
            if any(kw in title.lower() for kw in ["15 to 24", "25 to 54", "youth", "15-24", "25-54",
                                                    "unemploy"]):
                pts = fetch_vector_sample(vid, 2)
                results.append(f"  ** CANDIDATE — Latest: {pts}\n")
        else:
            results.append(f"Vector {vid}: {s}\n")
    except Exception as e:
        results.append(f"Vector {vid}: ERROR — {e}\n")

results.append("\n")

# ── EI regular beneficiaries: Table 14-10-0005-01 ────────────────────────────
results.append("## EI Regular Beneficiaries — Table 14-10-0005-01\n\n")
print("Fetching cube metadata for 14-10-0005-01...")
try:
    meta = get_cube_metadata("14100005")
    status = meta.get("status", "?")
    results.append(f"getCubeMetadata status: {status}\n\n")
    if status == "SUCCESS":
        obj = meta.get("object", {})
        dims = obj.get("dimension", [])
        results.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
        results.append(f"Frequency: {obj.get('freq', 'N/A')}\n\n")
        for dim in dims:
            results.append(f"### Dimension: {dim.get('dimensionNameEn', 'N/A')}\n")
            for m in dim.get("member", [])[:30]:
                results.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
            results.append("\n")
except Exception as e:
    results.append(f"ERROR: {e}\n\n")

print("Probing EI vectors...")
results.append("## EI — Direct Vector Probes\n\n")
ei_candidates = [1365054, 1365055, 1365056, 1365057, 1365058,
                 1365060, 1365061, 1365062, 1365063,
                 41700193, 41700194, 41700195]
for vid in ei_candidates:
    try:
        info = get_series_info(vid)
        s = info.get("status", "?")
        if s == "SUCCESS":
            obj = info.get("object", {})
            title = obj.get("SeriesTitleEn", "N/A")
            results.append(f"Vector {vid}: {title}\n")
            if any(kw in title.lower() for kw in ["regular", "beneficiar", "ei ", "employment insurance"]):
                pts = fetch_vector_sample(vid, 2)
                results.append(f"  ** CANDIDATE — Latest: {pts}\n")
        else:
            results.append(f"Vector {vid}: {s}\n")
    except Exception as e:
        results.append(f"Vector {vid}: ERROR — {e}\n")

results.append("\n")

output_text = "".join(results)
OUTPUT.write_text(output_text, encoding="utf-8")
print(f"\nResults written to {OUTPUT}")
print("\nFirst 3000 chars:")
print(output_text[:3000])
