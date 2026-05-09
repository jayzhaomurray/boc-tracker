"""Empirical distributions for Inflation section convention application.

Computes P50/P80/P95/P99 for six inflation-related tail axes, covering:
  1. |headline CPI Y/Y - 2%|  -- BoC-band indicator empirical frame (target-anchored)
  2. M/M (SA) monthly prints  -- for M/M momentum threshold retuning
  3. Core band width (max core - min core across 5 measures)
                              -- for tight-band threshold retuning
  4. |headline Y/Y - core_avg Y/Y|
                              -- for headline-core gap threshold retuning
  5. |tilt| where tilt = (above-3% dev) - (below-1% dev), monthly, since 1996
                              -- Q3 decision: continuous breadth tier (replaces 4-state)
  6. |5y CSCE - 2%|           -- Q1 decision: empirical frame for 5y anchor diagnostic
                              -- (BoC band applied separately as binary in-/outside-band)

Resolution: monthly, using the most recent observation per calendar month
(same approach as bocfed_spread and can2y_overnight_spread worked examples).

BoC-band rule: headline CPI and core measures are BoC-band indicators
(control range 1-3%, target 2%). The empirical frame uses |x - 2%| as
the tail axis (target-anchored), per distribution_conventions.md.

Console output is ASCII-safe. CSV writes tolerate PermissionError.

All data read from project data/ folder (SA cpi_all_items, plus core
measures cpi_trim, cpi_median, cpi_common, cpix, cpixfet).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_DIR = Path(__file__).resolve().parent

import json  # for breadth mapping

# Core measures tracked by the framework (BoC preferred trio + CPIX/CPIXFET)
CORE_NAMES = ["cpi_trim", "cpi_median", "cpi_common", "cpix", "cpixfet"]


def load_csv(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.set_index("date").sort_index()
    return df["value"]


def to_month_last(s: pd.Series) -> pd.Series:
    """Pick the last (most recent) observation in each calendar month."""
    return s.groupby(s.index.to_period("M")).last().to_timestamp()


def pct_block(arr: np.ndarray, label: str) -> tuple[float, float, float, float]:
    """Print a percentile block and return (P50, P80, P95, P99)."""
    p50 = float(np.percentile(arr, 50))
    p80 = float(np.percentile(arr, 80))
    p95 = float(np.percentile(arr, 95))
    p99 = float(np.percentile(arr, 99))
    print(f"  P50 (typical boundary)    : {p50:.4f}  [{label}]")
    print(f"  P80 (uncommon boundary)   : {p80:.4f}  [{label}]")
    print(f"  P95 (pronounced boundary) : {p95:.4f}  [{label}]")
    print(f"  P99 (rare boundary)       : {p99:.4f}  [{label}]")
    print(f"  Extreme: above P99        : > {p99:.4f}  [{label}]")
    return p50, p80, p95, p99


def main() -> None:
    # ------------------------------------------------------------------
    # Load headline CPI (SA) - monthly
    # ------------------------------------------------------------------
    cpi_raw = load_csv(DATA / "cpi_all_items.csv")
    cpi_ms = to_month_last(cpi_raw)

    # Load core measures (Y/Y is computed identically across SA/NSA for 12M)
    cores_raw = {name: load_csv(DATA / f"{name}.csv") for name in CORE_NAMES}
    cores_ms = {name: to_month_last(s) for name, s in cores_raw.items()}

    # ------------------------------------------------------------------
    # Compute derived series
    # ------------------------------------------------------------------
    # Headline Y/Y (12-month pct change on raw index)
    cpi_yoy = cpi_ms.pct_change(12) * 100.0

    # Headline M/M (1-month pct change on raw index, SA)
    cpi_mom = cpi_ms.pct_change(1) * 100.0

    # Core measures: CSVs already store Y/Y percent values (not raw index).
    # Do NOT compute pct_change; read values directly.
    core_df = pd.DataFrame({name: cores_ms[name] for name in CORE_NAMES})

    # Align all series to a common date range
    combo = pd.concat([cpi_yoy.rename("headline_yoy"),
                       cpi_mom.rename("headline_mom"),
                       core_df], axis=1).dropna()

    # Core band width = max(core measures) - min(core measures) across 5 measures
    combo["core_band_width"] = combo[CORE_NAMES].max(axis=1) - combo[CORE_NAMES].min(axis=1)

    # Core average
    combo["core_avg"] = combo[CORE_NAMES].mean(axis=1)

    # Headline minus core average (gap, signed)
    combo["headline_minus_core"] = combo["headline_yoy"] - combo["core_avg"]

    # BoC-band empirical frame: |headline Y/Y - 2%| (target-anchored)
    TARGET = 2.0
    combo["abs_dev_from_target"] = (combo["headline_yoy"] - TARGET).abs()

    # Restrict to 1996 onward where possible. In practice CPIX starts 2000-01-01,
    # so the effective window begins 2000-01-01 (data-limited, not filter-limited).
    combo = combo[combo.index >= "1996-01-01"]

    n = len(combo)
    date_min = combo.index.min().date()
    date_max = combo.index.max().date()

    # ==================================================================
    # SECTION 1: BoC-band indicator -- |headline CPI Y/Y - 2%| (pp)
    # ==================================================================
    print()
    print("=" * 72)
    print("SECTION 1: BoC-band empirical frame -- |headline CPI Y/Y - 2%|")
    print(f"  Tail axis : |CPI Y/Y - 2.0%| in pp, monthly, {date_min} to {date_max}")
    print(f"  N         : {n}")
    print("=" * 72)
    arr1 = combo["abs_dev_from_target"].to_numpy()
    print(f"  Median    : {np.median(arr1):.4f} pp")
    print(f"  Mean      : {np.mean(arr1):.4f} pp")
    print(f"  Min       : {np.min(arr1):.4f} pp")
    print(f"  Max       : {np.max(arr1):.4f} pp")
    print()
    s1_p50, s1_p80, s1_p95, s1_p99 = pct_block(arr1, "pp from target")
    print()
    # BoC-band frame: binary in/out 1-3%
    headline_arr = combo["headline_yoy"].to_numpy()
    in_band = ((headline_arr >= 1.0) & (headline_arr <= 3.0)).mean() * 100
    print(f"  BoC binary frame: share within 1-3% band: {in_band:.1f}%")
    print(f"  Share above 3% (outside top): {(headline_arr > 3.0).mean()*100:.1f}%")
    print(f"  Share below 1% (outside bottom): {(headline_arr < 1.0).mean()*100:.1f}%")
    print()
    print("  Selected percentiles of |headline - 2%| (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr1, p):.4f} pp")

    # ==================================================================
    # SECTION 2: M/M momentum -- raw monthly percent change (SA)
    # ==================================================================
    print()
    print("=" * 72)
    print("SECTION 2: M/M momentum -- headline CPI M/M (SA, %/month)")
    print(f"  Tail axis : M/M pct change (signed), monthly, {date_min} to {date_max}")
    print(f"  N         : {n}")
    print("=" * 72)
    arr2 = combo["headline_mom"].to_numpy()
    print(f"  Median    : {np.median(arr2):.4f}%/month")
    print(f"  Mean      : {np.mean(arr2):.4f}%/month")
    print(f"  Min       : {np.min(arr2):.4f}%/month")
    print(f"  Max       : {np.max(arr2):.4f}%/month")
    print()
    # For M/M momentum, the tail axis is target-anchored: |M/M - 0.165%|
    # (0.165% is the neutral monthly rate for 2% annualized)
    NEUTRAL_MOM = 0.1652  # geometric: (1.02)^(1/12) - 1 as percent
    combo["abs_mom_dev"] = (combo["headline_mom"] - NEUTRAL_MOM).abs()
    arr2_dev = combo["abs_mom_dev"].to_numpy()
    print(f"  Tail axis for tier: |M/M - {NEUTRAL_MOM:.4f}%| (deviation from neutral)")
    print(f"  Median |deviation| : {np.median(arr2_dev):.4f}%/month")
    print()
    print("  Selected percentiles of |M/M - neutral| (pp/month):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr2_dev, p):.4f}%/month")
    s2_p50, s2_p80, s2_p95, s2_p99 = pct_block(arr2_dev, "%/month from neutral")
    print()
    print("  Verification of framework's unsourced thresholds against percentiles:")
    print(f"    0.3%/month above neutral (0.465 total) -> "
          f"P{np.searchsorted(np.sort(arr2_dev), 0.3)*100/n:.0f} approx; "
          f"share above: {(arr2_dev > 0.3).mean()*100:.1f}%")
    print(f"    0.1%/month below neutral (0.065 total) -> "
          f"share |dev|>0.065: {(arr2_dev > 0.065).mean()*100:.1f}%")
    print(f"    Note: 0.3 above / 0.1 below from neutral are NOT symmetric;")
    print(f"    raw M/M distribution:")
    print(f"      share >= 0.3% : {(arr2 >= 0.3).mean()*100:.1f}%")
    print(f"      share <= 0.1% : {(arr2 <= 0.1).mean()*100:.1f}%")
    print(f"      share >= 0.465 (=0.165+0.3): {(arr2 >= 0.465).mean()*100:.1f}%")
    print(f"      share <= 0.065 (=0.165-0.1) : {(arr2 <= 0.065).mean()*100:.1f}%")

    # ==================================================================
    # SECTION 3: Core band width (max core - min core, all 5 measures, pp)
    # ==================================================================
    print()
    print("=" * 72)
    print("SECTION 3: Core band width -- max(core) - min(core) across 5 measures (pp)")
    print(f"  Tail axis : band width (non-negative, absolute envelope), monthly, {date_min} to {date_max}")
    print(f"  N         : {n}")
    print("=" * 72)
    arr3 = combo["core_band_width"].to_numpy()
    print(f"  Median    : {np.median(arr3):.4f} pp")
    print(f"  Mean      : {np.mean(arr3):.4f} pp")
    print(f"  Min       : {np.min(arr3):.4f} pp")
    print(f"  Max       : {np.max(arr3):.4f} pp")
    print()
    s3_p50, s3_p80, s3_p95, s3_p99 = pct_block(arr3, "pp band width")
    print()
    print("  Selected percentiles of core band width (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr3, p):.4f} pp")
    print()
    print("  Verification of framework's unsourced threshold (0.5pp 'tight band'):")
    print(f"    Share with width <= 0.5pp : {(arr3 <= 0.5).mean()*100:.1f}%  "
          f"(i.e., 0.5pp = P{(arr3 <= 0.5).mean()*100:.0f} approx)")

    # ==================================================================
    # SECTION 4: |Headline Y/Y - core average Y/Y| (pp)
    # ==================================================================
    print()
    print("=" * 72)
    print("SECTION 4: Headline-core gap -- |headline Y/Y - core avg Y/Y| (pp)")
    print(f"  Tail axis : |headline - core_avg| in pp, monthly, {date_min} to {date_max}")
    print(f"  N         : {n}")
    print("=" * 72)
    arr4 = combo["headline_minus_core"].abs().to_numpy()
    print(f"  Median    : {np.median(arr4):.4f} pp")
    print(f"  Mean      : {np.mean(arr4):.4f} pp")
    print(f"  Min       : {np.min(arr4):.4f} pp")
    print(f"  Max       : {np.max(arr4):.4f} pp")
    print()
    s4_p50, s4_p80, s4_p95, s4_p99 = pct_block(arr4, "pp |headline-core|")
    print()
    print("  Selected percentiles of |headline - core_avg| (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr4, p):.4f} pp")
    print()
    print("  Verification of framework's unsourced threshold (0.3pp gap):")
    print(f"    Share with |gap| > 0.3pp : {(arr4 > 0.3).mean()*100:.1f}%  "
          f"(i.e., 0.3pp threshold = P{(arr4 <= 0.3).mean()*100:.0f} approx)")
    print()
    # Signed gap stats
    signed_gap = combo["headline_minus_core"].to_numpy()
    print(f"  Signed gap (headline - core_avg) stats:")
    print(f"    Median   : {np.median(signed_gap):+.4f} pp")
    print(f"    Share headline > core : {(signed_gap > 0).mean()*100:.1f}%")
    print(f"    Share headline < core : {(signed_gap < 0).mean()*100:.1f}%")

    # ==================================================================
    # SECTION 5: |tilt| -- breadth tilt envelope (Q3 decision: continuous tier)
    # tilt = (above-3% share deviation from 1996-2019 avg)
    #        - (below-1% share deviation from 1996-2019 avg)
    # Tail axis: |tilt| in pp, monthly, since 1996 (full breadth window)
    # ==================================================================
    print()
    print("=" * 72)
    print("SECTION 5: Breadth tilt -- |tilt| in pp  (Q3: continuous tier)")
    print("  tilt = (above-3% share deviation) - (below-1% share deviation)")
    print("  from 1996-2019 historical averages.  Positive = pressure; Negative = softening.")
    print("  Tail axis: |tilt| (absolute envelope of a signed statistic).")
    print("=" * 72)
    mapping = json.loads((DATA / "cpi_breadth_mapping.json").read_text())
    weights_b = pd.Series({m["name"]: m["wt_value"] for m in mapping
                           if m["wt_value"] is not None})
    comp_b = pd.read_csv(DATA / "cpi_components.csv", parse_dates=["date"], index_col="date")
    keep_b = [c for c in comp_b.columns
              if c in weights_b.index
              and comp_b[c].first_valid_index() <= pd.Timestamp("1995-01-01")]
    comp_b = comp_b[keep_b]
    w_b = weights_b.reindex(keep_b).fillna(0)
    w_b = w_b / w_b.sum()
    yoy_c_b = comp_b.pct_change(12) * 100
    above3_b = yoy_c_b.gt(3).multiply(w_b, axis=1).sum(axis=1) * 100
    below1_b = yoy_c_b.lt(1).multiply(w_b, axis=1).sum(axis=1) * 100
    valid_b = yoy_c_b.notna().all(axis=1)
    above3_b = above3_b[valid_b]
    below1_b = below1_b[valid_b]
    ha_above_b = float(above3_b["1996":"2019"].mean())
    ha_below_b = float(below1_b["1996":"2019"].mean())
    above_dev_b = above3_b - ha_above_b
    below_dev_b = below1_b - ha_below_b
    tilt_b = above_dev_b - below_dev_b
    tilt_b = tilt_b.dropna()
    arr5_signed = tilt_b.to_numpy()
    arr5 = np.abs(arr5_signed)
    n5 = len(arr5)
    date_min5 = tilt_b.index.min().date()
    date_max5 = tilt_b.index.max().date()
    print(f"  Tail axis : |tilt| in pp, monthly, {date_min5} to {date_max5}")
    print(f"  N         : {n5}")
    print(f"  1996-2019 avg above-3% share : {ha_above_b:.2f}%")
    print(f"  1996-2019 avg below-1% share : {ha_below_b:.2f}%")
    print(f"  Signed tilt stats:")
    print(f"    Median (signed): {np.median(arr5_signed):.2f}pp")
    print(f"    Share positive  : {(arr5_signed > 0).mean()*100:.1f}%  (pressure tilt)")
    print(f"    Share negative  : {(arr5_signed < 0).mean()*100:.1f}%  (softening tilt)")
    print(f"  |tilt| stats:")
    print(f"    Median |tilt|  : {np.median(arr5):.2f}pp")
    print(f"    Mean   |tilt|  : {np.mean(arr5):.2f}pp")
    print(f"    Min    |tilt|  : {np.min(arr5):.2f}pp")
    print(f"    Max    |tilt|  : {np.max(arr5):.2f}pp")
    print()
    s5_p50, s5_p80, s5_p95, s5_p99 = pct_block(arr5, "pp |tilt|")
    print()
    print("  Selected percentiles of |tilt| (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr5, p):.2f}pp")
    latest_tilt = float(tilt_b.iloc[-1])
    latest_abs_tilt = abs(latest_tilt)
    latest_tilt_pctile = float((arr5 <= latest_abs_tilt).mean() * 100)
    descriptor5 = "pressure" if latest_tilt > 0 else "softening"
    print(f"\n  Current reading (as of {date_max5}):")
    print(f"    tilt = {latest_tilt:+.2f}pp  ({descriptor5})")
    print(f"    |tilt| = {latest_abs_tilt:.2f}pp  (~P{latest_tilt_pctile:.0f} of historical distribution)")

    # ==================================================================
    # SECTION 6: |5y CSCE - 2%| -- anchor diagnostic (Q1 decision: empirical)
    # BoC dual frame: binary in/outside 1-3% band + empirical 5-tier on |5y - 2%|
    # Note small N (quarterly since 2015); state N, downgrade confidence.
    # ==================================================================
    print()
    print("=" * 72)
    print("SECTION 6: 5y CSCE anchor -- |5y CSCE - 2%| in pp  (Q1: empirical frame)")
    print("  BoC frame (binary): in-band (1-3%) / outside-band.  Empirical: 5-tier ladder.")
    print("  Small-N caveat: quarterly series, N << 200 -- extreme tier sparsely populated.")
    print("=" * 72)
    csce5_raw = load_csv(DATA / "infl_exp_consumer_5y.csv")
    csce5 = csce5_raw.dropna()
    arr6_raw = csce5.to_numpy()
    arr6 = np.abs(arr6_raw - 2.0)
    n6 = len(arr6)
    date_min6 = csce5.index.min().date()
    date_max6 = csce5.index.max().date()
    print(f"  Tail axis : |5y CSCE - 2.0%| in pp, quarterly, {date_min6} to {date_max6}")
    print(f"  N         : {n6}  (SMALL-N: extreme tier sparsely populated)")
    in_band6 = ((arr6_raw >= 1.0) & (arr6_raw <= 3.0)).mean() * 100
    above3_6 = (arr6_raw > 3.0).mean() * 100
    below1_6 = (arr6_raw < 1.0).mean() * 100
    print(f"  BoC binary frame: in-band (1-3%): {in_band6:.1f}%,  above-3%: {above3_6:.1f}%,  below-1%: {below1_6:.1f}%")
    print(f"  NOTE: {above3_6:.0f}% of quarterly readings are above 3% -- binary BoC frame almost")
    print(f"    always signals outside-band. Empirical tier provides richer signal here.")
    print(f"  |5y - 2%| stats:")
    print(f"    Median   : {np.median(arr6):.4f}pp")
    print(f"    Mean     : {np.mean(arr6):.4f}pp")
    print(f"    Min      : {np.min(arr6):.4f}pp")
    print(f"    Max      : {np.max(arr6):.4f}pp")
    print()
    s6_p50, s6_p80, s6_p95, s6_p99 = pct_block(arr6, "pp |5y CSCE - 2%|")
    print()
    print("  Selected percentiles of |5y CSCE - 2%| (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr6, p):.4f}pp")
    latest_5y = float(csce5.iloc[-1])
    latest_abs_5y = abs(latest_5y - 2.0)
    latest_5y_pctile = float((arr6 <= latest_abs_5y).mean() * 100)
    boc_frame_5y = "in-band" if 1.0 <= latest_5y <= 3.0 else ("outside-band (above)" if latest_5y > 3.0 else "outside-band (below)")
    print(f"\n  Current reading (as of {date_max6}):")
    print(f"    5y CSCE = {latest_5y:.2f}%  (BoC frame: {boc_frame_5y})")
    print(f"    |5y - 2%| = {latest_abs_5y:.4f}pp  (~P{latest_5y_pctile:.0f} of historical distribution)")

    # ==================================================================
    # SUMMARY TABLE
    # ==================================================================
    print()
    print("=" * 72)
    print("SUMMARY: Convention tier thresholds (P50/P80/P95/P99)")
    print("=" * 72)
    rows = [
        ("headline |CPI Y/Y - 2%| (pp)", "pp from target", s1_p50, s1_p80, s1_p95, s1_p99),
        ("M/M momentum |M/M - 0.165%| (%/mo)", "%/mo from neutral", s2_p50, s2_p80, s2_p95, s2_p99),
        ("core band width (pp)", "pp", s3_p50, s3_p80, s3_p95, s3_p99),
        ("|headline - core_avg| (pp)", "pp", s4_p50, s4_p80, s4_p95, s4_p99),
        ("|tilt| breadth (pp) [monthly, N=364]", "pp", s5_p50, s5_p80, s5_p95, s5_p99),
        ("|5y CSCE - 2%| (pp) [quarterly, N=44]", "pp", s6_p50, s6_p80, s6_p95, s6_p99),
    ]
    print(f"  {'Indicator':<45}  {'P50':>7}  {'P80':>7}  {'P95':>7}  {'P99':>7}")
    print("  " + "-" * 73)
    for row in rows:
        name, unit, p50, p80, p95, p99 = row
        print(f"  {name:<45}  {p50:>7.4f}  {p80:>7.4f}  {p95:>7.4f}  {p99:>7.4f}")
    print()
    print(f"  Sections 1-4 window: monthly month-last, {date_min} to {date_max}, N={n}")
    print(f"  Section 5 window: monthly, {date_min5} to {date_max5}, N={n5}")
    print(f"  Section 6 window: quarterly, {date_min6} to {date_max6}, N={n6} (SMALL-N)")
    print(f"  Last computed: 2026-05-09")

    # ==================================================================
    # CSV output (optional, PermissionError tolerant)
    # ==================================================================
    out_csv = OUT_DIR / "inflation_distribution.csv"
    try:
        combo.to_csv(out_csv)
        print(f"\nWrote working series -> {out_csv.relative_to(ROOT)}")
    except PermissionError:
        print(f"\nSkipped CSV write (file locked): {out_csv.relative_to(ROOT)}")
    except Exception as e:
        print(f"\nSkipped CSV write ({e}): {out_csv.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
