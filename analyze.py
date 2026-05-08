"""
Generate dashboard blurbs from the analysis framework + latest data.

Reads markdown-files/analysis_framework.md, computes the values referenced by
each section, calls Claude Opus to generate a blurb following the framework's
structure and style rules, and writes data/blurbs.json. build.py reads that
JSON and injects each blurb above the corresponding section heading.

Currently only the inflation section is wired up. Add more sections by
extending the SECTIONS dict and writing a compute_*_values + format_*_values
pair for each.

Run:    python analyze.py
        python analyze.py --print-only       (compute + show prompt; no API call)
Output: data/blurbs.json
Env:    ANTHROPIC_API_KEY required for the actual API call
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

DATA = Path("data")
FRAMEWORK = Path("markdown-files/analysis_framework.md")
OUT = DATA / "blurbs.json"

MODEL = "claude-opus-4-7"


# ── Data helpers ─────────────────────────────────────────────────────────────

def load_series(name: str) -> pd.Series:
    df = pd.read_csv(DATA / f"{name}.csv", parse_dates=["date"]).sort_values("date").set_index("date")
    return df["value"]


def asof(s: pd.Series, d: pd.Timestamp) -> float | None:
    sub = s[s.index <= d].dropna()
    return float(sub.iloc[-1]) if not sub.empty else None


# ── Inflation section ────────────────────────────────────────────────────────

def compute_inflation_values() -> dict:
    cpi      = load_series("cpi_all_items")  # SA
    food     = load_series("cpi_food")
    energy   = load_series("cpi_energy")
    goods    = load_series("cpi_goods")
    services = load_series("cpi_services")
    trim     = load_series("cpi_trim")
    median_  = load_series("cpi_median")
    common   = load_series("cpi_common")
    cpix     = load_series("cpix")
    cpixfet  = load_series("cpixfet")

    yoy_h = (cpi.pct_change(12) * 100).dropna()
    mom_h = (cpi.pct_change(1) * 100).dropna()
    ar3_h = (((cpi / cpi.shift(3)) ** 4 - 1) * 100).dropna()

    yoy_food     = (food.pct_change(12) * 100).dropna()
    yoy_energy   = (energy.pct_change(12) * 100).dropna()
    yoy_goods    = (goods.pct_change(12) * 100).dropna()
    yoy_services = (services.pct_change(12) * 100).dropna()

    latest = min(s.index[-1] for s in [
        yoy_h, trim, median_, common, cpix, cpixfet,
        yoy_food, yoy_energy, yoy_goods, yoy_services,
    ])

    cores = {
        "trim":    asof(trim, latest),
        "median":  asof(median_, latest),
        "common":  asof(common, latest),
        "cpix":    asof(cpix, latest),
        "cpixfet": asof(cpixfet, latest),
    }
    core_lo = min(cores.values())
    core_hi = max(cores.values())
    core_avg = sum(cores.values()) / len(cores)

    headline_yoy = asof(yoy_h, latest)

    # CPI breadth from depth-3 components
    mapping = json.loads((DATA / "cpi_breadth_mapping.json").read_text())
    weights = pd.Series({m["name"]: m["wt_value"] for m in mapping if m["wt_value"] is not None})
    comp = pd.read_csv(DATA / "cpi_components.csv", parse_dates=["date"], index_col="date")
    keep = [c for c in comp.columns
            if c in weights.index and comp[c].first_valid_index() <= pd.Timestamp("1995-01-01")]
    comp = comp[keep]
    w = weights.reindex(keep).fillna(0)
    w = w / w.sum()
    yoy_c = comp.pct_change(12) * 100
    above3 = yoy_c.gt(3).multiply(w, axis=1).sum(axis=1) * 100
    below1 = yoy_c.lt(1).multiply(w, axis=1).sum(axis=1) * 100
    valid = yoy_c.notna().all(axis=1)
    above3 = above3[valid]
    below1 = below1[valid]
    ha_above = above3["1996":"2019"].mean()
    ha_below = below1["1996":"2019"].mean()
    # Snap to the most recent breadth date at or before `latest`, in case a
    # component's release lags the headline (partial-release windows).
    latest_breadth = above3.index[above3.index <= latest].max() if (above3.index <= latest).any() else above3.index.max()
    above_dev = float(above3.loc[latest_breadth] - ha_above)
    below_dev = float(below1.loc[latest_breadth] - ha_below)
    tilt = above_dev - below_dev

    # Inflation expectations (CSCE quarterly + BOS ABOVE3 quarterly)
    try:
        ie_consumer_1y = load_series("infl_exp_consumer_1y")
        ie_consumer_5y = load_series("infl_exp_consumer_5y")
        ie_above3      = load_series("infl_exp_above3")
        ie_consumer_1y_now    = float(ie_consumer_1y.iloc[-1])
        ie_consumer_5y_now    = float(ie_consumer_5y.iloc[-1])
        ie_above3_now         = float(ie_above3.iloc[-1])
        ie_consumer_5y_4q_ago = float(ie_consumer_5y.asof(ie_consumer_5y.index[-1] - pd.DateOffset(years=1)))
        ie_consumer_5y_drift  = ie_consumer_5y_now - ie_consumer_5y_4q_ago if pd.notna(ie_consumer_5y_4q_ago) else 0.0
        ie_as_of              = ie_consumer_1y.index[-1].strftime("%B %Y")
    except Exception:
        ie_consumer_1y_now = ie_consumer_5y_now = ie_above3_now = ie_consumer_5y_drift = None
        ie_as_of = None

    return {
        "latest_date":         latest.strftime("%B %Y"),
        "headline_yoy":        headline_yoy,
        "headline_mom_sa":     asof(mom_h, latest),
        "headline_3m_ar_sa":   asof(ar3_h, latest),
        "cores":               cores,
        "core_band_lo":        core_lo,
        "core_band_hi":        core_hi,
        "core_band_width":     core_hi - core_lo,
        "core_avg":            core_avg,
        "headline_minus_core": headline_yoy - core_avg,
        "food_yoy":            asof(yoy_food, latest),
        "energy_yoy":          asof(yoy_energy, latest),
        "goods_yoy":           asof(yoy_goods, latest),
        "services_yoy":        asof(yoy_services, latest),
        "breadth_above3":      float(above3.loc[latest_breadth]),
        "breadth_below1":      float(below1.loc[latest_breadth]),
        "breadth_above3_dev":  above_dev,
        "breadth_below1_dev":  below_dev,
        "breadth_tilt":        tilt,
        # Inflation expectations (added May 2026; quarterly cadence)
        "expectations_as_of":           ie_as_of,
        "expectations_consumer_1y":     ie_consumer_1y_now,
        "expectations_consumer_5y":     ie_consumer_5y_now,
        "expectations_consumer_5y_drift_4q": ie_consumer_5y_drift,
        "expectations_bos_above3":      ie_above3_now,
    }


def format_inflation_values(v: dict) -> str:
    c = v["cores"]
    if v.get("expectations_as_of"):
        exp_block = f"""

Inflation expectations (as of {v['expectations_as_of']}; quarterly):
  CSCE consumer 1y-ahead:    {v['expectations_consumer_1y']:+.2f}%   (near-term consumer expectation)
  CSCE consumer 5y-ahead:    {v['expectations_consumer_5y']:+.2f}%   (long-run anchor)
  5y drift over last 4q:     {v['expectations_consumer_5y_drift_4q']:+.2f}pp   (negative = re-anchoring; positive = drifting up)
  BOS firms expecting > 3%:  {v['expectations_bos_above3']:.0f}%   (business-side anchor diagnostic; high = anchor under stress)"""
    else:
        exp_block = "\n\nInflation expectations data: not loaded."
    return f"""== Latest data: {v['latest_date']} ==

Headline CPI Y/Y:         {v['headline_yoy']:+.2f}%
Headline M/M (SA):        {v['headline_mom_sa']:+.3f}%
Headline 3M AR (SA):      {v['headline_3m_ar_sa']:+.2f}%

