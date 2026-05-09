"""Empirical distributions for Labour Market section convention application.

Computes P50/P80/P95/P99 for convention-applicable tail axes:

  1. ULC Y/Y (%)
     Tail axis: |ULC Y/Y - 2%| in pp (target-anchored; 2% = inflation-consistent
     ULC growth at trend productivity)
     Data: quarterly since data start, N depends on series
     Descriptor pair: labour-cost pressure / labour-cost soft

  2. Real wages per measure (LFS-all, LFS-permanent, SEPH, LFS-Micro)
     Tail axis: signed real wage Y/Y (signed value; sign matters)
     Definition: real wage Y/Y = nominal wage Y/Y - headline CPI Y/Y
     Descriptor pair: real-wage-positive (gaining purchasing power) /
                      real-wage-negative (losing purchasing power)
     Computed per measure; also a range (max - min across the 4 measures).

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


def central_share_bands_signed(arr: np.ndarray, label: str) -> tuple[float, float, float, float, float, float, float, float]:
    """Print central-share percentile bands for signed two-tailed distribution.

    For a signed series, the convention is to use central-share bands:
    - Typical: P25-P75 (central 50%)
    - Uncommon: P10-P90 (central 70-80%; outer boundary at P10/P90)
    - Pronounced: P5-P95
    - Rare: P1-P99
    - Extreme: outside P1/P99
    """
    p1  = float(np.percentile(arr, 1))
    p5  = float(np.percentile(arr, 5))
    p10 = float(np.percentile(arr, 10))
    p25 = float(np.percentile(arr, 25))
    p50 = float(np.percentile(arr, 50))
    p75 = float(np.percentile(arr, 75))
    p90 = float(np.percentile(arr, 90))
    p95 = float(np.percentile(arr, 95))
    p99 = float(np.percentile(arr, 99))
    print(f"  Median                    : {p50:+.4f}%")
    print(f"  Typical   (P25-P75)       : {p25:+.3f}% to {p75:+.3f}%")
    print(f"  Uncommon  (P10-P90)       : {p10:+.3f}% to {p90:+.3f}%")
    print(f"  Pronounced(P5-P95)        : {p5:+.3f}% to {p95:+.3f}%")
    print(f"  Rare      (P1-P99)        : {p1:+.3f}% to {p99:+.3f}%")
    print(f"  Extreme   (<P1 or >P99)   : < {p1:+.3f}% or > {p99:+.3f}%")
    print()
    # For classifier: use |value - median| approach for the 5-tier ladder
    arr_absdev = np.abs(arr - p50)
    p50_dev, p80_dev, p95_dev, p99_dev = pct_block(arr_absdev, f"|{label} - median|")
    return p50, p25, p75, p10, p90, p5, p95, p1, p99  # type: ignore[return-value]


def main() -> None:
    # ------------------------------------------------------------------
    # Load series
    # ------------------------------------------------------------------
    lfs_wages_all  = load_csv(DATA / "lfs_wages_all.csv")       # monthly SA, level
    lfs_wages_perm = load_csv(DATA / "lfs_wages_permanent.csv") # monthly SA, level
    seph_earnings  = load_csv(DATA / "seph_earnings.csv")       # monthly SA, level
    lfs_micro      = load_csv(DATA / "lfs_micro.csv")           # already Y/Y from BoC
    ulc_index      = load_csv(DATA / "unit_labour_cost.csv")    # quarterly SA, index
    cpi_all        = load_csv(DATA / "cpi_all_items.csv")       # monthly SA, level

    # Y/Y for each series
    wages_all_yoy  = (lfs_wages_all.pct_change(12)  * 100).dropna()
    wages_perm_yoy = (lfs_wages_perm.pct_change(12) * 100).dropna()
    seph_yoy       = (seph_earnings.pct_change(12)  * 100).dropna()
    # lfs_micro is already Y/Y in the BoC Valet data; use directly
    headline_yoy   = (cpi_all.pct_change(12) * 100).dropna()
    ulc_yoy        = (ulc_index.pct_change(4) * 100).dropna()  # quarterly: 4 periods back

    # Real wages: align each nominal wage series with headline CPI at the same date.
    # Use inner-join intersection of each wage series with headline CPI.
    def real_wage(nom_yoy: pd.Series, cpi_yoy: pd.Series) -> pd.Series:
        aligned = nom_yoy.align(cpi_yoy, join="inner")
        return aligned[0] - aligned[1]

    real_lfs_all  = real_wage(wages_all_yoy, headline_yoy)
    real_lfs_perm = real_wage(wages_perm_yoy, headline_yoy)
    real_seph     = real_wage(seph_yoy, headline_yoy)

    # LFS-Micro is already Y/Y; align with headline CPI
    lfs_micro_aligned, cpi_aligned = lfs_micro.align(headline_yoy, join="inner")
    real_lfs_micro = lfs_micro_aligned - cpi_aligned

    # Real wage range: at each date where all four measures overlap, compute max-min spread
    common_idx = real_lfs_all.index.intersection(real_lfs_perm.index) \
                              .intersection(real_seph.index) \
                              .intersection(real_lfs_micro.index)
    real_df = pd.DataFrame({
        "lfs_all":   real_lfs_all.reindex(common_idx),
        "lfs_perm":  real_lfs_perm.reindex(common_idx),
        "seph":      real_seph.reindex(common_idx),
        "lfs_micro": real_lfs_micro.reindex(common_idx),
    }).dropna()
    real_range = real_df.max(axis=1) - real_df.min(axis=1)

    # ==================================================================
    # SECTION 1: ULC Y/Y — target-anchored
    # Tail axis: |ULC Y/Y - 2%| in pp
    # ==================================================================
    ulc_arr     = ulc_yoy.to_numpy()
    n_ulc       = len(ulc_yoy)
    date_min_u  = ulc_yoy.index.min().date()
    date_max_u  = ulc_yoy.index.max().date()
    median_ulc  = float(np.median(ulc_arr))
    TARGET_ULC  = 2.0  # 2% = inflation-consistent ULC growth at trend productivity

    arr1 = np.abs(ulc_arr - TARGET_ULC)

    print()
    print("=" * 72)
    print("SECTION 1: ULC Y/Y (%) -- target-anchored at 2%")
    print(f"  Tail axis : |ULC Y/Y - 2%| in pp (target = 2% = inflation-consistent")
    print(f"              ULC growth at trend productivity)")
    print(f"  Window    : quarterly, {date_min_u} to {date_max_u}")
    print(f"  N         : {n_ulc}")
    print("=" * 72)
    print(f"  Median ULC Y/Y            : {median_ulc:+.3f}%")
    print(f"  Mean ULC Y/Y              : {np.mean(ulc_arr):+.3f}%")
    print(f"  Min ULC Y/Y               : {np.min(ulc_arr):+.3f}%")
    print(f"  Max ULC Y/Y               : {np.max(ulc_arr):+.3f}%")
    print()
    print(f"  Target anchor: ULC Y/Y = {TARGET_ULC}% (consistent with 2% inflation at")
    print(f"  trend productivity; analyst synthesis, not an explicit BoC threshold)")
    print()
    print(f"  Tail axis: |ULC Y/Y - {TARGET_ULC}%| (pp absolute deviation from target)")
    print()
    if n_ulc < 200:
        print(f"  SMALL-N WARNING: N={n_ulc} < 200. Extreme tier sparse; downgrade confidence.")
        print()
    u1_p50, u1_p80, u1_p95, u1_p99 = pct_block(arr1, "pp |ULC Y/Y - 2%|")
    print()
    print("  Selected percentiles of |ULC Y/Y - 2%| (pp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"    P{p:02d} : {np.percentile(arr1, p):.3f}pp")
    print()
    # Framework threshold context
    above_3  = (ulc_arr > 3.0).mean() * 100
    above_2  = (ulc_arr > 2.0).mean() * 100
    below_2  = (ulc_arr < 2.0).mean() * 100
    below_0  = (ulc_arr < 0.0).mean() * 100
    print("  Framework threshold context (ULC Y/Y level):")
    print(f"    Share > 3% (labour-cost pressure signal) : {above_3:.1f}%")
    print(f"    Share > 2% (above inflation-consistent)  : {above_2:.1f}%")
    print(f"    Share < 2% (at or below target-pace)     : {below_2:.1f}%")
    print(f"    Share < 0% (negative ULC = falling costs): {below_0:.1f}%")
    print()
    print("  NOTE on the 3% threshold (Claim 4 audit):")
    print("  The framework's 'ULC Y/Y > 3% = labour-cost pressure' is analyst synthesis;")
    print("  no BoC publication explicitly names 3% as the threshold. The empirical")
    print(f"  distribution places 3% at {float(np.mean(ulc_arr < 3.0)*100):.1f}th percentile of all observations.")
    print("  The convention sweep replaces the unsourced '3%' with the empirical P80/P95")
    print("  framing so the tier language is grounded in the data distribution.")
    print()
    # Empirical context: what percentile is 3%?
    pct_3 = float(np.mean(ulc_arr <= 3.0) * 100)
    pct_target = float(np.mean(ulc_arr <= 2.0) * 100)
    print(f"  Empirical context:")
    print(f"    ULC Y/Y <= 2.0% in {pct_target:.0f}% of quarters (at or below inflation-consistent)")
    print(f"    ULC Y/Y <= 3.0% in {pct_3:.0f}% of quarters (the unsourced old threshold)")
    print(f"    ULC Y/Y at 3% sits approximately at P{pct_3:.0f} of the historical distribution")

    # ==================================================================
    # SECTION 2: Real wages per measure (signed, two-tailed)
    # Tail axis: signed real wage Y/Y for each measure
    # ==================================================================
    measures = [
        ("LFS-all", real_lfs_all),
        ("LFS-permanent", real_lfs_perm),
        ("SEPH", real_seph),
        ("LFS-Micro", real_lfs_micro),
    ]

    results_real = {}
    for name, ser in measures:
        arr = ser.dropna().to_numpy()
        n   = len(arr)
        date_min = ser.dropna().index.min().date()
        date_max = ser.dropna().index.max().date()
        median_rw = float(np.median(arr))

        print()
        print("=" * 72)
        print(f"SECTION 2: Real wages -- {name}")
        print(f"  Definition  : nominal wage Y/Y - headline CPI Y/Y (both monthly SA Y/Y)")
        print(f"  Tail axis   : signed real wage Y/Y % (two-tailed)")
        print(f"  Window      : monthly, {date_min} to {date_max}")
        print(f"  N           : {n}")
        if n < 200:
            print(f"  SMALL-N WARNING: N={n} < 200. Extreme tier sparse; downgrade confidence.")
        print("=" * 72)
        print(f"  Median real wage Y/Y      : {median_rw:+.3f}%")
        print(f"  Mean real wage Y/Y        : {np.mean(arr):+.3f}%")
        print(f"  Min real wage Y/Y         : {np.min(arr):+.3f}%")
        print(f"  Max real wage Y/Y         : {np.max(arr):+.3f}%")
        print()

        # Absolute deviation from median for the 5-tier classifier
        arr_dev = np.abs(arr - median_rw)
        p50_dev, p80_dev, p95_dev, p99_dev = pct_block(arr_dev, f"|{name} real wage - median|")
        results_real[name] = {
            "n": n, "median": median_rw,
            "p50_dev": p50_dev, "p80_dev": p80_dev,
            "p95_dev": p95_dev, "p99_dev": p99_dev,
            "date_min": date_min, "date_max": date_max,
        }

        print()
        # Descriptor pair framing: positive = gaining, negative = losing
        pct_positive = float((arr > 0).mean() * 100)
        pct_negative = float((arr < 0).mean() * 100)
        print(f"  Descriptor pair: real-wage-positive (gaining purchasing power) /")
        print(f"                   real-wage-negative (losing purchasing power)")
        print(f"  Share > 0 (real-wage-positive) : {pct_positive:.1f}%")
        print(f"  Share < 0 (real-wage-negative) : {pct_negative:.1f}%")
        print()
        # Current value (last observation)
        latest_val = float(ser.dropna().iloc[-1])
        latest_date = ser.dropna().index[-1]
        print(f"  Latest ({latest_date.strftime('%Y-%m')})        : {latest_val:+.2f}%")
        # Percentile of latest
        pct_of_latest = float(np.mean(arr <= latest_val) * 100)
        print(f"  Percentile of latest          : P{pct_of_latest:.0f}")
        sign_str = "positive (gaining purchasing power)" if latest_val > 0 else "negative (losing purchasing power)"
        dev_from_median = abs(latest_val - median_rw)
        if dev_from_median > p99_dev:
            tier = "extreme"
        elif dev_from_median > p95_dev:
            tier = "rare"
        elif dev_from_median > p80_dev:
            tier = "pronounced"
        elif dev_from_median > p50_dev:
            tier = "uncommon"
        else:
            tier = "typical"
        print(f"  Tier at latest value          : {tier} ({sign_str})")

    # ==================================================================
    # SECTION 3: Real wage range (max - min across 4 measures)
    # ==================================================================
    range_arr   = real_range.to_numpy()
    n_range     = len(range_arr)
    date_min_r  = real_range.index.min().date()
    date_max_r  = real_range.index.max().date()

    print()
    print("=" * 72)
    print("SECTION 3: Real wage range (max - min across 4 measures)")
    print(f"  Tail axis : range width in pp (absolute envelope)")
    print(f"  Window    : monthly, {date_min_r} to {date_max_r}")
    print(f"  N         : {n_range}")
    if n_range < 200:
        print(f"  SMALL-N WARNING: N={n_range} < 200. Extreme tier sparse; downgrade confidence.")
    print("=" * 72)
    range_p50, range_p80, range_p95, range_p99 = pct_block(range_arr, "pp real-wage range")
    print()
    latest_range = float(real_range.iloc[-1])
    print(f"  Latest range              : {latest_range:.2f}pp")

    # ==================================================================
    # SECTION 4: Summary classifier thresholds for analyze.py
    # ==================================================================
    print()
    print("=" * 72)
    print("SUMMARY: Classifier thresholds for analyze.py implementation")
    print("=" * 72)
    print()
    print("ULC Y/Y -- target-anchored at 2% (Claim 4 convention application):")
    print(f"  Tail axis: |ULC Y/Y - 2.0%| in pp, quarterly, {date_min_u} to {date_max_u}, N={n_ulc}")
    if n_ulc < 200:
        print(f"  SMALL-N: N={n_ulc}")
    print(f"  typical   <= {u1_p50:.3f}pp")
    print(f"  uncommon   > {u1_p50:.3f}pp to {u1_p80:.3f}pp")
    print(f"  pronounced > {u1_p80:.3f}pp to {u1_p95:.3f}pp")
    print(f"  rare       > {u1_p95:.3f}pp to {u1_p99:.3f}pp")
    print(f"  extreme    > {u1_p99:.3f}pp")
    print(f"  Descriptor pair: labour-cost-pressure / labour-cost-soft")
    print()
    print("Real wages per measure:")
    for name, r in results_real.items():
        n_flag = f"  SMALL-N: N={r['n']}" if r["n"] < 200 else f"  N={r['n']}"
        print(f"  {name}: signed Y/Y, monthly {r['date_min']} to {r['date_max']},{n_flag}")
        print(f"    median={r['median']:+.3f}%  |deviation thresholds:|")
        print(f"    typical   <= {r['p50_dev']:.3f}pp")
        print(f"    uncommon   > {r['p50_dev']:.3f}pp to {r['p80_dev']:.3f}pp")
        print(f"    pronounced > {r['p80_dev']:.3f}pp to {r['p95_dev']:.3f}pp")
        print(f"    rare       > {r['p95_dev']:.3f}pp to {r['p99_dev']:.3f}pp")
        print(f"    extreme    > {r['p99_dev']:.3f}pp")
        print(f"    Descriptor pair: real-wage-positive / real-wage-negative")
        print()

    # Write summary CSV for auditability
    rows = []
    rows.append({
        "indicator": "ulc_yoy",
        "tail_axis": "|ULC Y/Y - 2.0%| pp",
        "frequency": "quarterly",
        "n": n_ulc,
        "date_min": str(date_min_u),
        "date_max": str(date_max_u),
        "median_anchor": 2.0,
        "p50_boundary": round(u1_p50, 4),
        "p80_boundary": round(u1_p80, 4),
        "p95_boundary": round(u1_p95, 4),
        "p99_boundary": round(u1_p99, 4),
        "descriptor": "labour-cost-pressure / labour-cost-soft",
    })
    for name, r in results_real.items():
        key = f"real_wage_{name.lower().replace('-','_').replace(' ','_')}"
        rows.append({
            "indicator": key,
            "tail_axis": f"signed real wage Y/Y = nominal {name} Y/Y - headline CPI Y/Y",
            "frequency": "monthly",
            "n": r["n"],
            "date_min": str(r["date_min"]),
            "date_max": str(r["date_max"]),
            "median_anchor": round(r["median"], 4),
            "p50_boundary": round(r["p50_dev"], 4),
            "p80_boundary": round(r["p80_dev"], 4),
            "p95_boundary": round(r["p95_dev"], 4),
            "p99_boundary": round(r["p99_dev"], 4),
            "descriptor": "real-wage-positive / real-wage-negative",
        })
    out_csv = OUT_DIR / "labour_distribution.csv"
    try:
        pd.DataFrame(rows).to_csv(out_csv, index=False)
        print(f"\nCSV written to: {out_csv}")
    except PermissionError:
        print(f"\nWARNING: Could not write CSV (file open?) -- skipping.")


if __name__ == "__main__":
    main()
