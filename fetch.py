"""
Fetch data from public APIs and save to CSV files in the data/ folder.

Run:    python fetch.py
Output: data/cpi_all_items.csv
        data/unemployment_rate.csv
        data/yield_2yr.csv
"""

import requests
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


# ── Series configuration ──────────────────────────────────────────────────────
#
# STATSCAN_SERIES
#   Key:   filename for the saved CSV (e.g. "wage_growth" -> data/wage_growth.csv)
#   Value: Statistics Canada WDS vector ID
#          Find vectors at: www150.statcan.gc.ca — navigate to a table, click a
#          series, and look for the "Vector" identifier (format: V + numbers).
#
# BOC_VALET_SERIES
#   Key:   filename for the saved CSV
#   Value: (series_key, start_date)
#          Browse all series keys at: bankofcanada.ca/valet/lists/series/json

STATSCAN_SERIES = {
    "cpi_all_items":     41690914,  # Table 18-10-0006-01: All-items CPI, Canada, not SA (2002=100)
    "unemployment_rate": 2062815,   # Table 14-10-0287-01: Unemployment rate, Canada, SA (%)
}

BOC_VALET_SERIES = {
    "yield_2yr":  ("BD.CDN.2YR.DQ.YLD",  "1990-01-01"),  # 2-yr GoC benchmark bond yield, daily
    "cpi_trim":   ("CPI_TRIM",            "1990-01-01"),  # CPI-trim, Y/Y %, monthly
    "cpi_median": ("CPI_MEDIAN",          "1990-01-01"),  # CPI-median, Y/Y %, monthly
    "cpi_common": ("CPI_COMMON",          "1990-01-01"),  # CPI-common, Y/Y %, monthly
    "cpix":       ("ATOM_V41693242",      "1990-01-01"),  # CPIX (excl. 8 volatile), Y/Y %, monthly
    "cpixfet":    ("STATIC_CPIXFET",      "1990-01-01"),  # CPIXFET (excl. food & energy), Y/Y %, monthly
}


# ── Fetchers ──────────────────────────────────────────────────────────────────

def fetch_statscan(vector_id: int, n_periods: int = 10000) -> pd.DataFrame:
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
    r = requests.post(
        url,
        json=[{"vectorId": vector_id, "latestN": n_periods}],
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()

    item = payload[0]
    if item.get("status") != "SUCCESS":
        raise ValueError(f"StatsCan error for vector {vector_id}:\n{item}")

    points = item["object"]["vectorDataPoint"]
    df = pd.DataFrame(points)[["refPer", "value"]].copy()
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna().sort_values("date").reset_index(drop=True)


def fetch_boc_valet(series_key: str, start_date: str) -> pd.DataFrame:
    url = f"https://www.bankofcanada.ca/valet/observations/{series_key}/json"
    r = requests.get(url, params={"start_date": start_date}, timeout=30)
    r.raise_for_status()
    payload = r.json()

    if "observations" not in payload:
        raise ValueError(
            f"BoC Valet returned no observations for '{series_key}'.\n"
            f"Check the key at: https://www.bankofcanada.ca/valet/lists/series/json"
        )

    records = [
        {"date": ob["d"], "value": float(ob[series_key]["v"])}
        for ob in payload["observations"]
        if ob.get(series_key, {}).get("v") is not None
    ]
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    for name, vector_id in STATSCAN_SERIES.items():
        print(f"Fetching {name} from Statistics Canada...")
        df = fetch_statscan(vector_id)
        path = DATA_DIR / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"  -> {len(df)} rows saved to {path}")

    for name, (series_key, start_date) in BOC_VALET_SERIES.items():
        print(f"Fetching {name} from Bank of Canada Valet API...")
        df = fetch_boc_valet(series_key, start_date)
        path = DATA_DIR / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"  -> {len(df)} rows saved to {path}")

    print("\nDone. Run build.py to regenerate index.html.")


if __name__ == "__main__":
    main()
