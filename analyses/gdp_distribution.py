"""Empirical distributions for GDP & Activity section convention application.

Computes P50/P80/P95/P99 for three GDP-related tail axes:

  1. |GDP Q/Q AR - 2%|  -- quarterly GDP momentum deviation from potential proxy
     (using gdp_total_contribution, quarterly, since 1961; tail axis: target-anchored)

  2. |Inventory contribution to GDP growth| (pp, AR)
     (using gdp_contrib_inventories, quarterly, since 1961; tail axis: absolute envelope)
     Retunes the framework's asserted +-3pp threshold empirically.

  3. GDP monthly Y/Y  -- signed two-tailed, since 1997
     (using gdp_monthly pct_change(12), monthly; tail axis: signed vs. median)

Note on industry contributions: the dashboard tracks gdp_industry_goods,
gdp_industry_manufacturing, gdp_industry_mining_oil, gdp_industry_services
as Y/Y levels (monthly). The framework does not assert tier thresholds for
individual industries; these are not tiered here. If per-industry tier language
is added to the framework later, this script should be extended.

Resolution: quarterly for contributions series, monthly for gdp_monthly.

ASCII-safe console output. CSV writes tolerate PermissionError.

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
    # Load quarterly series
    # ------------------------------------------------------------------
    gdp_ar      = load_csv(DATA / "gdp_total_contribution.csv")   # Q/Q AR, pp
    invn        = load_csv(DATA / "gdp_contrib_inventories.csv")  # Q/Q AR, pp

    # Load monthly GDP for Y/Y series
    gdp_monthly = load_csv(DATA / "gdp_monthly.csv")

    # ------------------------------------------------------------------
    # SECTION 1: |GDP Q/Q AR - 2%| -- target-anchored deviation (pp)
    # Using 2% as the nominal potential-growth proxy (BoC April 2026 MPR central
    # estimate: 1.2-1.3%; 2% is the historical long-run mid-cycle benchmark and
    # the conventional "above-potential" threshold from analysis_framework.md).
    # Tail axis: target-anchored, |Q/Q AR - 2%|.
    # Window: quarterly since 1961 (full data availability).
    # ------------------------------------------------------------------
    TARGET_QQ = 2.0

    # Drop NaN
    gdp_ar_clean = gdp_ar.dropna()
    n_qq = len(gdp_ar_clean)
    date_min_qq = gdp_ar_clean.index.min().date()
    date_max_qq = gdp_ar_clean.index.max().date()

    arr1 = (gdp_ar_clean - TARGET_QQ).abs().to_numpy()

    print()
    print("=" * 72)
    print("SECTION 1: GDP Q/Q AR momentum -- |Q/Q AR - 2%| (pp)")
    print(f"  Tail axis : |Q/Q AR - 2.0%| in pp, quarterly, {date_min_qq} to {date_max_qq}")
    print(f"  N         : {n_qq}")
    print("=" * 72)
    print(f"  Median Q/Q AR             : {np.median(gdp_ar_clean.to_numpy()):+.4f}%")
    print(f"  Mean Q/Q AR               : {np.mean(gdp_ar_clean.to_numpy()):+.4f}%")
    print(f"  Min Q/Q AR                : {np.min(gdp_ar_clean.to_numpy()):+.4f}%")
    print(f"  Max Q/Q AR                : {np.max(gdp_ar_clean.to_numpy()):+.4f}%")
    print()
    print(f"  Tail axis: |Q/Q AR - {TARGET_QQ:.1f}%| (target-anchored deviation)")
    print(f"  Median |deviation|        : {np.median(arr1):.4f} pp")
    print()
    s1_p50, s1_p80, s1_p95, s1_p99 = pct_block(arr1, "pp from 2%")
    print()
    print("  Selected percentiles of |Q/Q AR - 2%| (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr1, p):.4f} pp")
    print()
    # Framework thresholds to verify
    print("  Framework threshold checks:")
    print(f"    |Q/Q AR - 2%| > 0% (any above-potential):")
    print(f"      Share |dev| > 0.5pp : {(arr1 > 0.5).mean()*100:.1f}%")
    print(f"      Share |dev| > 1.0pp : {(arr1 > 1.0).mean()*100:.1f}%")
    print(f"      Share |dev| > 2.0pp : {(arr1 > 2.0).mean()*100:.1f}%")
    print(f"      Share |dev| > 3.0pp : {(arr1 > 3.0).mean()*100:.1f}%")
    # Framework says >~1.5% Q/Q AR = above-potential; verify ~0.5pp from target
    above_potential = (gdp_ar_clean > 1.5).mean() * 100
    below_zero = (gdp_ar_clean < 0.0).mean() * 100
    print(f"    Q/Q AR > 1.5% (above-potential by framework): {above_potential:.1f}% of quarters")
    print(f"    Q/Q AR < 0% (contraction): {below_zero:.1f}% of quarters")

    # ==================================================================
    # SECTION 2: Inventory contribution -- |inventory pp| (absolute envelope)
    # ==================================================================
    invn_clean = invn.dropna()
    n_invn = len(invn_clean)
    date_min_invn = invn_clean.index.min().date()
    date_max_invn = invn_clean.index.max().date()

    arr2 = invn_clean.abs().to_numpy()

    print()
    print("=" * 72)
    print("SECTION 2: Inventory contribution -- |inventory contrib| (pp AR)")
    print(f"  Tail axis : |inventory pp AR|, quarterly, {date_min_invn} to {date_max_invn}")
    print(f"  N         : {n_invn}")
    print("=" * 72)
    print(f"  Median inventory contrib  : {np.median(invn_clean.to_numpy()):+.4f} pp")
    print(f"  Mean   |contrib|          : {np.mean(arr2):+.4f} pp")
    print(f"  Min (signed)              : {np.min(invn_clean.to_numpy()):+.4f} pp")
    print(f"  Max (signed)              : {np.max(invn_clean.to_numpy()):+.4f} pp")
    print(f"  Min |abs|                 : {np.min(arr2):.4f} pp")
    print(f"  Max |abs|                 : {np.max(arr2):.4f} pp")
    print()
    s2_p50, s2_p80, s2_p95, s2_p99 = pct_block(arr2, "pp |inventory|")
    print()
    print("  Selected percentiles of |inventory contrib| (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr2, p):.4f} pp")
    print()
    print("  Verification of framework's asserted +-3pp threshold:")
    print(f"    Share |invn| > 2.0pp : {(arr2 > 2.0).mean()*100:.1f}%")
    print(f"    Share |invn| > 2.5pp : {(arr2 > 2.5).mean()*100:.1f}%")
    print(f"    Share |invn| > 3.0pp : {(arr2 > 3.0).mean()*100:.1f}%"
          f"   <- framework threshold")
    print(f"    Share |invn| > 3.5pp : {(arr2 > 3.5).mean()*100:.1f}%")
    print(f"    Share |invn| > 4.0pp : {(arr2 > 4.0).mean()*100:.1f}%")
    print()
    # Recent episodes
    recent = invn_clean[invn_clean.index >= "2020-01-01"]
    print("  Recent large inventory episodes (since 2020, |invn| > 2pp):")
    for dt, val in recent[recent.abs() > 2.0].items():
        print(f"    {dt.date()}  {val:+.3f} pp")

    # ==================================================================
    # SECTION 3: Monthly GDP Y/Y (signed, two-tailed) since 1997
    # ==================================================================
    gdp_yoy_m = (gdp_monthly.pct_change(12) * 100.0).dropna()
    n_yoy = len(gdp_yoy_m)
    date_min_yoy = gdp_yoy_m.index.min().date()
    date_max_yoy = gdp_yoy_m.index.max().date()

    arr3_signed = gdp_yoy_m.to_numpy()
    median_yoy = float(np.median(arr3_signed))

    # Tail axis: signed deviation from median (symmetric, two-tailed)
    arr3_dev = (arr3_signed - median_yoy)

    print()
    print("=" * 72)
    print("SECTION 3: Monthly GDP Y/Y -- signed two-tailed distribution")
    print(f"  Tail axis : GDP Y/Y in %, monthly, {date_min_yoy} to {date_max_yoy}")
    print(f"  N         : {n_yoy}")
    print("=" * 72)
    print(f"  Median GDP Y/Y            : {median_yoy:+.4f}%")
    print(f"  Mean GDP Y/Y              : {np.mean(arr3_signed):+.4f}%")
    print(f"  Min GDP Y/Y               : {np.min(arr3_signed):+.4f}%")
    print(f"  Max GDP Y/Y               : {np.max(arr3_signed):+.4f}%")
    print()
    # For a symmetric two-tailed distribution, tier by central-share bands.
    # P50 = middle 50%, so look at the central 50% band around median.
    p25 = float(np.percentile(arr3_signed, 25))
    p75 = float(np.percentile(arr3_signed, 75))
    p10 = float(np.percentile(arr3_signed, 10))
    p90 = float(np.percentile(arr3_signed, 90))
    p5  = float(np.percentile(arr3_signed, 5))
    p95 = float(np.percentile(arr3_signed, 95))
    p1  = float(np.percentile(arr3_signed, 1))
    p99 = float(np.percentile(arr3_signed, 99))
    print(f"  Central-share percentile bands (P50=middle50%, etc.):")
    print(f"    Typical  (P25-P75) : {p25:+.4f}% to {p75:+.4f}%")
    print(f"    Uncommon (P10-P25 and P75-P90): outer boundary {p10:+.4f}% / {p90:+.4f}%")
    print(f"    Pronounced (P5-P10 and P90-P95): outer boundary {p5:+.4f}% / {p95:+.4f}%")
    print(f"    Rare (P1-P5 and P95-P99): outer boundary {p1:+.4f}% / {p99:+.4f}%")
    print(f"    Extreme: below P1 or above P99: < {p1:+.4f}% or > {p99:+.4f}%")
    print()
    # Convention approach for signed two-tailed: absolute deviation from median
    arr3_absdev = np.abs(arr3_dev)
    print(f"  Tail axis alternative: |Y/Y - median| in pp")
    print(f"  (median = {median_yoy:.4f}%)")
    s3_p50, s3_p80, s3_p95, s3_p99 = pct_block(arr3_absdev, "pp |Y/Y - median|")
    print()
    print("  Selected percentiles of |GDP Y/Y - median| (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr3_absdev, p):.4f} pp")
    print()
    print("  Framework threshold checks (Y/Y vs potential-growth band):")
    in_potential_band = ((arr3_signed >= 1.2) & (arr3_signed <= 1.5)).mean() * 100
    above_potential   = (arr3_signed > 1.5).mean() * 100
    below_zero        = (arr3_signed < 0.0).mean() * 100
    print(f"    Y/Y in 1.2-1.5% (potential band): {in_potential_band:.1f}% of months")
    print(f"    Y/Y > 1.5% (above potential): {above_potential:.1f}% of months")
    print(f"    Y/Y < 0% (contraction): {below_zero:.1f}% of months")

    # ==================================================================
    # SUMMARY TABLE
    # ==================================================================
    print()
    print("=" * 72)
    print("SUMMARY: Convention tier thresholds (P50/P80/P95/P99)")
    print("=" * 72)
    rows = [
        ("GDP Q/Q AR deviation |AR - 2%| (pp)", "pp from 2%",    s1_p50, s1_p80, s1_p95, s1_p99),
        ("Inventory |contrib| (pp AR)",          "pp |invn|",     s2_p50, s2_p80, s2_p95, s2_p99),
        ("GDP monthly |Y/Y - median| (pp)",      "pp |Y/Y-med|",  s3_p50, s3_p80, s3_p95, s3_p99),
    ]
    print(f"  {'Indicator':<42}  {'P50':>7}  {'P80':>7}  {'P95':>7}  {'P99':>7}")
    print("  " + "-" * 72)
    for row in rows:
        name, unit, p50, p80, p95, p99 = row
        print(f"  {name:<42}  {p50:>7.4f}  {p80:>7.4f}  {p95:>7.4f}  {p99:>7.4f}")
    print()
    print(f"  Quarterly window: {date_min_qq} to {date_max_qq}, N={n_qq}")
    print(f"  Monthly window:   {date_min_yoy} to {date_max_yoy}, N={n_yoy}")
    print(f"  Last computed: 2026-05-09")
    print()
    print("  Convention notes:")
    print("  - GDP Q/Q AR: tail axis = |Q/Q AR - 2%|; 2% is conventional potential-proxy")
    print("    (BoC April 2026 central: 1.2-1.3%/yr; 2% benchmarks 'above potential').")
    print("  - Inventory: absolute envelope tail axis (already non-negative).")
    print("    Framework's +-3pp = roughly P80 by this distribution.")
    print("  - GDP Y/Y monthly: signed two-tailed; median used for centering.")
    print("  - Output gap: BoC-band indicator (published each MPR). Dashboard does NOT")
    print("    fetch this series. Convention rule applies (binary in/out per MPR range)")
    print("    but cannot be implemented until data fetch is wired in.")

    # ==================================================================
    # CSV output (PermissionError tolerant)
    # ==================================================================
    # Build a combined quarterly frame for CSV export
    quarterly_frame = pd.DataFrame({
        "gdp_qq_ar":                gdp_ar_clean,
        "abs_dev_from_2pct":        (gdp_ar_clean - TARGET_QQ).abs(),
        "inventory_contrib":        invn_clean,
        "abs_inventory_contrib":    invn_clean.abs(),
    })
    out_csv = OUT_DIR / "gdp_distribution.csv"
    try:
        quarterly_frame.to_csv(out_csv)
        print(f"\nWrote quarterly working series -> {out_csv.relative_to(ROOT)}")
    except PermissionError:
        print(f"\nSkipped CSV write (file locked): {out_csv.relative_to(ROOT)}")
    except Exception as e:
        print(f"\nSkipped CSV write ({e}): {out_csv.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
