"""Empirical distributions for Housing section convention application.

Computes P50/P80/P95/P99 for four housing-related tail axes:

  1. Housing starts 12-month moving average (SAAR, thousands)
     Tail axis: |starts_12mma - long-run median| in thousands
     (monthly, since 1990, N depends on data window)
     Descriptor pair: strong / weak

  2. NHPI Y/Y (%)
     Tail axis: signed NHPI Y/Y; central-share bands (two-tailed)
     (monthly, since 1982 approx -- first 12 months drop for Y/Y)
     Descriptor pair: hot / soft

  3. CREA MLS HPI Y/Y (%)
     Tail axis: signed CREA Y/Y; central-share bands (two-tailed)
     (monthly, since 2015 approx -- first 12 months drop for Y/Y)
     Descriptor pair: hot / soft

  4. Housing affordability ratio (BoC INDINF_AFFORD_Q)
     Tail axis: |afford - long-run median| (one-tailed high = worse)
     (quarterly, since 2000)
     Descriptor pair: stressed / comfortable

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


def central_share_bands(arr: np.ndarray, label: str) -> None:
    """Print central-share percentile bands for a signed two-tailed distribution."""
    p25  = float(np.percentile(arr, 25))
    p75  = float(np.percentile(arr, 75))
    p10  = float(np.percentile(arr, 10))
    p90  = float(np.percentile(arr, 90))
    p5   = float(np.percentile(arr, 5))
    p95  = float(np.percentile(arr, 95))
    p1   = float(np.percentile(arr, 1))
    p99  = float(np.percentile(arr, 99))
    print(f"  Central-share percentile bands ({label}):")
    print(f"    Typical   (P25-P75)         : {p25:+.3f}% to {p75:+.3f}%")
    print(f"    Uncommon  (P10 / P90)       : outer boundary {p10:+.3f}% / {p90:+.3f}%")
    print(f"    Pronounced(P5  / P95)       : outer boundary {p5:+.3f}% / {p95:+.3f}%")
    print(f"    Rare      (P1  / P99)       : outer boundary {p1:+.3f}% / {p99:+.3f}%")
    print(f"    Extreme   (<P1 or >P99)     : < {p1:+.3f}% or > {p99:+.3f}%")


def main() -> None:
    # ------------------------------------------------------------------
    # Load series
    # ------------------------------------------------------------------
    starts      = load_csv(DATA / "housing_starts.csv")          # monthly SAAR, thousands
    nhpi        = load_csv(DATA / "new_housing_price_index.csv")  # monthly index Dec 2016=100
    crea        = load_csv(DATA / "crea_mls_hpi.csv")             # monthly index 2019=100
    afford      = load_csv(DATA / "housing_affordability.csv")    # quarterly ratio

    # ------------------------------------------------------------------
    # SECTION 1: Housing starts 12-month moving average
    # Tail axis: |starts_12mma - long-run median| in thousands
    # ------------------------------------------------------------------
    starts_12mma = starts.rolling(12).mean().dropna()
    n_starts     = len(starts_12mma)
    date_min_s   = starts_12mma.index.min().date()
    date_max_s   = starts_12mma.index.max().date()
    median_starts = float(np.median(starts_12mma.to_numpy()))

    arr1 = np.abs(starts_12mma.to_numpy() - median_starts)

    print()
    print("=" * 72)
    print("SECTION 1: Housing starts 12-month moving average")
    print(f"  Tail axis : |starts_12mma - median| in thousands SAAR")
    print(f"  Window    : monthly, {date_min_s} to {date_max_s}")
    print(f"  N         : {n_starts}")
    print("=" * 72)
    print(f"  Median starts_12mma       : {median_starts:.3f}k SAAR")
    print(f"  Mean starts_12mma         : {np.mean(starts_12mma.to_numpy()):.3f}k SAAR")
    print(f"  Min starts_12mma          : {np.min(starts_12mma.to_numpy()):.3f}k SAAR")
    print(f"  Max starts_12mma          : {np.max(starts_12mma.to_numpy()):.3f}k SAAR")
    print()
    print(f"  Tail axis: |starts_12mma - {median_starts:.3f}k| (absolute deviation from median)")
    print()
    s1_p50, s1_p80, s1_p95, s1_p99 = pct_block(arr1, "thousands |starts - median|")
    print()
    print("  Selected percentiles of |starts_12mma - median| (thousands):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr1, p):.3f}k")
    print()
    # Framework threshold context
    print("  Framework threshold checks (starts_12mma level):")
    below_180 = (starts_12mma < 180).mean() * 100
    above_280 = (starts_12mma > 280).mean() * 100
    print(f"    Share <180k (recessionary) : {below_180:.1f}%")
    print(f"    Share >280k (elevated)     : {above_280:.1f}%")
    print(f"    Affordable-restoring pace (430-480k per CMHC June 2025): "
          f"far above all observed data (max {np.max(starts_12mma.to_numpy()):.0f}k)")

    # Also report level-based percentiles (useful for the formula notes)
    print()
    print("  Level-based percentiles of starts_12mma (thousands SAAR):")
    for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(starts_12mma.to_numpy(), p):.1f}k")

    # ==================================================================
    # SECTION 2: NHPI Y/Y (%)
    # Tail axis: signed two-tailed; use central-share bands + |Y/Y - median|
    # ==================================================================
    nhpi_yoy   = (nhpi.pct_change(12) * 100).dropna()
    n_nhpi     = len(nhpi_yoy)
    date_min_n = nhpi_yoy.index.min().date()
    date_max_n = nhpi_yoy.index.max().date()
    median_nhpi_yoy = float(np.median(nhpi_yoy.to_numpy()))

    arr2_signed = nhpi_yoy.to_numpy()
    arr2_absdev = np.abs(arr2_signed - median_nhpi_yoy)

    print()
    print("=" * 72)
    print("SECTION 2: NHPI Y/Y (%)")
    print(f"  Tail axis : signed Y/Y % and |Y/Y - median| (two-tailed)")
    print(f"  Window    : monthly, {date_min_n} to {date_max_n}")
    print(f"  N         : {n_nhpi}")
    print("=" * 72)
    print(f"  Median NHPI Y/Y           : {median_nhpi_yoy:+.3f}%")
    print(f"  Mean NHPI Y/Y             : {np.mean(arr2_signed):+.3f}%")
    print(f"  Min NHPI Y/Y              : {np.min(arr2_signed):+.3f}%")
    print(f"  Max NHPI Y/Y              : {np.max(arr2_signed):+.3f}%")
    print()
    central_share_bands(arr2_signed, "signed NHPI Y/Y")
    print()
    print(f"  Tail axis: |NHPI Y/Y - median ({median_nhpi_yoy:.3f}%)| (pp)")
    s2_p50, s2_p80, s2_p95, s2_p99 = pct_block(arr2_absdev, "pp |NHPI Y/Y - median|")
    print()
    print("  Selected percentiles of |NHPI Y/Y - median| (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr2_absdev, p):.3f}pp")
    print()
    # Framework thresholds
    above_5 = (arr2_signed > 5).mean() * 100
    below_0 = (arr2_signed < 0).mean() * 100
    print("  Framework threshold checks (NHPI Y/Y level):")
    print(f"    Share >5% (meaningful accel) : {above_5:.1f}%")
    print(f"    Share <0% (price declines)   : {below_0:.1f}%")
    # Historical context
    peak_idx   = arr2_signed.argmax()
    trough_idx = arr2_signed.argmin()
    print(f"    Peak Y/Y: {arr2_signed[peak_idx]:+.2f}% ({nhpi_yoy.index[peak_idx].strftime('%Y-%m')})")
    print(f"    Trough Y/Y: {arr2_signed[trough_idx]:+.2f}% ({nhpi_yoy.index[trough_idx].strftime('%Y-%m')})")

    # ==================================================================
    # SECTION 3: CREA MLS HPI Y/Y (%)
    # Tail axis: signed two-tailed; central-share bands + |Y/Y - median|
    # ==================================================================
    crea_yoy   = (crea.pct_change(12) * 100).dropna()
    n_crea     = len(crea_yoy)
    date_min_c = crea_yoy.index.min().date()
    date_max_c = crea_yoy.index.max().date()
    median_crea_yoy = float(np.median(crea_yoy.to_numpy()))

    arr3_signed = crea_yoy.to_numpy()
    arr3_absdev = np.abs(arr3_signed - median_crea_yoy)

    print()
    print("=" * 72)
    print("SECTION 3: CREA MLS HPI Y/Y (%)")
    print(f"  Tail axis : signed Y/Y % and |Y/Y - median| (two-tailed)")
    print(f"  Window    : monthly, {date_min_c} to {date_max_c}")
    print(f"  N         : {n_crea}")
    print("=" * 72)
    print(f"  Median CREA Y/Y           : {median_crea_yoy:+.3f}%")
    print(f"  Mean CREA Y/Y             : {np.mean(arr3_signed):+.3f}%")
    print(f"  Min CREA Y/Y              : {np.min(arr3_signed):+.3f}%")
    print(f"  Max CREA Y/Y              : {np.max(arr3_signed):+.3f}%")
    print()
    central_share_bands(arr3_signed, "signed CREA Y/Y")
    print()
    print(f"  Tail axis: |CREA Y/Y - median ({median_crea_yoy:.3f}%)| (pp)")
    s3_p50, s3_p80, s3_p95, s3_p99 = pct_block(arr3_absdev, "pp |CREA Y/Y - median|")
    print()
    print("  Selected percentiles of |CREA Y/Y - median| (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr3_absdev, p):.3f}pp")
    print()
    # Historical peaks
    peak_c   = arr3_signed.argmax()
    trough_c = arr3_signed.argmin()
    print(f"    Peak Y/Y: {arr3_signed[peak_c]:+.2f}% ({crea_yoy.index[peak_c].strftime('%Y-%m')})")
    print(f"    Trough Y/Y: {arr3_signed[trough_c]:+.2f}% ({crea_yoy.index[trough_c].strftime('%Y-%m')})")
    if n_crea < 200:
        print(f"  SMALL-N WARNING: N={n_crea} < 200. Extreme tier (top 1%) sparsely populated.")

    # ==================================================================
    # SECTION 4: Housing affordability ratio (BoC INDINF_AFFORD_Q)
    # Tail axis: |afford - long-run median| (one-tailed high = worse)
    # ==================================================================
    afford_clean = afford.dropna()
    n_afford     = len(afford_clean)
    date_min_a   = afford_clean.index.min().date()
    date_max_a   = afford_clean.index.max().date()
    median_afford = float(np.median(afford_clean.to_numpy()))

    arr4 = np.abs(afford_clean.to_numpy() - median_afford)

    print()
    print("=" * 72)
    print("SECTION 4: Housing affordability ratio (BoC INDINF_AFFORD_Q)")
    print(f"  Tail axis : |afford ratio - long-run median| (target-anchored around median)")
    print(f"  Window    : quarterly, {date_min_a} to {date_max_a}")
    print(f"  N         : {n_afford}")
    print("=" * 72)
    print(f"  Median affordability ratio : {median_afford:.4f}")
    print(f"  Mean ratio                 : {np.mean(afford_clean.to_numpy()):.4f}")
    print(f"  Min ratio                  : {np.min(afford_clean.to_numpy()):.4f}")
    print(f"  Max ratio                  : {np.max(afford_clean.to_numpy()):.4f}")
    print()
    print(f"  Tail axis: |afford - {median_afford:.4f}| (absolute deviation from median)")
    print()
    s4_p50, s4_p80, s4_p95, s4_p99 = pct_block(arr4, "|afford - median|")
    print()
    print("  Selected percentiles of |afford - median| (ratio):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr4, p):.4f}")
    print()
    # Level-based percentiles for prose calibration
    print("  Level-based percentiles of affordability ratio:")
    for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(afford_clean.to_numpy(), p):.4f}")
    print()
    # Framework thresholds context
    above_040 = (afford_clean > 0.40).mean() * 100
    above_050 = (afford_clean > 0.50).mean() * 100
    print("  Framework threshold checks (afford level):")
    print(f"    Share >0.40 (elevated vs long-run) : {above_040:.1f}%")
    print(f"    Share >0.50 (peak-stress)           : {above_050:.1f}%")

    # ==================================================================
    # SUMMARY TABLE
    # ==================================================================
    print()
    print("=" * 72)
    print("SUMMARY: Convention tier thresholds (P50/P80/P95/P99)")
    print("=" * 72)
    rows = [
        ("Housing starts |12mma - median| (thousands)",
         "k |starts - median|",  s1_p50, s1_p80, s1_p95, s1_p99),
        ("NHPI Y/Y |Y/Y - median| (pp)",
         "pp |NHPI Y/Y-med|",    s2_p50, s2_p80, s2_p95, s2_p99),
        ("CREA HPI Y/Y |Y/Y - median| (pp)",
         "pp |CREA Y/Y-med|",    s3_p50, s3_p80, s3_p95, s3_p99),
        ("Affordability |ratio - median|",
         "|afford-median|",      s4_p50, s4_p80, s4_p95, s4_p99),
    ]
    print(f"  {'Indicator':<46}  {'P50':>7}  {'P80':>7}  {'P95':>7}  {'P99':>7}")
    print("  " + "-" * 80)
    for row in rows:
        name, unit, p50, p80, p95, p99 = row
        print(f"  {name:<46}  {p50:>7.4f}  {p80:>7.4f}  {p95:>7.4f}  {p99:>7.4f}")
    print()
    print(f"  Starts window    : {date_min_s} to {date_max_s}, N={n_starts}")
    print(f"  NHPI window      : {date_min_n} to {date_max_n}, N={n_nhpi}")
    print(f"  CREA window      : {date_min_c} to {date_max_c}, N={n_crea}")
    print(f"  Afford window    : {date_min_a} to {date_max_a}, N={n_afford}")
    print(f"  Medians used     : starts={median_starts:.3f}k, NHPI Y/Y={median_nhpi_yoy:.3f}%,"
          f" CREA Y/Y={median_crea_yoy:.3f}%, afford={median_afford:.4f}")
    print(f"  Last computed    : 2026-05-09")
    print()
    print("  Convention notes:")
    print("  - Starts: |12mma - median| = absolute-envelope tail axis. Descriptor: strong / weak.")
    print("  - NHPI Y/Y: signed two-tailed; median used for centering. Descriptor: hot / soft.")
    print(f"    (Median NHPI Y/Y = {median_nhpi_yoy:.2f}%; positive because the 1980s-90s boom dominates.)")
    print(f"    SMALL-N caveat: CREA N={n_crea} < 200; extreme tier sparsely populated, lower confidence.")
    print("  - Affordability: |ratio - median| = deviation-envelope. Descriptor: stressed / comfortable.")
    print(f"    No published BoC band thresholds. Analyst-synthesis framing for 0.40 / 0.50 levels.")
    print(f"    (N={n_afford} quarterly, < 200 -- small-N caveat applies to affordability too.)")

    # ==================================================================
    # CSV output (PermissionError tolerant)
    # ==================================================================
    try:
        monthly_frame = pd.DataFrame({
            "housing_starts":            starts,
            "starts_12mma":              starts.rolling(12).mean(),
            "starts_12mma_abs_dev":      (starts.rolling(12).mean() - median_starts).abs(),
            "nhpi_yoy_pct":              nhpi_yoy,
            "nhpi_yoy_abs_dev":          nhpi_yoy.sub(median_nhpi_yoy).abs(),
            "crea_yoy_pct":              crea_yoy,
            "crea_yoy_abs_dev":          crea_yoy.sub(median_crea_yoy).abs(),
        })
        out_csv = OUT_DIR / "housing_distribution.csv"
        monthly_frame.to_csv(out_csv)
        print(f"\nWrote monthly working series -> {out_csv.relative_to(ROOT)}")
    except PermissionError:
        print(f"\nSkipped CSV write (file locked): housing_distribution.csv")
    except Exception as e:
        print(f"\nSkipped CSV write ({e}): housing_distribution.csv")


if __name__ == "__main__":
    main()
