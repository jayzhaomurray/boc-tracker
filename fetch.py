"""
Fetch data from public APIs and save to CSV files in the data/ folder.

Run:    python fetch.py           (one-shot)
        python fetch.py --wait    (poll StatsCan until new data appears — use on 8:30 AM runs)
Output: data/cpi_all_items.csv
        data/unemployment_rate.csv
        data/yield_2yr.csv
"""

import argparse
import io
import json
import os
import re
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
#   Value: Statistics Canada WDS vector ID (int), OR a 2-tuple (vector_id, scale_factor).
#          Scale factor is multiplied into the fetched values on every future fetch
#          (e.g. 0.000001 to convert millions to trillions).
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
    "cpi_shelter":         41691050,   # Table 18-10-0004-01: CPI Shelter, Canada, NSA (2002=100)
    # GDP / Activity section (added May 2026)
    # gdp_monthly: StatsCan publishes in C$ millions; 2-tuple applies scale to store in C$ trillions
    "gdp_monthly":               (65201210, 0.000001),  # Table 36-10-0434: Monthly real GDP, all industries, chained 2017 $, SAAR (C$ trillions)
    # Industry overlays for gdp_monthly chart (same table, same scale — vectors verified 2026-05-08)
    "gdp_industry_goods":        (65201211, 0.000001),  # Table 36-10-0434: Goods-producing industries, chained 2017 $, SAAR (C$ trillions)
    "gdp_industry_services":     (65201212, 0.000001),  # Table 36-10-0434: Services-producing industries, chained 2017 $, SAAR (C$ trillions)
    "gdp_industry_manufacturing":(65201263, 0.000001),  # Table 36-10-0434: Manufacturing, chained 2017 $, SAAR (C$ trillions)
    "gdp_industry_mining_oil":   (65201236, 0.000001),  # Table 36-10-0434: Mining, quarrying, and oil and gas extraction, chained 2017 $, SAAR (C$ trillions)
    "gdp_quarterly":             62305752,  # Table 36-10-0104: Quarterly real GDP, expenditure-based, chained 2017 $, SAAR
    "gdp_total_contribution":    79448580,  # Table 36-10-0104: TOTAL GDP at market prices, contribution to annualized Q/Q growth (pp). Headline AR comparator for the contributions chart and for compute_gdp_values; replaces v1594571783 (rounded, dropped May 2026). Gap vs. six-component sum = non-profits + statistical discrepancy.
    "gdp_contrib_consumption":   79448555,  # Table 36-10-0104: Household final consumption, contribution to annualized Q/Q growth
    "gdp_contrib_govt":          79448562,  # Table 36-10-0104: Government final consumption, contribution to annualized Q/Q growth
    "gdp_contrib_investment":    79448563,  # Table 36-10-0104: Gross fixed capital formation, contribution to annualized Q/Q growth
    "gdp_contrib_inventories":   79448572,  # Table 36-10-0104: Change in inventories, contribution to annualized Q/Q growth
    "gdp_contrib_exports":       79448573,  # Table 36-10-0104: Exports of goods and services, contribution to annualized Q/Q growth
    "gdp_contrib_imports":       (79448576, -1),  # Table 36-10-0104: imports — scale_factor=-1 stores it as "Less: imports" so positive contribution = imports fell (StatsCan/MPR presentation convention)
    # Note: prime-age employment rate (output gap proxy) was attempted via v2062952 but returns HTTP 409 from WDS.
    # Skipped for now; the existing unemployment_rate series in the Labour section serves as the activity proxy.
    # Labour Market section additions (May 2026): BoC SAN 2025-17 multi-indicator framework — employment rate,
    # participation rate, job vacancy rate, unit labour costs. Avg hours and involuntary PT skipped: only NSA
    # or annual at the cadence we want; flagged for the next round.
    "employment_rate":           2062817,  # Table 14-10-0287-01: Employment rate, Canada, 15+, total, SA (%)
    "participation_rate":        2062816,  # Table 14-10-0287-01: Participation rate, Canada, 15+, total, SA (%)
    "job_vacancy_rate":      1212389365,   # Table 14-10-0371-01: Job vacancy rate, Canada total, monthly NSA (%). Earlier rev used quarterly SA (v1374464764) but no monthly SA series exists; we use NSA + 12M MA derived line on the chart instead.
    "unemployment_level":   (2062814, 0.001),   # Table 14-10-0287-01: Unemployment, Canada, 15+, total, SA — scaled thousands → millions for the chart
    "job_vacancy_level":   (1212389364, 0.000001),  # Table 14-10-0371-01: Job vacancies count, Canada total, monthly NSA — scaled persons → millions so it shares an axis with unemployment_level
    "unit_labour_cost":         1409159,   # Table 36-10-0206-01: Unit labour cost, business sector, Canada, quarterly SA (index)
    # Housing section (added May 2026)
    "housing_starts":            52300157,  # Table 34-10-0158-01: Housing starts, Canada total, SAAR (units)
    "new_housing_price_index": 111955442,  # Table 18-10-0205-01: New Housing Price Index, Canada total, Dec 2016 = 100, NSA
    "residential_permits":     1675119646,  # Table 34-10-0292-01: Total residential building permits, value SA, current $ thousands
    # Housing deep-dive (added May 2026). Vector v52300170 for units_under_construction is Tier 2 pending:
    # inferred from value magnitude ~246k matching CMHC published counts; getSeriesInfoFromVector API unavailable.
    "units_under_construction": 52300170,  # Table 34-10-0158-01: Units under construction, Canada total, SAAR (thousands) — Tier 2
    # Labour deep-dive additions
    "youth_unemployment_rate": 2062842,    # Table 14-10-0287-01: Unemployment rate, Total Gender, 15-24, SA
    "prime_age_unemployment_rate": 2062950, # Table 14-10-0287-01: Unemployment rate, Total Gender, 25-54, SA
    # Labour force by age group — participation and employment rates (added May 2026)
    # Note: unemployment rates for youth (2062842) and prime-age (2062950) already exist above.
    # Note: prime-age employment rate V2062952 previously returned HTTP 409 from WDS (see comment above);
    # included here to re-test — fetch failure will be reported and existing CSV (if any) preserved.
    "lf_participation_prime": 2062951,  # Table 14-10-0287-01: Participation rate, 25-54, SA (%)
    "lf_employment_prime":    2062952,  # Table 14-10-0287-01: Employment rate, 25-54, SA (%)
    "lf_participation_youth": 2062843,  # Table 14-10-0287-01: Participation rate, 15-24, SA (%)
    "lf_employment_youth":    2062844,  # Table 14-10-0287-01: Employment rate, 15-24, SA (%)
    # Capacity utilization (quarterly, %; added May 2026)
    "capacity_util_total":    4331081,  # Table 16-10-0359-01: Canada, Total industrial capacity utilization, SA (%)
    "capacity_util_mfg":      4331088,  # Table 16-10-0359-01: Canada, Manufacturing capacity utilization, SA (%)
    # EI regular beneficiaries (monthly, SA, persons; added May 2026)
    "ei_regular_beneficiaries": 64549350,  # Table 14-10-0005-01: Canada, EI regular benefits recipients, SA
    # Merchandise trade (monthly, SA, C$ millions; added May 2026)
    "trade_exports_us":       87008898,  # Table 12-10-0119-01: Exports, Customs basis, SA, United States (C$ millions)
    "trade_imports_us":       87008782,  # Table 12-10-0119-01: Imports, Customs basis, SA, United States (C$ millions)
    "trade_balance_us":       87008985,  # Table 12-10-0119-01: Trade balance, BOP basis, SA, United States (C$ millions)
    "trade_exports_total":    87008897,  # Table 12-10-0119-01: Exports, Customs basis, SA, All countries (C$ millions)
    "trade_imports_total":    87008781,  # Table 12-10-0119-01: Imports, Customs basis, SA, All countries (C$ millions)
    "trade_balance_total":    87008984,  # Table 12-10-0119-01: Trade balance, BOP basis, SA, All countries (C$ millions)
    # Population components (quarterly, persons; added May 2026)
    # Note: pop_total V1 was flagged as unusually small — excluded pending verification.
    "pop_immigrants":       29850342,   # Table 17-10-0040-01: Canada, Immigrants
    "pop_emigrants":        29850343,   # Table 17-10-0040-01: Canada, Emigrants
    "pop_net_emigration": 1566834788,   # Table 17-10-0040-01: Canada, Net emigration
    "pop_net_npr":          29850346,   # Table 17-10-0040-01: Canada, Net non-permanent residents
    "pop_npr_inflows":    1566834758,   # Table 17-10-0040-01: Canada, NPR inflows
}