Core measures (Y/Y):
  CPI-trim:               {c['trim']:+.2f}%
  CPI-median:             {c['median']:+.2f}%
  CPI-common:             {c['common']:+.2f}%
  CPIX:                   {c['cpix']:+.2f}%
  CPIXFET:                {c['cpixfet']:+.2f}%

Core band:                low {v['core_band_lo']:.2f}%, high {v['core_band_hi']:.2f}%, width {v['core_band_width']:.2f}pp
Core average:             {v['core_avg']:+.2f}%
Headline minus core avg:  {v['headline_minus_core']:+.2f}pp

Category breakdown (Y/Y):
  Food:                   {v['food_yoy']:+.2f}%
  Energy:                 {v['energy_yoy']:+.2f}%
  Goods:                  {v['goods_yoy']:+.2f}%
  Services:               {v['services_yoy']:+.2f}%

CPI Breadth:
  Share above 3%:         {v['breadth_above3']:.1f}%   (1996-2019 avg deviation: {v['breadth_above3_dev']:+.1f}pp)
  Share below 1%:         {v['breadth_below1']:.1f}%   (1996-2019 avg deviation: {v['breadth_below1_dev']:+.1f}pp)
  Breadth tilt:           {v['breadth_tilt']:+.1f}pp   (positive = broad-based pressure; negative = broad-based softening){exp_block}
