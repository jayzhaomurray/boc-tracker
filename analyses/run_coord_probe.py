"""
Coordinate-based probe for 6 StatsCan tables.
Runs after getCubeMetadata confirms correct product IDs.
"""

import requests
import time
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
}

BASE = "https://www150.statcan.gc.ca/t1/wds/rest"


def get_series(pid, coord):
    url = f"{BASE}/getSeriesInfoFromCubePidCoord/{pid}/{coord}"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        return data[0]
    return data


def fetch_sample(vid, n=3):
    url = f"{BASE}/getDataFromVectorsAndLatestNPeriods"
    r = requests.post(
        url, json=[{"vectorId": vid, "latestN": n}], headers=headers, timeout=30
    )
    r.raise_for_status()
    item = r.json()[0]
    if item.get("status") != "SUCCESS":
        return []
    pts = item["object"]["vectorDataPoint"]
    return [(p["refPer"], p["value"]) for p in pts]


results = {}


def probe_coord(pid, coord, label, key):
    try:
        resp = get_series(pid, coord)
        s = resp.get("status", "?")
        if s == "SUCCESS":
            obj = resp["object"]
            vid = obj.get("vectorId")
            title = obj.get("SeriesTitleEn", "N/A")
            freq = obj.get("frequencyCode")
            print(f"  Coord {coord} ({label}): vid={vid}")
            print(f"    Title: {title}")
            print(f"    Freq: {freq}")
            if vid:
                pts = fetch_sample(int(vid), 3)
                print(f"    Latest 3: {pts}")
                if pts:
                    results[key] = {
                        "pid": pid,
                        "label": label,
                        "vid": int(vid),
                        "title": title,
                        "freq": freq,
                        "pts": pts,
                    }
        else:
            print(f"  Coord {coord} ({label}): {s}")
    except Exception as e:
        print(f"  ERROR {coord}: {e}")
    time.sleep(0.25)


# =============================================================
# TABLE 1a: 16100109 - Industrial capacity utilization, quarterly
# Canada=1, Total industrial=1, Manufacturing=8
# =============================================================
print("=== TABLE 1: Capacity Utilization (16100109) ===")
probe_coord(16100109, "1.1", "Canada, Total industrial", "cu_total")
probe_coord(16100109, "1.8", "Canada, Manufacturing", "cu_mfg")
probe_coord(16100109, "1.9", "Canada, Food manufacturing", "cu_food")

# Also try 16100012 - Manufacturing capacity utilization by NAICS
# Dim1=Geography(Canada=1), Dim2=NAICS(Manufacturing=1), Dim3=PrincipalStats(CU rate=1)
print()
print("=== TABLE 1b: Manufacturing capacity utilization (16100012) ===")
probe_coord(16100012, "1.1.1", "Canada, Manufacturing, CU rate", "cu_mfg_16100012")
probe_coord(16100012, "1.1", "Canada, Manufacturing", "cu_mfg_16100012_nodim3")

print()

# =============================================================
# TABLE 2: 14100011 - EI regular beneficiaries, by province, monthly SA
# Canada=1, Regular benefits=2, Both sexes=1, 15+ years=1
# =============================================================
print("=== TABLE 2: EI Regular Beneficiaries (14100011) ===")
probe_coord(14100011, "1.2.1.1", "Canada, Regular benefits, Both sexes, 15+", "ei_total")
probe_coord(14100011, "1.2.2.1", "Canada, Regular benefits, Males, 15+", "ei_males")
probe_coord(14100011, "1.2.3.1", "Canada, Regular benefits, Females, 15+", "ei_females")
probe_coord(14100011, "1.16.1.1", "Canada, Reg benefits w/o earnings, Both, 15+", "ei_no_earnings")

print()

# =============================================================
# TABLE 3: 12100011 - Merchandise trade, monthly
# Canada=1, Import=1/Export=2/Balance=3, Customs=1, SA=2, US=2/All=1
# =============================================================
print("=== TABLE 3: Merchandise Trade (12100011) ===")
probe_coord(12100011, "1.2.1.2.2", "Canada, Exports, Customs, SA, US", "trade_exp_us")
probe_coord(12100011, "1.1.1.2.2", "Canada, Imports, Customs, SA, US", "trade_imp_us")
probe_coord(12100011, "1.3.1.2.2", "Canada, Trade Balance, Customs, SA, US", "trade_bal_us")
probe_coord(12100011, "1.2.1.2.1", "Canada, Exports, Customs, SA, All countries", "trade_exp_all")
probe_coord(12100011, "1.1.1.2.1", "Canada, Imports, Customs, SA, All countries", "trade_imp_all")
probe_coord(12100011, "1.3.1.2.1", "Canada, Trade Balance, Customs, SA, All countries", "trade_bal_all")