# Note: housing_starts units are thousands of SAAR units (e.g. 236 = 236,000 annualized starts)
# residential_permits units are current C$ thousands (e.g. 8,132,058 = ~$8.1 billion)

BOC_VALET_SERIES = {
    # 2-tuple: (series_key, start_date). 3-tuple: (series_key, start_date, scale_factor)
    # Scale factor is applied to the fetched values (e.g. 0.001 to convert millions to billions)
    "yield_2yr":      ("BD.CDN.2YR.DQ.YLD",    "1990-01-01"),  # 2-yr GoC benchmark bond yield, daily
    "yield_5yr":      ("BD.CDN.5YR.DQ.YLD",    "1990-01-01"),  # 5-yr GoC benchmark bond yield, daily
    "yield_10yr":     ("BD.CDN.10YR.DQ.YLD",   "1990-01-01"),  # 10-yr GoC benchmark bond yield, daily
    "yield_30yr":     ("BD.CDN.LONG.DQ.YLD",   "1990-01-01"),  # 30-yr GoC benchmark bond yield, daily
    "corra_daily":    ("AVG.INTWO",             "2009-01-01"),  # CORRA (Canadian Overnight Repo Rate Average), daily
    "overnight_rate": ("STATIC_ATABLE_V39079",  "1990-01-01"),  # BoC overnight rate target, monthly (long history; used by chart)
    "overnight_rate_daily": ("V39079",          "2009-04-21"),  # BoC overnight rate target, DAILY (since 2009-04-21; used by analyze.py for meeting-resolution)
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
    # Inflation expectations (added May 2026; quarterly cadence, persistent Valet keys)
    "infl_exp_consumer_1y": ("CES_C1_SHORT_TERM", "2014-01-01"),  # CSCE 1-year-ahead consumer inflation expectation, % (mean)
    "infl_exp_consumer_5y": ("CES_C1_LONG_TERM",  "2014-01-01"),  # CSCE 5-year-ahead consumer inflation expectation, % (mean)
    "infl_exp_above3":      ("ABOVE3",            "2013-01-01"),  # BOS: % of firms expecting inflation > 3% over next 2 years (most-current vintage)
    # BOS expectations distribution buckets (sum to ~100% across the four buckets); aligned vintage may be ~1 quarter behind ABOVE3
    "bos_dist_below1":      ("INDINF_BOSBELOW1_Q", "2003-01-01"),  # BOS: % of firms expecting CPI inflation <1% over next 2 years
    "bos_dist_1to2":        ("INDINF_BOS1TO2_Q",   "2003-01-01"),  # BOS: % of firms expecting CPI inflation 1-2%
    "bos_dist_2to3":        ("INDINF_BOS2TO3_Q",   "2003-01-01"),  # BOS: % of firms expecting CPI inflation 2-3% (target-consistent)
    "bos_dist_above3":      ("INDINF_BOSOVER3_Q",  "2003-01-01"),  # BOS: % of firms expecting CPI inflation >3%
    # Housing price indices (added May 2026)
    "crea_mls_hpi":         ("FVI_CREA_MLS_HPI_CANADA", "2014-01-01"),  # CREA MLS HPI, all of Canada, index 2019=100; BoC Financial Vulnerability Indicators; monthly
    "housing_affordability": ("INDINF_AFFORD_Q",        "2000-01-01"),  # BoC housing affordability index (quarterly; ~ratio of mortgage payment to income)
    # Housing deep-dive (added May 2026)
    "mortgage_rate_5yr":       ("V80691335",                                   "1990-01-01"),  # 5-yr conventional mortgage rate, weekly; BoC Valet (confirmed via seriesDetails probe)
    "crea_resales":            ("FVI_CREA_HOUSE_RESALE_INDEXED_CANADA",        "2014-01-01"),  # CREA residential resales, indexed; monthly; BoC FVI
    "crea_snlr":               ("FVI_CREA_HOUSE_SALES_TO_NEW_LISTINGS_CANADA", "2014-01-01"),  # CREA sales-to-new-listings ratio (%); monthly; BoC FVI
    "crea_resales_toronto":    ("FVI_HOUSE_RESALES_12M_TORONTO",               "2014-01-01"),  # Toronto 12M rolling resales; monthly; BoC FVI
    "crea_resales_vancouver":  ("FVI_HOUSE_RESALES_12M_VANCOUVER",             "2014-01-01"),  # Vancouver 12M rolling resales; monthly; BoC FVI
    "crea_resales_calgary":    ("FVI_HOUSE_RESALES_12M_CALGARY",               "2014-01-01"),  # Calgary 12M rolling resales; monthly; BoC FVI
}