"""


# ── Monetary Policy section ──────────────────────────────────────────────────

def _classify_bocfed(s: float) -> str:
    a = abs(s)
    if a > 1.5:  return "rare"
    if a > 1.0:  return "unusual"
    if a > 0.5:  return "notable"
    return "typical"


def _classify_can2y_overnight(s: float) -> str:
    a = abs(s)
    if a > 1.0:  return "unusual"
    if a > 0.5:  return "notable"
    if a > 0.25: return "modest"
    return "near-zero"


def _classify_regime(rate: float, lo: float = 2.25, hi: float = 3.25) -> str:
    if rate > hi:  return "restrictive"
    if rate < lo:  return "accommodative"
    return "neutral"


def _classify_qt_phase(date: pd.Timestamp) -> str:
    # Verified BoC operational timeline (see analysis_framework.md Monetary Policy).
    if date < pd.Timestamp("2020-04-01"):  return "pre-pandemic"
    if date < pd.Timestamp("2021-10-27"):  return "QE (GBPP)"
    if date < pd.Timestamp("2022-04-25"):  return "reinvestment"
    if date < pd.Timestamp("2025-01-29"):  return "passive QT"
    return "post-QT / floor maintenance"


def _load_fad_calendar() -> list:
    """
    Combined FAD dates from data/fad_history.json (static historical, committed)
    and data/fad_calendar.json (dynamic from iCal feed). Sorted and deduped.
    """
    dates: set = set()
    for fname in ("fad_history.json", "fad_calendar.json"):
        path = DATA / fname
        if not path.exists():
            continue
        try:
            for entry in json.loads(path.read_text()):
                if "date" in entry:
                    dates.add(pd.Timestamp(entry["date"]))
        except Exception:
            pass
    return sorted(dates)


def _analyze_rate_action(daily_rate: pd.Series, fad_dates: list) -> dict:
    """
    Determine the BoC's current action state from FAD outcomes (meeting-resolution).

    Action state is the headline read — what the Bank is doing right now — and
    it's the reference point that makes the market signals interpretable. A
    "hawkish drift" means very different things in a cutting cycle vs. a hold
    vs. a hiking cycle; without this, the blurb generator silently assumes the
    cycle direction.

    Three states only — on hold / cutting / hiking — determined by the most
    recent FAD's outcome. Continuity nuance ("just resumed after pause," "third
    cut in a row") is carried by the meeting count fields, not the state name.
    """
    today = daily_rate.index[-1]

    # Build outcomes for past FADs by comparing daily rate just before vs. shortly after each FAD.
    # The daily series shows rate changes ~1 business day after the FAD; a 5-day lookahead
    # buffers across weekends regardless of which weekday the FAD falls on.
    outcomes = []
    for fad in fad_dates:
        if fad > today:
            break  # fad_dates is sorted; future FADs end the loop
        rate_before = daily_rate.asof(fad - pd.Timedelta(days=1))
        rate_after  = daily_rate.asof(fad + pd.Timedelta(days=5))
        if pd.isna(rate_before) or pd.isna(rate_after):
            continue
        rate_before, rate_after = float(rate_before), float(rate_after)
        change = rate_after - rate_before
        if abs(change) < 0.001:
            decision, change_bps = "hold", 0
        elif change < 0:
            decision, change_bps = "cut", int(round(abs(change) * 100))
        else:
            decision, change_bps = "hike", int(round(change * 100))
        outcomes.append({
            "date": fad, "decision": decision,
            "rate_before": rate_before, "rate_after": rate_after,
            "change_bps": change_bps,
        })

    # Rate-change events from the daily series (full history; covers cycles older than the FAD calendar).
    diffs = daily_rate.diff().dropna()
    changes = diffs[diffs.abs() > 0.001]

    # Action state from latest FAD outcome — fall back to rate-change inference if no FADs in calendar.
    if outcomes:
        latest = outcomes[-1]
        if latest["decision"] == "hold":
            action_state = "on hold"
        elif latest["decision"] == "cut":
            action_state = "cutting"
        else:
            action_state = "hiking"
    elif len(changes) > 0:
        last_dir = "cut" if float(changes.iloc[-1]) < 0 else "hike"
        action_state = f"{last_dir.replace('cut', 'cutting').replace('hike', 'hiking')}"
    else:
        action_state = "on hold"

    # Counters. Meetings_unchanged = consecutive holds back to (but not including) last change.
    # Consecutive_same_direction_moves = run of consecutive same-direction moves ending at latest FAD.
    meetings_unchanged = 0
    consecutive_same_direction_moves = 0
    if outcomes:
        if action_state == "on hold":
            for f in reversed(outcomes):
                if f["decision"] == "hold":
                    meetings_unchanged += 1
                else:
                    break
        else:
            target = outcomes[-1]["decision"]
            for f in reversed(outcomes):
                if f["decision"] == target:
                    consecutive_same_direction_moves += 1
                else:
                    break

    # Last change (from FAD outcomes preferred; fall back to rate changes).
    last_change_fad = None
    for f in reversed(outcomes):
        if f["decision"] != "hold":
            last_change_fad = f
            break

    if last_change_fad is not None:
        last_change_date_str  = last_change_fad["date"].strftime("%B %d, %Y")
        last_change_direction = last_change_fad["decision"]
        last_change_bps       = last_change_fad["change_bps"]
        days_since_last_change = int((today - last_change_fad["date"]).days)
    elif len(changes) > 0:
        # Fall back to daily rate change date (off by ~1 day from the actual FAD)
        c_date = changes.index[-1]
        c_val = float(changes.iloc[-1])
        last_change_date_str  = c_date.strftime("%B %d, %Y")
        last_change_direction = "cut" if c_val < 0 else "hike"
        last_change_bps       = int(round(abs(c_val) * 100))
        days_since_last_change = int((today - c_date).days)
    else:
        last_change_date_str  = None
        last_change_direction = None
        last_change_bps       = None
        days_since_last_change = None

    # Prior cycle — derived from the daily rate series so it works even when the FAD
    # calendar doesn't reach back that far. Cycle = run of same-direction moves
    # ending at the most recent change; "active duration" is first move to last move.
    if len(changes) == 0:
        prior_info = {
            "prior_cycle_direction":             None,
            "prior_cycle_total_bps":             None,
            "prior_cycle_start_rate":            None,
            "prior_cycle_start_date_str":        None,
            "prior_cycle_first_move_date_str":   None,
            "prior_cycle_end_rate":              None,
            "prior_cycle_active_duration_months": None,
        }
    else:
        last_change_value = float(changes.iloc[-1])
        last_rate_change_date = changes.index[-1]
        end_rate = float(daily_rate.loc[last_rate_change_date])
        cycle_first_move_idx = 0
        for i in range(len(changes) - 1, -1, -1):
            val = float(changes.iloc[i])
            same_dir = (val < 0 and last_change_value < 0) or (val > 0 and last_change_value > 0)
            if not same_dir:
                cycle_first_move_idx = i + 1
                break
        cycle_first_move_date = changes.index[cycle_first_move_idx]
        prior_idx = daily_rate.index.get_loc(cycle_first_move_date)
        if prior_idx > 0:
            cycle_start_rate = float(daily_rate.iloc[prior_idx - 1])
            cycle_start_date = daily_rate.index[prior_idx - 1]
        else:
            cycle_start_rate = float(daily_rate.iloc[0])
            cycle_start_date = daily_rate.index[0]
        prior_direction = "cuts" if last_change_value < 0 else "hikes"
        prior_total_bps = int(round(abs(cycle_start_rate - end_rate) * 100))
        prior_active_duration_months = (last_rate_change_date.to_period("M") - cycle_first_move_date.to_period("M")).n
        prior_info = {
            "prior_cycle_direction":             prior_direction,
            "prior_cycle_total_bps":             prior_total_bps,
            "prior_cycle_start_rate":            cycle_start_rate,
            "prior_cycle_start_date_str":        cycle_start_date.strftime("%B %Y"),
            "prior_cycle_first_move_date_str":   cycle_first_move_date.strftime("%B %Y"),
            "prior_cycle_end_rate":              end_rate,
            "prior_cycle_active_duration_months": int(prior_active_duration_months),
        }

    return {
        "action_state":                     action_state,
        "meetings_unchanged":               meetings_unchanged,
        "consecutive_same_direction_moves": consecutive_same_direction_moves,
        "days_since_last_change":           days_since_last_change,
        "last_change_date_str":             last_change_date_str,
        "last_change_direction":            last_change_direction,
        "last_change_bps":                  last_change_bps,
        **prior_info,
    }


def compute_policy_values() -> dict:
    # Daily overnight rate (V39079, since 2009-04-21) drives the action-state analysis;
    # FAD calendar gives meeting-resolution counts. The monthly overnight_rate is kept
    # for the chart (longer history) but not used here.
    overnight    = load_series("overnight_rate_daily")
    fed          = load_series("fed_funds")
    cad_2y       = load_series("yield_2yr")
    us_2y        = load_series("us_2yr")
    total_assets = load_series("boc_total_assets")
    goc_bonds    = load_series("boc_goc_bonds")
    settlement   = load_series("boc_settlement_balances")

    # Latest values (each at its own as-of date — frequencies differ)
    overnight_now    = float(overnight.iloc[-1])
    overnight_date   = overnight.index[-1]
    fed_now          = float(fed.iloc[-1])
    cad_2y_now       = float(cad_2y.iloc[-1])
    cad_2y_date      = cad_2y.index[-1]
    us_2y_now        = float(us_2y.iloc[-1])
    total_assets_now = float(total_assets.iloc[-1])
    bs_date          = total_assets.index[-1]
    goc_bonds_now    = float(goc_bonds.iloc[-1])
    settlement_now   = float(settlement.iloc[-1])

    # Spreads — align by forward-filling monthly overnight onto daily yields
    bf = overnight.to_frame("boc").join(fed.to_frame("fed"), how="outer").sort_index().ffill().dropna()
    bocfed_spread = float(bf["boc"].iloc[-1] - bf["fed"].iloc[-1])

    co = cad_2y.to_frame("y2").join(overnight.to_frame("on"), how="outer").sort_index().ffill().dropna()
    co["spread"] = co["y2"] - co["on"]
    can2y_overnight = float(co["spread"].iloc[-1])

    # 4-week / 12-week drift in can2y_overnight (4w = tactical repricing; 12w = trend confirmation)
    spread_4w_ago  = float(co["spread"].asof(co.index[-1] - pd.Timedelta(days=28)))
    spread_12w_ago = float(co["spread"].asof(co.index[-1] - pd.Timedelta(days=84)))
    drift_4w  = can2y_overnight - spread_4w_ago
    drift_12w = can2y_overnight - spread_12w_ago

    cu = cad_2y.to_frame("y2").join(us_2y.to_frame("us2"), how="outer").sort_index().ffill().dropna()
    can_us_2y = float(cu["y2"].iloc[-1] - cu["us2"].iloc[-1])

    # Recent BoC and Fed cycle peak/trough (last 5 years — captures full hike+cut cycle)
    cycle_cutoff = overnight.index[-1] - pd.DateOffset(years=5)
    boc_window = overnight[overnight.index >= cycle_cutoff]
    boc_peak = float(boc_window.max())
    boc_peak_date = boc_window.idxmax()
    boc_trough = float(boc_window.min())
    boc_trough_date = boc_window.idxmin()

    fed_window = fed[fed.index >= cycle_cutoff]
    fed_peak = float(fed_window.max())
    fed_peak_date = fed_window.idxmax()
    fed_trough = float(fed_window.min())
    fed_trough_date = fed_window.idxmin()

    # Balance sheet trajectory: 6mo and 12mo changes (weekly data)
    ta_6mo_ago  = float(total_assets.asof(bs_date - pd.DateOffset(months=6)))
    ta_12mo_ago = float(total_assets.asof(bs_date - pd.DateOffset(months=12)))
    gb_6mo_ago  = float(goc_bonds.asof(bs_date - pd.DateOffset(months=6)))
    gb_12mo_ago = float(goc_bonds.asof(bs_date - pd.DateOffset(months=12)))

    non_goc_now = total_assets_now - goc_bonds_now
    non_goc_6mo_ago  = ta_6mo_ago - gb_6mo_ago
    non_goc_12mo_ago = ta_12mo_ago - gb_12mo_ago

    action = _analyze_rate_action(overnight, _load_fad_calendar())

    return {
        "latest_date":             cad_2y_date.strftime("%B %Y"),  # most recent data overall
        "as_of_overnight":         overnight_date.strftime("%B %Y"),
        "as_of_yield":             cad_2y_date.strftime("%B %d, %Y"),
        "as_of_balance_sheet":     bs_date.strftime("%B %d, %Y"),

        # Action state: the verb. What is the BoC doing, for how long, and what came before.
        **action,

        "overnight":               overnight_now,
        "regime":                  _classify_regime(overnight_now),
        "neutral_low":             2.25,
        "neutral_high":            3.25,
        "boc_cycle_peak":          boc_peak,
        "boc_cycle_peak_date":     boc_peak_date.strftime("%b %Y"),
        "boc_cycle_trough":        boc_trough,
        "boc_cycle_trough_date":   boc_trough_date.strftime("%b %Y"),
        "boc_distance_from_peak":   overnight_now - boc_peak,
        "boc_distance_from_trough": overnight_now - boc_trough,

        "fed_funds":               fed_now,
        "fed_cycle_peak":          fed_peak,
        "fed_cycle_peak_date":     fed_peak_date.strftime("%b %Y"),
        "fed_cycle_trough":        fed_trough,
        "fed_cycle_trough_date":   fed_trough_date.strftime("%b %Y"),
        "fed_distance_from_peak":   fed_now - fed_peak,
        "fed_distance_from_trough": fed_now - fed_trough,

        "bocfed_spread":           bocfed_spread,
        "bocfed_tier":             _classify_bocfed(bocfed_spread),

        "cad_2y":                  cad_2y_now,
        "us_2y":                   us_2y_now,
        "can2y_overnight_spread":  can2y_overnight,
        "can2y_overnight_tier":    _classify_can2y_overnight(can2y_overnight),
        "drift_4w":                drift_4w,
        "drift_12w":                drift_12w,
        "can_us_2y_spread":         can_us_2y,
        "can_us_minus_bocfed":      can_us_2y - bocfed_spread,

        "qt_phase":                  _classify_qt_phase(bs_date),
        "total_assets":              total_assets_now,
        "goc_bonds":                 goc_bonds_now,
        "non_goc":                   non_goc_now,
        "settlement":                settlement_now,
        "settlement_target_low":     20,
        "settlement_target_high":    60,

        "ta_change_6mo":             total_assets_now - ta_6mo_ago,
        "ta_change_12mo":            total_assets_now - ta_12mo_ago,
        "gb_change_6mo":             goc_bonds_now - gb_6mo_ago,
        "gb_change_12mo":            goc_bonds_now - gb_12mo_ago,
        "non_goc_change_6mo":        non_goc_now - non_goc_6mo_ago,
        "non_goc_change_12mo":       non_goc_now - non_goc_12mo_ago,

        "distance_from_baseline":    total_assets_now - 120,   # ~$120B pre-COVID baseline
        "distance_from_peak_qe":     total_assets_now - 575,   # ~$575B March 2021 peak
    }


def format_policy_values(v: dict) -> str:
    # Build the action-state summary line. The verb leads. Three states only.
    if v.get("action_state") == "on hold" and v.get("last_change_date_str"):
        n = v.get("meetings_unchanged", 0)
        action_summary = (
            f"ON HOLD at {v['overnight']:.2f}% for {n} meeting{'s' if n != 1 else ''} "
            f"since the last change ({v['days_since_last_change']} days ago); "
            f"last move was a {v['last_change_bps']}bp {v['last_change_direction']} on {v['last_change_date_str']}."
        )
    elif v.get("action_state") in ("cutting", "hiking"):
        n = v.get("consecutive_same_direction_moves", 0)
        verb = "cut" if v['action_state'] == "cutting" else "hike"
        if n >= 2:
            run = f"{n} consecutive {verb}s"
        else:
            run = f"first {verb} in this direction (after a hold)"
        action_summary = (
            f"ACTIVELY {v['action_state'].upper()} at {v['overnight']:.2f}% - {run}; "
            f"last move was a {v['last_change_bps']}bp {v['last_change_direction']} on {v['last_change_date_str']}."
        )
    else:
        action_summary = f"current rate {v['overnight']:.2f}%."

    if v.get("prior_cycle_total_bps"):
        prior_cycle_line = (
            f"  Prior cycle:                   {v['prior_cycle_total_bps']}bps of {v['prior_cycle_direction']} "
            f"over {v['prior_cycle_active_duration_months']} months - from a {v['prior_cycle_start_rate']:.2f}% peak "
            f"(cycle started {v['prior_cycle_first_move_date_str']}) to {v['prior_cycle_end_rate']:.2f}% "
            f"on {v['last_change_date_str']}."
        )
    else:
        prior_cycle_line = "  Prior cycle:                   (no prior cycle in window)"

    return f"""== Latest data ==

