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
    above_dev = float(above3.loc[latest] - ha_above)
    below_dev = float(below1.loc[latest] - ha_below)
    tilt = above_dev - below_dev

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
        "breadth_above3":      float(above3.loc[latest]),
        "breadth_below1":      float(below1.loc[latest]),
        "breadth_above3_dev":  above_dev,
        "breadth_below1_dev":  below_dev,
        "breadth_tilt":        tilt,
    }


def format_inflation_values(v: dict) -> str:
    c = v["cores"]
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
  Breadth tilt:           {v['breadth_tilt']:+.1f}pp   (positive = broad-based pressure; negative = broad-based softening)
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

Balance sheet (C$B, as of {v['as_of_balance_sheet']}):
  Operating phase:               {v['qt_phase']}
  Total assets:                  {v['total_assets']:.1f}B   ({v['distance_from_baseline']:+.1f}B vs ~$120B baseline; {v['distance_from_peak_qe']:+.1f}B vs ~$575B March 2021 peak)
  GoC bonds:                     {v['goc_bonds']:.1f}B
  Non-GoC components:            {v['non_goc']:.1f}B   (T-bills, term repos, advances, FX swaps, etc.)
  Settlement balances:           {v['settlement']:.1f}B   (post-QT target range: ${v['settlement_target_low']}–${v['settlement_target_high']}B)

Trajectory (change over last 6mo / 12mo):
  Total assets:                  {v['ta_change_6mo']:+.1f}B / {v['ta_change_12mo']:+.1f}B
  GoC bonds:                     {v['gb_change_6mo']:+.1f}B / {v['gb_change_12mo']:+.1f}B
  Non-GoC components:            {v['non_goc_change_6mo']:+.1f}B / {v['non_goc_change_12mo']:+.1f}B   (rapid expansion = stress signal)
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
    # Future: "labour", "external"
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


def call_claude(prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


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
        except Exception:
            pass

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

    out: dict = {}
    if OUT.exists():
        try:
            out = json.loads(OUT.read_text())
        except Exception:
            out = {}
    out[section_id] = {
        "as_of": values["latest_date"],
        "model": MODEL,
        "text":  blurb,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nWrote: {OUT}")


if __name__ == "__main__":
    main()