FRED_SERIES = {
    "us_2yr":   ("DGS2",             "1990-01-01"),  # 2-yr US Treasury constant maturity, daily
    "usdcad":   ("DEXCAUS",          "1990-01-01"),  # USD/CAD exchange rate (CAD per USD), daily
    "wti":      ("DCOILWTICO",       "1990-01-01"),  # WTI crude oil, USD/barrel, daily
    "brent":    ("DCOILBRENTEU",     "1990-01-01"),  # Brent crude oil, USD/barrel, daily
    # Peer central bank policy rates (OECD monthly series via FRED)
    "ecb_rate": ("ECBDFR",           "1999-01-01"),  # ECB deposit facility rate, weekly
    "boe_rate": ("IRSTCB01GBM156N",  "1990-01-01"),  # Bank of England Bank Rate, monthly (OECD/FRED)
    "rba_rate": ("IRSTCB01AUM156N",  "1990-01-01"),  # RBA cash rate target, monthly (OECD/FRED)
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
    # Preserve NaN rows so structural gaps (e.g. JVWS Apr-Sep 2020 COVID suspension,
    # statusCode=1 in the WDS response) survive into the CSV. Plotly auto-breaks
    # lines at NaN; pandas rolling means handle NaN windows via min_periods.
    return df.sort_values("date").reset_index(drop=True)


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


def fetch_indeed_canada() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Indeed Hiring Lab Canada Job Postings Index — daily SA, baseline Feb 1 2020 = 100.

    Source: github.com/hiring-lab/data, CC BY 4.0. The "total postings" variable is
    the headline series; "new postings" is a sub-cut for postings new in the most
    recent 7 days. We use total postings, SA, daily.

    Returns (daily, monthly) — both with `date, value` columns. Monthly is the
    simple mean of the SA index within each calendar month (month-start label, to
    match StatsCan's date convention). The user can swap to NSA or to a different
    aggregation later (e.g. month-end value, median, or trimmed mean) — for now
    monthly mean is the default; flagged for review.

    Coverage: Feb 1 2020 onward — covers the JVWS COVID suspension (Apr-Sep 2020)
    where StatsCan has no data. BoC has used Indeed-Canada postings as a
    complementary read on JVWS in SAN 2021-18 and SWP 2022-17.
    """
    url = "https://raw.githubusercontent.com/hiring-lab/data/master/CA/aggregate_job_postings_CA.csv"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df = df[df["variable"] == "total postings"].copy()
    df = df[["date", "indeed_job_postings_index_SA"]].rename(
        columns={"indeed_job_postings_index_SA": "value"}
    )
    df["date"] = pd.to_datetime(df["date"])
    daily = df.sort_values("date").reset_index(drop=True)
    # Monthly mean, month-start convention (matches StatsCan).
    monthly = (
        daily.set_index("date")["value"]
        .resample("MS")
        .mean()
        .dropna()
        .reset_index()
    )
    monthly.columns = ["date", "value"]
    return daily, monthly


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


def fetch_fad_calendar() -> list:
    """BoC Fixed Announcement Date (FAD) calendar from the Bank's iCal feed.

    Returns a sorted list of {date, title} dicts for every event whose summary
    starts with "Interest Rate Announcement" — this captures both standalone
    FADs and the four FADs paired with MPR releases. The feed contains roughly
    a year of upcoming events plus recently past events, which is enough to
    count consecutive no-change FADs since the most recent rate change.
    """
    r = requests.get(
        "https://www.bankofcanada.ca/?feed=ical&content_type=upcoming-events",
        timeout=30,
    )
    r.raise_for_status()
    # Unfold lines per RFC5545: continuation lines start with whitespace.
    text = re.sub(r"\r?\n[ \t]", "", r.text)

    fads = []
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", text, flags=re.DOTALL):
        summary_m = re.search(r"^SUMMARY:(.*)$", block, flags=re.MULTILINE)
        dtstart_m = re.search(r"^DTSTART(?:;[^:]*)?:(\d{8})", block, flags=re.MULTILINE)
        if not summary_m or not dtstart_m:
            continue
        summary = summary_m.group(1).strip()
        if not summary.startswith("Interest Rate Announcement"):
            continue
        d = dtstart_m.group(1)
        fads.append({"date": f"{d[:4]}-{d[4:6]}-{d[6:8]}", "title": summary})

    fads.sort(key=lambda x: x["date"])
    return fads


# ── Retry helper ──────────────────────────────────────────────────────────────

def _latest_saved_date(path: Path) -> pd.Timestamp | None:
    """Return the latest date already saved in a CSV (long or wide format), or None."""
    if not path.exists():
        return None
    try:
        col = pd.read_csv(path, usecols=[0], parse_dates=True)
        return pd.to_datetime(col.iloc[:, 0]).max()
    except (pd.errors.EmptyDataError, pd.errors.ParserError, ValueError, IndexError, KeyError):
        # Expected: empty file, malformed CSV, missing/unparseable date column.
        # Other exceptions (e.g. OSError on permissions) propagate so they're visible.
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

    for name, entry in STATSCAN_SERIES.items():
        # entry is either a plain int (vector_id) or a 2-tuple (vector_id, scale_factor)
        if isinstance(entry, tuple):
            vector_id, scale = entry
        else:
            vector_id, scale = entry, 1.0
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
            if scale != 1.0:
                df["value"] = df["value"] * scale
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

    print("Fetching indeed_postings_ca (Indeed Hiring Lab Canada postings index)...")
    result = _safe("indeed_postings_ca", fetch_indeed_canada)
    if result is not None:
        daily, monthly = result
        daily_path = DATA_DIR / "indeed_postings_ca.csv"
        monthly_path = DATA_DIR / "indeed_postings_ca_monthly.csv"
        daily.to_csv(daily_path, index=False)
        monthly.to_csv(monthly_path, index=False)
        print(f"  -> {len(daily)} daily rows saved to {daily_path}")
        print(f"  -> {len(monthly)} monthly rows saved to {monthly_path}")

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

    print("Fetching BoC FAD calendar from iCal feed...")
    fads = _safe("fad_calendar", fetch_fad_calendar)
    if fads is not None:
        path = DATA_DIR / "fad_calendar.json"
        path.write_text(json.dumps(fads, indent=2))
        date_range = f" ({fads[0]['date']} to {fads[-1]['date']})" if fads else ""
        print(f"  -> {len(fads)} FAD entries saved to {path}{date_range}")

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