Policy stance (as of {v['as_of_overnight']}):
  {action_summary}
{prior_cycle_line}
  Position vs neutral band:      {v['regime']} (neutral band {v['neutral_low']:.2f}-{v['neutral_high']:.2f}%; rate is {v['overnight']:.2f}%)
  BoC cycle (last 5y):           peak {v['boc_cycle_peak']:.2f}% ({v['boc_cycle_peak_date']}) -> now ({v['boc_distance_from_peak']:+.2f}pp from peak); trough {v['boc_cycle_trough']:.2f}% ({v['boc_cycle_trough_date']})
  Fed cycle (last 5y):           peak {v['fed_cycle_peak']:.2f}% ({v['fed_cycle_peak_date']}) -> now {v['fed_funds']:.2f}% ({v['fed_distance_from_peak']:+.2f}pp from peak); trough {v['fed_cycle_trough']:.2f}% ({v['fed_cycle_trough_date']})

BoC - Fed spread:                {v['bocfed_spread']:+.2f}pp   tier: {v['bocfed_tier']}  (typ <+/-0.5pp; notable >=+/-0.5pp; unusual >=+/-1.0pp; rare >=+/-1.5pp)

2-Year yields (as of {v['as_of_yield']}):
  Canada 2Y:                     {v['cad_2y']:.2f}%
  US 2Y:                         {v['us_2y']:.2f}%
  Canada 2Y - Overnight:         {v['can2y_overnight_spread']:+.2f}pp   tier: {v['can2y_overnight_tier']}  (near-zero <+/-0.25pp; modest >=+/-0.25pp; notable >=+/-0.5pp; unusual >=+/-1.0pp)
    4-week drift:                {v['drift_4w']:+.2f}pp   (tactical repricing)
    12-week drift:               {v['drift_12w']:+.2f}pp   (trend confirmation)
  Canada 2Y - US 2Y:             {v['can_us_2y_spread']:+.2f}pp
  (Canada 2Y - US 2Y) - (BoC - Fed):  {v['can_us_minus_bocfed']:+.2f}pp   (divergence indicator; small = aligned, large = pricing future stance change OR relative-premium move)

Balance sheet (C$B, as of {v['as_of_balance_sheet']}; operating phase: {v['qt_phase']}):

  ASSET SIDE (what the BoC holds):
    Total assets:                {v['total_assets']:.1f}B   ({v['distance_from_baseline']:+.1f}B vs ~$120B baseline; {v['distance_from_peak_qe']:+.1f}B vs ~$575B March 2021 peak)
                                 6mo change: {v['ta_change_6mo']:+.1f}B; 12mo change: {v['ta_change_12mo']:+.1f}B
    GoC bonds:                   {v['goc_bonds']:.1f}B
                                 6mo change: {v['gb_change_6mo']:+.1f}B; 12mo change: {v['gb_change_12mo']:+.1f}B
    Non-GoC components:          {v['non_goc']:.1f}B    (T-bills, term repos, advances, FX swaps, etc.)
                                 6mo change: {v['non_goc_change_6mo']:+.1f}B; 12mo change: {v['non_goc_change_12mo']:+.1f}B   (rapid expansion = stress signal)

  LIABILITY SIDE (what the BoC owes):
    Settlement balances:         {v['settlement']:.1f}B    (deposits banks keep at the BoC overnight; post-QT target range: ${v['settlement_target_low']}–${v['settlement_target_high']}B)
