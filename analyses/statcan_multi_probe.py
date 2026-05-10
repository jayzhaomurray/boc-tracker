"""
Multi-table StatsCan probe for 6 tables.
Uses WDS REST API with multiple approaches to find confirmed vector IDs.

Tables:
1. 34-10-0035-01 Capacity utilization, total manufacturing, Canada, quarterly SA
2. 14-10-0022-01 EI regular beneficiaries, total Canada, monthly SA
3. 12-10-0011-01 Merchandise trade Canada-US, monthly C$
4. 17-10-0040-01 Population components, quarterly
5. 17-10-0009-01 Population by age group, Canada, quarterly
6. 14-10-0027-01 Labour force by age group and sex, monthly SA
"""

import requests
import json
import time
from pathlib import Path

OUTPUT = Path("analyses/statcan_probe_results_2026_05_10.md")

BASE = "https://www150.statcan.gc.ca/t1/wds/rest"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research-probe/1.0)",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def get_cube_metadata(product_id: int) -> dict:
    url = f"{BASE}/getCubeMetadata"
    r = requests.post(url, json=[{"productId": product_id}], headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()[0]


def get_series_from_coord(product_id: int, coord: str) -> dict:
    url = f"{BASE}/getSeriesInfoFromCubePidCoord/{product_id}/{coord}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def get_series_info(vector_id: int) -> dict:
    url = f"{BASE}/getSeriesInfoFromVector"
    r = requests.post(url, json=[{"vectorId": vector_id}], headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()[0]


def fetch_vector_sample(vector_id: int, n: int = 3) -> list:
    url = f"{BASE}/getDataFromVectorsAndLatestNPeriods"
    r = requests.post(url, json=[{"vectorId": vector_id, "latestN": n}], headers=HEADERS, timeout=30)
    r.raise_for_status()
    payload = r.json()
    item = payload[0]
    if item.get("status") != "SUCCESS":
        return []
    pts = item.get("object", {}).get("vectorDataPoint", [])
    return [(p["refPer"], p["value"]) for p in pts]


def try_pid(table_id_str: str) -> tuple:
    """Given '34-10-0035-01', return list of candidate product IDs to try."""
    # Strip hyphens
    stripped = table_id_str.replace("-", "")
    # Form 1: drop last 2 digits (the '01' suffix)
    pid1 = int(stripped[:-2])
    # Form 2: keep all digits
    pid2 = int(stripped)
    return [pid1, pid2]


def probe_table(table_id: str, target_desc: str, coord_candidates: list, direct_vectors: list):
    """
    Probe one table. Returns (lines, confirmed_vectors).
    confirmed_vectors is list of dicts.
    """
    lines = []
    confirmed = []

    lines.append(f"\n## Table {table_id}\n\n")
    lines.append(f"**Target:** {target_desc}\n\n")

    pids = try_pid(table_id)
    working_pid = None
    dim_info = {}

    for pid in pids:
        lines.append(f"### getCubeMetadata productId={pid}\n\n")
        print(f"  getCubeMetadata pid={pid}...")
        try:
            meta = get_cube_metadata(pid)
            status = meta.get("status", "?")
            lines.append(f"Status: {status}\n\n")
            if status == "SUCCESS":
                working_pid = pid
                obj = meta.get("object", {})
                dims = obj.get("dimension", [])
                lines.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
                lines.append(f"Frequency code: {obj.get('freq', 'N/A')}\n")
                lines.append(f"Dimensions ({len(dims)}):\n\n")
                for di, dim in enumerate(dims):
                    dname = dim.get("dimensionNameEn", f"Dim{di}")
                    members = dim.get("member", [])
                    lines.append(f"**Dim {di+1}: {dname}**\n")
                    dim_info[di+1] = {"name": dname, "members": []}
                    for m in members[:60]:
                        mid = m.get("memberId")
                        mname = m.get("memberNameEn", "")
                        lines.append(f"  [{mid}] {mname}\n")
                        dim_info[di+1]["members"].append({"id": mid, "name": mname})
                    lines.append("\n")
                break
            else:
                obj = meta.get("object", {})
                lines.append(f"Response object: {json.dumps(obj)[:200]}\n\n")
        except Exception as e:
            lines.append(f"ERROR: {e}\n\n")
        time.sleep(0.3)

    # Coordinate probes
    if working_pid and coord_candidates:
        lines.append("### Coordinate Probes\n\n")
        print(f"  Trying {len(coord_candidates)} coordinates...")
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
                    lines.append(f"**Coord {coord}** ({label}): vectorId={vid}\n")
                    lines.append(f"  Title: {title}\n")
                    lines.append(f"  Freq: {freq} | UOM/Scale: {uom}\n")
                    if vid:
                        pts = fetch_vector_sample(int(vid), 3)
                        lines.append(f"  Latest 3 pts: {pts}\n")
                        if pts and pts[-1][0] >= "2024":
                            confirmed.append({
                                "series": label,
                                "table": table_id,
                                "vector_id": int(vid),
                                "title": title,
                                "freq": freq,
                                "latest_date": pts[-1][0],
                                "latest_value": pts[-1][1],
                            })
                            lines.append(f"  **CONFIRMED (recent data)**\n")
                else:
                    lines.append(f"Coord {coord}: status={s}\n")
            except Exception as e:
                lines.append(f"Coord {coord}: ERROR — {e}\n")
            lines.append("\n")
            time.sleep(0.2)

    # Direct vector probes
    if direct_vectors:
        lines.append("### Direct Vector Probes\n\n")
        print(f"  Probing {len(direct_vectors)} direct vectors...")
        for vid, label in direct_vectors:
            try:
                info = get_series_info(vid)
                s = info.get("status", "?")
                if s == "SUCCESS":
                    obj = info.get("object", {})
                    title = obj.get("SeriesTitleEn", "N/A")
                    freq = obj.get("frequencyCode", "N/A")
                    uom = obj.get("scalarFactorCode", "N/A")
                    lines.append(f"**Vector {vid}** ({label}):\n")
                    lines.append(f"  Title: {title}\n")
                    lines.append(f"  Freq: {freq} | UOM/Scale: {uom}\n")
                    pts = fetch_vector_sample(vid, 3)
                    lines.append(f"  Latest 3 pts: {pts}\n")
                    if pts and pts[-1][0] >= "2024":
                        confirmed.append({
                            "series": label,
                            "table": table_id,
                            "vector_id": vid,
                            "title": title,
                            "freq": freq,
                            "latest_date": pts[-1][0],
                            "latest_value": pts[-1][1],
                        })
                        lines.append(f"  **CONFIRMED (recent data)**\n")
                else:
                    lines.append(f"Vector {vid}: {s}\n")
            except Exception as e:
                lines.append(f"Vector {vid}: ERROR — {e}\n")
            lines.append("\n")
            time.sleep(0.2)

    return "".join(lines), confirmed


# ============================================================
# TABLE DEFINITIONS
# ============================================================

# 1. Capacity utilization 34-10-0035-01
# Dim 1: Geography (Canada=1), Dim 2: Industry (Total all industries=1, Total mfg=2?)
cu_coords = [
    ("1.1", "Canada, Total all industries"),
    ("1.2", "Canada, member 2"),
    ("1.3", "Canada, member 3"),
    ("1.4", "Canada, member 4"),
    ("1.5", "Canada, member 5"),
    ("1.6", "Canada, member 6"),
    ("1.7", "Canada, member 7"),
    ("1.8", "Canada, member 8"),
    ("1.9", "Canada, member 9"),
    ("1.10", "Canada, member 10"),
    ("1.11", "Canada, member 11"),
    ("1.12", "Canada, member 12"),
    ("1.13", "Canada, member 13"),
    ("1.14", "Canada, member 14"),
    ("1.15", "Canada, member 15"),
]
# Known candidate vectors for capacity utilization from StatsCan
cu_vectors = [
    (41704001, "cu candidate 1"),
    (41704002, "cu candidate 2"),
    (41704003, "cu candidate 3"),
    (41704004, "cu candidate 4"),
    (41704005, "cu candidate 5"),
    (81819701, "cu v2 1"),
    (81819702, "cu v2 2"),
    (81819703, "cu v2 3"),
    (94789, "cu old 1"),
    (94790, "cu old 2"),
    (94791, "cu old 3"),
    (96380, "cu alt 1"),
    (96381, "cu alt 2"),
    (96382, "cu alt 3"),
]

# 2. EI beneficiaries 14-10-0022-01
# Dim: Geography, Claim type (Regular=1?), Sex, Duration
ei_coords = [
    ("1.1", "Canada, Regular beneficiaries (guess)"),
    ("1.1.1", "Canada, Reg ben, total"),
    ("1.1.1.1", "Canada, Reg ben, total, all"),
    ("1.2", "Canada, member 2"),
    ("1.3", "Canada, member 3"),
    ("1.4", "Canada, member 4"),
    ("1.5", "Canada, member 5"),
    ("1.6", "Canada, member 6"),
    ("1.7", "Canada, member 7"),
    ("1.8", "Canada, member 8"),
    ("1.9", "Canada, member 9"),
    ("1.10", "Canada, member 10"),
]
ei_vectors = [
    (1406516, "EI regular ben Canada"),
    (1406517, "EI regular ben Canada 2"),
    (1406518, "EI regular ben Canada 3"),
    (1800697, "EI v2 1"),
    (1800698, "EI v2 2"),
    (1800699, "EI v2 3"),
    (71802, "EI old 1"),
    (71803, "EI old 2"),
    (71804, "EI old 3"),
    (71805, "EI old 4"),
    (71806, "EI old 5"),
    (1400081, "EI alt 1"),
    (1400082, "EI alt 2"),
    (1400083, "EI alt 3"),
    (1400084, "EI alt 4"),
    (1400085, "EI alt 5"),
]

# 3. Merchandise trade 12-10-0011-01
# Canada-US exports, imports, balance
trade_coords = [
    ("1.222.1", "Canada, US, exports"),
    ("1.222.2", "Canada, US, imports"),
    ("1.222.3", "Canada, US, balance"),
    ("1.1.1", "Canada, All, exports"),
    ("1.1.2", "Canada, All, imports"),
    ("1.1.3", "Canada, All, balance"),
    ("1.2.1", "Canada, US?, exports"),
    ("1.2.2", "Canada, US?, imports"),
    ("1.2.3", "Canada, US?, balance"),
    ("1.3.1", "Canada, m3, exports"),
    ("1.3.2", "Canada, m3, imports"),
    ("1.3.3", "Canada, m3, balance"),
]
trade_vectors = [
    (65527, "trade v1"),
    (65528, "trade v2"),
    (65529, "trade v3"),
    (65530, "trade v4"),
    (65531, "trade v5"),
    (65532, "trade v6"),
    (1401, "trade alt 1"),
    (1402, "trade alt 2"),
    (20622, "trade alt 3"),
    (20623, "trade alt 4"),
    (20624, "trade alt 5"),
    (20625, "trade alt 6"),
    (20626, "trade alt 7"),
    (20627, "trade alt 8"),
]

# 4. Population components 17-10-0040-01
# Natural increase, net immigration
pop_comp_coords = [
    ("1.1", "Canada, Natural increase"),
    ("1.2", "Canada, Net immigration"),
    ("1.3", "Canada, member 3"),
    ("1.4", "Canada, member 4"),
    ("1.5", "Canada, member 5"),
    ("1.6", "Canada, member 6"),
    ("1.7", "Canada, member 7"),
    ("1.8", "Canada, member 8"),
    ("1.9", "Canada, member 9"),
]
pop_comp_vectors = [
    (1400441, "pop comp 1"),
    (1400442, "pop comp 2"),
    (1400443, "pop comp 3"),
    (1400444, "pop comp 4"),
    (1400445, "pop comp 5"),
    (1400446, "pop comp 6"),
    (1400447, "pop comp 7"),
    (1400448, "pop comp 8"),
    (1400449, "pop comp 9"),
    (1400450, "pop comp 10"),
    (471601, "pop comp old 1"),
    (471602, "pop comp old 2"),
    (471603, "pop comp old 3"),
    (471604, "pop comp old 4"),
    (471605, "pop comp old 5"),
]

# 5. Population by age group 17-10-0009-01
# Canada, quarterly
pop_age_coords = [
    ("1.1.1", "Canada, All ages, Both sexes"),
    ("1.1.2", "Canada, All ages, Males"),
    ("1.1.3", "Canada, All ages, Females"),
    ("1.2.1", "Canada, 0-14, Both sexes"),
    ("1.3.1", "Canada, 15-24, Both sexes"),
    ("1.4.1", "Canada, 25-44, Both sexes"),
    ("1.5.1", "Canada, 45-64, Both sexes"),
    ("1.6.1", "Canada, 65+, Both sexes"),
    ("1.1", "Canada, member 1"),
    ("1.2", "Canada, member 2"),
    ("1.3", "Canada, member 3"),
    ("1.4", "Canada, member 4"),
    ("1.5", "Canada, member 5"),
    ("1.6", "Canada, member 6"),
    ("1.7", "Canada, member 7"),
    ("1.8", "Canada, member 8"),
    ("1.9", "Canada, member 9"),
    ("1.10", "Canada, member 10"),
    ("1.11", "Canada, member 11"),
    ("1.12", "Canada, member 12"),
]
pop_age_vectors = [
    (1400001, "pop age 1"),
    (1400002, "pop age 2"),
    (1400003, "pop age 3"),
    (1400004, "pop age 4"),
    (1400005, "pop age 5"),
    (471501, "pop age old 1"),
    (471502, "pop age old 2"),
    (471503, "pop age old 3"),
    (471504, "pop age old 4"),
]

# 6. Labour force by age group 14-10-0027-01
# Participation rate, employment rate, Canada, monthly SA
lf_coords = [
    ("1.1.1.1.1", "Canada, 15+, Both, EPOP"),
    ("1.1.1.1.2", "Canada, 15+, Both, Participation"),
    ("1.1.1.1.3", "Canada, 15+, Both, Unemployment"),
    ("1.1.1", "Canada, both, total"),
    ("1.1.2", "Canada, m, total"),
    ("1.1.3", "Canada, f, total"),
    ("1.2.1", "Canada, 15-24, Both"),
    ("1.3.1", "Canada, 25-54, Both"),
    ("1.4.1", "Canada, 55+, Both"),
    ("1.1", "Canada, member 1"),
    ("1.2", "Canada, member 2"),
    ("1.3", "Canada, member 3"),
    ("1.4", "Canada, member 4"),
    ("1.5", "Canada, member 5"),
    ("1.6", "Canada, member 6"),
    ("1.7", "Canada, member 7"),
    ("1.8", "Canada, member 8"),
]
lf_vectors = [
    (2062809, "LF participation rate Canada"),
    (2062810, "LF EPOP Canada"),
    (2062811, "LF unemployment Canada"),
    (2064895, "LF v2 1"),
    (2064896, "LF v2 2"),
    (2064897, "LF v2 3"),
    (75001, "LF old 1"),
    (75002, "LF old 2"),
    (75003, "LF old 3"),
    (75004, "LF old 4"),
    (75005, "LF old 5"),
    (1406500, "LF alt 1"),
    (1406501, "LF alt 2"),
    (1406502, "LF alt 3"),
]


# ============================================================
# RUN ALL PROBES
# ============================================================

all_lines = []
all_lines.append("# StatsCan Vector Probe Results\n\n")
all_lines.append("**Date:** 2026-05-10\n\n")
all_lines.append("**Method:** WDS REST API — getCubeMetadata, getSeriesInfoFromCubePidCoord, getDataFromVectorsAndLatestNPeriods\n\n")
all_lines.append("---\n")

all_confirmed = []

tables = [
    ("34-10-0035-01", "Capacity utilization, total manufacturing, Canada, quarterly SA",
     cu_coords, cu_vectors),
    ("14-10-0022-01", "EI regular beneficiaries, total Canada, monthly SA",
     ei_coords, ei_vectors),
    ("12-10-0011-01", "Merchandise trade Canada-US exports/imports/balance, monthly C$",
     trade_coords, trade_vectors),
    ("17-10-0040-01", "Population components — natural increase, net immigration, quarterly",
     pop_comp_coords, pop_comp_vectors),
    ("17-10-0009-01", "Population by age group, Canada, quarterly",
     pop_age_coords, pop_age_vectors),
    ("14-10-0027-01", "Labour force by age/sex — participation rate + employment rate, monthly SA",
     lf_coords, lf_vectors),
]

for table_id, target_desc, coords, vectors in tables:
    print(f"\n=== Probing Table {table_id} ===")
    lines, confirmed = probe_table(table_id, target_desc, coords, vectors)
    all_lines.append(lines)
    all_confirmed.extend(confirmed)

# ============================================================
# CONFIRMED VECTORS SUMMARY
# ============================================================

all_lines.append("\n---\n\n## CONFIRMED VECTORS\n\n")

if all_confirmed:
    all_lines.append("| Series | Table | Vector ID | Frequency | Latest date | Latest value | CSV name |\n")
    all_lines.append("|--------|-------|-----------|-----------|-------------|--------------|----------|\n")
    for c in all_confirmed:
        freq_label = {6: "Quarterly", 9: "Monthly", 12: "Annual"}.get(c["freq"], str(c["freq"]))
        csv_name = c["series"].lower().replace(" ", "_").replace(",", "").replace("(", "").replace(")", "")[:40]
        all_lines.append(
            f"| {c['title'][:50]} | {c['table']} | {c['vector_id']} | {freq_label} | "
            f"{c['latest_date']} | {c['latest_value']} | {csv_name} |\n"
        )
else:
    all_lines.append("**No vectors confirmed via direct probes.** Review dimension trees above to identify correct coordinates.\n\n")

output_text = "".join(all_lines)
OUTPUT.write_text(output_text, encoding="utf-8")
print(f"\n\nResults written to {OUTPUT}")
print(f"Confirmed vectors: {len(all_confirmed)}")
for c in all_confirmed:
    print(f"  V{c['vector_id']}: {c['title']} ({c['table']}) latest={c['latest_date']}")
