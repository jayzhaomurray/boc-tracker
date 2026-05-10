"""
Probe: Capacity utilization rate — Table 34-10-0035-01
 - Total manufacturing capacity utilization, Canada, quarterly, SA

Run: python analyses/capacity_utilization_probe.py
Output: analyses/capacity_utilization_probe_results.md
"""

import requests
from pathlib import Path

OUTPUT = Path("analyses/capacity_utilization_probe_results.md")


def get_cube_metadata(product_id: int) -> dict:
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata"
    r = requests.post(url, json=[{"productId": product_id}], timeout=30)
    r.raise_for_status()
    return r.json()[0]


def get_series_info(vector_id: int) -> dict:
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromVector"
    r = requests.post(url, json=[{"vectorId": vector_id}], timeout=30)
    r.raise_for_status()
    return r.json()[0]


def get_series_from_coord(product_id: int, coord: str) -> dict:
    url = f"https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromCubePidCoord/{product_id}/{coord}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


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
results.append("# Capacity Utilization Probe Results\n")
results.append("Date: 2026-05-10\n\n")
results.append("Target: Table 34-10-0035-01 — Capacity utilization rates, by industry, quarterly, SA\n\n")

# Try both product ID forms for 34-10-0035-01
product_id_candidates = [3410003501, 341000350101]

working_pid = None
for pid in product_id_candidates:
    results.append(f"## getCubeMetadata — productId {pid}\n\n")
    print(f"Trying getCubeMetadata with productId={pid}...")
    try:
        meta = get_cube_metadata(pid)
        status = meta.get("status", "?")
        results.append(f"Status: {status}\n\n")
        if status == "SUCCESS":
            working_pid = pid
            obj = meta.get("object", {})
            dims = obj.get("dimension", [])
            results.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
            results.append(f"Frequency: {obj.get('freq', 'N/A')}\n")
            results.append(f"Dimensions: {len(dims)}\n\n")
            for dim in dims:
                results.append(f"### Dimension: {dim.get('dimensionNameEn', 'N/A')}\n")
                members = dim.get("member", [])
                for m in members[:50]:
                    results.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
                results.append("\n")
            break  # found a working pid, stop trying
        else:
            results.append(f"Returned non-SUCCESS: {meta}\n\n")
    except Exception as e:
        results.append(f"ERROR: {e}\n\n")

# Coordinate-based lookups
# Table 34-10-0035-01 typically has dimensions:
#   1. Geography (Canada = 1)
#   2. Industry (Total = 1 or All industries = 1, Manufacturing = some index)
# Try coords for total / total manufacturing
if working_pid:
    results.append("## Coordinate-Based Lookups\n\n")
    coord_candidates = [
        ("1.1", "Canada, first industry member"),
        ("1.2", "Canada, second industry member"),
        ("1.3", "Canada, third industry member"),
        ("1.4", "Canada, fourth industry member"),
        ("1.5", "Canada, fifth industry member"),
        ("1.6", "Canada, sixth industry member"),
        ("1.7", "Canada, seventh industry member"),
        ("1.8", "Canada, eighth industry member"),
        ("1.9", "Canada, ninth industry member"),
        ("1.10", "Canada, tenth industry member"),
        ("1.11", "Canada, eleventh industry member"),
        ("1.12", "Canada, twelfth industry member"),
    ]
    print("Trying coordinate-based lookups...")
    for coord, label in coord_candidates:
        try:
            resp = get_series_from_coord(working_pid, coord)
            if isinstance(resp, list) and len(resp) > 0:
                item = resp[0]
            else:
                item = resp
            s = item.get("status", "?")
            if s == "SUCCESS":
                obj = item.get("object", {})
                vid = obj.get("vectorId")
                title = obj.get("SeriesTitleEn", "N/A")
                freq = obj.get("frequencyCode", "N/A")
                uom = obj.get("scalarFactorCode", "N/A")
                results.append(f"Coord {coord} ({label}): vectorId={vid}\n")
                results.append(f"  Title: {title}\n")
                results.append(f"  Freq: {freq} | UOM: {uom}\n")
                if vid:
                    pts = fetch_vector_sample(int(vid), 3)
                    results.append(f"  Latest 3 points: {pts}\n")
            else:
                results.append(f"Coord {coord}: {s}\n")
        except Exception as e:
            results.append(f"Coord {coord}: ERROR — {e}\n")
        results.append("\n")

# Direct vector probes — capacity utilization, total manufacturing Canada
# Known candidates from StatsCan references and nearby series
results.append("## Direct Vector Probes\n\n")
print("Probing direct vector candidates for capacity utilization...")
cu_candidates = [
    # Capacity utilization, total manufacturing, Canada
    41704528, 41704529, 41704530,
    # Older series
    55410, 55411, 55412, 55413, 55414,
    # From 34-10-0035 neighbourhood
    34100035, 34100036, 34100037,
    # Common Stats Can range for this table
    1400, 1401, 1402, 1403, 1404, 1405,
]
for vid in cu_candidates:
    try:
        info = get_series_info(vid)
        s = info.get("status", "?")
        if s == "SUCCESS":
            obj = info.get("object", {})
            title = obj.get("SeriesTitleEn", "N/A")
            freq = obj.get("frequencyCode", "N/A")
            uom = obj.get("scalarFactorCode", "N/A")
            results.append(f"Vector {vid}: {title}\n")
            results.append(f"  Freq: {freq} | UOM: {uom}\n")
            if any(kw in title.lower() for kw in ["capacity", "utiliz", "manufacturing", "total"]):
                pts = fetch_vector_sample(vid, 3)
                results.append(f"  ** CANDIDATE — Latest 3: {pts}\n")
        else:
            results.append(f"Vector {vid}: {s}\n")
    except Exception as e:
        results.append(f"Vector {vid}: ERROR — {e}\n")
    results.append("\n")

results.append("## CONFIRMED VECTORS\n\n")
results.append("(Populate after reviewing results above)\n\n")
results.append("| Series | Vector ID | CSV name |\n")
results.append("|--------|-----------|----------|\n")
results.append("| Total manufacturing capacity utilization, Canada, SA | TBD | capacity_util_mfg_sa |\n\n")

output_text = "".join(results)
OUTPUT.write_text(output_text, encoding="utf-8")
print(f"\nResults written to {OUTPUT}")
print("\nFirst 3000 chars:")
print(output_text[:3000])
