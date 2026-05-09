"""Empirical distribution of |can2y_overnight_spread| since 2001.

Establishes the convention-aligned tier thresholds for the Canada 2Y - Overnight
spread. Used to calibrate _classify_can2y_overnight() in analyze.py and the
framework prose in analysis_framework.md.

DATA AND RESOLUTION CHOICE
---------------------------------------------------------------------------
The indicator is `can2y_overnight_spread` = Canada 2Y benchmark yield minus
the BoC overnight rate target.

The existing Tier-2 audit (policy.md Claim 6, 2026-05-09) computed the
empirical distribution at **daily** resolution (N=6,338, 2001-01-02 to
2026-05-07) using overnight_rate_daily.csv (available from 2009-04-21 onward,
forward-filled from overnight_rate.csv for earlier dates). That daily
methodology produced median |spread| 30bp, ±25bp = 44%, ±50bp = top 35%,
±100bp = top 10% -- consistent with the framework's pre-convention claims.

The project-level distribution convention (distribution_conventions.md) uses
**monthly month-start** sampling as its canonical resolution for spread-tier
classification. The bocfed_spread worked example follows this convention
(overnight_rate.csv + fed_funds.csv, monthly month-start, N=364). To be
consistent with that worked example -- and to ensure the resulting thresholds
are calibrated against the same temporal sampling the blurb generator will
encounter at its monthly cadence -- this script also uses monthly month-start
sampling.

For the full 2001+ window, overnight_rate_daily.csv covers only 2009-04-21
onward. For 2001-2009 we fall back to overnight_rate.csv (monthly), picking
the first observation of each month as the month-start anchor. This is the
same forward-fill approach used in the bocfed_spread worked example and is
documented here for auditability.

Result: N ~ 292 monthly month-start observations, 2001-01 to present.
Because N < 300, the small-N caveat in distribution_conventions.md applies:
state N alongside percentiles; the extreme tier (top 1%) is sparsely
populated.

Outputs:
    analyses/can2y_overnight_spread_distribution.csv   (monthly series)
    analyses/can2y_overnight_spread_distribution.png   (histogram)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_DIR = Path(__file__).resolve().parent

ANCHORS_BP = [25, 50, 100]


def load_csv(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.set_index("date").sort_index()
    return df["value"]


def to_month_start(s: pd.Series) -> pd.Series:
    """Snap to month start: pick the first observation in each calendar month."""
    return s.groupby(s.index.to_period("M")).first().to_timestamp()


def build_overnight_monthly() -> pd.Series:
    """Return monthly month-start overnight rate back to 2001.

    Uses daily series where available (2009-04-21+), falls back to monthly
    series for earlier dates. Picks first observation of each month in both
    cases, consistent with bocfed_spread methodology.
    """
    # Monthly series: available 2001+ (or earlier)
    monthly_raw = load_csv(DATA / "overnight_rate.csv")
    monthly_ms = to_month_start(monthly_raw)

    # Daily series: available 2009-04-21+
    daily_raw = load_csv(DATA / "overnight_rate_daily.csv")
    daily_ms = to_month_start(daily_raw)

    # Combine: prefer daily where available, fall back to monthly
    combined = monthly_ms.copy()
    combined.update(daily_ms)
    return combined


def main() -> None:
    # -- Load and align series --------------------------------------------------
    cad_2y_raw = load_csv(DATA / "yield_2yr.csv")
    cad_2y_ms = to_month_start(cad_2y_raw)

    overnight_ms = build_overnight_monthly()

    df = pd.concat({"cad_2y": cad_2y_ms, "overnight": overnight_ms}, axis=1).dropna()
    df = df[df.index >= "2001-01-01"]

    df["spread_pp"] = df["cad_2y"] - df["overnight"]
    df["abs_spread_bp"] = df["spread_pp"].abs() * 100.0

    n = len(df)
    abs_bp = df["abs_spread_bp"].to_numpy()
    median_bp = float(np.median(abs_bp))
    mean_bp = float(np.mean(abs_bp))

    # -- Print stats -----------------------------------------------------------
    print("=" * 72)
    print(
        f"Canada 2Y - Overnight |spread| distribution, monthly month-start, "
        f"{df.index.min().date()} to {df.index.max().date()}"
    )
    print(f"N = {n}")
    print("=" * 72)
    print(f"Median |spread|   : {median_bp:5.1f} bp")
    print(f"Mean   |spread|   : {mean_bp:5.1f} bp")
    print()

    print("Share at-or-below each |spread| anchor:")
    for a in ANCHORS_BP:
        share_within = (abs_bp <= a).mean() * 100
        share_above = 100 - share_within
        print(f"  |spread| <= {a:3d} bp : {share_within:5.1f}%   (so >{a}bp = top {share_above:4.1f}%)")
    print()

    print("Selected percentiles of |spread| (bp):")
    for p in [50, 75, 80, 90, 95, 99]:
        pv = float(np.percentile(abs_bp, p))
        print(f"  P{p:02d} : {pv:6.1f} bp")
    print()

    # Convention tier thresholds
    p50 = float(np.percentile(abs_bp, 50))
    p80 = float(np.percentile(abs_bp, 80))
    p95 = float(np.percentile(abs_bp, 95))
    p99 = float(np.percentile(abs_bp, 99))

    print("Convention tier thresholds (P50/P80/P95/P99):")
    print(f"  P50 (typical boundary)     : {p50:6.1f} bp")
    print(f"  P80 (uncommon boundary)    : {p80:6.1f} bp")
    print(f"  P95 (pronounced boundary)  : {p95:6.1f} bp")
    print(f"  P99 (rare boundary)        : {p99:6.1f} bp")
    print(f"  Extreme: above P99         : > {p99:.1f} bp")
    print()

    print("Framework anchor labels vs computed reality (daily-resolution audit, for reference):")
    rows = [
        ("median",  "30 bp",      f"{median_bp:.1f} bp"),
        ("+/-25bp", "44% within", f"{(abs_bp <= 25).mean()*100:.1f}% within"),
        ("+/-50bp", "top third",  f"top {(abs_bp > 50).mean()*100:.1f}%"),
        ("+/-100bp","top 10%",    f"top {(abs_bp > 100).mean()*100:.1f}%"),
    ]
    label_w = max(len(r[0]) for r in rows)
    claim_w = max(len(r[1]) for r in rows)
    for label, claim, real in rows:
        print(f"  {label:<{label_w}}  claim: {claim:<{claim_w}}   monthly reality: {real}")
    print()

    # Signed spread stats
    signed_bp = (df["spread_pp"] * 100).to_numpy()
    median_signed = float(np.median(signed_bp))
    mean_signed = float(np.mean(signed_bp))

    print("Signed spread (Canada 2Y - Overnight) distribution stats:")
    print(f"  Median: {median_signed:+6.1f} bp")
    print(f"  Mean  : {mean_signed:+6.1f} bp")
    print(f"  Min   : {signed_bp.min():+6.1f} bp")
    print(f"  Max   : {signed_bp.max():+6.1f} bp")
    print(f"  Share positive (cad_2y > overnight): {(signed_bp > 0).mean()*100:5.1f}%")
    print(f"  Share negative (cad_2y < overnight): {(signed_bp < 0).mean()*100:5.1f}%")
    print(f"  Share = 0                           : {(signed_bp == 0).mean()*100:5.1f}%")
    print()

    # -- CSV output ------------------------------------------------------------
    out_csv = OUT_DIR / "can2y_overnight_spread_distribution.csv"
    try:
        df.to_csv(out_csv)
        print(f"Wrote raw monthly series -> {out_csv.relative_to(ROOT)}")
    except PermissionError:
        print(f"Skipped CSV write (file locked): {out_csv.relative_to(ROOT)}")

    # -- Histogram -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Left: |spread| in bp
    ax = axes[0]
    bin_edges = np.arange(0, abs_bp.max() + 25, 25)
    ax.hist(abs_bp, bins=bin_edges, color="#2c7fb8", edgecolor="white", alpha=0.85)
    ax.axvline(median_bp, color="black", linestyle="--", linewidth=1.2,
               label=f"Median = {median_bp:.1f} bp")
    tier_colors = {"P50": "#41ab5d", "P80": "#fd8d3c", "P95": "#cb181d", "P99": "#762a83"}
    for label, val, color in [("P50", p50, tier_colors["P50"]),
                               ("P80", p80, tier_colors["P80"]),
                               ("P95", p95, tier_colors["P95"]),
                               ("P99", p99, tier_colors["P99"])]:
        ax.axvline(val, color=color, linestyle="-", linewidth=1.4,
                   label=f"{label} = {val:.1f} bp")
    ax.set_title("|spread| distribution with convention tier boundaries")
    ax.set_xlabel("|Canada 2Y - Overnight| (basis points)")
    ax.set_ylabel("Count of months")
    ax.legend(loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    # Right: signed spread
    ax = axes[1]
    bin_edges_signed = np.arange(
        np.floor(signed_bp.min() / 25) * 25,
        np.ceil(signed_bp.max() / 25) * 25 + 25,
        25,
    )
    ax.hist(signed_bp, bins=bin_edges_signed, color="#7570b3", edgecolor="white", alpha=0.85)
    ax.axvline(0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)
    ax.axvline(median_signed, color="black", linestyle="--", linewidth=1.2,
               label=f"Median = {median_signed:+.1f} bp")
    for val, color in [(p80, tier_colors["P80"]), (p95, tier_colors["P95"]), (p99, tier_colors["P99"])]:
        ax.axvline(+val, color=color, linestyle="-", linewidth=1.2, alpha=0.7)
        ax.axvline(-val, color=color, linestyle="-", linewidth=1.2, alpha=0.7)
    ax.set_title("Signed spread distribution (Canada 2Y - Overnight)")
    ax.set_xlabel("Canada 2Y - Overnight (basis points)")
    ax.set_ylabel("Count of months")
    ax.legend(loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    fig.suptitle(
        f"Canada 2Y - Overnight spread, monthly month-start, "
        f"{df.index.min().date()} to {df.index.max().date()}, N={n}",
        fontsize=12,
        y=1.02,
    )

    out_png = OUT_DIR / "can2y_overnight_spread_distribution.png"
    fig.tight_layout()
    fig.savefig(out_png, dpi=140, bbox_inches="tight")
    print(f"Wrote histogram -> {out_png.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
