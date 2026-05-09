"""Empirical distribution of |bocfed_spread| since 1996.

Audits the framework's threshold claim:
    "median |spread| 38bp; ±50bp = top half; ±100bp = top 10%; ±150bp = top 5%"

Reads data/overnight_rate.csv (monthly) and data/fed_funds.csv (mixed daily/monthly),
aligns them at month-start, computes |BoC overnight - Fed funds| in basis points,
prints distribution stats, and writes a histogram with vertical lines at the
framework's ±50/100/150bp anchors so the percentile each anchor marks is visible.

Outputs:
    analyses/bocfed_spread_distribution.csv   (raw monthly series for inspection)
    analyses/bocfed_spread_distribution.png   (histogram with anchor lines)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_DIR = Path(__file__).resolve().parent

ANCHORS_BP = [50, 100, 150]


def load_monthly(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.set_index("date").sort_index()
    return df["value"]


def to_month_start(s: pd.Series) -> pd.Series:
    """Snap to month start. For mixed-frequency series (fed_funds), pick the
    first observation in each month — equivalent to month-start sampling."""
    return s.groupby(s.index.to_period("M")).first().to_timestamp()


def main() -> None:
    boc = to_month_start(load_monthly(DATA / "overnight_rate.csv"))
    fed = to_month_start(load_monthly(DATA / "fed_funds.csv"))

    df = pd.concat({"boc": boc, "fed": fed}, axis=1).dropna()
    df = df[df.index >= "1996-01-01"]
    df["spread_pp"] = df["boc"] - df["fed"]
    df["abs_spread_bp"] = df["spread_pp"].abs() * 100.0

    n = len(df)
    abs_bp = df["abs_spread_bp"].to_numpy()
    median_bp = float(np.median(abs_bp))
    mean_bp = float(np.mean(abs_bp))

    print("=" * 72)
    print(f"BoC-Fed |spread| distribution, monthly month-start, {df.index.min().date()} to {df.index.max().date()}")
    print(f"N = {n}")
    print("=" * 72)
    print(f"Median |spread|   : {median_bp:5.1f} bp        (framework claims 38 bp)")
    print(f"Mean   |spread|   : {mean_bp:5.1f} bp")
    print()

    print("Share at-or-below each |spread| anchor:")
    print(f"  |spread| <= 25 bp : {(abs_bp <= 25).mean()*100:5.1f}%")
    for a in ANCHORS_BP:
        share_within = (abs_bp <= a).mean() * 100
        share_above = 100 - share_within
        print(f"  |spread| <= {a:3d} bp : {share_within:5.1f}%   (so >{a}bp = top {share_above:4.1f}%)")

    print()
    print("Selected percentiles of |spread| (bp):")
    for p in [50, 75, 80, 90, 95, 99]:
        print(f"  P{p:02d} : {np.percentile(abs_bp, p):6.1f}")

    print()
    print("Framework anchor labels vs computed reality:")
    rows = [
        ("median", "38 bp", f"{median_bp:.1f} bp"),
        ("±50bp",  "top half (50%)", f"top {(abs_bp > 50).mean()*100:.1f}%"),
        ("±100bp", "top 10%",        f"top {(abs_bp > 100).mean()*100:.1f}%"),
        ("±150bp", "top 5%",         f"top {(abs_bp > 150).mean()*100:.1f}%"),
    ]
    label_w = max(len(r[0]) for r in rows)
    claim_w = max(len(r[1]) for r in rows)
    for label, claim, real in rows:
        print(f"  {label:<{label_w}}  claim: {claim:<{claim_w}}   reality: {real}")

    out_csv = OUT_DIR / "bocfed_spread_distribution.csv"
    try:
        df.to_csv(out_csv)
        print(f"\nWrote raw monthly series -> {out_csv.relative_to(ROOT)}")
    except PermissionError:
        print(f"\nSkipped CSV write (file locked): {out_csv.relative_to(ROOT)}")

    signed_bp = (df["spread_pp"] * 100).to_numpy()
    median_signed = float(np.median(signed_bp))
    mean_signed = float(np.mean(signed_bp))

    print()
    print("Signed spread (BoC - Fed) distribution stats:")
    print(f"  Median: {median_signed:+6.1f} bp")
    print(f"  Mean  : {mean_signed:+6.1f} bp")
    print(f"  Min   : {signed_bp.min():+6.1f} bp")
    print(f"  Max   : {signed_bp.max():+6.1f} bp")
    print(f"  Share BoC < Fed (negative): {(signed_bp < 0).mean()*100:5.1f}%")
    print(f"  Share BoC > Fed (positive): {(signed_bp > 0).mean()*100:5.1f}%")
    print(f"  Share = 0                : {(signed_bp == 0).mean()*100:5.1f}%")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Left: |spread| in bp (right-skewed by construction)
    ax = axes[0]
    bin_edges = np.arange(0, abs_bp.max() + 25, 25)
    ax.hist(abs_bp, bins=bin_edges, color="#2c7fb8", edgecolor="white", alpha=0.85)
    ax.axvline(median_bp, color="black", linestyle="--", linewidth=1.2,
               label=f"Median = {median_bp:.1f} bp")
    anchor_colors = {"50": "#41ab5d", "100": "#fd8d3c", "150": "#cb181d"}
    for a in ANCHORS_BP:
        share_above = (abs_bp > a).mean() * 100
        ax.axvline(a, color=anchor_colors[str(a)], linestyle="-", linewidth=1.4,
                   label=f"±{a}bp = top {share_above:.1f}%")
    ax.set_title(f"|spread| distribution (what the ±50/100/150 thresholds describe)")
    ax.set_xlabel("|BoC - Fed| (basis points)")
    ax.set_ylabel("Count of months")
    ax.legend(loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    # Right: signed spread (symmetric-ish, mass on both sides)
    ax = axes[1]
    bin_edges_signed = np.arange(np.floor(signed_bp.min() / 25) * 25,
                                  np.ceil(signed_bp.max() / 25) * 25 + 25, 25)
    ax.hist(signed_bp, bins=bin_edges_signed, color="#7570b3", edgecolor="white", alpha=0.85)
    ax.axvline(0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)
    ax.axvline(median_signed, color="black", linestyle="--", linewidth=1.2,
               label=f"Median = {median_signed:+.1f} bp")
    for a in ANCHORS_BP:
        ax.axvline(+a, color=anchor_colors[str(a)], linestyle="-", linewidth=1.4,
                   alpha=0.7, label=f"±{a}bp")
        ax.axvline(-a, color=anchor_colors[str(a)], linestyle="-", linewidth=1.4,
                   alpha=0.7)
    ax.set_title("Signed spread distribution (BoC - Fed)")
    ax.set_xlabel("BoC - Fed (basis points)")
    ax.set_ylabel("Count of months")
    ax.legend(loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    fig.suptitle(
        f"BoC overnight - Fed funds spread, monthly month-start, "
        f"{df.index.min().date()} to {df.index.max().date()}, N={n}",
        fontsize=12, y=1.02,
    )

    out_png = OUT_DIR / "bocfed_spread_distribution.png"
    fig.tight_layout()
    fig.savefig(out_png, dpi=140, bbox_inches="tight")
    print(f"Wrote histogram -> {out_png.relative_to(ROOT)}")


def sensitivity_main() -> None:
    """Test methodology sensitivity: which variation (if any) produces median |spread| ~38bp.

    Tests time windows, resolution variants, and exclusion variants.
    Prints a table; does NOT overwrite existing CSV/PNG outputs.
    """
    TARGET_BP = 38.0
    TOLERANCE_BP = 5.0

    ROOT_local = Path(__file__).resolve().parents[1]
    DATA_local = ROOT_local / "data"

    # ------------------------------------------------------------------
    # 1. Load base series
    # ------------------------------------------------------------------
    boc_monthly_raw = load_monthly(DATA_local / "overnight_rate.csv")
    fed_raw = load_monthly(DATA_local / "fed_funds.csv")

    # Month-start-aligned monthly series (existing methodology)
    boc_ms = to_month_start(boc_monthly_raw)
    fed_ms = to_month_start(fed_raw)
    df_monthly = pd.concat({"boc": boc_ms, "fed": fed_ms}, axis=1).dropna()
    df_monthly["abs_bp"] = (df_monthly["boc"] - df_monthly["fed"]).abs() * 100.0

    # Daily series (2009-04-21 onward; fed_funds is daily in recent window)
    boc_daily_raw = load_monthly(DATA_local / "overnight_rate_daily.csv")
    fed_daily_raw = load_monthly(DATA_local / "fed_funds.csv")
    df_daily = pd.concat({"boc": boc_daily_raw, "fed": fed_daily_raw}, axis=1).dropna()
    df_daily["abs_bp"] = (df_daily["boc"] - df_daily["fed"]).abs() * 100.0

    # End-of-month sampling: last obs in each calendar month
    def to_month_end(s: pd.Series) -> pd.Series:
        return s.groupby(s.index.to_period("M")).last().to_timestamp()

    boc_me = to_month_end(boc_monthly_raw)
    fed_me = to_month_end(fed_raw)
    df_month_end = pd.concat({"boc": boc_me, "fed": fed_me}, axis=1).dropna()
    df_month_end["abs_bp"] = (df_month_end["boc"] - df_month_end["fed"]).abs() * 100.0

    # ------------------------------------------------------------------
    # 2. Define variants
    # ------------------------------------------------------------------
    NEAR_38 = f"<-- within +/-{TOLERANCE_BP:.0f}bp of {TARGET_BP:.0f}"

    def row(label: str, df: pd.DataFrame, start: str, end: str) -> dict:
        sub = df[(df.index >= start) & (df.index <= end)]["abs_bp"].dropna()
        n = len(sub)
        if n == 0:
            return {"label": label, "start": start, "end": end, "N": 0, "median_bp": float("nan"), "near38": ""}
        med = float(sub.median())
        near = NEAR_38 if abs(med - TARGET_BP) <= TOLERANCE_BP else ""
        return {"label": label, "start": start, "end": end, "N": n, "median_bp": med, "near38": near}

    variants: list[dict] = []

    # --- Section 1: Time windows, monthly month-start ---
    variants.append(row("Monthly MS: full (1996-01 to 2026-04)",    df_monthly, "1996-01-01", "2026-04-30"))
    variants.append(row("Monthly MS: 1996-01 to 2023-12",           df_monthly, "1996-01-01", "2023-12-31"))
    variants.append(row("Monthly MS: 2000-01 to 2023-12",           df_monthly, "2000-01-01", "2023-12-31"))
    variants.append(row("Monthly MS: 1996-01 to 2019-12 (pre-COVID)", df_monthly, "1996-01-01", "2019-12-31"))
    variants.append(row("Monthly MS: 1996-01 to 2008-12 (pre-ZLB)", df_monthly, "1996-01-01", "2008-12-31"))
    variants.append(row("Monthly MS: 2009-01 to 2019-12 (ZLB-era)", df_monthly, "2009-01-01", "2019-12-31"))

    # --- Section 2: Resolution variants ---
    variants.append(row("Daily: 2009-04 to 2026-04 (full daily window)",  df_daily, "2009-04-21", "2026-04-30"))
    variants.append(row("Daily: 2009-04 to 2023-12 (drops recent div)",   df_daily, "2009-04-21", "2023-12-31"))
    variants.append(row("Monthly end-of-month: full (1996-01 to 2026-04)", df_month_end, "1996-01-01", "2026-04-30"))

    # --- Section 3: Exclusion variants, monthly month-start, full window ---
    # Exclude COVID floor (Apr 2020 - Mar 2022)
    df_no_covid = df_monthly[~((df_monthly.index >= "2020-04-01") & (df_monthly.index <= "2022-03-31"))].copy()
    sub = df_no_covid[(df_no_covid.index >= "1996-01-01")]["abs_bp"].dropna()
    med = float(sub.median())
    near = NEAR_38 if abs(med - TARGET_BP) <= TOLERANCE_BP else ""
    variants.append({
        "label": "Monthly MS: full, excl COVID floor (Apr2020-Mar2022)",
        "start": "1996-01-01", "end": "2026-04-30",
        "N": len(sub), "median_bp": med, "near38": near,
    })

    # Exclude GFC (Oct 2008 - Dec 2009) AND COVID floor
    df_no_gfc_covid = df_monthly[
        ~(
            ((df_monthly.index >= "2008-10-01") & (df_monthly.index <= "2009-12-31")) |
            ((df_monthly.index >= "2020-04-01") & (df_monthly.index <= "2022-03-31"))
        )
    ].copy()
    sub2 = df_no_gfc_covid[(df_no_gfc_covid.index >= "1996-01-01")]["abs_bp"].dropna()
    med2 = float(sub2.median())
    near2 = NEAR_38 if abs(med2 - TARGET_BP) <= TOLERANCE_BP else ""
    variants.append({
        "label": "Monthly MS: full, excl GFC (Oct2008-Dec2009) + COVID floor",
        "start": "1996-01-01", "end": "2026-04-30",
        "N": len(sub2), "median_bp": med2, "near38": near2,
    })

    # ------------------------------------------------------------------
    # 3. Print results table
    # ------------------------------------------------------------------
    print()
    print("=" * 90)
    print("SENSITIVITY ANALYSIS: which methodology produces median |spread| ~38bp?")
    print(f"Target: {TARGET_BP:.0f} bp  +/- {TOLERANCE_BP:.0f} bp  (i.e., {TARGET_BP - TOLERANCE_BP:.0f}-{TARGET_BP + TOLERANCE_BP:.0f} bp)")
    print("=" * 90)
    print(f"{'Variant':<60}  {'N':>5}  {'Median |bp|':>11}  {'Match?'}")
    print("-" * 90)
    for v in variants:
        med_str = f"{v['median_bp']:8.1f} bp" if v["N"] > 0 else "     n/a   "
        print(f"{v['label']:<60}  {v['N']:>5}  {med_str}  {v['near38']}")
    print("=" * 90)

    # Summary of matches
    matches = [v for v in variants if v["near38"]]
    print()
    if matches:
        print(f"VARIANTS WITHIN +/-{TOLERANCE_BP:.0f}bp OF {TARGET_BP:.0f}bp:")
        for v in matches:
            print(f"  -> {v['label']}  (N={v['N']}, median={v['median_bp']:.1f} bp)")
    else:
        print(f"NO variant produced a median within +/-{TOLERANCE_BP:.0f}bp of {TARGET_BP:.0f}bp.")
        print("The 38bp figure in analysis_framework.md cannot be explained by any tested")
        print("methodology choice. It appears to be an error in the framework document.")

    print()


import sys as _sys

if __name__ == "__main__":
    if "--sensitivity" in _sys.argv:
        sensitivity_main()
    else:
        main()
        print()
        sensitivity_main()
