# Distribution conventions

How to label readings of indicators on the analytical framework's tier ladder. Designed to: (a) prevent the silent methodology drift the 2026-05-09 audit surfaced (e.g. bocfed_spread thresholds calibrated against daily data but labelled "since 1996"); (b) give blurb writers consistent vocabulary across sections; (c) keep the BoC's published bands authoritative where they apply.

## Tier ladder

Picture the data sorted from "most common" near the median to "most extreme" out in the tails. Tiers carve up the distribution like this:

| Tier | Share of all observations |
|---|---|
| **Typical** | middle 50% |
| **Uncommon** | next 30% out |
| **Pronounced** | next 15% out |
| **Rare** | next 4% out |
| **Extreme** | the most extreme 1% |

(50 + 30 + 15 + 4 + 1 = 100. Each tier is a strictly outer ring than the one before it.)

**For symmetric distributions** (e.g. height, signed spread) each tier's share splits evenly across the two sides. **For skewed distributions** (e.g. weight, `|spread|`) the same population shares apply, but the absolute ranges differ between sides — that's the correct behaviour for asymmetric data.

**Why these boundaries.** P95 and P99 are well-anchored statistical conventions (≈ 2σ-equivalent and 3σ-equivalent for a normal distribution). Calibrated-language research — Mosteller-Youtz survey of probability words, IPCC likelihood scale, EU pharmacovigilance frequency categories — converges on a tighter-at-extremes ladder of similar shape. Equal-sized buckets (quartiles, quintiles) would fight the labels, since "rare" and "extreme" carry inherent low-frequency content in everyday English.

## Per-indicator metadata

Every indicator the framework tiers must specify two pieces of metadata at its definition in `analysis_framework.md`:

### 1. Tail axis — what's being percentile-ranked

| Indicator type | Tail axis |
|---|---|
| Two-tailed (signed value, sign matters) | signed value relative to median; tier by central-share band |
| Absolute envelope (already non-negative) | the value itself; tier by P50/P80/P95/P99 of `x` |
| One-tailed (e.g. high is bad) | `x − median` (one side only) |
| Target-anchored | `x − target`; tier by central-share around target |

### 2. Descriptor pair — the natural directional words at the pronounced tier and above

| Indicator type | Descriptor pair |
|---|---|
| Spreads, signed | high / low |
| Inflation | hot / soft |
| Labour-market tightness | tight / slack |
| Volume / flow | strong / weak |
| Magnitude envelope (no direction) | wide / narrow, large / small |

These are guidance, not a lookup table — pick the natural English pair at the indicator's definition. New indicators name their descriptor pair in the framework section that introduces them.

## BoC-band indicators: dual classification

For indicators where the BoC publishes an authoritative band, range, or target:

- **BoC frame: binary.** In-band or outside-band. Use BoC's published edges. Don't manufacture sub-thresholds for "far outside."
- **Empirical frame: 5-tier ladder** (above) of the indicator's tail axis.

Both classifications are computed and available in framework metadata; **prose surfaces what's analytically salient** — usually one frame suffices, both are surfaced when they tell complementary stories. Inside-band readings often need only the BoC frame; far-outside readings often need only the empirical (the band breach is implied).

Common BoC-band indicators:

| Indicator | BoC band |
|---|---|
| Inflation (headline / core) | 1–3 % control range, 2 % target |
| Policy rate vs. neutral | 2.25–3.25 % range, 2.75 % midpoint |
| Output gap | BoC's published range each MPR |

For indicators without a published BoC band (BoC–Fed spread, can2y_overnight_spread, housing starts, etc.), only the empirical frame applies.

The band edge is conventionally inclusive — at exactly 3.0 % inflation the reading is in-band; the breach starts above 3.0 %.

## Methodology rules

### Always state window, resolution, tail axis, and N when citing a tier

In framework prose: `(median |spread| 62.5 bp, monthly month-start, since 1996, N=364)`. This catches silent methodology drift — you can't cite a number without revealing what it's measuring.