"""


# ── Labour Market section ────────────────────────────────────────────────────

def compute_labour_values() -> dict:
    unemployment = load_series("unemployment_rate")
    wages_all    = load_series("lfs_wages_all")        # level, SA
    wages_perm   = load_series("lfs_wages_permanent")  # level, SA
    seph         = load_series("seph_earnings")        # level, SA
    lfs_micro    = load_series("lfs_micro")            # already Y/Y from BoC
    cpi_services = load_series("cpi_services")         # NSA level
    cpi_all      = load_series("cpi_all_items")        # SA level

    # Y/Y wage and price measures
    wages_all_yoy  = (wages_all.pct_change(12)  * 100).dropna()
    wages_perm_yoy = (wages_perm.pct_change(12) * 100).dropna()
    seph_yoy       = (seph.pct_change(12)       * 100).dropna()
    services_yoy   = (cpi_services.pct_change(12) * 100).dropna()
    headline_yoy   = (cpi_all.pct_change(12)    * 100).dropna()

    # Earliest of all latest dates so every value is available
    latest = min(s.index[-1] for s in [
        unemployment, wages_all_yoy, wages_perm_yoy, seph_yoy, lfs_micro, services_yoy, headline_yoy
    ])

    u_now = float(asof(unemployment, latest))
    u_3m  = float(asof(unemployment, latest - pd.DateOffset(months=3)))
    u_6m  = float(asof(unemployment, latest - pd.DateOffset(months=6)))
    u_12m = float(asof(unemployment, latest - pd.DateOffset(months=12)))

    cutoff_5y = latest - pd.DateOffset(years=5)
    u_window = unemployment[(unemployment.index >= cutoff_5y) & (unemployment.index <= latest)]
    u_5y_min = float(u_window.min())
    u_5y_max = float(u_window.max())
    u_5y_pct = float((u_window <= u_now).mean() * 100)

    wages_all_now  = float(asof(wages_all_yoy, latest))
    wages_perm_now = float(asof(wages_perm_yoy, latest))
    seph_now       = float(asof(seph_yoy, latest))
    lfs_micro_now  = float(asof(lfs_micro, latest))
    services_now   = float(asof(services_yoy, latest))
    headline_now   = float(asof(headline_yoy, latest))

    wage_measures = {
        "lfs_all":       wages_all_now,
        "lfs_permanent": wages_perm_now,
        "seph":          seph_now,
        "lfs_micro":     lfs_micro_now,
    }
    wage_band_lo    = min(wage_measures.values())
    wage_band_hi    = max(wage_measures.values())
    wage_band_width = wage_band_hi - wage_band_lo
    wage_avg        = sum(wage_measures.values()) / len(wage_measures)
    wages_above_3   = sum(1 for v in wage_measures.values() if v > 3.0)

    # LFS-Micro vs raw LFS gap (negative = composition flattering raw, the dominant Canadian pattern)
    lfs_micro_minus_raw = lfs_micro_now - wages_all_now

    # Real wages (BoC convention: wage Y/Y - headline CPI Y/Y)
    real_wage_lfs_all   = wages_all_now - headline_now
    real_wage_lfs_micro = lfs_micro_now - headline_now

    # Wage vs services CPI (leading indicator of services inflation persistence)
    wage_minus_services  = wages_all_now - services_now
    micro_minus_services = lfs_micro_now - services_now

    return {
        "latest_date":               latest.strftime("%B %Y"),
        "as_of_unemployment":        latest.strftime("%B %Y"),
        "as_of_wages":               latest.strftime("%B %Y"),

        "unemployment":              u_now,
        "unemployment_3mo_change":   u_now - u_3m,
        "unemployment_6mo_change":   u_now - u_6m,
        "unemployment_12mo_change":  u_now - u_12m,
        "unemployment_5y_min":       u_5y_min,
        "unemployment_5y_max":       u_5y_max,
        "unemployment_5y_percentile": u_5y_pct,

        "wages_lfs_all":             wages_all_now,
        "wages_lfs_permanent":       wages_perm_now,
        "wages_seph":                seph_now,
        "wages_lfs_micro":           lfs_micro_now,
        "wage_band_lo":              wage_band_lo,
        "wage_band_hi":              wage_band_hi,
        "wage_band_width":           wage_band_width,
        "wage_avg":                  wage_avg,
        "wages_above_3pct_count":    int(wages_above_3),
        "wage_threshold":            3.0,

        "lfs_micro_minus_raw_lfs":   lfs_micro_minus_raw,

        "headline_cpi_yoy":          headline_now,
        "services_cpi_yoy":          services_now,
        "real_wage_lfs_all":         real_wage_lfs_all,
        "real_wage_lfs_micro":       real_wage_lfs_micro,
        "wage_minus_services":       wage_minus_services,
        "micro_minus_services":      micro_minus_services,
    }


def format_labour_values(v: dict) -> str:
    return f"""== Latest data ==

Labour market state (as of {v['as_of_unemployment']}):
  Unemployment rate:             {v['unemployment']:.2f}%
                                 3-month change: {v['unemployment_3mo_change']:+.2f}pp; 12-month change: {v['unemployment_12mo_change']:+.2f}pp
                                 Last 5y range: {v['unemployment_5y_min']:.2f}% to {v['unemployment_5y_max']:.2f}%; current at {v['unemployment_5y_percentile']:.0f}th percentile
  BoC framing reference:         No fixed NAIRU; the Bank uses qualitative reads ("modest excess supply" / "tight") relative to multi-indicator benchmarks (SAN 2025-17). Don't anchor to a single number.

Wage growth (Y/Y, as of {v['as_of_wages']}):
  LFS, all employees:            {v['wages_lfs_all']:+.2f}%
  LFS, permanent employees:      {v['wages_lfs_permanent']:+.2f}%
  SEPH, all employees:           {v['wages_seph']:+.2f}%
  LFS-Micro (composition-adj):   {v['wages_lfs_micro']:+.2f}%   <- BoC's preferred measure (SAN 2024-23)
  Wage band:                     low {v['wage_band_lo']:+.2f}%, high {v['wage_band_hi']:+.2f}%, width {v['wage_band_width']:.2f}pp
  Average across measures:       {v['wage_avg']:+.2f}%
  Measures above 3% threshold:   {v['wages_above_3pct_count']} of 4   (3% = soft anchor for 2% inflation target with ~1% productivity)

  LFS-Micro minus raw LFS:       {v['lfs_micro_minus_raw_lfs']:+.2f}pp   (negative = composition flattering raw average; this is the dominant Canadian pattern)

Pass-through and real wages:
  Headline CPI Y/Y:              {v['headline_cpi_yoy']:+.2f}%   (deflator for real wages, BoC convention)
  Services CPI Y/Y:              {v['services_cpi_yoy']:+.2f}%
  Real wages (LFS, all):         {v['real_wage_lfs_all']:+.2f}pp   (positive = workers gaining purchasing power)
  Real wages (LFS-Micro):        {v['real_wage_lfs_micro']:+.2f}pp
  LFS wages minus services CPI:  {v['wage_minus_services']:+.2f}pp   (positive = wage pressure not yet fully passed through to services prices)
  LFS-Micro minus services CPI:  {v['micro_minus_services']:+.2f}pp

