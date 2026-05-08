"""
Fetch data from public APIs and save to CSV files in the data/ folder.

Run:    python fetch.py           (one-shot)
        python fetch.py --wait    (poll StatsCan until new data appears — use on 8:30 AM runs)
Output: data/cpi_all_items.csv
        data/unemployment_rate.csv
        data/yield_2yr.csv
"""

import argparse
import json
import os
import time
import requests
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

MAX_RETRIES  = 10   # maximum StatsCan poll attempts before giving up
RETRY_DELAY  = 30   # seconds between retries

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")


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
    "cpi_all_items":       41690914,   # Table 18-10-0006-01: All-items CPI, Canada, SA (2002=100)
    "cpi_all_items_nsa":   41690973,   # Table 18-10-0004-01: All-items CPI, Canada, NSA (2002=100)
    "unemployment_rate":    2062815,   # Table 14-10-0287-01: Unemployment rate, Canada, SA (%)
    "lfs_wages_all":      105812645,   # Table 14-10-0320-02: LFS avg hourly wages, all employees 15+, SA
    "lfs_wages_permanent": 105812715,  # Table 14-10-0320-02: LFS avg hourly wages, permanent employees, SA
    "seph_earnings":       79311153,   # Table 14-10-0223-01: SEPH avg weekly earnings, all employees, Canada, SA
    "cpi_services":        41691230,   # Table 18-10-0004-01: CPI Services, Canada, NSA (2002=100)
    "cpi_food":            41690974,   # Table 18-10-0004-01: CPI Food, Canada, NSA (2002=100)
    "cpi_energy":          41691239,   # Table 18-10-0004-01: CPI Energy, Canada, NSA (2002=100)
    "cpi_goods":           41691222,   # Table 18-10-0004-01: CPI Goods, Canada, NSA (2002=100)
}

BOC_VALET_SERIES = {
    # 2-tuple: (series_key, start_date). 3-tuple: (series_key, start_date, scale_factor)
    # Scale factor is applied to the fetched values (e.g. 0.001 to convert millions to billions)
    "yield_2yr":      ("BD.CDN.2YR.DQ.YLD",    "1990-01-01"),  # 2-yr GoC benchmark bond yield, daily
    "overnight_rate": ("STATIC_ATABLE_V39079",  "1990-01-01"),  # BoC overnight rate target, monthly
    "cpi_trim":       ("CPI_TRIM",              "1990-01-01"),  # CPI-trim, Y/Y %, monthly
    "cpi_median":     ("CPI_MEDIAN",            "1990-01-01"),  # CPI-median, Y/Y %, monthly
    "cpi_common":     ("CPI_COMMON",            "1990-01-01"),  # CPI-common, Y/Y %, monthly
    "cpix":           ("ATOM_V41693242",        "1990-01-01"),  # CPIX (excl. 8 volatile), Y/Y %, monthly
    "cpixfet":          ("STATIC_CPIXFET",        "1990-01-01"),  # CPIXFET (excl. food & energy), Y/Y %, monthly
    "lfs_micro":        ("INDINF_LFSMICRO_M",    "2000-01-01"),  # BoC LFS-Micro composition-adjusted wage growth, Y/Y %, monthly
    # BoC balance sheet (Statement of Financial Position), weekly. Source values in CAD millions; rescaled to billions for display.
    "boc_total_assets":         ("V36610", "2000-01-01", 0.001),  # Total assets, weekly
    "boc_goc_bonds":            ("V36613", "2000-01-01", 0.001),  # GoC bonds held outright, weekly
    "boc_settlement_balances":  ("V36636", "2000-01-01", 0.001),  # Members of Payments Canada deposits (settlement balances), weekly
}

FRED_SERIES = {
    "us_2yr": ("DGS2",           "1990-01-01"),  # 2-yr US Treasury constant maturity, daily
    "usdcad": ("DEXCAUS",        "1990-01-01"),  # USD/CAD exchange rate (CAD per USD), daily
    "wti":    ("DCOILWTICO",     "1990-01-01"),  # WTI crude oil, USD/barrel, daily
    "brent":  ("DCOILBRENTEU",   "1990-01-01"),  # Brent crude oil, USD/barrel, daily
}
# fed_funds is fetched separately as target midpoint — see fetch_fed_funds_target()


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


