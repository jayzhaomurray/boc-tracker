"""
Empirical test: does (CPI-trim minus CPI-median) correlate with the cross-sectional
skewness of price changes across CPI basket components?

The reading-guide claim is: "If trim > median, the distribution of price changes is
right-skewed." This script tests that claim against the data.

Method:
  1. Use the BoC's published CPI-trim and CPI-median (Y/Y %) — no methodology
     replication needed; we trust their numbers.
  2. From the 60 depth-3 CPI components and their basket weights, compute the
     weighted cross-sectional Y/Y % change distribution for each month.
  3. Measure skewness of that distribution two ways:
       - Pearson's moment skewness (third standardized moment)
       - Bowley's quartile skewness: (Q3 + Q1 - 2*Q2) / (Q3 - Q1)
  4. Correlate (trim - median) against each skewness measure across the historical
     record. Strong positive correlation => the signal is empirically supported.
     Weak / zero / negative => the signal is noise.

Caveats:
  - Our 60 components are coarser than the BoC's ~149 sub-components.
  - Our data is not seasonally adjusted; BoC's trim and median are.
  - We're testing time-series co-movement, not exact level reproduction.
"""

from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT  = Path(__file__).resolve().parent


# ── Helpers ──────────────────────────────────────────────────────────────────

def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    """Weighted quantile via the cumulative-weight definition (linear interp)."""
    order = np.argsort(values)
    v = values[order]
    w = weights[order]
    cw = np.cumsum(w)
    cw = cw / cw[-1]
    return float(np.interp(q, cw, v))


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.average(values, weights=weights))


def weighted_std(values: np.ndarray, weights: np.ndarray) -> float:
    m = weighted_mean(values, weights)
    return float(np.sqrt(np.average((values - m) ** 2, weights=weights)))


def pearson_skewness(values: np.ndarray, weights: np.ndarray) -> float:
    """Third standardized moment (weighted). >0 = right-skewed."""
    m = weighted_mean(values, weights)
    s = weighted_std(values, weights)
    if s == 0:
        return 0.0
    return float(np.average(((values - m) / s) ** 3, weights=weights))