print()

# =============================================================
# TABLE 4: 17100040 - International migration components, quarterly
# Canada=1, Immigrants=1, Net emigration=6, Net NPR=5
# NOTE: This table does NOT have natural increase (births-deaths)
# Natural increase is in a different table
# =============================================================
print("=== TABLE 4: International Migration Components (17100040) ===")
probe_coord(17100040, "1.1", "Canada, Immigrants", "pop_immigrants")
probe_coord(17100040, "1.6", "Canada, Net emigration", "pop_net_emigration")
probe_coord(17100040, "1.2", "Canada, Emigrants", "pop_emigrants")
probe_coord(17100040, "1.3", "Canada, Returning emigrants", "pop_returning")
probe_coord(17100040, "1.4", "Canada, Net temporary emigration", "pop_net_temp_emig")
probe_coord(17100040, "1.5", "Canada, Net non-permanent residents", "pop_net_npr")
probe_coord(17100040, "1.7", "Canada, NPR inflows", "pop_npr_inflows")
probe_coord(17100040, "1.8", "Canada, NPR outflows", "pop_npr_outflows")

print()

# =============================================================
# TABLE 5: 17100009 - Population estimates, quarterly
# Need to check what dimensions are available (prior probe showed only Geography dim)
# =============================================================
print("=== TABLE 5: Population estimates (17100009) ===")
# Try various coords - since prior probe showed vector 1 = Canada total
probe_coord(17100009, "1", "Canada total", "pop_total")
probe_coord(17100009, "1.1", "Canada, dim2=1", "pop_1_1")
probe_coord(17100009, "1.2", "Canada, dim2=2", "pop_1_2")
probe_coord(17100009, "1.3", "Canada, dim2=3", "pop_1_3")

print()

# =============================================================
# TABLE 6: 14100287 - Labour force characteristics, monthly SA + trend-cycle
# Canada=1, characteristics: Population=1...Employment rate=9
# Gender: Total=1, Dim4 Age: 15+=1, Dim5 Stats: Estimate=1, Dim6 DataType: SA=1
# =============================================================
print("=== TABLE 6: Labour Force Characteristics (14100287) ===")
# Participation rate = characteristic 8
# Employment rate = characteristic 9
# Canada=1, char=8, Total gender=1, 15+ =1, Estimate=1, SA=1
probe_coord(14100287, "1.8.1.1.1.1", "Canada, Participation rate, Total, 15+, Estimate, SA", "lf_part_rate")
probe_coord(14100287, "1.9.1.1.1.1", "Canada, Employment rate, Total, 15+, Estimate, SA", "lf_emp_rate")
probe_coord(14100287, "1.7.1.1.1.1", "Canada, Unemployment rate, Total, 15+, Estimate, SA", "lf_unemp_rate")
probe_coord(14100287, "1.3.1.1.1.1", "Canada, Employment, Total, 15+, Estimate, SA", "lf_employment")
probe_coord(14100287, "1.8.1.6.1.1", "Canada, Participation rate, Total, 25-54, Estimate, SA", "lf_part_rate_prime")
probe_coord(14100287, "1.9.1.6.1.1", "Canada, Employment rate, Total, 25-54, Estimate, SA", "lf_emp_rate_prime")
probe_coord(14100287, "1.8.1.2.1.1", "Canada, Participation rate, Total, 15-24, Estimate, SA", "lf_part_rate_youth")
probe_coord(14100287, "1.9.1.2.1.1", "Canada, Employment rate, Total, 15-24, Estimate, SA", "lf_emp_rate_youth")

print()
print("=" * 60)
print("ALL CONFIRMED VECTORS:")
for k, v in results.items():
    latest = v["pts"][-1] if v["pts"] else ("N/A", "N/A")
    print(f"  {k}: vid={v['vid']} freq={v['freq']}")
    print(f"    Title: {v['title']}")
    print(f"    Latest: {latest[0]} = {latest[1]}")

# Save JSON for next step
with open("analyses/coord_probe_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print()
print("Saved to analyses/coord_probe_results.json")