Coverage gap: this framework tracks unemployment + wage measures + the wage-vs-services-CPI relationship. BoC also explicitly tracks employment rate, involuntary part-time, average hours, job vacancies, newcomer/youth unemployment composition, and unit labour costs (ULC). The view is partial; flag conclusions accordingly when the partial read might mislead.
"""


# ── Financial Conditions (external) section ──────────────────────────────────

def compute_external_values() -> dict:
    wti      = load_series("wti")       # daily, USD/bbl
    brent    = load_series("brent")     # daily, USD/bbl
    wcs      = load_series("wcs")       # monthly, USD/bbl
    usdcad   = load_series("usdcad")    # daily, CAD per USD

    # Latest available dates per frequency
    latest_daily = min(s.index[-1] for s in [wti, brent, usdcad])
    latest_wcs   = wcs.index[-1]

    # Oil
    wti_now  = float(asof(wti, latest_daily))
    wti_1y   = float(asof(wti, latest_daily - pd.DateOffset(years=1)))
    wti_3m   = float(asof(wti, latest_daily - pd.DateOffset(months=3)))
    wti_yoy_pct       = (wti_now / wti_1y - 1) * 100 if wti_1y > 0 else None
    wti_3mo_change    = (wti_now / wti_3m - 1) * 100 if wti_3m > 0 else None
    cpi_impulse_wti   = wti_yoy_pct * 0.037 if wti_yoy_pct is not None else None  # gasoline 3.7% of basket

    brent_now = float(asof(brent, latest_daily))

    wcs_now = float(asof(wcs, latest_wcs))
    # WTI value at WCS as-of date (closest daily before/at latest_wcs)
    wti_at_wcs_date = float(asof(wti, latest_wcs))
    wcs_wti_diff = wti_at_wcs_date - wcs_now  # positive = WCS at a discount to WTI

    # USDCAD
    usdcad_now  = float(asof(usdcad, latest_daily))
    usdcad_3m   = float(asof(usdcad, latest_daily - pd.DateOffset(months=3)))
    usdcad_6m   = float(asof(usdcad, latest_daily - pd.DateOffset(months=6)))
    usdcad_12m  = float(asof(usdcad, latest_daily - pd.DateOffset(years=1)))
    usdcad_3mo_change_pct  = (usdcad_now / usdcad_3m  - 1) * 100
    usdcad_6mo_change_pct  = (usdcad_now / usdcad_6m  - 1) * 100
    usdcad_12mo_change_pct = (usdcad_now / usdcad_12m - 1) * 100

    in_stress_corridor   = bool(1.45 <= usdcad_now <= 1.47)
    near_stress_corridor = bool(1.43 <= usdcad_now <= 1.49)

    # CPI pass-through from CAD: ~0.3-0.6 pp per 10% sustained move; using 0.045 pp per 1%
    # Sign convention: depreciation (USDCAD up) = positive impulse on CPI; appreciation = negative
    implied_cpi_pp_from_cad = usdcad_12mo_change_pct * 0.045

    # CAD-WTI co-movement over last year (daily change correlation)
    df_co = wti.to_frame("wti").join(usdcad.to_frame("cad"), how="inner").dropna()
    recent = df_co[df_co.index >= latest_daily - pd.DateOffset(years=1)]
    if len(recent) > 30:
        chg = recent.pct_change().dropna()
        try:
            wti_cad_corr = float(chg["wti"].corr(chg["cad"]))
        except Exception:
            wti_cad_corr = None
    else:
        wti_cad_corr = None

    # Petrocurrency directional alignment over last 3 months
    wti_dir = "up" if (wti_3mo_change is not None and wti_3mo_change > 1) else \
              ("down" if (wti_3mo_change is not None and wti_3mo_change < -1) else "flat")
    cad_dir_usdcad = "up" if usdcad_3mo_change_pct > 1 else \
                     ("down" if usdcad_3mo_change_pct < -1 else "flat")
    # USDCAD up = CAD weaker. Petrocurrency: oil up + CAD strong (USDCAD down), or oil down + CAD weak (USDCAD up)
    if wti_dir == "up" and cad_dir_usdcad == "down":
        petrocurrency = "aligned (oil up, CAD strengthening)"
    elif wti_dir == "down" and cad_dir_usdcad == "up":
        petrocurrency = "aligned (oil down, CAD weakening)"
    elif wti_dir == "flat" or cad_dir_usdcad == "flat":
        petrocurrency = "ambiguous (one side roughly flat)"
    else:
        petrocurrency = "diverging (CAD and oil moving against the petrocurrency relationship)"

    return {
        "latest_date":          latest_daily.strftime("%B %Y"),
        "as_of_daily":          latest_daily.strftime("%B %d, %Y"),
        "as_of_wcs":            latest_wcs.strftime("%B %Y"),

        "wti":                  wti_now,
        "wti_yoy_pct":          wti_yoy_pct if wti_yoy_pct is not None else 0.0,
        "wti_3mo_change_pct":   wti_3mo_change if wti_3mo_change is not None else 0.0,
        "brent":                brent_now,

        "wcs":                  wcs_now,
        "wcs_wti_differential": wcs_wti_diff,

        "usdcad":                  usdcad_now,
        "usdcad_3mo_change_pct":   usdcad_3mo_change_pct,
        "usdcad_6mo_change_pct":   usdcad_6mo_change_pct,
        "usdcad_12mo_change_pct":  usdcad_12mo_change_pct,
        "in_stress_corridor":      in_stress_corridor,
        "near_stress_corridor":    near_stress_corridor,

        "cpi_impulse_from_wti":         cpi_impulse_wti if cpi_impulse_wti is not None else 0.0,
        "implied_cpi_pp_from_cad_12mo": implied_cpi_pp_from_cad,

        "wti_3mo_direction":     wti_dir,
        "cad_3mo_direction":     cad_dir_usdcad,
        "petrocurrency_alignment": petrocurrency,
        "wti_cad_correlation_1y": wti_cad_corr if wti_cad_corr is not None else 0.0,
    }


def format_external_values(v: dict) -> str:
    stress_label = "INSIDE 1.45-1.47" if v['in_stress_corridor'] else \
                   ("near (1.43-1.49)" if v['near_stress_corridor'] else "no")
    return f"""== Latest data ==

Oil (as of {v['as_of_daily']}):
  WTI:                           ${v['wti']:.2f}/bbl
  WTI Y/Y change:                {v['wti_yoy_pct']:+.1f}%
  WTI 3-month change:            {v['wti_3mo_change_pct']:+.1f}%
  Brent:                         ${v['brent']:.2f}/bbl
  Implied headline CPI impulse:  {v['cpi_impulse_from_wti']:+.2f}pp   (WTI Y/Y * gasoline-basket-weight 3.7%; mechanical, gasoline channel only)

WCS — Western Canada Select (as of {v['as_of_wcs']}):
  WCS price:                     ${v['wcs']:.2f}/bbl
  WCS-to-WTI discount:           ${v['wcs_wti_differential']:.2f}/bbl   (typical $10-15; >$20 = pipeline-constrained; <$12 = post-TMX expansion)

USDCAD (as of {v['as_of_daily']}):
  Level:                         {v['usdcad']:.4f}   (higher = weaker CAD)
  3-month change:                {v['usdcad_3mo_change_pct']:+.2f}%
  6-month change:                {v['usdcad_6mo_change_pct']:+.2f}%
  12-month change:               {v['usdcad_12mo_change_pct']:+.2f}%
  Stress corridor (1.45-1.47):   {stress_label}
  Implied 12mo CPI pass-through: {v['implied_cpi_pp_from_cad_12mo']:+.2f}pp   (12mo CAD move * ~0.045pp per 1%; goods CPI; concentrated over 12-18 months)

Petrocurrency relationship:
  WTI 3mo direction:             {v['wti_3mo_direction']}
  CAD 3mo direction (USDCAD):    {v['cad_3mo_direction']}   (USDCAD higher = CAD weaker)
  Alignment:                     {v['petrocurrency_alignment']}
  WTI-CAD daily-change correlation (last 1y): {v['wti_cad_correlation_1y']:+.2f}   (post-2016 typical: weak; <0.3 absolute = decoupled)