def bowley_skewness(values: np.ndarray, weights: np.ndarray) -> float:
    """Quartile-based skewness, robust to outliers. >0 = right-skewed."""
    q1 = weighted_quantile(values, weights, 0.25)
    q2 = weighted_quantile(values, weights, 0.50)
    q3 = weighted_quantile(values, weights, 0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0.0
    return (q3 + q1 - 2 * q2) / iqr


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    # Components: wide DataFrame, date index, columns = component names
    comp = pd.read_csv(DATA / "cpi_components.csv", parse_dates=["date"], index_col="date")
    print(f"Components loaded: {comp.shape[1]} series, {len(comp)} months "
          f"({comp.index.min().date()} to {comp.index.max().date()})")

    # Weights from breadth mapping
    with open(DATA / "cpi_breadth_mapping.json") as f:
        mapping = json.load(f)
    raw_weights = {m["name"]: m["wt_value"] for m in mapping if m["wt_value"] is not None}

    # Drop components whose history starts later than 1995 — keeps the analysis on
    # a stable basket and matches what build.py does for the breadth chart.
    keep = [c for c in comp.columns
            if c in raw_weights
            and comp[c].first_valid_index() <= pd.Timestamp("1995-01-01")]
    comp = comp[keep]
    weights = pd.Series({c: raw_weights[c] for c in keep})
    weights = weights / weights.sum()
    print(f"After dropping late-starting components: {len(keep)} components, "
          f"weight sum = {weights.sum():.4f}")

    # Y/Y % change per component
    yoy = comp.pct_change(12) * 100

    # BoC published trim & median (Y/Y %)
    trim   = pd.read_csv(DATA / "cpi_trim.csv",   parse_dates=["date"]).set_index("date")["value"]
    median = pd.read_csv(DATA / "cpi_median.csv", parse_dates=["date"]).set_index("date")["value"]
    spread = (trim - median).dropna()

    # Compute skewness for each month where we have a full cross-section
    rows = []
    w_arr = weights.reindex(yoy.columns).fillna(0.0).to_numpy()
    for date, row in yoy.iterrows():
        v = row.to_numpy()
        mask = ~np.isnan(v)
        if mask.sum() < 30:                       # need a reasonable cross-section
            continue
        v_, w_ = v[mask], w_arr[mask]
        w_ = w_ / w_.sum()
        rows.append({
            "date": date,
            "n_components": int(mask.sum()),
            "weighted_mean":   weighted_mean(v_, w_),
            "weighted_median": weighted_quantile(v_, w_, 0.5),
            "pearson_skew":    pearson_skewness(v_, w_),
            "bowley_skew":     bowley_skewness(v_, w_),
        })
    skew_df = pd.DataFrame(rows).set_index("date")

    # Merge with BoC trim/median spread
    df = skew_df.join(trim.rename("boc_trim")).join(median.rename("boc_median"))
    df["boc_spread"] = df["boc_trim"] - df["boc_median"]
    df = df.dropna(subset=["boc_spread", "pearson_skew", "bowley_skew"])

    # Correlations
    pearson_corr = df["boc_spread"].corr(df["pearson_skew"])
    bowley_corr  = df["boc_spread"].corr(df["bowley_skew"])
    spearman_p   = df["boc_spread"].corr(df["pearson_skew"], method="spearman")
    spearman_b   = df["boc_spread"].corr(df["bowley_skew"],  method="spearman")

    # Sign-agreement — does the SIGN of (trim - median) match the SIGN of skewness?
    sign_agree_p = ((np.sign(df["boc_spread"]) == np.sign(df["pearson_skew"]))).mean()
    sign_agree_b = ((np.sign(df["boc_spread"]) == np.sign(df["bowley_skew"]))).mean()

    print()
    print("Results")
    print("=======")
    print(f"Months analyzed: {len(df)} ({df.index.min().date()} to {df.index.max().date()})")
    print()
    print(f"Pearson corr (BoC trim-median spread vs Pearson skewness): {pearson_corr:+.3f}")
    print(f"Pearson corr (BoC trim-median spread vs Bowley skewness):  {bowley_corr:+.3f}")
    print(f"Spearman corr (vs Pearson skew): {spearman_p:+.3f}")
    print(f"Spearman corr (vs Bowley skew):  {spearman_b:+.3f}")
    print()
    print(f"Sign-agreement rate (Pearson skew vs spread): {sign_agree_p:.1%}")
    print(f"Sign-agreement rate (Bowley skew vs spread):  {sign_agree_b:.1%}")
    print()
    print("Reading: a positive correlation near +1 (and high sign-agreement) supports")
    print("the claim that trim > median signals a right-skewed distribution. A weak or")
    print("negative correlation, or sign-agreement near 50%, refutes the claim.")

    # Save outputs
    df.to_csv(OUT / "trim_vs_median_skewness_results.csv")
    print(f"\nWrote: {OUT / 'trim_vs_median_skewness_results.csv'}")

    # Plots
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, skew_col, label, corr in [
        (axes[0], "pearson_skew", "Pearson skewness", pearson_corr),
        (axes[1], "bowley_skew",  "Bowley skewness",  bowley_corr),
    ]:
        ax.scatter(df[skew_col], df["boc_spread"], s=10, alpha=0.5)
        ax.axhline(0, color="#888", lw=0.7)
        ax.axvline(0, color="#888", lw=0.7)
        ax.set_xlabel(f"{label} of YoY price-change cross-section")
        ax.set_ylabel("BoC CPI-trim minus CPI-median (pp)")
        ax.set_title(f"{label}  (Pearson r = {corr:+.3f})")
        ax.grid(True, alpha=0.3)
    fig.suptitle("Does (trim − median) track cross-sectional skewness?", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "trim_vs_median_skewness_plot.png", dpi=130, bbox_inches="tight")
    print(f"Wrote: {OUT / 'trim_vs_median_skewness_plot.png'}")


if __name__ == "__main__":
    main()