### Recompute thresholds annually, ideally pre-MPR

Empirical percentiles drift as data extends. The BoC updates its own estimates around MPR releases (~four times a year); riding that calendar is natural. Document the recompute date in framework prose so staleness is visible.

### Borderline readings: ±2 percentile points = fuzzy

A reading at P79 vs P81 is mechanically across a tier boundary but practically indistinguishable. Pick the side that better matches analytical context (recent trajectory, BoC framing, broader regime). Cite the percentile so the call is auditable.

### Small-N caveat: state N, downgrade confidence at N<200

For series with N < 200, the extreme tier (top 1%) is sparsely populated — single new outliers can swing the threshold. Don't collapse tiers (keep the ladder uniform across series). State N alongside the percentile and downgrade confidence in prose.

## Synonymic latitude within tier

Formal tier names (typical / uncommon / pronounced / rare / extreme) are for **classification**. Prose can use any natural synonym that reads as the right tier. Examples per tier:

| Tier | Anchor (signed) | Natural variants |
|---|---|---|
| Typical | typical | typical, normal, near-typical, around average |
| Uncommon | slightly high / low | slightly elevated, somewhat high, modestly above |
| Pronounced | high / low | high, hot, tight, materially elevated, clearly above |
| Rare | very high / very low | very high, exceptionally elevated, well above |
| Extreme | extremely high / very low | extremely high, runaway, crisis-level, cycle-defining |

**Constraint:** pick a synonym that clearly belongs to the right tier. Don't bleed across tiers. The percentile cited alongside is the auditable backstop.

## Phrasing template

In framework prose (where the percentile is cited):

> "[Indicator] is currently [value] — [tier or natural synonym] reading ([percentile or BoC frame]; [window + resolution + N])."

In blurbs (the percentile may be dropped if the synonym is unambiguous):

> "[Indicator] is [synonym]" — optionally with the rare / extreme tier or BoC frame appended when it materially adds to the message.

## Design notes

Non-obvious calls behind the rules above — preserved because the convention will affect every blurb across all six sections going forward.

- **Labels: "uncommon → pronounced," not "modest" or "notable / unusual."** "Modest" overlaps with "typical" in everyday English. "Notable" and "unusual" aren't distinguishably escalating in prose without the percentile cited alongside. "Uncommon → pronounced" has formal precedent (EU pharmacovigilance) and clear monotonic escalation.
- **Boundaries P50 / P80 / P95 / P99: tighter-at-extremes, not equal-sized.** Mosteller-Youtz, IPCC, and EU pharma all converge on a tighter-at-extremes ladder. Equal-sized buckets (quartiles, quintiles) would fight the labels — "rare" carries low-frequency content that contradicts a top-25% threshold.
- **Binary BoC frame, not three-state.** BoC publishes the band edge (e.g., 1–3 % inflation) but no formal "far-outside" threshold. Three-state (in / outside / far-outside) would invent a calibration the BoC didn't publish.
- **Central-X% framing for skewed distributions.** `\|x − median\|` over-flags the thin side of asymmetric data (e.g., a 75 lb adult man would be only "extreme" under symmetric framing, despite being medically near-impossible). Central-X% handles symmetric and skewed uniformly via empirical percentiles.
- **English labels, not numeric tiers.** Three independent calibrated-language frameworks settle on labelled tiers; numeric tiers (Tier 1 / Tier 2 …) lose readability. The dashboard's audience expects natural prose.
- **Synonymic latitude within tier, not strict label enforcement.** Strict enforcement makes blurbs mechanical and identical-sounding. The percentile cited alongside is the auditable backstop, so within-tier synonyms ("slightly elevated," "uncommon," "somewhat high") are safe.
- **Validation:** sanity-checked against intuition tests on US adult height, weight, and Texas hold'em probabilities. Bocfed_spread methodology drift documented in `analyses/bocfed_spread_38bp_test.md` (the worked example that surfaced the need for this convention).

## Reference catalog

Live record of indicators that have had the convention applied. Each entry: tail axis, descriptor pair, BoC frame (if any), tier thresholds, last computed.