Coverage gap: this framework tracks oil and bilateral USDCAD only. BoC also tracks CEER (multilateral CAD index — sometimes diverges materially from USDCAD), credit spreads, equity markets, and explicit FX risk premium decomposition (which has been the dominant CAD driver in 2024-2025 episodes per BoC SAN 2025-2 and MPR Jan 2025 In Focus). The view is partial; flag conclusions accordingly when the partial read might mislead.
"""


# ── GDP & Activity section ──────────────────────────────────────────────────

def compute_gdp_values() -> dict:
    gdp_monthly  = load_series("gdp_monthly")
    gdp_q_level  = load_series("gdp_quarterly")
    gdp_qq       = load_series("gdp_qq_growth")            # already pre-computed Q/Q % AR
    contrib_cons = load_series("gdp_contrib_consumption")
    contrib_inv  = load_series("gdp_contrib_investment")
    contrib_govt = load_series("gdp_contrib_govt")
    contrib_exp  = load_series("gdp_contrib_exports")
    contrib_imp  = load_series("gdp_contrib_imports")      # sign-flipped: positive = imports declined
    contrib_invn = load_series("gdp_contrib_inventories")

    # Monthly GDP Y/Y, M/M
    gdp_m_yoy = (gdp_monthly.pct_change(12) * 100).dropna()
    gdp_m_mom = (gdp_monthly.pct_change(1)  * 100).dropna()

    latest_m = gdp_monthly.index[-1]
    latest_q = gdp_q_level.index[-1]

    monthly_yoy = float(asof(gdp_m_yoy, latest_m))
    monthly_mom = float(asof(gdp_m_mom, latest_m))

    quarterly_qq_ar = float(gdp_qq.iloc[-1])
    # Last 4 quarters of Q/Q AR for trend context
    last_4q = gdp_qq.tail(4)
    qq_4q_avg = float(last_4q.mean())

    # Contributions (latest quarter)
    cons = float(contrib_cons.iloc[-1])
    inv  = float(contrib_inv.iloc[-1])
    govt = float(contrib_govt.iloc[-1])
    exp  = float(contrib_exp.iloc[-1])
    imp  = float(contrib_imp.iloc[-1])
    invn = float(contrib_invn.iloc[-1])

    net_trade = exp + imp  # imports already sign-flipped per StatsCan convention
    final_domestic_demand = cons + inv + govt
    total_check = cons + inv + govt + exp + imp + invn

    # Identify dominant driver (largest absolute contribution)
    contribs = {
        "Consumption": cons,
        "Investment": inv,
        "Government": govt,
        "Net trade": net_trade,
        "Inventories": invn,
    }
    dominant_label, dominant_value = max(contribs.items(), key=lambda kv: abs(kv[1]))

    return {
        "latest_date":              latest_m.strftime("%B %Y"),  # use monthly for header
        "as_of_monthly":            latest_m.strftime("%B %Y"),
        "as_of_quarterly":          latest_q.strftime("%B %Y"),

        "monthly_gdp_yoy":          monthly_yoy,
        "monthly_gdp_mom":          monthly_mom,
        "quarterly_qq_ar":          quarterly_qq_ar,
        "quarterly_qq_ar_4q_avg":   qq_4q_avg,
        "quarterly_qq_ar_last_4q":  [float(x) for x in last_4q.values.tolist()],

        "contrib_consumption":      cons,
        "contrib_investment":       inv,
        "contrib_government":       govt,
        "contrib_exports":          exp,
        "contrib_imports":          imp,
        "contrib_net_trade":        net_trade,
        "contrib_inventories":      invn,
        "final_domestic_demand":    final_domestic_demand,
        "total_check":              total_check,
        "dominant_driver":          dominant_label,
        "dominant_driver_value":    dominant_value,
    }


def format_gdp_values(v: dict) -> str:
    last_4q_str = ", ".join(f"{x:+.2f}%" for x in v['quarterly_qq_ar_last_4q'])
    return f"""== Latest data ==

Real GDP — monthly (as of {v['as_of_monthly']}):
  Y/Y change:                  {v['monthly_gdp_yoy']:+.2f}%
  M/M change:                  {v['monthly_gdp_mom']:+.2f}%

Real GDP — quarterly (as of {v['as_of_quarterly']}):
  Q/Q at annualized rate:      {v['quarterly_qq_ar']:+.2f}%   (headline number; >0 = expansion, <0 = contraction)
  Last 4 quarters Q/Q AR:      {last_4q_str}
  4-quarter average:           {v['quarterly_qq_ar_4q_avg']:+.2f}%

Contributions to last quarter's annualized growth (percentage points; sum to total):
  Consumption:                 {v['contrib_consumption']:+.2f}pp
  Investment:                  {v['contrib_investment']:+.2f}pp
  Government:                  {v['contrib_government']:+.2f}pp
  Exports:                     {v['contrib_exports']:+.2f}pp
  Less: imports (sign-flip):   {v['contrib_imports']:+.2f}pp   (positive = imports fell)
  Net trade:                   {v['contrib_net_trade']:+.2f}pp
  Inventories:                 {v['contrib_inventories']:+.2f}pp   (often noisy; reverses next quarter)

Synthesis:
  Final domestic demand:       {v['final_domestic_demand']:+.2f}pp   (consumption + investment + govt; the "underlying" read)
  Sum of tracked components:   {v['total_check']:+.2f}pp   (will differ from Q/Q AR by the statistical discrepancy term, which StatsCan publishes separately and this framework does not currently track)
  Dominant driver:             {v['dominant_driver']} at {v['dominant_driver_value']:+.2f}pp

Coverage gap: this framework tracks aggregate GDP and demand-side contributions only. It does not include output-gap estimates, capacity utilization, or productivity decomposition. Conclusions about how-far-from-potential are necessarily rough.
"""


# ── Housing section ─────────────────────────────────────────────────────────

def compute_housing_values() -> dict:
    starts  = load_series("housing_starts")               # SAAR units
    nhpi    = load_series("new_housing_price_index")      # index Dec 2016 = 100
    permits = load_series("residential_permits")          # $thousands SA

    # Y/Y and M/M for each
    starts_yoy = (starts.pct_change(12) * 100).dropna()
    starts_mom = (starts.pct_change(1)  * 100).dropna()
    nhpi_yoy   = (nhpi.pct_change(12)   * 100).dropna()
    nhpi_mom   = (nhpi.pct_change(1)    * 100).dropna()
    permits_yoy = (permits.pct_change(12) * 100).dropna()
    permits_mom = (permits.pct_change(1)  * 100).dropna()

    # Earliest of all latest dates
    latest = min(s.index[-1] for s in [starts, starts_yoy, nhpi, nhpi_yoy, permits, permits_yoy])

    starts_now      = float(asof(starts, latest))
    starts_now_yoy  = float(asof(starts_yoy, latest))
    starts_now_mom  = float(asof(starts_mom, latest))
    starts_3mo_avg  = float(starts.tail(3).mean())  # 3-month moving average to filter noise

    nhpi_now      = float(asof(nhpi, latest))
    nhpi_now_yoy  = float(asof(nhpi_yoy, latest))
    nhpi_now_mom  = float(asof(nhpi_mom, latest))

    permits_now      = float(asof(permits, latest))
    permits_now_yoy  = float(asof(permits_yoy, latest))
    permits_now_mom  = float(asof(permits_mom, latest))

    # Cycle-position interpretation for starts (HYPOTHESIS-GRADE thresholds).
    # Data is in thousands of units annualized (e.g. 251 = 251,000 SAAR).
    if starts_3mo_avg < 180:
        starts_regime = "subdued (recession-era levels)"
    elif starts_3mo_avg > 280:
        starts_regime = "elevated / booming"
    else:
        starts_regime = "near trend"

    return {
        "latest_date":         latest.strftime("%B %Y"),
        "as_of":               latest.strftime("%B %Y"),

        "housing_starts":            starts_now,
        "housing_starts_3mo_avg":    starts_3mo_avg,
        "housing_starts_yoy":        starts_now_yoy,
        "housing_starts_mom":        starts_now_mom,
        "housing_starts_regime":     starts_regime,

        "nhpi":                      nhpi_now,
        "nhpi_yoy":                  nhpi_now_yoy,
        "nhpi_mom":                  nhpi_now_mom,

        "residential_permits":       permits_now,
        "residential_permits_yoy":   permits_now_yoy,
        "residential_permits_mom":   permits_now_mom,
    }


def format_housing_values(v: dict) -> str:
    return f"""== Latest data: {v['as_of']} ==

Housing starts (SAAR; values are in thousands of units annualized — e.g. 251 means 251,000):
  Latest:                      {v['housing_starts']:,.0f}k   (= {int(v['housing_starts']*1000):,} units annualized)
  3-month moving average:      {v['housing_starts_3mo_avg']:,.0f}k   (filters month-to-month noise)
  Y/Y change:                  {v['housing_starts_yoy']:+.1f}%
  M/M change:                  {v['housing_starts_mom']:+.1f}%
  Regime classification:       {v['housing_starts_regime']}   (HYPOTHESIS-GRADE thresholds: <180k subdued; 180-280k near trend; >280k elevated)

New Housing Price Index (Dec 2016 = 100):
  Latest:                      {v['nhpi']:.1f}
  Y/Y change:                  {v['nhpi_yoy']:+.1f}%   (>5% = meaningful price acceleration; <0% = price declines, rare)
  M/M change:                  {v['nhpi_mom']:+.2f}%

Residential building permits (value, SA, leading indicator ~6-12 months ahead of starts):
  Latest:                      ${v['residential_permits']/1_000_000:,.2f}B   (raw value: ${v['residential_permits']:,.0f}k)
  Y/Y change:                  {v['residential_permits_yoy']:+.1f}%
  M/M change:                  {v['residential_permits_mom']:+.1f}%

