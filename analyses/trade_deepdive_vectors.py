"""
Probe C: Trade-related StatsCan vectors.
 - Merchandise exports, total: Table 12-10-0011-01
 - Canada-US bilateral exports: Table 12-10-0009-01
 - Canada-US bilateral imports: Table 12-10-0009-01

Run: python analyses/trade_deepdive_vectors.py
Output: analyses/trade_deepdive_vectors_results.md
"""

import requests
from pathlib import Path

OUTPUT = Path("analyses/trade_deepdive_vectors_results.md")


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
results.append("# Trade Deep-Dive Vector Probe Results\n")
results.append(f"Date: 2026-05-09\n\n")

# ── Merchandise exports: Table 12-10-0011-01 ─────────────────────────────────
results.append("## Merchandise Exports (Total) — Table 12-10-0011-01\n\n")
print("Fetching cube metadata for 12-10-0011-01...")
try:
    meta = get_cube_metadata("12100011")
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

print("Probing merchandise exports vectors...")
results.append("## Merchandise Exports — Direct Vector Probes\n\n")
export_candidates = [1530071, 1530072, 1530073, 1530074, 1530075,
                     53339274, 53339275, 53339276, 53339277,
                     228072, 228073, 228074, 228075]
for vid in export_candidates:
    try:
        info = get_series_info(vid)
        s = info.get("status", "?")
        if s == "SUCCESS":
            obj = info.get("object", {})
            title = obj.get("SeriesTitleEn", "N/A")
            results.append(f"Vector {vid}: {title}\n")
            if any(kw in title.lower() for kw in ["total", "export", "all"]):
                pts = fetch_vector_sample(vid, 3)
                results.append(f"  ** CANDIDATE — Latest: {pts}\n")
        else:
            results.append(f"Vector {vid}: {s}\n")
    except Exception as e:
        results.append(f"Vector {vid}: ERROR — {e}\n")

results.append("\n")

# ── Canada-US bilateral trade: Table 12-10-0009-01 ───────────────────────────
results.append("## Canada-US Bilateral Trade — Table 12-10-0009-01\n\n")
print("Fetching cube metadata for 12-10-0009-01...")
try:
    meta = get_cube_metadata("12100009")
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

print("Probing Canada-US bilateral trade vectors...")
results.append("## Canada-US Bilateral — Direct Vector Probes\n\n")
bilateral_candidates = [1530055, 1530056, 1530057, 1530058, 1530059,
                        1530060, 1530061, 1530062, 1530063, 1530064,
                        228055, 228056, 228057, 228058,
                        53339258, 53339259, 53339260, 53339261,
                        41704560, 41704561, 41704562]
for vid in bilateral_candidates:
    try:
        info = get_series_info(vid)
        s = info.get("status", "?")
        if s == "SUCCESS":
            obj = info.get("object", {})
            title = obj.get("SeriesTitleEn", "N/A")
            results.append(f"Vector {vid}: {title}\n")
            if any(kw in title.lower() for kw in ["united states", "us ", "export", "import"]):
                pts = fetch_vector_sample(vid, 3)
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
