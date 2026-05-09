# BoC-Fed spread: testing the 38 bp claim in analysis_framework.md

**Claim under test** (framework line 114): "Empirical distribution since 1996 (median |spread| 38bp)"

**Audit finding (prior):** Monthly month-start resolution, 1996-01 to 2026-04 produces median 62.5 bp.

---

## Sensitivity results (11 methodology variants tested)

| Variant | N | Median |bp| | Match (33-43 bp)? |
|---|---|---|---|
| Monthly MS: full 1996-2026 | 364 | 62.5 | no |
| Monthly MS: 1996-2023 | 336 | 62.5 | no |
| Monthly MS: 2000-2023 | 288 | 62.5 | no |
| Monthly MS: 1996-2019 pre-COVID | 288 | 74.0 | no |
| Monthly MS: 1996-2008 pre-ZLB | 156 | 77.5 | no |
| Monthly MS: 2009-2019 ZLB era | 132 | 62.5 | no |
| **Daily: 2009-04 to 2026-04** | **4429** | **37.5** | **YES** |
| **Daily: 2009-04 to 2023-12** | **3825** | **37.5** | **YES** |
| Monthly end-of-month: full | 364 | 62.5 | no |
| Monthly MS: excl COVID floor | 340 | 74.0 | no |
| Monthly MS: excl GFC + COVID floor | 325 | 74.0 | no |

---

## Finding

Two variants produce 37.5 bp, within the ±5 bp tolerance of the claimed 38 bp: **daily resolution, restricted to the post-ZLB era (2009-04 onward)**, with or without the recent BoC-below-Fed divergence. The 0.5 bp gap from 38 is rounding.

This is the most likely origin of the 38 bp figure. The BoC overnight rate has daily data only from 2009-04-21 (`overnight_rate_daily.csv`). If the original computation used daily resolution and the available daily window, the result is 37.5 bp — plausibly written as "~38 bp." The claim's window attribution ("since 1996") is wrong: the daily series doesn't reach 1996, and no monthly variant produces anything close to 38 bp.

## Correction needed

`analysis_framework.md` line 114 should be updated to:

- Change "since 1996" to "since 2009 (daily rate data)" or similar
- Change 38 bp to 37.5 bp, or note that monthly resolution gives 62.5 bp and daily gives 37.5 bp
- The ±50/100/150 bp tier labels and percentile claims derived from this median should also be re-audited against the corrected baseline

The most defensible fix depends on which resolution the thresholds are meant to operationalize. If the thresholds are used to flag blurb-level regime differences (monthly analytical cadence), the monthly baseline of 62.5 bp is more appropriate. If they come from the daily computation, the window label "since 1996" must be corrected to "since 2009."
