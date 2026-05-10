"""
Probe D: Demographics-related StatsCan vectors.
 - Population total, quarterly: Table 17-10-0009-01
 - Net international migration: Table 17-10-0009-01
 - Natural increase (births minus deaths): same table or component vectors

Run: python analyses/demographics_deepdive_vectors.py
Output: analyses/demographics_deepdive_vectors_results.md
"""

import requests
from pathlib import Path

OUTPUT = Path("analyses/demographics_deepdive_vectors_results.md")


def get_series_info(vector_id: int) -> dict:
    url = f"https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromVector/{vector_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def get_cube_metadata(product_id: str) -> dict:
    url = f"https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata/{product_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_vector_sample(vector_id: int, n: int = 4) -> list:
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
results.append("# Demographics Deep-Dive Vector Probe Results\n")
results.append(f"Date: 2026-05-09\n\n")

# ── Population and migration: Table 17-10-0009-01 ────────────────────────────
results.append("## Population & Migration Components — Table 17-10-0009-01\n\n")
print("Fetching cube metadata for 17-10-0009-01...")
try:
    meta = get_cube_metadata("17100009")
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

# Probe candidate vectors for population total and migration
print("Probing population/migration vectors...")
results.append("## Population & Migration — Direct Vector Probes\n\n")

# Known/candidate vectors for 17-10-0009
demo_candidates = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                   57752, 57753, 57754, 57755, 57756,
                   57757, 57758, 57759, 57760, 57761,
                   1458410, 1458411, 1458412, 1458413, 1458414,
                   1458415, 1458416, 1458417, 1458418, 1458419,
                   1458420, 1458421, 1458422, 1458423, 1458424]
for vid in demo_candidates:
    try:
        info = get_series_info(vid)
        s = info.get("status", "?")
        if s == "SUCCESS":
            obj = info.get("object", {})
            title = obj.get("SeriesTitleEn", "N/A")
            freq = obj.get("frequencyCode", "N/A")
            results.append(f"Vector {vid} [{freq}]: {title}\n")
            if any(kw in title.lower() for kw in [
                "population", "migration", "natural increase",
                "births", "deaths", "immigration", "emigration", "canada"
            ]):
                pts = fetch_vector_sample(vid, 4)
                results.append(f"  ** CANDIDATE — Latest: {pts}\n")
        else:
            results.append(f"Vector {vid}: {s}\n")
    except Exception as e:
        results.append(f"Vector {vid}: ERROR — {e}\n")

results.append("\n")

# Also try Table 17-10-0008-01 (quarterly population components)
results.append("## Population Components — Table 17-10-0008-01 (also checked)\n\n")
print("Fetching cube metadata for 17-10-0008-01...")
try:
    meta = get_cube_metadata("17100008")
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

output_text = "".join(results)
OUTPUT.write_text(output_text, encoding="utf-8")
print(f"\nResults written to {OUTPUT}")
print("\nFirst 3000 chars:")
print(output_text[:3000])
