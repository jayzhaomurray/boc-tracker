"""
Probe A: GDP-related StatsCan vectors.
 - Capacity utilization, total economy: Table 36-10-0007-01
 - Hours worked, monthly aggregate: Table 14-10-0035-01

Run: python analyses/gdp_deepdive_vectors.py
Output: analyses/gdp_deepdive_vectors_results.md
"""

import requests
import json
from pathlib import Path

OUTPUT = Path("analyses/gdp_deepdive_vectors_results.md")


def get_cube_metadata(product_id: str) -> dict:
    url = f"https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata/{product_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def get_series_info(vector_id: int) -> dict:
    url = f"https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromVector/{vector_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_vector_sample(vector_id: int, n: int = 5) -> list:
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
results.append("# GDP Deep-Dive Vector Probe Results\n")
results.append(f"Date: 2026-05-09\n\n")

# ── Capacity utilization: Table 36-10-0007-01 ─────────────────────────────────
results.append("## Capacity Utilization — Table 36-10-0007-01\n\n")

print("Fetching cube metadata for 36-10-0007-01...")
try:
    meta = get_cube_metadata("36100007")
    status = meta.get("status", "?")
    results.append(f"getCubeMetadata status: {status}\n\n")

    if status == "SUCCESS":
        obj = meta.get("object", {})
        dims = obj.get("dimension", [])
        results.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
        results.append(f"Frequency: {obj.get('freq', 'N/A')}\n")
        results.append(f"Dimensions: {len(dims)}\n\n")

        # List all members of each dimension
        for dim in dims:
            results.append(f"### Dimension: {dim.get('dimensionNameEn', 'N/A')}\n")
            members = dim.get("member", [])
            for m in members[:30]:  # cap at 30
                results.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
            results.append("\n")
except Exception as e:
    results.append(f"ERROR: {e}\n\n")

# Try likely vector IDs for total capacity utilization
# Based on known table structure: total economy is usually first member
CAPACITY_UTIL_CANDIDATES = [
    (36100007, "total_economy_candidate_1"),
]

# Try to probe some candidate vectors directly
print("Probing capacity utilization vectors...")
results.append("## Capacity Utilization — Direct Vector Probes\n\n")

# Known from previous research: v41704478 is often cited for total economy CU
candidate_vectors = [41704478, 41704479, 41704480, 56843, 41704498]
for vid in candidate_vectors:
    try:
        info = get_series_info(vid)
        s = info.get("status", "?")
        if s == "SUCCESS":
            obj = info.get("object", {})
            results.append(f"Vector {vid}: SUCCESS\n")
            results.append(f"  Title: {obj.get('SeriesTitleEn', 'N/A')}\n")
            results.append(f"  Freq: {obj.get('frequencyCode', 'N/A')}\n")
            results.append(f"  UOM: {obj.get('scalarFactorCode', 'N/A')}\n")
            # fetch sample
            pts = fetch_vector_sample(vid, 3)
            if pts:
                results.append(f"  Latest 3 points: {pts}\n")
        else:
            results.append(f"Vector {vid}: {s}\n")
    except Exception as e:
        results.append(f"Vector {vid}: ERROR — {e}\n")
    results.append("\n")


# ── Hours worked: Table 14-10-0035-01 ────────────────────────────────────────
results.append("## Hours Worked — Table 14-10-0035-01\n\n")

print("Fetching cube metadata for 14-10-0035-01...")
try:
    meta = get_cube_metadata("14100035")
    status = meta.get("status", "?")
    results.append(f"getCubeMetadata status: {status}\n\n")

    if status == "SUCCESS":
        obj = meta.get("object", {})
        dims = obj.get("dimension", [])
        results.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
        results.append(f"Frequency: {obj.get('freq', 'N/A')}\n")
        results.append(f"Dimensions: {len(dims)}\n\n")

        for dim in dims:
            results.append(f"### Dimension: {dim.get('dimensionNameEn', 'N/A')}\n")
            members = dim.get("member", [])
            for m in members[:30]:
                results.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
            results.append("\n")
except Exception as e:
    results.append(f"ERROR: {e}\n\n")

# Try known / candidate vectors for hours worked
print("Probing hours worked vectors...")
results.append("## Hours Worked — Direct Vector Probes\n\n")

# Common vectors for aggregate hours worked (actual hours, all industries, Canada)
hours_candidates = [2062848, 2062843, 2063003, 81819, 3411411]
for vid in hours_candidates:
    try:
        info = get_series_info(vid)
        s = info.get("status", "?")
        if s == "SUCCESS":
            obj = info.get("object", {})
            results.append(f"Vector {vid}: SUCCESS\n")
            results.append(f"  Title: {obj.get('SeriesTitleEn', 'N/A')}\n")
            results.append(f"  Freq: {obj.get('frequencyCode', 'N/A')}\n")
            results.append(f"  UOM: {obj.get('scalarFactorCode', 'N/A')}\n")
            pts = fetch_vector_sample(vid, 3)
            if pts:
                results.append(f"  Latest 3 points: {pts}\n")
        else:
            results.append(f"Vector {vid}: {s}\n")
    except Exception as e:
        results.append(f"Vector {vid}: ERROR — {e}\n")
    results.append("\n")


output_text = "".join(results)
OUTPUT.write_text(output_text, encoding="utf-8")
print(f"Results written to {OUTPUT}")
print("\nSummary:")
print(output_text[:3000])