def fetch_fred(series_id: str, start_date: str) -> pd.DataFrame:
    url = "https://api.stlouisfed.org/fred/series/observations"
    r = requests.get(url, params={
        "series_id": series_id,
        "observation_start": start_date,
        "api_key": FRED_API_KEY,
        "file_type": "json",
    }, timeout=30)
    r.raise_for_status()
    obs = r.json()["observations"]
    records = [
        {"date": o["date"], "value": float(o["value"])}
        for o in obs if o["value"] != "."
    ]
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def fetch_fed_funds_target() -> pd.DataFrame:
    """Fed funds target: FEDFUNDS monthly (pre-2008) + midpoint of DFEDTARU/DFEDTARL daily (post-2008)."""
    monthly = fetch_fred("FEDFUNDS", "1990-01-01")   # monthly effective rate ≈ target pre-2008
    upper   = fetch_fred("DFEDTARU", "2008-01-01")   # daily upper bound, from Dec 2008
    lower   = fetch_fred("DFEDTARL", "2008-01-01")   # daily lower bound, from Dec 2008
    mid = (
        upper.set_index("date")["value"]
        .add(lower.set_index("date")["value"])
        .div(2)
        .reset_index()
    )
    mid.columns = ["date", "value"]
    cutoff = mid["date"].min() if not mid.empty else pd.Timestamp("2008-12-16")
    pre = monthly[monthly["date"] < cutoff]
    combined = pd.concat([pre, mid]).sort_values("date").reset_index(drop=True)
    return combined


def fetch_cpi_components() -> pd.DataFrame:
    """Fetch all 60 CPI component series and return as a wide DataFrame (date × component)."""
    mapping_path = DATA_DIR / "cpi_breadth_mapping.json"
    if not mapping_path.exists():
        raise FileNotFoundError(
            f"Missing {mapping_path} — run the breadth mapping probe first."
        )
    with open(mapping_path) as f:
        mapping = json.load(f)

    vectors = [m["cpi_vector"] for m in mapping]
    names   = [m["name"]       for m in mapping]

    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
    r = requests.post(
        url,
        json=[{"vectorId": v, "latestN": 500} for v in vectors],
        timeout=120,
    )
    r.raise_for_status()
    payload = r.json()

    series: dict = {}
    for item, name in zip(payload, names):
        if item.get("status") != "SUCCESS":
            print(f"  Warning: '{name}' fetch failed — skipping.")
            continue
        pts = item["object"]["vectorDataPoint"]
        series[name] = pd.Series(
            {pd.Timestamp(p["refPer"]): pd.to_numeric(p["value"], errors="coerce")
             for p in pts},
            name=name,
        )

    df = pd.DataFrame(series)
    df.index.name = "date"
    return df.sort_index()


def fetch_wcs() -> pd.DataFrame:
    """Western Canada Select crude price (monthly) from Alberta Economic Dashboard API."""
    r = requests.get(
        "https://api.economicdata.alberta.ca/data?table=OilPrices",
        timeout=30,
    )
    r.raise_for_status()
    records = []
    for raw in r.json():
        item = {k.strip(): v for k, v in raw.items()}  # strip trailing whitespace from keys
        if item.get("Type") == "WCS":
            records.append({"date": item["Date"][:10], "value": item["Value"]})
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


# ── Retry helper ──────────────────────────────────────────────────────────────