Coverage gap: this framework tracks new construction (starts, permits) and new-home prices (NHPI) only. It does NOT track resale activity (CREA MLS), mortgage rate spreads, mortgage renewal volumes, or regional breakdowns (Toronto / Vancouver vs. rest of Canada). Conclusions are macro-level; flag accordingly when a partial read might mislead.
"""


# ── Section registry ─────────────────────────────────────────────────────────

SECTIONS = {
    "inflation": {
        "name":     "Inflation",
        "compute":  compute_inflation_values,
        "format":   format_inflation_values,
    },
    "policy": {
        "name":     "Monetary Policy",
        "compute":  compute_policy_values,
        "format":   format_policy_values,
    },
    "gdp": {
        "name":     "GDP & Activity",
        "compute":  compute_gdp_values,
        "format":   format_gdp_values,
    },
    "labour": {
        "name":     "Labour Market",
        "compute":  compute_labour_values,
        "format":   format_labour_values,
    },
    "housing": {
        "name":     "Housing",
        "compute":  compute_housing_values,
        "format":   format_housing_values,
    },
    "financial": {
        "name":     "Financial Conditions",
        "compute":  compute_external_values,
        "format":   format_external_values,
    },
}


# ── Prompt + API call ────────────────────────────────────────────────────────

def build_prompt(section_id: str, framework: str, values_str: str,
                 prior_blurb: str | None = None) -> str:
    section_name = SECTIONS[section_id]["name"]
    prior = ""
    if prior_blurb:
        prior = (
            "\n== Prior month's blurb for this section (reference only; "
            "if signals have materially changed, surface what changed) ==\n\n"
            + prior_blurb + "\n"
        )
    return f"""You are generating a short analytical blurb for a public economic dashboard tracking Bank of Canada indicators. Read the analytical framework below, then read the latest computed data, then generate the blurb for the **{section_name}** section.

Output only the blurb prose. No preamble, no markdown headers, no quotation marks. Follow the framework's structure (takeaway -> anchor -> support -> closing nuance) and the writing-style rules (plain verbs, semicolons for parallel facts, conventional shorthand, plain hedges, no explanatory codas, no forecasts, no policy prescription). 3 sentences typically; 4 if there is a real tension worth surfacing in a closing slot.
{prior}
== Analytical Framework ==

{framework}

{values_str}

Now generate the {section_name} section blurb."""


def call_claude(prompt: str, max_tokens: int = 512) -> str:
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def review_blurb(blurb: str, framework: str, values_str: str, section_name: str) -> str:
    """
    Second LLM call to catch factual / interpretive errors before the blurb is saved.

    The model writes plausible-sounding prose; one-shot generation can miss
    domain-specific errors (asset/liability confusion, sign mistakes, wrong
    direction, wrong attribution, dates that don't match the data) that a
    higher-level meta-instruction in the framework can't reliably prevent.
    This pass attacks those failure modes directly with a focused checklist.

    Returns "PASS" or a bulleted list of issues. Issues do NOT block saving —
    they're recorded in blurbs.json under `review_flags` so the user can
    iterate on flagged blurbs while still seeing the latest output.
    """
    review_prompt = f"""You are reviewing an AI-generated analytical blurb for a Bank of Canada economics dashboard. The blurb was just generated against the framework section and computed data values below. Your job: check for factual or interpretive errors against those inputs.

== Framework section the blurb was generated against ==

{framework}

== Computed data values it should reflect ==

{values_str}

== Generated blurb ==

{blurb}

== Review checklist ==

For each, state PASS or describe the specific issue:

1. **Direction / sign correctness.** Every claim about something rising / falling / being above-or-below something else must match the data. E.g. "yields have risen" requires the data to show that.

2. **Asset / liability / structural correctness.** Does the blurb correctly distinguish things on opposite sides of a balance sheet, opposite signs of a spread, different categorical buckets? E.g. settlement balances are a BoC liability not asset; a -138bps BoC-Fed spread means BoC below Fed.

3. **Attribution.** Does the blurb attribute moves to the right entity? E.g. don't say "BoC has cut" if data shows hold; don't say "wages are rising" if measures are mixed.

4. **Dates and timeframes.** Do dates referenced match what the data shows?

5. **Action-state verb correctness.** If action_state is "on hold", verbs should reflect holding, not cutting/hiking.

6. **Magnitude / threshold correctness.** If the blurb cites a percentile, threshold, or magnitude, does it match the data?

== Output ==

Respond with EXACTLY one of:

- The single word "PASS" if the blurb has no factual errors against the framework and data.
- Otherwise, a bulleted list of specific factual issues. Each bullet: name the exact phrase, what's wrong, what the data actually shows.

Do NOT comment on writing style, voice, length, or word choice. Only factual / interpretive correctness against the inputs above."""
    return call_claude(review_prompt, max_tokens=600)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-only", action="store_true",
                        help="Compute values and print the prompt; do not call API.")
    parser.add_argument("--section", default="inflation",
                        help="Section to generate (default: inflation).")
    args = parser.parse_args()

    section_id = args.section
    if section_id not in SECTIONS:
        print(f"Unknown section: {section_id}. Known: {list(SECTIONS)}", file=sys.stderr)
        sys.exit(2)

    framework = FRAMEWORK.read_text(encoding="utf-8")
    section = SECTIONS[section_id]
    values = section["compute"]()
    values_str = section["format"](values)

    print(f"=== {section['name']} — values for {values['latest_date']} ===\n")
    print(values_str)

    # Load any prior blurb for this section
    prior = None
    if OUT.exists():
        try:
            prior_data = json.loads(OUT.read_text())
            prior = prior_data.get(section_id, {}).get("text")
        except json.JSONDecodeError as e:
            print(f"  Warning: blurbs.json could not be parsed (line {e.lineno}, col {e.colno}); proceeding without prior-blurb context.", file=sys.stderr)

    prompt = build_prompt(section_id, framework, values_str, prior_blurb=prior)

    if args.print_only:
        print("\n=== Prompt (not sent) ===\n")
        print(prompt[:1500] + ("\n... (truncated)" if len(prompt) > 1500 else ""))
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        print("Set the env var and rerun. The prompt is ready and the data is computed; "
              "only the API call is missing.", file=sys.stderr)
        sys.exit(1)

    print(f"\nCalling Claude ({MODEL})...")
    blurb = call_claude(prompt)

    print("\n=== Generated blurb ===\n")
    print(blurb)

    print("\nRunning self-review pass for factual correctness...")
    review = review_blurb(blurb, framework, values_str, section["name"])
    print("\n=== Self-review verdict ===\n")
    print(review)
    review_passed = review.strip().upper().startswith("PASS")

    out: dict = {}
    if OUT.exists():
        try:
            out = json.loads(OUT.read_text())
        except json.JSONDecodeError as e:
            # Don't silently overwrite — back up the corrupt file so we don't lose other sections' blurbs.
            from datetime import datetime
            backup_path = OUT.with_suffix(f".corrupt.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            OUT.rename(backup_path)
            print(f"  Warning: blurbs.json was corrupt (line {e.lineno}, col {e.colno}). Backed up to {backup_path.name} before writing fresh file.", file=sys.stderr)
            out = {}
    entry = {
        "as_of": values["latest_date"],
        "model": MODEL,
        "text":  blurb,
    }
    if not review_passed:
        # Save flags so the user can iterate on blurbs that the review questioned;
        # don't block saving — stale-but-flagged is more useful than nothing.
        entry["review_flags"] = review
        print("\nWARNING: self-review flagged issues. Blurb saved with review_flags; iterate when you next review the dashboard.", file=sys.stderr)
    out[section_id] = entry
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nWrote: {OUT}")


if __name__ == "__main__":
    main()