| Indicator | Tail axis | Descriptor | BoC frame | Thresholds | Last computed | Source |
|---|---|---|---|---|---|---|
| `bocfed_spread` | `\|spread\|` in bp, monthly month-start, since 1996, N=364 | high / low | none | typical ≤62.5; uncommon to 100; pronounced to 187; rare to 231; extreme >231 | 2026-05-09 | `analyses/bocfed_spread_distribution.py` |
| `can2y_overnight_spread` | `\|spread\|` in bp, monthly month-start, since 2001, N=304 | high (positive, hawkish-priced) / low (negative, dovish-priced) | none | typical ≤32; uncommon to 71; pronounced to 120; rare to 179; extreme >179 | 2026-05-09 | `analyses/can2y_overnight_spread_distribution.py` |
| `headline_cpi_yoy` | `\|CPI Y/Y − 2%\|` in pp, monthly, since 2000, N=315 | hot / soft | 1–3% control range, 2% target (binary: in-band / outside-band) | typical ≤0.62pp; uncommon to 1.29pp; pronounced to 2.80pp; rare to 4.88pp; extreme >4.88pp | 2026-05-09 | `analyses/inflation_distribution.py` |
| `inflation_mom_sa` | `\|M/M SA − 0.165%\|` in %/month, monthly, since 2000, N=315 | hot / soft | none (neutral = 0.165%/mo algebraic identity; no BoC-published band) | typical ≤0.165%/mo; uncommon to 0.341%/mo; pronounced to 0.547%/mo; rare to 0.876%/mo; extreme >0.876%/mo | 2026-05-09 | `analyses/inflation_distribution.py` |
| `core_band_width` | max(core) − min(core) across 5 measures in pp, monthly, since 2000, N=315 (5 measures incl. CPI-common; note: CPI-common not current BoC preferred since 2022) | wide / narrow | none | typical ≤0.70pp; uncommon to 1.00pp; pronounced to 1.40pp; rare to 1.90pp; extreme >1.90pp | 2026-05-09 | `analyses/inflation_distribution.py` |
| `headline_core_gap` | `\|headline Y/Y − core_avg Y/Y\|` in pp, monthly, since 2000, N=315 | large / small | none | typical ≤0.55pp; uncommon to 1.05pp; pronounced to 1.70pp; rare to 2.34pp; extreme >2.34pp | 2026-05-09 | `analyses/inflation_distribution.py` |
| `usdcad_level` | `\|USDCAD − 1.3072\|` in CAD, monthly month-last, since 1990, N=437 | high (weak CAD) / low (strong CAD) | none | typical ≤0.0958; uncommon to 0.2343; pronounced to 0.3068; rare to 0.3374; extreme >0.3374 | 2026-05-09 | `analyses/financial_distribution.py` |
| `wti_yoy` | `\|WTI Y/Y\|` in %, monthly month-last, since 1991, N=425 | inflationary / disinflationary | none | typical ≤20.12%; uncommon to 42.31%; pronounced to 72.02%; rare to 118.04%; extreme >118.04% | 2026-05-09 | `analyses/financial_distribution.py` |
| `wcs_wti_diff` | WTI−WCS differential in $/bbl, monthly, since 2005, N=255 | wide / narrow | none | typical ≤$16.46; uncommon to $22.96; pronounced to $32.11; rare to $39.34; extreme >$39.34 | 2026-05-09 | `analyses/financial_distribution.py` |
| `gdp_contrib_inventories` | `\|inventory contrib\|` in pp AR, quarterly, since 1961, N=259 | large / small | none | typical ≤1.56pp; uncommon to 3.55pp; pronounced to 5.78pp; rare to 8.69pp; extreme >8.69pp | 2026-05-09 | `analyses/gdp_distribution.py` |
| `breadth_tilt` | `\|tilt\|` in pp, absolute envelope, monthly since 1995-12, N=364 | pressure / softening | none | typical ≤10.88pp; uncommon to 20.35pp; pronounced to 41.10pp; rare to 63.27pp; extreme >63.27pp | 2026-05-09 | `analyses/inflation_distribution.py` |
| `csce_5y_dev` | `\|5y CSCE − 2%\|` in pp, quarterly since 2015-Q1, N=44 SMALL-N | hot / soft | 1–3% control range (binary: in-band/outside-band) | typical ≤1.55pp; uncommon to 1.91pp; pronounced to 2.00pp; rare to 2.19pp; extreme >2.19pp | 2026-05-09 | `analyses/inflation_distribution.py` |
| `housing_starts_12mma` | `\|starts 12-month MA − 197.865k\|` in thousands SAAR, monthly, since 1990, N=424 | strong / weak | none | typical ≤32.5k; uncommon to 52.8k; pronounced to 71.4k; rare to 86.3k; extreme >86.3k | 2026-05-09 | `analyses/housing_distribution.py` |
| `nhpi_yoy` | `\|NHPI Y/Y − 1.704%\|` in pp, monthly, since 1982, N=531 | hot / soft | none | typical ≤2.0pp; uncommon to 5.3pp; pronounced to 10.3pp; rare to 13.7pp; extreme >13.7pp | 2026-05-09 | `analyses/housing_distribution.py` |
| `crea_hpi_yoy` | `\|CREA MLS HPI Y/Y − 3.660%\|` in pp, monthly, since 2015, N=134 SMALL-N | hot / soft | none | typical ≤6.6pp; uncommon to 12.6pp; pronounced to 22.4pp; rare to 25.4pp; extreme >25.4pp | 2026-05-09 | `analyses/housing_distribution.py` |
| `housing_affordability` | `\|afford ratio − 0.3335\|`, quarterly, since 2000, N=104 SMALL-N | stressed / comfortable | none (BoC publishes indicator without bands; 0.40/0.50 levels are analyst synthesis) | typical ≤0.028; uncommon to 0.059; pronounced to 0.174; rare to 0.206; extreme >0.206 | 2026-05-09 | `analyses/housing_distribution.py` |
| `ulc_yoy` | `\|ULC Y/Y − 2.0%\|` in pp (target-anchored), quarterly, since 1982, N=176 SMALL-N | labour-cost-pressure / labour-cost-soft | none | typical ≤1.4pp; uncommon to 3.1pp; pronounced to 4.6pp; rare to 6.8pp; extreme >6.8pp | 2026-05-09 | `analyses/labour_distribution.py` |
| `real_wage_lfs_all` | `\|RW Y/Y − median (+1.01%)\|` in pp, monthly, since 2002, N=291 | real-wage-positive / real-wage-negative | none | typical ≤0.94pp; uncommon to 2.21pp; pronounced to 4.10pp; rare to 5.76pp; extreme >5.76pp | 2026-05-09 | `analyses/labour_distribution.py` |
| `real_wage_lfs_perm` | `\|RW Y/Y − median (+0.97%)\|` in pp, monthly, since 2002, N=291 | real-wage-positive / real-wage-negative | none | typical ≤1.01pp; uncommon to 2.25pp; pronounced to 3.98pp; rare to 5.30pp; extreme >5.30pp | 2026-05-09 | `analyses/labour_distribution.py` |
| `real_wage_seph` | `\|RW Y/Y − median (+0.73%)\|` in pp, monthly, since 2002, N=290 | real-wage-positive / real-wage-negative | none | typical ≤0.89pp; uncommon to 1.91pp; pronounced to 4.54pp; rare to 7.47pp; extreme >7.47pp | 2026-05-09 | `analyses/labour_distribution.py` |
| `real_wage_lfs_micro` | `\|RW Y/Y − median (+0.59%)\|` in pp, monthly, since 2000, N=315 | real-wage-positive / real-wage-negative | none | typical ≤0.67pp; uncommon to 1.47pp; pronounced to 2.86pp; rare to 4.06pp; extreme >4.06pp | 2026-05-09 | `analyses/labour_distribution.py` |