def _latest_saved_date(path: Path) -> pd.Timestamp | None:
    """Return the latest date already saved in a CSV (long or wide format), or None."""
    if not path.exists():
        return None
    try:
        col = pd.read_csv(path, usecols=[0], parse_dates=True)
        return pd.to_datetime(col.iloc[:, 0]).max()
    except Exception:
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main(wait: bool = False):
    # Per-series fetches are isolated: a single source going down (network blip,
    # bad API key, schema change) prints a clear error and continues; existing
    # CSVs are preserved so the build still has data, just stale where the fetch
    # failed. The pipeline only fully fails if everything is broken.
    failed: list[str] = []

    def _safe(label: str, fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            # GitHub Actions annotation — renders as a red banner in the run UI.
            print(f"::error title=Fetch failed: {label}::{msg}")
            print(f"  ERROR fetching {label}: {msg}")
            print(f"  Existing {label}.csv (if any) preserved; build will use stale data.")
            failed.append(label)
            return None

    for name, vector_id in STATSCAN_SERIES.items():
        path = DATA_DIR / f"{name}.csv"
        prior = _latest_saved_date(path) if wait else None
        print(f"Fetching {name} from Statistics Canada...")
        df = None
        for attempt in range(MAX_RETRIES):
            df = _safe(name, fetch_statscan, vector_id)
            if df is None:
                break  # error already reported; stop retrying
            if prior is None or df["date"].max() > prior:
                break
            if attempt < MAX_RETRIES - 1:
                print(f"  No update yet (latest: {df['date'].max().date()}), "
                      f"retrying in {RETRY_DELAY}s [{attempt + 1}/{MAX_RETRIES}]")
                time.sleep(RETRY_DELAY)
        else:
            print(f"  No new data after {MAX_RETRIES} attempts, proceeding.")
        if df is not None:
            df.to_csv(path, index=False)
            print(f"  -> {len(df)} rows saved to {path}")

    for name, entry in BOC_VALET_SERIES.items():
        series_key = entry[0]
        start_date = entry[1]
        scale      = entry[2] if len(entry) > 2 else 1.0
        print(f"Fetching {name} from Bank of Canada Valet API...")
        df = _safe(name, fetch_boc_valet, series_key, start_date)
        if df is None:
            continue
        if scale != 1.0:
            df["value"] = df["value"] * scale
        path = DATA_DIR / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"  -> {len(df)} rows saved to {path}")

    if FRED_API_KEY:
        print("Fetching fed_funds (target midpoint) from FRED...")
        df = _safe("fed_funds", fetch_fed_funds_target)
        if df is not None:
            path = DATA_DIR / "fed_funds.csv"
            df.to_csv(path, index=False)
            print(f"  -> {len(df)} rows saved to {path}")

        for name, (series_id, start_date) in FRED_SERIES.items():
            print(f"Fetching {name} from FRED...")
            df = _safe(name, fetch_fred, series_id, start_date)
            if df is None:
                continue
            path = DATA_DIR / f"{name}.csv"
            df.to_csv(path, index=False)
            print(f"  -> {len(df)} rows saved to {path}")
    else:
        print("Skipping FRED series (FRED_API_KEY not set).")

    print("Fetching wcs (Western Canada Select) from Alberta Economic Dashboard...")
    df = _safe("wcs", fetch_wcs)
    if df is not None:
        path = DATA_DIR / "wcs.csv"
        df.to_csv(path, index=False)
        print(f"  -> {len(df)} rows saved to {path}")

    path = DATA_DIR / "cpi_components.csv"
    prior = _latest_saved_date(path) if wait else None
    print("Fetching CPI components (breadth chart)...")
    df = None
    for attempt in range(MAX_RETRIES):
        df = _safe("cpi_components", fetch_cpi_components)
        if df is None:
            break
        if prior is None or df.index.max() > prior:
            break
        if attempt < MAX_RETRIES - 1:
            print(f"  No update yet (latest: {df.index.max().date()}), "
                  f"retrying in {RETRY_DELAY}s [{attempt + 1}/{MAX_RETRIES}]")
            time.sleep(RETRY_DELAY)
    else:
        print(f"  No new data after {MAX_RETRIES} attempts, proceeding.")
    if df is not None:
        df.to_csv(path)
        print(f"  -> {len(df)} months × {len(df.columns)} components saved to {path}")

    if failed:
        print()
        print("=" * 60)
        print(f"WARNING: {len(failed)} series failed to fetch:")
        for name in failed:
            print(f"  - {name}")
        print("Existing CSVs preserved; build will use stale data for those.")
        print("=" * 60)

    print("\nDone. Run build.py to regenerate index.html.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--wait", action="store_true",
        help="Poll StatsCan until new data appears (use on scheduled 8:30 AM ET runs)",
    )
    main(wait=parser.parse_args().wait)
