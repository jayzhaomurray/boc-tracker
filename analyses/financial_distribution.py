"""Empirical distributions for Financial Conditions (External) section
convention application.

Computes P50/P80/P95/P99 for three financial-conditions tail axes, covering:
  1. |USDCAD - median|  -- two-tailed signed; tier by central-share band
                           Descriptor pair: high (weak CAD) / low (strong CAD)
  2. WTI Y/Y pct change -- one-tailed for negative shock (oil disinflationary
                           impulse on headline CPI); also abs-envelope for
                           magnitude tiering
  3. WCS-WTI differential -- absolute envelope (always positive discount)
                              Descriptor pair: wide / narrow
  4. Brent Y/Y pct change -- same axis as WTI Y/Y for cross-reference

No BoC-published band applies to any of these indicators.  Empirical-only
frame throughout.

Resolution:
  USDCAD  -- daily, BoC noon rate.  Aggregated to monthly (last obs in month)
             to match the spread-convention methodology.
  WTI     -- daily.  Aggregated to monthly (last obs in month).
  WCS     -- already monthly.
  Brent   -- daily.  Aggregated to monthly (last obs in month).

Console output is ASCII-safe.  CSV writes tolerate PermissionError.

All data read from project data/ folder.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_DIR = Path(__file__).resolve().parent


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
    # Load raw series
    # ------------------------------------------------------------------
    usdcad_raw = load_csv(DATA / "usdcad.csv")
    wti_raw    = load_csv(DATA / "wti.csv")
    brent_raw  = load_csv(DATA / "brent.csv")
    wcs_raw    = load_csv(DATA / "wcs.csv")

    # Monthly last-observation
    usdcad = to_month_last(usdcad_raw)
    wti    = to_month_last(wti_raw)
    brent  = to_month_last(brent_raw)
    wcs    = wcs_raw.copy()  # already monthly

    # Align daily series date range to available data (longest common)
    # USDCAD goes back to 1990; WTI and Brent also 1990.  Use 1990 onward.
    # WCS goes back to 2005.

    # ------------------------------------------------------------------
    # SECTION 1: USDCAD -- two-tailed, |USDCAD - median| in CAD units
    # ------------------------------------------------------------------
    usdcad_full = usdcad.dropna()
    usdcad_median = float(np.median(usdcad_full.to_numpy()))

    date_min_cad = usdcad_full.index.min().date()
    date_max_cad = usdcad_full.index.max().date()
    n_cad = len(usdcad_full)

    print()
    print("=" * 72)
    print("SECTION 1: USDCAD level -- |USDCAD - long-run median|")
    print(f"  Tail axis : |USDCAD - median| in CAD, monthly month-last, {date_min_cad} to {date_max_cad}")
    print(f"  N         : {n_cad}")
    print(f"  Long-run median USDCAD : {usdcad_median:.4f}")
    print("=" * 72)

    arr1 = (usdcad_full - usdcad_median).abs().to_numpy()
    print(f"  Mean |dev|  : {np.mean(arr1):.4f}")
    print(f"  Min |dev|   : {np.min(arr1):.4f}  (observations nearest median)")
    print(f"  Max |dev|   : {np.max(arr1):.4f}  (most extreme CAD level)")
    print()
    s1_p50, s1_p80, s1_p95, s1_p99 = pct_block(arr1, "CAD deviation from median")
    print()
    print("  Selected percentiles of |USDCAD - median| (CAD):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr1, p):.4f}")
    print()
    # Stress corridor check: how many observations >= 1.45?
    stress_share = (usdcad_full >= 1.45).mean() * 100
    n_stress = (usdcad_full >= 1.45).sum()
    print(f"  Share of monthly obs with USDCAD >= 1.45 : {stress_share:.1f}%  (n={n_stress})")
    # By year
    for yr in [1998, 1999, 2000, 2001, 2002, 2003, 2016, 2020, 2025]:
        yr_obs = usdcad_full[usdcad_full.index.year == yr]
        if len(yr_obs) == 0:
            continue
        n_above = (yr_obs >= 1.45).sum()
        print(f"    {yr}: {n_above} months >= 1.45  (of {len(yr_obs)})")

    print()
    # What percentile is 1.45 in the full distribution?
    arr1_signed = usdcad_full.to_numpy()
    pct_1p45 = float(np.searchsorted(np.sort(arr1_signed), 1.45)) / n_cad * 100
    print(f"  USDCAD=1.45 sits at roughly P{pct_1p45:.0f} of the full monthly distribution")
    # Signed statistics
    print()
    print("  Signed USDCAD level stats (full history):")
    print(f"    Min     : {np.min(arr1_signed):.4f}")
    print(f"    P05     : {np.percentile(arr1_signed, 5):.4f}")
    print(f"    P25     : {np.percentile(arr1_signed, 25):.4f}")
    print(f"    Median  : {np.percentile(arr1_signed, 50):.4f}")
    print(f"    P75     : {np.percentile(arr1_signed, 75):.4f}")
    print(f"    P95     : {np.percentile(arr1_signed, 95):.4f}")
    print(f"    P99     : {np.percentile(arr1_signed, 99):.4f}")
    print(f"    Max     : {np.max(arr1_signed):.4f}")
    print()
    # Find peak and date
    max_idx = usdcad_full.idxmax()
    print(f"  All-time monthly peak: {usdcad_full.max():.4f}  on {max_idx.date()}")
    # Daily peak for the most commonly cited episodes
    print()
    print("  Daily USDCAD peaks within named episode windows (from raw daily data):")
    for label, start, end in [
        ("Jan 2016 oil crash",     "2016-01-01", "2016-01-31"),
        ("Mar 2020 COVID shock",   "2020-03-01", "2020-03-31"),
        ("Dec 2024-Jan 2025 eps.", "2024-12-01", "2025-01-31"),
        ("Feb 2025 peak",          "2025-02-01", "2025-02-28"),
        ("Full 2025 onward",       "2025-01-01", "2026-12-31"),
    ]:
        sub = usdcad_raw[(usdcad_raw.index >= start) & (usdcad_raw.index <= end)]
        if len(sub) == 0:
            print(f"    {label:<30} : no data")
            continue
        pk = sub.max()
        pk_date = sub.idxmax().date()
        print(f"    {label:<30} : {pk:.4f}  on {pk_date}")

    # ==================================================================
    # SECTION 2: WTI Y/Y -- one-tailed (negative = disinflationary shock)
    # ==================================================================
    wti_yoy = (wti.pct_change(12) * 100.0).dropna()
    date_min_wti = wti_yoy.index.min().date()
    date_max_wti = wti_yoy.index.max().date()
    n_wti = len(wti_yoy)

    print()
    print("=" * 72)
    print("SECTION 2: WTI Y/Y pct change -- tail axis for oil-as-CPI-impulse")
    print(f"  Tail axis : WTI Y/Y % (signed), monthly month-last, {date_min_wti} to {date_max_wti}")
    print(f"  N         : {n_wti}")
    print("=" * 72)

    arr2 = wti_yoy.to_numpy()
    print(f"  Median WTI Y/Y : {np.median(arr2):+.2f}%")
    print(f"  Mean   WTI Y/Y : {np.mean(arr2):+.2f}%")
    print(f"  Min    WTI Y/Y : {np.min(arr2):+.2f}%  (most negative = largest disinflationary shock)")
    print(f"  Max    WTI Y/Y : {np.max(arr2):+.2f}%  (largest inflationary shock)")
    print()

    # Absolute-magnitude axis for tier thresholding
    arr2_abs = np.abs(arr2)
    print("  Absolute-magnitude percentiles of |WTI Y/Y| (%):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr2_abs, p):.2f}%")
    print()
    s2a_p50, s2a_p80, s2a_p95, s2a_p99 = pct_block(arr2_abs, "|WTI Y/Y|, %")
    print()

    # One-tailed (negative side only) for disinflationary shock
    neg_mask = arr2 < 0
    arr2_neg = arr2[neg_mask]
    print(f"  One-tailed disinflationary analysis (WTI Y/Y < 0):")
    print(f"    Share of months with WTI Y/Y < 0 : {neg_mask.mean()*100:.1f}%  (n={neg_mask.sum()})")
    print(f"    Median negative Y/Y              : {np.median(arr2_neg):+.2f}%")
    print(f"    P10 of negative side (deep dips) : {np.percentile(arr2_neg, 10):+.2f}%")
    print(f"    Min negative Y/Y                 : {np.min(arr2_neg):+.2f}%")
    print()
    # What does the signed distribution look like at key thresholds?
    for threshold in [-10, -20, -30, -50]:
        share = (arr2 < threshold).mean() * 100
        print(f"    Share with WTI Y/Y < {threshold:3d}% : {share:.1f}%")
    print()
    # Signed percentiles (full, for symmetric tiering)
    print("  Signed WTI Y/Y percentiles (for symmetric tiering reference):")
    for p in [1, 5, 10, 20, 50, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr2, p):+.2f}%")

    # ==================================================================
    # SECTION 3: WCS-WTI differential -- absolute envelope
    # ==================================================================
    # WCS is monthly; WTI aggregated to monthly.  Align on common dates.
    combo_wcs = pd.DataFrame({"wcs": wcs_raw, "wti_mo": to_month_last(wti_raw)}).dropna()
    combo_wcs["diff"] = combo_wcs["wti_mo"] - combo_wcs["wcs"]  # positive = WCS at discount

    date_min_wcs = combo_wcs.index.min().date()
    date_max_wcs = combo_wcs.index.max().date()
    n_wcs = len(combo_wcs)

    print()
    print("=" * 72)
    print("SECTION 3: WCS-WTI differential -- absolute envelope ($/bbl discount)")
    print(f"  Tail axis : WTI - WCS differential in $/bbl, monthly, {date_min_wcs} to {date_max_wcs}")
    print(f"  N         : {n_wcs}")
    print("=" * 72)

    arr3 = combo_wcs["diff"].to_numpy()
    print(f"  Median differential : ${np.median(arr3):.2f}/bbl")
    print(f"  Mean   differential : ${np.mean(arr3):.2f}/bbl")
    print(f"  Min    differential : ${np.min(arr3):.2f}/bbl")
    print(f"  Max    differential : ${np.max(arr3):.2f}/bbl")
    print()
    s3_p50, s3_p80, s3_p95, s3_p99 = pct_block(arr3, "$/bbl WCS discount")
    print()
    print("  Selected percentiles of WCS-WTI differential ($/bbl):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : ${np.percentile(arr3, p):.2f}")
    print()
    # Framework threshold checks
    for threshold in [10, 12, 15, 20, 25]:
        share_above = (arr3 > threshold).mean() * 100
        share_below = (arr3 < threshold).mean() * 100
        print(f"    Share diff > ${threshold}/bbl : {share_above:.1f}%   |   Share diff <= ${threshold} : {share_below:.1f}%")
    print()
    # Peak episodes
    print("  Largest monthly differentials (by year):")
    combo_wcs["year"] = combo_wcs.index.year
    for yr in [2006, 2012, 2013, 2014, 2015, 2016, 2018, 2022, 2023, 2024, 2025]:
        yr_sub = combo_wcs[combo_wcs["year"] == yr]["diff"]
        if len(yr_sub) == 0:
            continue
        print(f"    {yr}: max ${yr_sub.max():.2f}  (median ${yr_sub.median():.2f})")

    # ==================================================================
    # SECTION 4: Brent Y/Y -- for cross-reference only (follows WTI)
    # ==================================================================
    brent_yoy = (brent.pct_change(12) * 100.0).dropna()
    date_min_br = brent_yoy.index.min().date()
    date_max_br = brent_yoy.index.max().date()
    n_br = len(brent_yoy)

    arr4 = brent_yoy.to_numpy()
    arr4_abs = np.abs(arr4)

    print()
    print("=" * 72)
    print("SECTION 4: Brent Y/Y -- cross-reference (follows WTI)")
    print(f"  N={n_br}, {date_min_br} to {date_max_br}")
    print("=" * 72)
    print(f"  Median Brent Y/Y : {np.median(arr4):+.2f}%")
    print(f"  Mean   Brent Y/Y : {np.mean(arr4):+.2f}%")
    print()
    print("  Absolute-magnitude percentiles of |Brent Y/Y| (%):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr4_abs, p):.2f}%")
    s4_p50, s4_p80, s4_p95, s4_p99 = pct_block(arr4_abs, "|Brent Y/Y|, %")

    # ==================================================================
    # SUMMARY TABLE
    # ==================================================================
    print()
    print("=" * 72)
    print("SUMMARY: Convention tier thresholds (P50/P80/P95/P99)")
    print("=" * 72)
    rows = [
        ("|USDCAD - median| (CAD)", "CAD from median", s1_p50, s1_p80, s1_p95, s1_p99),
        ("|WTI Y/Y| (%)",           "pct",             s2a_p50, s2a_p80, s2a_p95, s2a_p99),
        ("WCS-WTI differential ($/bbl)", "$/bbl",       s3_p50, s3_p80, s3_p95, s3_p99),
        ("|Brent Y/Y| (%)",         "pct",             s4_p50, s4_p80, s4_p95, s4_p99),
    ]
    print(f"  {'Indicator':<35}  {'Unit':<18}  {'P50':>7}  {'P80':>7}  {'P95':>7}  {'P99':>7}")
    print("  " + "-" * 80)
    for name, unit, p50, p80, p95, p99 in rows:
        print(f"  {name:<35}  {unit:<18}  {p50:>7.4f}  {p80:>7.4f}  {p95:>7.4f}  {p99:>7.4f}")
    print()
    print(f"  Note: USDCAD window = {date_min_cad} to {date_max_cad}, N={n_cad}")
    print(f"  Note: WTI Y/Y window = {date_min_wti} to {date_max_wti}, N={n_wti}")
    print(f"  Note: WCS-WTI window = {date_min_wcs} to {date_max_wcs}, N={n_wcs}")
    print(f"  Last computed: 2026-05-09")

    # ==================================================================
    # CSV output (optional, PermissionError tolerant)
    # ==================================================================
    out_csv = OUT_DIR / "financial_distribution.csv"
    try:
        combo_export = pd.DataFrame({
            "usdcad": usdcad_full,
            "usdcad_dev_from_median": usdcad_full - usdcad_median,
        }).join(wti_yoy.rename("wti_yoy"), how="outer") \
          .join(brent_yoy.rename("brent_yoy"), how="outer") \
          .join(combo_wcs["diff"].rename("wcs_wti_diff"), how="outer")
        combo_export.to_csv(out_csv)
        print(f"\nWrote working series -> {out_csv.relative_to(ROOT)}")
    except PermissionError:
        print(f"\nSkipped CSV write (file locked): {out_csv.relative_to(ROOT)}")
    except Exception as e:
        print(f"\nSkipped CSV write ({e}): {out_csv.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
