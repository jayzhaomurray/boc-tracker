"""
Probe: 6 StatsCan tables — confirm vector IDs for BoC tracker
Date: 2026-05-10

Tables:
  1. 34-10-0035-01 — Capacity utilization, total manufacturing, Canada, quarterly, SA
  2. 14-10-0022-01 — EI regular beneficiaries, Canada, monthly, SA
  3. 12-10-0011-01 — Merchandise trade Canada-US bilateral, monthly, C$
  4. 17-10-0040-01 — Population components (natural increase, net immigration), quarterly
  5. 17-10-0009-01 — Population stock by age group, Canada, quarterly
  6. 14-10-0027-01 — Labour force by age+sex (participation + employment rate), Canada, monthly SA

Output: analyses/statcan_probe_results_2026_05_10.md
"""

import requests
import json

OUTPUT_PATH = "analyses/statcan_probe_results_2026_05_10.md"


# ---- API helpers ----

def get_cube_metadata(product_id: int) -> dict:
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata"
    r = requests.post(url, json=[{"productId": product_id}], timeout=30)
    r.raise_for_status()
    return r.json()[0]


def get_series_from_coord(product_id: int, coord: str) -> dict:
    url = (
        f"https://www150.statcan.gc.ca/t1/wds/rest/"
        f"getSeriesInfoFromCubePidCoord/{product_id}/{coord}"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        return data[0]
    return data


def fetch_vector_sample(vector_id: int, n: int = 3) -> list:
    url = (
        "https://www150.statcan.gc.ca/t1/wds/rest/"
        "getDataFromVectorsAndLatestNPeriods"
    )
    r = requests.post(
        url, json=[{"vectorId": vector_id, "latestN": n}], timeout=30
    )
    r.raise_for_status()
    payload = r.json()
    item = payload[0]
    if item.get("status") != "SUCCESS":
        return []
    pts = item["object"]["vectorDataPoint"]
    return [(p["refPer"], p["value"]) for p in pts]


def pid(table_str: str) -> int:
    """Convert '34-10-0035-01' -> 3410003501"""
    return int(table_str.replace("-", "")[:10])


# ---- Per-table probe logic ----

lines = []


def h(text):
    lines.append(text + "\n")


def probe_table(name, table_id, product_id, coord_list, note=""):
    """Run getCubeMetadata + coordinate lookups. Return list of confirmed dicts."""
    h(f"\n## Table {table_id} — {name}\n")
    if note:
        h(f"*Note: {note}*\n")

    confirmed = []

    # Step 1: cube metadata
    print(f"[{table_id}] getCubeMetadata pid={product_id}...")
    try:
        meta = get_cube_metadata(product_id)
        status = meta.get("status", "?")
        h(f"getCubeMetadata status: **{status}**\n")
        if status == "SUCCESS":
            obj = meta.get("object", {})
            h(f"Table title: {obj.get('cubeTitleEn', 'N/A')}")
            h(f"Frequency code: {obj.get('freq', 'N/A')}\n")
            dims = obj.get("dimension", [])
            for dim in dims:
                h(f"### Dimension: {dim.get('dimensionNameEn', 'N/A')}")
                for m in dim.get("member", [])[:60]:
                    h(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}")
                h("")
        else:
            h(f"Non-SUCCESS response: {meta}\n")
            return confirmed
    except Exception as e:
        h(f"getCubeMetadata ERROR: {e}\n")
        return confirmed

    # Step 2: coordinate lookups
    h("### Coordinate lookups\n")
    for coord, label in coord_list:
        print(f"  coord {coord} ({label})...")
        try:
            resp = get_series_from_coord(product_id, coord)
            s = resp.get("status", "?")
            if s == "SUCCESS":
                obj = resp.get("object", {})
                vid = obj.get("vectorId")
                title = obj.get("SeriesTitleEn", "N/A")
                freq = obj.get("frequencyCode", "N/A")
                h(f"**Coord {coord}** ({label}): vectorId=**{vid}**")
                h(f"  Title: {title}")
                h(f"  Frequency code: {freq}")
                if vid:
                    pts = fetch_vector_sample(int(vid), 3)
                    h(f"  Latest 3 data points: {pts}")
                    if pts:
                        confirmed.append({
                            "label": label,
                            "table": table_id,
                            "vector_id": vid,
                            "freq": freq,
                            "latest_date": pts[-1][0] if pts else "N/A",
                            "latest_value": pts[-1][1] if pts else "N/A",
                            "title": title,
                        })
                h("")
            else:
                h(f"Coord {coord}: {s}")
                h("")
        except Exception as e:
            h(f"Coord {coord}: ERROR — {e}")
            h("")

    return confirmed


# ====================================================================
# TABLE 1: Capacity utilization — 34-10-0035-01
# product_id candidates: 3410003501
# Dimensions from prior probes: Geography x Industry
# Canada=1, need to find total manufacturing
# ====================================================================

# From prior probe the getCubeMetadata returned 406 for 3410003501.
# Try alternate product ID forms including with the 01 suffix stripped differently
cap_util_pids = [3410003501, 341000350101, 3410003500, 34100035]

# Also try the StatsCan web endpoint style (no trailing -01)
cap_util_confirmed = []

lines.append("# StatsCan 6-Table Probe Results\n")
lines.append("Date: 2026-05-10\n\n")
lines.append(
    "Probing 6 tables via StatsCan WDS REST API to confirm vector IDs.\n\n"
)

# ---- Table 1: Capacity Utilization ----
lines.append("---\n")
lines.append("\n## Table 1: 34-10-0035-01 — Capacity Utilization, Total Manufacturing\n\n")

print("TABLE 1: Capacity utilization (34-10-0035-01)")
working_pid_1 = None
for pid_try in [3410003501, 341000350101]:
    print(f"  Trying pid={pid_try}...")
    try:
        meta = get_cube_metadata(pid_try)
        status = meta.get("status", "?")
        lines.append(f"getCubeMetadata pid={pid_try}: **{status}**\n")
        if status == "SUCCESS":
            working_pid_1 = pid_try
            obj = meta.get("object", {})
            lines.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
            lines.append(f"Frequency code: {obj.get('freq', 'N/A')}\n\n")
            dims = obj.get("dimension", [])
            for dim in dims:
                lines.append(f"**Dimension: {dim.get('dimensionNameEn', 'N/A')}**\n")
                for m in dim.get("member", [])[:50]:
                    lines.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
                lines.append("\n")
            break
        else:
            lines.append(f"  Non-SUCCESS: {meta}\n\n")
    except Exception as e:
        lines.append(f"  ERROR pid={pid_try}: {e}\n\n")

cap_util_confirmed = []
if working_pid_1:
    # Canada=1, need to find total manufacturing
    # Typical structure: dim1=Geography(Canada=1), dim2=Industry
    # Manufacturing total is usually first or last member
    cap_coords = [
        ("1.1", "Canada, industry member 1"),
        ("1.2", "Canada, industry member 2"),
        ("1.3", "Canada, industry member 3"),
        ("1.4", "Canada, industry member 4"),
        ("1.5", "Canada, industry member 5"),
        ("1.6", "Canada, industry member 6"),
        ("1.7", "Canada, industry member 7"),
        ("1.8", "Canada, industry member 8"),
        ("1.9", "Canada, industry member 9"),
        ("1.10", "Canada, industry member 10"),
        ("1.11", "Canada, industry member 11"),
        ("1.12", "Canada, industry member 12"),
        ("1.13", "Canada, industry member 13"),
        ("1.14", "Canada, industry member 14"),
        ("1.15", "Canada, industry member 15"),
    ]
    lines.append("**Coordinate lookups:**\n\n")
    for coord, label in cap_coords:
        print(f"  coord {coord}...")
        try:
            resp = get_series_from_coord(working_pid_1, coord)
            s = resp.get("status", "?")
            if s == "SUCCESS":
                obj = resp.get("object", {})
                vid = obj.get("vectorId")
                title = obj.get("SeriesTitleEn", "N/A")
                freq = obj.get("frequencyCode", "N/A")
                lines.append(f"Coord {coord}: vectorId={vid}\n")
                lines.append(f"  Title: {title}\n")
                lines.append(f"  FreqCode: {freq}\n")
                if vid:
                    pts = fetch_vector_sample(int(vid), 3)
                    lines.append(f"  Latest 3: {pts}\n")
                    if pts:
                        cap_util_confirmed.append({
                            "label": label,
                            "table": "34-10-0035-01",
                            "vector_id": vid,
                            "freq": freq,
                            "latest_date": pts[-1][0],
                            "latest_value": pts[-1][1],
                            "title": title,
                        })
                lines.append("\n")
            else:
                lines.append(f"Coord {coord}: {s}\n\n")
        except Exception as e:
            lines.append(f"Coord {coord}: ERROR — {e}\n\n")
else:
    lines.append("FAILED: No working product ID found for 34-10-0035-01\n\n")
    # Fallback: try known vector IDs from StatsCan documentation
    lines.append("**Fallback: direct vector scan for capacity utilization, total manufacturing Canada**\n\n")
    # StatsCan capacity util table 34-10-0035-01 known vectors from public docs
    # Try range around v41707257 which appears in some StatsCan references
    fallback_vids = [
        41707257, 41707258, 41707259, 41707260, 41707261,
        41707262, 41707263, 41707264, 41707265, 41707266,
        # older series
        1400065, 1400066, 1400067, 1400068, 1400069, 1400070,
        # StatsCan v-number style
        36815, 36816, 36817, 36818, 36819, 36820,
    ]
    print("  Trying fallback vector scan for capacity utilization...")
    for vid in fallback_vids:
        try:
            url = "https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromVector"
            r = requests.post(url, json=[{"vectorId": vid}], timeout=20)
            r.raise_for_status()
            info = r.json()[0]
            s = info.get("status", "?")
            if s == "SUCCESS":
                obj = info.get("object", {})
                title = obj.get("SeriesTitleEn") or ""
                freq = obj.get("frequencyCode", "N/A")
                lines.append(f"Vector {vid}: {title} | Freq={freq}\n")
                if any(kw in title.lower() for kw in ["capacity", "utiliz", "manufactur", "total"]):
                    pts = fetch_vector_sample(vid, 3)
                    lines.append(f"  ** MATCH — Latest 3: {pts}\n")
                    if pts:
                        cap_util_confirmed.append({
                            "label": "Total manufacturing capacity utilization, Canada, SA",
                            "table": "34-10-0035-01",
                            "vector_id": vid,
                            "freq": freq,
                            "latest_date": pts[-1][0],
                            "latest_value": pts[-1][1],
                            "title": title,
                        })
        except Exception as e:
            lines.append(f"Vector {vid}: ERROR — {e}\n")
        lines.append("\n")


# ====================================================================
# TABLE 2: EI regular beneficiaries — 14-10-0022-01
# product_id: 1410002201
# Need: Canada total, regular benefits, SA
# ====================================================================

lines.append("---\n")
lines.append("\n## Table 2: 14-10-0022-01 — EI Regular Beneficiaries\n\n")
print("\nTABLE 2: EI regular beneficiaries (14-10-0022-01)")

ei_pid = 1410002201
ei_confirmed = []

for pid_try in [ei_pid, 141000220101]:
    print(f"  Trying pid={pid_try}...")
    try:
        meta = get_cube_metadata(pid_try)
        status = meta.get("status", "?")
        lines.append(f"getCubeMetadata pid={pid_try}: **{status}**\n")
        if status == "SUCCESS":
            obj = meta.get("object", {})
            lines.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
            lines.append(f"Frequency code: {obj.get('freq', 'N/A')}\n\n")
            dims = obj.get("dimension", [])
            dim_info = {}
            for dim in dims:
                dname = dim.get("dimensionNameEn", "N/A")
                lines.append(f"**Dimension: {dname}**\n")
                members = {}
                for m in dim.get("member", []):
                    mid = m.get("memberId")
                    mname = m.get("memberNameEn", "")
                    members[mname.lower()] = mid
                    lines.append(f"  - [{mid}] {mname}\n")
                dim_info[dname] = members
                lines.append("\n")

            # Build coordinate candidates
            # Typical structure for 14-10-0022:
            # Dim1: Geography (Canada=1)
            # Dim2: Type of beneficiary (regular=1 or similar)
            # Dim3: Sex (total=1)
            # Dim4: Seasonal adjustment (SA=2 or similar)
            # Try all first members for Canada
            ei_coords = []
            # Try combos: geography=1 (Canada), benefit type variations, sex=1, adj variations
            for b in range(1, 6):   # benefit type
                for s in range(1, 3):  # sex
                    for a in range(1, 4):  # seasonal adj
                        ei_coords.append((f"1.{b}.{s}.{a}", f"Canada,type{b},sex{s},adj{a}"))

            lines.append("**Coordinate lookups (sampling key combos):**\n\n")
            for coord, label in ei_coords[:30]:  # limit to avoid too many calls
                print(f"  coord {coord}...")
                try:
                    resp = get_series_from_coord(ei_pid, coord)
                    s = resp.get("status", "?")
                    if s == "SUCCESS":
                        obj2 = resp.get("object", {})
                        vid = obj2.get("vectorId")
                        title = obj2.get("SeriesTitleEn", "N/A")
                        freq = obj2.get("frequencyCode", "N/A")
                        lines.append(f"Coord {coord}: vectorId={vid}\n")
                        lines.append(f"  Title: {title}\n")
                        lines.append(f"  FreqCode: {freq}\n")
                        if vid:
                            pts = fetch_vector_sample(int(vid), 3)
                            lines.append(f"  Latest 3: {pts}\n")
                            if pts and any(kw in (title or "").lower() for kw in
                                          ["regular", "beneficiar", "canada", "regular benefits"]):
                                ei_confirmed.append({
                                    "label": label,
                                    "table": "14-10-0022-01",
                                    "vector_id": vid,
                                    "freq": freq,
                                    "latest_date": pts[-1][0],
                                    "latest_value": pts[-1][1],
                                    "title": title,
                                })
                        lines.append("\n")
                    else:
                        pass  # skip non-success quietly to reduce noise
                except Exception as e:
                    lines.append(f"Coord {coord}: ERROR — {e}\n\n")
            break
        else:
            lines.append(f"  Non-SUCCESS: {meta}\n\n")
    except Exception as e:
        lines.append(f"  ERROR pid={pid_try}: {e}\n\n")


# ====================================================================
# TABLE 3: Merchandise trade 12-10-0011-01
# product_id: 1210001101
# Prior probe got SUCCESS and showed dimensions:
#   Geography(Canada=1), Trade(Import=1,Export=2,Balance=3),
#   Basis(Customs=1,BOP=2), SeasonalAdj(Unadj=1,SA=2),
#   Partners(AllCountries=1, UnitedStates=2)
# We want: Canada, Export/Import/Balance, Customs, SA, US
# Coordinates: 1.2.1.2.2 (exports, customs, SA, US)
#              1.1.1.2.2 (imports, customs, SA, US)
#              1.3.1.2.2 (balance, customs, SA, US)
# ====================================================================

lines.append("---\n")
lines.append("\n## Table 3: 12-10-0011-01 — Merchandise Trade, Canada-US Bilateral\n\n")
print("\nTABLE 3: Merchandise trade (12-10-0011-01)")

trade_pid = 1210001101
trade_confirmed = []

for pid_try in [trade_pid, 121000110101]:
    print(f"  Trying pid={pid_try}...")
    try:
        meta = get_cube_metadata(pid_try)
        status = meta.get("status", "?")
        lines.append(f"getCubeMetadata pid={pid_try}: **{status}**\n")
        if status == "SUCCESS":
            obj = meta.get("object", {})
            lines.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
            lines.append(f"Frequency code: {obj.get('freq', 'N/A')}\n\n")
            dims = obj.get("dimension", [])
            for dim in dims:
                lines.append(f"**Dimension: {dim.get('dimensionNameEn', 'N/A')}**\n")
                for m in dim.get("member", [])[:30]:
                    lines.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
                lines.append("\n")

            # From prior probe (2026-05-09) the confirmed dimension structure:
            # Dim1: Geography — Canada=1
            # Dim2: Trade — Import=1, Export=2, Balance=3
            # Dim3: Basis — Customs=1, BOP=2
            # Dim4: Seasonal adjustment — Unadjusted=1, SA=2
            # Dim5: Principal trading partners — AllCountries=1, UnitedStates=2
            trade_coords = [
                ("1.2.1.2.2", "Canada, Exports, Customs, SA, United States"),
                ("1.1.1.2.2", "Canada, Imports, Customs, SA, United States"),
                ("1.3.1.2.2", "Canada, Trade Balance, Customs, SA, United States"),
                ("1.2.1.2.1", "Canada, Exports, Customs, SA, All Countries"),
                ("1.1.1.2.1", "Canada, Imports, Customs, SA, All Countries"),
                ("1.3.1.2.1", "Canada, Trade Balance, Customs, SA, All Countries"),
            ]
            lines.append("**Coordinate lookups:**\n\n")
            for coord, label in trade_coords:
                print(f"  coord {coord} ({label})...")
                try:
                    resp = get_series_from_coord(trade_pid, coord)
                    s = resp.get("status", "?")
                    if s == "SUCCESS":
                        obj2 = resp.get("object", {})
                        vid = obj2.get("vectorId")
                        title = obj2.get("SeriesTitleEn", "N/A")
                        freq = obj2.get("frequencyCode", "N/A")
                        lines.append(f"Coord {coord} ({label}): vectorId={vid}\n")
                        lines.append(f"  Title: {title}\n")
                        lines.append(f"  FreqCode: {freq}\n")
                        if vid:
                            pts = fetch_vector_sample(int(vid), 3)
                            lines.append(f"  Latest 3: {pts}\n")
                            if pts:
                                trade_confirmed.append({
                                    "label": label,
                                    "table": "12-10-0011-01",
                                    "vector_id": vid,
                                    "freq": freq,
                                    "latest_date": pts[-1][0],
                                    "latest_value": pts[-1][1],
                                    "title": title,
                                })
                        lines.append("\n")
                    else:
                        lines.append(f"Coord {coord}: {s}\n\n")
                except Exception as e:
                    lines.append(f"Coord {coord}: ERROR — {e}\n\n")
            break
        else:
            lines.append(f"  Non-SUCCESS: {meta}\n\n")
    except Exception as e:
        lines.append(f"  ERROR pid={pid_try}: {e}\n\n")


# ====================================================================
# TABLE 4: Population components — 17-10-0040-01
# product_id: 1710004001
# Need: Natural increase, Net immigration; Canada; quarterly
# ====================================================================

lines.append("---\n")
lines.append("\n## Table 4: 17-10-0040-01 — Population Components (Natural Increase, Net Immigration)\n\n")
print("\nTABLE 4: Population components (17-10-0040-01)")

pop_comp_pid = 1710004001
pop_comp_confirmed = []

for pid_try in [pop_comp_pid, 171000400101]:
    print(f"  Trying pid={pid_try}...")
    try:
        meta = get_cube_metadata(pid_try)
        status = meta.get("status", "?")
        lines.append(f"getCubeMetadata pid={pid_try}: **{status}**\n")
        if status == "SUCCESS":
            obj = meta.get("object", {})
            lines.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
            lines.append(f"Frequency code: {obj.get('freq', 'N/A')}\n\n")
            dims = obj.get("dimension", [])
            dim_member_map = {}
            for dim in dims:
                dname = dim.get("dimensionNameEn", "N/A")
                lines.append(f"**Dimension: {dname}**\n")
                members_list = dim.get("member", [])
                dim_member_map[dname] = {m.get("memberNameEn", "").lower(): m.get("memberId") for m in members_list}
                for m in members_list[:40]:
                    lines.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
                lines.append("\n")

            # Enumerate coordinates for Canada + each component member
            # Geography Canada=1, Components vary — try all component IDs
            pop_comp_coords = []
            # Find geography dim and component dim
            for dname, mmap in dim_member_map.items():
                if "component" in dname.lower() or "growth" in dname.lower():
                    for mname, mid in mmap.items():
                        pop_comp_coords.append(
                            (f"1.{mid}", f"Canada, {mname}")
                        )
                    break

            if not pop_comp_coords:
                # fallback: try numeric coords
                for i in range(1, 20):
                    pop_comp_coords.append((f"1.{i}", f"Canada, component {i}"))

            lines.append("**Coordinate lookups:**\n\n")
            for coord, label in pop_comp_coords[:25]:
                print(f"  coord {coord} ({label})...")
                try:
                    resp = get_series_from_coord(pop_comp_pid, coord)
                    s = resp.get("status", "?")
                    if s == "SUCCESS":
                        obj2 = resp.get("object", {})
                        vid = obj2.get("vectorId")
                        title = obj2.get("SeriesTitleEn", "N/A")
                        freq = obj2.get("frequencyCode", "N/A")
                        lines.append(f"Coord {coord} ({label}): vectorId={vid}\n")
                        lines.append(f"  Title: {title}\n")
                        lines.append(f"  FreqCode: {freq}\n")
                        if vid:
                            pts = fetch_vector_sample(int(vid), 3)
                            lines.append(f"  Latest 3: {pts}\n")
                            if pts:
                                pop_comp_confirmed.append({
                                    "label": label,
                                    "table": "17-10-0040-01",
                                    "vector_id": vid,
                                    "freq": freq,
                                    "latest_date": pts[-1][0],
                                    "latest_value": pts[-1][1],
                                    "title": title,
                                })
                        lines.append("\n")
                    else:
                        lines.append(f"Coord {coord}: {s}\n\n")
                except Exception as e:
                    lines.append(f"Coord {coord}: ERROR — {e}\n\n")
            break
        else:
            lines.append(f"  Non-SUCCESS: {meta}\n\n")
    except Exception as e:
        lines.append(f"  ERROR pid={pid_try}: {e}\n\n")


# ====================================================================
# TABLE 5: Population stock by age group — 17-10-0009-01
# product_id: 1710000901
# From prior probe: structure confirmed, vector 1 = Canada total population
# Need: Canada total + age group breakdown
# Prior result: Vector 1 = Canada population = 41,472,081 (2026-01-01)
# ====================================================================

lines.append("---\n")
lines.append("\n## Table 5: 17-10-0009-01 — Population Stock by Age Group\n\n")
print("\nTABLE 5: Population stock by age group (17-10-0009-01)")

pop_stock_pid = 1710000901
pop_stock_confirmed = []

for pid_try in [pop_stock_pid, 171000090101]:
    print(f"  Trying pid={pid_try}...")
    try:
        meta = get_cube_metadata(pid_try)
        status = meta.get("status", "?")
        lines.append(f"getCubeMetadata pid={pid_try}: **{status}**\n")
        if status == "SUCCESS":
            obj = meta.get("object", {})
            lines.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
            lines.append(f"Frequency code: {obj.get('freq', 'N/A')}\n\n")
            dims = obj.get("dimension", [])
            dim_names = []
            dim_member_counts = []
            for dim in dims:
                dname = dim.get("dimensionNameEn", "N/A")
                members_list = dim.get("member", [])
                dim_names.append(dname)
                dim_member_counts.append(len(members_list))
                lines.append(f"**Dimension: {dname}** ({len(members_list)} members)\n")
                for m in members_list[:50]:
                    lines.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
                lines.append("\n")

            # Prior probe confirms: dim1=Geography(Canada=1), dim2=Age groups
            # Vector 1 confirmed = Canada total population
            # Build coords for Canada + various age groups
            # Try to get age group members from metadata
            age_dim = None
            for dim in dims:
                dname = dim.get("dimensionNameEn", "")
                if "age" in dname.lower():
                    age_dim = dim
                    break

            pop_stock_coords = []
            if age_dim:
                for m in age_dim.get("member", [])[:30]:
                    mid = m.get("memberId")
                    mname = m.get("memberNameEn", "")
                    pop_stock_coords.append((f"1.{mid}", f"Canada, {mname}"))
            else:
                for i in range(1, 30):
                    pop_stock_coords.append((f"1.{i}", f"Canada, age group {i}"))

            lines.append("**Coordinate lookups:**\n\n")
            for coord, label in pop_stock_coords[:30]:
                print(f"  coord {coord} ({label})...")
                try:
                    resp = get_series_from_coord(pop_stock_pid, coord)
                    s = resp.get("status", "?")
                    if s == "SUCCESS":
                        obj2 = resp.get("object", {})
                        vid = obj2.get("vectorId")
                        title = obj2.get("SeriesTitleEn", "N/A")
                        freq = obj2.get("frequencyCode", "N/A")
                        lines.append(f"Coord {coord} ({label}): vectorId={vid}\n")
                        lines.append(f"  Title: {title}\n")
                        lines.append(f"  FreqCode: {freq}\n")
                        if vid:
                            pts = fetch_vector_sample(int(vid), 3)
                            lines.append(f"  Latest 3: {pts}\n")
                            if pts:
                                pop_stock_confirmed.append({
                                    "label": label,
                                    "table": "17-10-0009-01",
                                    "vector_id": vid,
                                    "freq": freq,
                                    "latest_date": pts[-1][0],
                                    "latest_value": pts[-1][1],
                                    "title": title,
                                })
                        lines.append("\n")
                    else:
                        lines.append(f"Coord {coord}: {s}\n\n")
                except Exception as e:
                    lines.append(f"Coord {coord}: ERROR — {e}\n\n")
            break
        else:
            lines.append(f"  Non-SUCCESS: {meta}\n\n")
    except Exception as e:
        lines.append(f"  ERROR pid={pid_try}: {e}\n\n")


# ====================================================================
# TABLE 6: Labour force by age group and sex — 14-10-0027-01
# product_id: 1410002701
# Need: Canada, participation rate + employment rate, total (age/sex), monthly SA
# ====================================================================

lines.append("---\n")
lines.append("\n## Table 6: 14-10-0027-01 — Labour Force by Age Group and Sex (Participation + Employment Rate)\n\n")
print("\nTABLE 6: Labour force by age group (14-10-0027-01)")

lf_pid = 1410002701
lf_confirmed = []

for pid_try in [lf_pid, 141000270101]:
    print(f"  Trying pid={pid_try}...")
    try:
        meta = get_cube_metadata(pid_try)
        status = meta.get("status", "?")
        lines.append(f"getCubeMetadata pid={pid_try}: **{status}**\n")
        if status == "SUCCESS":
            obj = meta.get("object", {})
            lines.append(f"Table title: {obj.get('cubeTitleEn', 'N/A')}\n")
            lines.append(f"Frequency code: {obj.get('freq', 'N/A')}\n\n")
            dims = obj.get("dimension", [])
            dim_info_lf = {}
            for dim in dims:
                dname = dim.get("dimensionNameEn", "N/A")
                lines.append(f"**Dimension: {dname}**\n")
                members_list = dim.get("member", [])
                dim_info_lf[dname] = {m.get("memberNameEn", "").lower(): m.get("memberId") for m in members_list}
                for m in members_list[:40]:
                    lines.append(f"  - [{m.get('memberId')}] {m.get('memberNameEn', '')}\n")
                lines.append("\n")

            # Build coordinates for key series
            # Typical structure: Geography, LF characteristics, Sex, Age group
            # Canada=1, participation rate=8(?), employment rate=9(?), total sex=1, 15+ = 1
            # Try a range of coords to find participation rate and employment rate for Canada, total, 15+
            lf_coords = []

            # Get characteristic memberId for participation rate and employment rate
            char_dim_name = None
            char_part_id = None
            char_emp_id = None
            sex_total_id = None
            age_total_id = None

            for dname, mmap in dim_info_lf.items():
                if "characteristic" in dname.lower() or "labour force" in dname.lower():
                    char_dim_name = dname
                    char_part_id = mmap.get("participation rate")
                    char_emp_id = mmap.get("employment rate")
                elif "sex" in dname.lower() or "gender" in dname.lower():
                    sex_total_id = mmap.get("total - sex") or mmap.get("both sexes") or mmap.get("total - gender") or 1
                elif "age" in dname.lower():
                    age_total_id = (
                        mmap.get("15 years and over") or
                        mmap.get("total, 15 years and over") or
                        mmap.get("all ages") or
                        1
                    )

            # Build coords based on identified member IDs
            if char_part_id and sex_total_id and age_total_id:
                lf_coords = [
                    (f"1.{char_part_id}.{sex_total_id}.{age_total_id}",
                     "Canada, Participation rate, Total sex, 15+"),
                    (f"1.{char_emp_id}.{sex_total_id}.{age_total_id}",
                     "Canada, Employment rate, Total sex, 15+"),
                ]

            # Also try a broader sweep
            # Participation rate typically has high characteristic ID (8 or 9)
            extra_coords = []
            for char_i in range(6, 12):
                for sex_i in [1]:
                    for age_i in [1, 2]:
                        extra_coords.append(
                            (f"1.{char_i}.{sex_i}.{age_i}",
                             f"Canada, char{char_i}, sex{sex_i}, age{age_i}")
                        )
            lf_coords = lf_coords + extra_coords

            lines.append("**Coordinate lookups:**\n\n")
            for coord, label in lf_coords[:25]:
                print(f"  coord {coord} ({label})...")
                try:
                    resp = get_series_from_coord(lf_pid, coord)
                    s = resp.get("status", "?")
                    if s == "SUCCESS":
                        obj2 = resp.get("object", {})
                        vid = obj2.get("vectorId")
                        title = obj2.get("SeriesTitleEn", "N/A")
                        freq = obj2.get("frequencyCode", "N/A")
                        lines.append(f"Coord {coord} ({label}): vectorId={vid}\n")
                        lines.append(f"  Title: {title}\n")
                        lines.append(f"  FreqCode: {freq}\n")
                        if vid:
                            pts = fetch_vector_sample(int(vid), 3)
                            lines.append(f"  Latest 3: {pts}\n")
                            if pts:
                                lf_confirmed.append({
                                    "label": label,
                                    "table": "14-10-0027-01",
                                    "vector_id": vid,
                                    "freq": freq,
                                    "latest_date": pts[-1][0],
                                    "latest_value": pts[-1][1],
                                    "title": title,
                                })
                        lines.append("\n")
                    else:
                        lines.append(f"Coord {coord}: {s}\n\n")
                except Exception as e:
                    lines.append(f"Coord {coord}: ERROR — {e}\n\n")
            break
        else:
            lines.append(f"  Non-SUCCESS: {meta}\n\n")
    except Exception as e:
        lines.append(f"  ERROR pid={pid_try}: {e}\n\n")


# ====================================================================
# CONFIRMED VECTORS SUMMARY
# ====================================================================

all_confirmed = (
    cap_util_confirmed
    + ei_confirmed
    + trade_confirmed
    + pop_comp_confirmed
    + pop_stock_confirmed
    + lf_confirmed
)

lines.append("\n---\n")
lines.append("\n## CONFIRMED VECTORS — Summary Table\n\n")
lines.append(
    "| Series | Table | Vector ID | FreqCode | Latest date | Latest value | Suggested CSV name |\n"
)
lines.append(
    "|--------|-------|-----------|----------|-------------|--------------|--------------------|\n"
)

csv_name_map = {
    "34-10-0035-01": "capacity_util_mfg_sa",
    "14-10-0022-01": "ei_regular_beneficiaries_sa",
    "12-10-0011-01": "trade_canada_us",
    "17-10-0040-01": "pop_components_qtrly",
    "17-10-0009-01": "pop_by_age_qtrly",
    "14-10-0027-01": "lf_participation_employment_sa",
}

for c in all_confirmed:
    csv = csv_name_map.get(c["table"], "tbd")
    short_title = (c.get("title") or c.get("label") or "")[:60]
    lines.append(
        f"| {short_title} | {c['table']} | {c['vector_id']} | "
        f"{c['freq']} | {c['latest_date']} | {c['latest_value']} | {csv} |\n"
    )

if not all_confirmed:
    lines.append("| (no confirmed vectors yet) | | | | | | |\n")

lines.append("\n")

# Per-table status
lines.append("## Per-Table Status\n\n")
tables = [
    ("34-10-0035-01", "Capacity utilization, total manufacturing, SA", cap_util_confirmed),
    ("14-10-0022-01", "EI regular beneficiaries, Canada, SA", ei_confirmed),
    ("12-10-0011-01", "Merchandise trade, Canada-US bilateral", trade_confirmed),
    ("17-10-0040-01", "Population components (natural increase, net immigration)", pop_comp_confirmed),
    ("17-10-0009-01", "Population stock by age group", pop_stock_confirmed),
    ("14-10-0027-01", "Labour force by age group and sex (participation + employment rate)", lf_confirmed),
]
for tid, desc, confirmed_list in tables:
    status = "CONFIRMED" if confirmed_list else "NOT CONFIRMED"
    lines.append(f"- **{tid}** ({desc}): **{status}** — {len(confirmed_list)} vectors\n")

output_text = "".join(lines)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(output_text)

print(f"\nResults written to {OUTPUT_PATH}")
print(f"\nConfirmed vectors: {len(all_confirmed)}")
for c in all_confirmed:
    print(f"  [{c['table']}] vid={c['vector_id']} | {c.get('title', c.get('label', ''))[:70]} | latest={c['latest_date']} {c['latest_value']}")
