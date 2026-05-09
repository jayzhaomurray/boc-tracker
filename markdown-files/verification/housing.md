# Verification log: Housing section

Per-claim source log for the Housing section of `analysis_framework.md` (lines 219-251). Each claim in the framework is paired with: (a) the framework prose verbatim, (b) the primary source(s) used to verify, (c) a direct quote where possible, (d) a verification verdict, (e) a provenance tier (see `_tiers.md`), and (f) defects + open questions.

This file is **not** in CLAUDE.md's "First moves" auto-load list — it is a working log kept separate from framework prose. The framework itself carries inline citations; this log carries the page-level evidence chain.

**Provenance tiers (see `_tiers.md` for full glossary):**
- **Tier 1 — Generated.** Claude-written, no verification.
- **Tier 2 — Autonomously verified.** Claude / sub-agent ran sources, the user did NOT review.
- **Tier 3 — User-verified.** User pushed back on framings, accepted/rejected/revised per claim.

**Verification verdict glossary (orthogonal to tier):**

- **VERIFIED** — direct quote from a primary source supports the framework claim.
- **PARTIALLY VERIFIED** — primary source supports the substance but the framework's specific framing or numbers extend beyond the source.
- **CONTESTED** — primary sources disagree, or multiple primary sources contradict the framework's claim.
- **UNSOURCED — analyst judgment** — the claim is the analyst's framing, not a direct primary-source claim.
- **PENDING** — not yet researched.

All entries below are **Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.** The framework's own "VERIFICATION STATUS: verified end-to-end (May 2026)" header (line 221) reflects an earlier autonomous pass; this audit re-runs verification claim-by-claim and surfaces multiple defects that the prior "verified end-to-end" header missed.

---

## Claim 1: Long-run housing-starts average since 1977 (~194k SAAR) and recent 10-year average (~245k SAAR)

### Framework prose (verbatim)

> Long-run average since 1977 is ~194k SAAR. Recent 10-year averages have been higher (~245k)…

Repeated in thresholds bullet:

> **Long-run average since 1977: ~194k SAAR; recent 10-year average: ~245k SAAR.**

### Verification verdict

**CONTESTED — date anchor inconsistent with project data; 10-year average overstated.**

### Source — project data `data/housing_starts.csv`

- Series start in project: **1990-01-01** (vector 52300157, StatsCan Table 34-10-0158-01, monthly SAAR units).
- The "since 1977" anchor cannot be verified against project data; the project's monthly SAAR series begins in 1990.
- **Mean (Jan 1990 – Dec 2024):** 193.33k. Median: 195.08k.
- **Mean (Jan 1990 – present, Mar 2026):** 195.46k.
- **Recent 10-year mean (May 2016 – Apr 2026):** 235.46k. Calendar 2016-2025: 233.99k. Calendar 2015-2024: 227.51k. **None of these matches the 245k claim.** The closest match (~245k) corresponds to calendar 2024 alone (244.80k), not a 10-year window.

### Defects flagged

1. **"Since 1977" date anchor unverified.** The project's series starts in 1990. The 194k mean is computed from 1990 onward, not 1977. Either (a) the framework borrowed "1977" from a CMHC published-history reference and it happens to coincide with the 1990-onward mean, or (b) "1977" is wrong. **Cannot be verified with current project data.** StatsCan annual Table 34-10-0126-01 reportedly extends further back; not fetched.
2. **Recent 10-year average overstated.** Framework says ~245k; actual is 233-235k depending on window. The 245k figure matches calendar 2024 alone (CMHC has reported recent annual starts of ~245-259k for 2024-2025 individually) — likely the framework is conflating a single recent year with a 10-year mean.
3. **Reads as canonical but is at minimum imprecise.** A "verified May 2026" threshold should not be off by ~10k on the recent 10-year average.

### Open questions for user review

- Source the "since 1977" anchor against a CMHC publication (e.g. Housing Information Monthly) or StatsCan annual table, and either confirm the date or replace with "since 1990 (project data start)."
- Recompute the recent 10-year average against project data and update to ~234k (or specify a calendar window).

---

## Claim 2: CMHC 2023 Housing Shortages report — 4.8M-unit gap and 430-500k starts/year through 2030

### Framework prose (verbatim)

> the 2023 CMHC Housing Shortages report estimated Canada needs ~430-500k starts/year through 2030 to close the 4.8M-unit affordability gap.

Also referenced in thresholds:

> **Affordability-restoring pace per CMHC: 430-500k/year.**

### Verification verdict

**CONTESTED — citation conflated. The 4.8M figure is from a different (June 2025) CMHC report, not the 2023 Housing Shortages report. The 430-500k starts pace targets a different end-year (2035, not 2030).**

### Source 1 — CMHC, "Housing shortages in Canada: Updating how much housing we need by 2030" (Sep 13, 2023)

**URL:** https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-research/research-reports/accelerate-supply/housing-shortages-canada-updating-how-much-we-need-by-2030

**Direct quote:** *"To restore affordability, we maintain our 2022 projection that Canada will need 3.5 million more units on top of what's already being built."*

- **Unit gap in the 2023 report: 3.5 million units (baseline scenario), to 2030.** Two alternative scenarios discussed (low-economic-growth: 3.1M; high-population-growth: 4.0M). **The 4.8M figure does not appear** in this report.

### Source 2 — CMHC, "Housing Shortages in Canada: Solving the Affordability Crisis" (June 2025)

**URL:** https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-research/research-reports/accelerate-supply/housing-shortages-canada-solving-affordability-crisis

**Public reporting (CBC News, Construct Connect, BNN Bloomberg, June 19 2025):**

- *"Up to 4.8 million new homes will need to be built over the next decade to restore affordability levels last seen in 2019."*
- *"Between 430,000 and 480,000 new housing units are needed per year across the ownership and rental markets by 2035."*

CBC News URL: https://www.cbc.ca/news/business/cmhc-affordability-homes-1.7565525

**Both figures the framework cites (4.8M, 430-500k starts/year) come from this June 2025 report, not the 2023 Housing Shortages report.** The end-year is **2035**, not 2030. The framework's upper bound is "500k" but CMHC's reported upper bound is "480k."

### Defects flagged

1. **Defect type 1 (citation misattribution).** The framework attributes the 4.8M and 430-500k figures to "the 2023 CMHC Housing Shortages report." The 2023 report says 3.5M units. The 4.8M / 430-480k numbers come from a **June 2025** CMHC report ("Solving the Affordability Crisis"). Citation needs to be updated to the 2025 report.
2. **End-year mismatch.** Framework says "through 2030"; the 2025 report's annual-starts pace targets **2035**, not 2030.
3. **Upper-bound range overstated.** Framework says "430-500k"; the 2025 report's upper bound is 480k. The "500k" is a rounding-up beyond the source.
4. **No fabricated quotes** — both numbers exist in CMHC publications, just attributed to the wrong report.

### Open questions for user review

1. Re-attribute citation to the **June 2025 "Solving the Affordability Crisis"** report.
2. Update end-year to 2035.
3. Tighten upper bound to 480k (or quote the range "430,000-480,000").
4. Decide whether to keep the 2023 report reference at all (the 3.5M figure may also warrant inclusion, since it sets the historical baseline that the 2025 report updated).

---

## Claim 3: Permits-to-starts lag (2-10 months single-detached, 9-15+ months multi-unit) cited as CMHC Spring 2026 analysis

### Framework prose (verbatim)

> per CMHC's Spring 2026 analysis, single-detached permits lead starts by 2-10 months, but **multi-unit / high-rise permits lead by 9-15+ months** (Calgary high-rise ~17 months; Toronto ~11 months; Montreal ~16 months).

Repeated in thresholds:

> **Permits as leading indicator: 9-15 months blended (type-dependent: 2-10 months single-detached, 9-15+ months multi-unit/high-rise).**

### Verification verdict

**PARTIALLY VERIFIED — numbers are correct, but the citation is wrong. The numbers come from a CMHC Observer article (April 2026), not the Spring 2026 Housing Supply Report.**

### Source 1 — CMHC Observer article: "Building permits are early indicators of housing market sentiment" (April 17, 2026)

**URL:** https://www.cmhc-schl.gc.ca/observer/2026/canadas-construction-pulse-permits-lead-starts-confirm

**Direct quote:** *"high-rise structures show a longer delay between the acquisition of a building permit and the housing start (roughly 9 to 15 months) relative to single-detached houses (roughly 2-10 months)."*

**City-specific lags (from Table 1a):**
- Montreal high-rise: 486.5 days (~16 months) ✓
- Toronto high-rise: 334 days (~11 months) ✓
- Calgary high-rise: 517 days (~17 months) ✓

All three city-specific lag numbers are verified. The 2-10 / 9-15 month split is verified.

### Source 2 — CMHC Spring 2026 Housing Supply Report

**URL:** https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/market-reports/housing-market/housing-supply-report

**Finding:** The Spring 2026 Housing Supply Report **does NOT contain** a permits-to-starts lag analysis. It focuses on starts, completions, and units under construction across major CMAs. The lag numbers the framework cites are from the April 2026 Observer article, not the Supply Report.

### Defects flagged

1. **Defect type 4 (mis-attributed source).** The framework cites "CMHC's Spring 2026 analysis" — but the Spring 2026 *Housing Supply Report* does not contain this analysis. The numbers are from the **April 17, 2026 CMHC Observer** article. Recommend updating the citation.
2. **The numerical claims themselves are VERIFIED** — single-detached 2-10 months, high-rise 9-15 months, and the three city-specific lags are all directly supported by the Observer article.
3. **No fabricated quotes** — the numbers reproduce CMHC's published figures correctly.
4. **No US heuristic transfer** — these are Canadian-specific permit-start lag estimates from CMHC.

### Open questions for user review

1. Replace "CMHC's Spring 2026 analysis" with **"CMHC Observer (April 17, 2026), 'Building permits are early indicators of housing market sentiment'"**.
2. Optionally specify the Calgary/Toronto/Montreal numbers in days (517/334/486.5) rather than approximating to months — but the framework's month rounding is reasonable for a thresholds bullet.

---

## Claim 4: SAN 2025-21 mortgage renewal claims — ~60% renew 2025-2026; ~60% see higher payments; 5-year fixed face 15-20% increases

### Framework prose (verbatim)

> ~60% of all outstanding mortgages renew in 2025-2026; ~60% of those renewing will see higher payments; **5-year fixed holders face average payment increases of 15-20%** vs. December 2024 levels.

Repeated in thresholds:

> **Mortgage renewal stress (FSR 2025 quantification): ~60% of outstanding mortgages renew 2025-26; 5-year fixed holders face 15-20% payment increases.**

### Verification verdict

**VERIFIED.** All three numbers reproduce SAN 2025-21 verbatim or near-verbatim.

### Source — BoC Staff Analytical Note 2025-21, "How will mortgage payments change at renewal? An updated analysis" (July 2025)

**URL:** https://www.bankofcanada.ca/2025/07/staff-analytical-note-2025-21/

**Direct quotes:**
- *"About 60% of all outstanding mortgages in Canada are expected to renew in 2025 or 2026."*
- *"About 60% of mortgage holders renewing in 2025 and 2026 are expected to see a payment increase."*
- *"mortgage holders with a five-year, fixed rate contract renewing in 2025 or 2026 could face an average payment increase of around 15%-20%."*

Additional finding (not currently in framework prose): *"Holders of these mortgages renewing in 2026 are likely to see an average increase in payments of 20%."*

### Defects flagged

1. **Citation tag inconsistency:** The framework calls this "FSR 2025 quantification" in the thresholds bullet. The actual source is **SAN 2025-21**, not FSR 2025. FSR 2025 cites SAN 2025-21 but updates the numbers — see Claim 5 below for the FSR 2025 framing, which gives a *smaller* expected payment increase (~8% in 2025, ~5% in 2026 averaged across all renewing mortgages).
2. **No fabricated quotes** — all three numbers reproduce SAN 2025-21 directly.
3. **No US heuristic transfer.**
4. **Date qualifier "vs. December 2024 levels"** is the framework's wording, not SAN 2025-21's. The SAN says "could face an average payment increase of around 15%-20%" without specifying a baseline date.

### Open questions for user review

1. Tag the citation as **SAN 2025-21**, not "FSR 2025." Or, if you want to keep both, add the FSR 2025 update separately (next claim).
2. Drop the "vs. December 2024 levels" qualifier or source it.

---

## Claim 5: SAN 2023-19 payment projection — $1,200 (Feb 2022) → $1,600 by end-2027 (+34%); variable-rate fixed-payment up to ~54%

### Framework prose (verbatim)

> SAN 2023-19 projects median monthly mortgage payment rising from $1,200 (Feb 2022) to $1,600 by end-2027 (+34%); variable-rate fixed-payment holders face up to ~54% increase.

### Verification verdict

**VERIFIED.** Both numerical projections reproduce SAN 2023-19 verbatim.

### Source — BoC Staff Analytical Note 2023-19, "The impact of higher interest rates on mortgage payments" (December 2023)

**URL:** https://www.bankofcanada.ca/2023/12/staff-analytical-note-2023-19/

**Direct quotes:**
- *"the median monthly mortgage payment for all outstanding mortgages will increase from $1,200 in February 2022 to $1,600 by the end of 2027 — an increase of 34%."*
- *"the median payment for this mortgage type [variable-rate, fixed-payment] increases sharply in those years, reaching $2,190 by the end of 2027 — an increase of 54% from the February 2022 level."*

The variable-rate-fixed-payment ~54% number is a point estimate (54%, not "up to ~54%"). Framework's "up to ~54%" wording slightly hedges what is in fact a specific median projection.

### Defects flagged

1. **No fabricated quotes** — both numbers exact.
2. **Minor wording drift:** SAN 2023-19 says "an increase of 54%" (point projection for the median variable-rate-fixed-payment holder by end-2027), not "up to ~54%." The framework's "up to" softening is technically inaccurate.
3. **No US heuristic transfer.**
4. **No threshold-without-source defect** — these are SAN 2023-19's own projections.

### Open questions for user review

1. Tighten "up to ~54%" to "+54% (median variable-rate fixed-payment holder by end-2027)" to match SAN 2023-19's own framing.

---

## Claim 6: FSR 2024 mortgage debt-service ratio — "over one-third of new mortgages had MDSR > 25%, double the 2019 share"

### Framework prose (verbatim)

> mortgage debt-service ratio (BoC FSR 2024: "over one-third of new mortgages had MDSR > 25%, double the 2019 share")

### Verification verdict

**VERIFIED.** The quote reproduces FSR 2024 essentially verbatim.

### Source — BoC Financial Stability Report 2024 (May 2024)

**URL:** https://www.bankofcanada.ca/2024/05/financial-stability-report-2024/

**Reported finding (FSR 2024 directly states):** *"At the end of 2023, over one-third of new mortgages had a mortgage debt service ratio greater than 25%, double the share of new mortgages with the same ratio in 2019."*

The framework's quotation captures this faithfully. The framework abbreviates "mortgage debt service ratio" as "MDSR," which is the framework's shorthand, not BoC vocabulary — minor.

### Defects flagged

1. **No fabricated quote.**
2. **Minor abbreviation:** "MDSR" is framework shorthand, not BoC's published term. Cosmetic.
3. **No US heuristic transfer.**

### Open questions for user review

1. Spell out "mortgage debt-service ratio" instead of abbreviating "MDSR" if the abbreviation isn't used elsewhere in the dashboard.

---

## Claim 7: Housing-starts cyclical anchors — 2008-09 trough, COVID April 2020, March 2021 / Nov 2021 peaks, 2021 annual peak

### Framework prose (verbatim)

> 2008-09 recession bottomed at ~118-149k starts annualized; COVID April 2020 monthly SAAR was ~165k. Below 180k signals acute construction contraction.

> readings above 300k SAAR are exceptional (March 2021 peaked at ~321k; November 2021 was ~306k). Annual starts peaked at ~271k in 2021.

### Verification verdict

**PARTIALLY VERIFIED — most numbers off by small but non-trivial amounts; framework consistently rounds in directions that overstate the trough and understate the recovery's peak month.**

### Source — project data `data/housing_starts.csv`

Verified directly by reading the CSV (StatsCan vector 52300157, monthly SAAR, units in thousands):

| Framework claim | Project-data actual |
|---|---|
| 2008-09 trough "118-149k" | **Actual min 111.78k (April 2009).** Bottom 8 months: 111.78, 115.72, 127.86, 132.31, 137.57, 141.14, 142.73, 150.31. |
| COVID April 2020 "~165k" | **Actual 161.00k.** |
| March 2021 "peaked at ~321k" | **Actual 319.84k.** |
| November 2021 "~306k" | **Actual 305.21k.** |
| Annual starts peak "~271k in 2021" | **Actual 273.75k in 2021.** |

### Defects flagged

1. **2008-09 trough range understates depth.** Framework says "118-149k"; actual minimum is 111.78k (April 2009). The lower bound of the framework's range is 6k higher than the true minimum. Recommend "~112-150k" or "around 112k at the deepest (April 2009)."
2. **COVID April 2020 figure off by ~4k.** Framework says ~165k; actual is 161.00k. Likely a rounded-up CMHC-press-release-style number rather than the StatsCan vector value.
3. **Annual 2021 peak slightly understated.** Framework says ~271k; actual is 273.75k. (Possible source: CMHC annual figure may differ from monthly-SAAR averaged annually, or the framework is rounding differently.)
4. **March 2021 ~321k and Nov 2021 ~306k:** within rounding of 319.84 / 305.21. Not flagged.
5. **No fabricated quotes** — these are quantitative anchors, not sourced quotes.
6. **No US heuristic transfer.**
7. **Pattern note:** All discrepancies tilt in the direction of making cyclical episodes look milder (trough less deep, peak less high). Not large enough to be load-bearing for any blurb conclusion, but a consistent rounding bias that should be flagged.

### Open questions for user review

1. Update the 2008-09 trough lower bound to ~112k (or quote the actual April 2009 minimum of 111.8k).
2. Update COVID April 2020 to 161k.
3. Update annual 2021 peak to ~274k.
4. Or, if these numbers came from a different source (CMHC annual press release vs. StatsCan monthly SAAR), name the source so the discrepancy is intentional and traceable.

---

## Claim 8: Affordability ratio bands — ~0.28-0.40 pre-2015 norm; >0.40 elevated; >0.50 peak-stress; range "2000-present, ~0.28-0.55"

### Framework prose (verbatim)

> the historical range (2000-present, ~0.28-0.55). Pre-2015 era norm was roughly 0.30-0.40; the 2022-23 peak stress episode pushed the ratio above 0.50.

Threshold bullet:

> **Affordability ratio ~0.28-0.40** = pre-2015 era historical norm. **Ratio >0.40** = elevated relative to long-run average. **Ratio >0.50** = peak-stress territory (2022-23 episode).

### Verification verdict

**PARTIALLY VERIFIED — bounds are slightly off and the "pre-2015 norm" range is loosely defined; the 0.50 peak-stress threshold is verified by data but is analyst synthesis (no BoC publication labels 0.50 as a stress threshold).**

### Source 1 — project data `data/housing_affordability.csv` (BoC INDINF_AFFORD_Q, quarterly)

Verified directly:

| Framework claim | Project-data actual |
|---|---|
| Range "2000-present, ~0.28-0.55" | **Actual 0.275 - 0.545.** Min Q1 2002, max Q3 2023. |
| Pre-2015 norm "~0.28-0.40" (in prose, "0.30-0.40") | **Pre-2015 quartiles (Q1-Q3): 0.302-0.331. Min 0.275 (Q1 2002), max 0.403 (Q4 2008).** |
| 2022-23 peak >0.50 | **Verified.** Q3 2023 = 0.545 (max ever). 2022-23 episode had four quarters above 0.50. |

The pre-2015 IQR (0.30-0.33) is much tighter than the framework's "0.28-0.40" or "0.30-0.40" ranges. The 0.40 upper bound only fires in late 2008 (Q4 2008 = 0.403). For most pre-2015 quarters, the ratio sat in 0.30-0.36.

### Source 2 — BoC Real Estate Market Definitions page

**URL:** https://www.bankofcanada.ca/rates/indicators/capacity-and-inflation-pressures/real-estate-market-definitions/

**Finding:** The page defines INDINF_AFFORD_Q as "the share of disposable income that a representative household would put toward housing-related expenses" but **does not publish band thresholds** (no "0.40 = elevated," no "0.50 = peak-stress" published by the BoC). The framework's banding is analyst synthesis.

### Defects flagged

1. **Defect type 3 (threshold without primary source).** The 0.40 / 0.50 / 0.28 bands are analyst synthesis. The BoC publishes the indicator with no published threshold bands. The framework presents these as if canonical.
2. **Pre-2015 norm range misstated.** In the prose at line 232 the range is "0.30-0.40"; in the thresholds at line 247 it is "0.28-0.40." These two should at least match each other. The actual pre-2015 IQR is 0.30-0.33, with extremes 0.275 (low) and 0.403 (high, only Q4 2008).
2a. **Range "0.28-0.55" understates the actual minimum (0.275 → would round to 0.28, OK) and overstates the maximum (0.55 vs actual 0.545 — within rounding but worth noting).**
3. **Internal inconsistency between line 232 (0.30-0.40) and line 247 (0.28-0.40).** Pick one.
4. **No fabricated quotes** — these are quantitative bands, not source quotes.
5. **No US heuristic transfer** — INDINF_AFFORD_Q is a Canadian indicator.

### Open questions for user review

1. Either anchor the 0.40 / 0.50 thresholds in a BoC publication or explicitly label them as analyst synthesis (cf. Labour Claim 6's "the BoC doesn't publish 3% but the identity supports it" framing).
2. Reconcile the line-232 (0.30-0.40) and line-247 (0.28-0.40) pre-2015 ranges.
3. Tighten the pre-2015 norm to "the IQR was 0.30-0.33; the 2008 episode pushed briefly above 0.40" if you want narrative accuracy.

---

## Claim 9: NHPI methodology — "27 CMAs; excludes condo apartments, custom builds, resale"

### Framework prose (verbatim)

> NHPI tracks contractor-reported prices for newly built single-detached, semi-detached, and row homes across 27 CMAs; **it excludes condo apartments** (a major share of recent supply), custom-built homes, and resale.

### Verification verdict

**VERIFIED.** All four claims (27 CMAs, single-detached / semi / row coverage, condo exclusion, resale exclusion) match StatsCan's NHPI methodology.

### Source — StatsCan NHPI methodology (Survey 2310 / Catalogue 62-007-X)

**URL:** https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=2310

**Reported methodology highlights:**
- Coverage: *"27 census metropolitan areas (CMAs)"* ✓
- Dwelling types: *"new single homes, semi-detached homes and townhomes (row or garden homes)"* ✓
- Exclusions: condo apartments are covered separately by the **New Condominium Apartment Price Index (NCAPI)**, not NHPI ✓; resale by the **Resale Residential Property Price Index (RRPPI)** ✓
- Methodology: *"matched-model approach…with explicit quality adjustments. Sales values…from the Canada Mortgage and Housing Corporation's Market Absorption Survey provide the weights."*

### Defects flagged

1. **"Custom-built homes" exclusion** — not explicitly stated in the StatsCan methodology summary the sub-agent retrieved, but is implicit (the survey is the Market Absorption Survey, which captures CMHC builder data, not bespoke custom builds). Worth a sub-agent re-check against the NHPI methodology PDF (Catalogue 62-007-X) before relying on this claim.
2. **"Contractor-reported prices"** — slightly imprecise: NHPI is *builder*-reported, derived from the CMHC Market Absorption Survey. "Builder-reported" is more accurate than "contractor-reported."
3. **No fabricated quotes.**
4. **No US heuristic transfer.**

### Open questions for user review

1. Verify "custom-built homes" exclusion against the StatsCan NHPI methodology PDF directly.
2. Replace "contractor-reported" with "builder-reported."

---

## Claim 10: CREA MLS HPI methodology + "BoC's affordability indicator anchored to it"

### Framework prose (verbatim)

> CREA MLS HPI is hedonic on all MLS transactions (resale-dominant) and is the index the BoC's own affordability indicator is anchored to.

### Verification verdict

**CONTESTED — two-part claim with two distinct defects: (a) the CREA MLS HPI is a hybrid (repeat-sales + hedonic), not purely hedonic; (b) the BoC's affordability indicator is NOT anchored to the CREA MLS HPI — it explicitly uses the MLS *average resale price* (a different series).**

### Source 1 — CREA MLS HPI methodology

**URL:** https://www.crea.ca/files/HPI_Methodology-July-2023-rev-ENG.pdf
**Plain-language overview:** https://www.crea.ca/housing-market-stats/mls-home-price-index/

**Direct findings:** *"The MLS-HPI uses a hybrid model, combining repeat sales and hedonic components."* The 2022 methodology change: benchmark prices now use a 5-year rolling window of attributes; the index represents *"What's a current typical home worth today?"*

**The framework's "hedonic on all MLS transactions" is incorrect.** The HPI is hybrid (repeat-sales + hedonic), not purely hedonic.

### Source 2 — BoC Real Estate Market Definitions page (housing affordability indicator)

**URL:** https://www.bankofcanada.ca/rates/indicators/capacity-and-inflation-pressures/real-estate-market-definitions/

**Direct quote:** *"P_0 is the 6-month moving average of the Multiple Listing Service average resale price; therefore, this measure strictly reflects existing homes and would include all housing types sold in Canada."*

**The BoC's affordability indicator uses the MLS *average resale price*, NOT the CREA MLS HPI.** These are different series:
- MLS average resale price = simple average of all MLS transaction prices in a period.
- CREA MLS HPI = hybrid (repeat-sales + hedonic) constant-quality index.

The framework conflates the two. The BoC page does not mention CREA MLS HPI in the affordability indicator definition.

### Defects flagged

1. **CRITICAL — Defect type 1 / 4 (mis-described methodology + mis-attributed anchoring).** Two distinct errors in one sentence:
   - CREA MLS HPI is hybrid, not "hedonic." This is a methodology mis-description.
   - BoC affordability indicator uses MLS average resale price, not CREA MLS HPI. The framework's "anchored to it" claim is unsupported by the BoC's own published methodology.
2. **Why this matters:** the framework's framing implies the CREA MLS HPI is the canonical resale price input the BoC uses. It is not. A user-facing blurb could spread this error if not corrected.
3. **No fabricated quotes** — but the *factual claim* about anchoring is fabricated in the sense that no primary source supports it; the BoC's published methodology contradicts it.
4. **No US heuristic transfer.**

### Open questions for user review

1. **Correct the methodology description:** "CREA MLS HPI is a hybrid repeat-sales / hedonic index on MLS transactions (resale-dominant)."
2. **Correct the BoC anchoring claim:** The BoC's affordability indicator uses the **MLS average resale price** (a 6-month moving average), not the CREA MLS HPI. Either (a) replace the CREA MLS HPI claim with the MLS average resale price, (b) drop the BoC-anchoring sentence entirely if the dashboard isn't using the BoC's affordability indicator's house-price input, or (c) verify whether the BoC has any *other* indicator that is in fact anchored to the CREA MLS HPI (the Financial Vulnerability Indicators page may use HPI; not yet checked).
3. The framework also separately describes CREA MLS HPI as a series in `data/` (line 225: "BoC Financial Vulnerability Indicators; available 2014-present"). Verify whether the BoC Financial Vulnerability Indicators page uses the CREA MLS HPI directly — that may be the source of the framework's "anchored" claim, but if so the wording should specifically name FVI, not "the BoC's affordability indicator."

---

## Claim 11: NHPI 1989 peak — 16.6% nationally, Toronto-Oshawa +32.7%, Vancouver +14.2%

### Framework prose (verbatim)

> the 1989 peak was 16.6% nationally (Toronto-Oshawa +32.7%, Vancouver +14.2%).

### Verification verdict

**VERIFIED** (all three figures match StatsCan's December 2016 daily release).

### Source 1 — StatsCan, *The Daily*, "New Housing Price Index, December 2016" (Feb 9, 2017)

**URL:** https://www150.statcan.gc.ca/n1/daily-quotidien/170209/dq170209a-eng.htm

**Reported finding (verified by web search):** *"In March 1989, the NHPI at the Canada level posted a record year-over-year increase of 16.6%, with price gains led by the combined metropolitan region of Toronto and Oshawa (+32.7%) and Vancouver (+14.2%)."*

All three figures (16.6% national, +32.7% Toronto-Oshawa, +14.2% Vancouver) match the framework verbatim.

### Source 2 — project data `data/new_housing_price_index.csv`

The series in the project goes back to **January 1981**. Computed Y/Y peak in March 1989 from the project series is 16.50% (the project's NHPI values are rounded to 1 decimal, so pct_change-on-rounded-values produces 16.50% rather than 16.6%; StatsCan's published 16.6% uses unrounded values). Functionally identical.

### Defects flagged

1. **No fabricated quotes** — verbatim from the StatsCan daily release.
2. **No US heuristic transfer** — Canadian NHPI peak.
3. **No threshold-without-source defect** — this is a historical anchor, not a band threshold.
4. **Claim 11 is the cleanest claim in the section.** Tier 2 sign-off candidate without revision.

### Open questions for user review

None. This claim is solid.

---

## Claim 12: NHPI 2021-22 episode "reached 9-10%+"

### Framework prose (verbatim)

> The 2021-22 episode reached 9-10%+

### Verification verdict

**CONTESTED — understates the actual peak. NHPI 2021-22 Y/Y peaked at 12.17% (August 2021) per project data, not 9-10%+.**

### Source — project data `data/new_housing_price_index.csv`

Computed Y/Y for 2021:
- Jan 2021: +5.4%
- Apr 2021: +9.9%
- May 2021: +11.3%
- Jun 2021: +11.9%
- Jul 2021: +11.9%
- **Aug 2021: +12.17% (peak)**
- Sep 2021: +11.3%
- Dec 2021: +11.6%
- Jan 2022: +11.8%
- Mar 2022: +11.0%

The Y/Y stayed in **double digits** (10-12%) for ~10 consecutive months from May 2021 through Feb 2022. The framework's "9-10%+" framing fires below the actual peak.

### Defects flagged

1. **Number understated.** Framework says "9-10%+"; actual peak is 12.2%. Either tighten to "peaked above 12%" or "reached double digits for ~10 consecutive months in 2021-22."
2. **Pattern note (cf. Claim 7):** consistent with Claim 7's pattern of cyclical-episode magnitudes being rounded down — the framework's quantitative anchors lean toward making episodes look milder than they were.
3. **No fabricated quotes.**
4. **No US heuristic transfer.**

### Open questions for user review

1. Update to "peaked at ~12% in August 2021" or similar.

---

## Cross-claim defects index (Tier 2 audit, Housing Claims 1-12)

| Defect class | Where found | Severity |
|---|---|---|
| Mis-attributed source (citation conflated with different report) | **Claim 2: "2023 CMHC Housing Shortages report" — actually the June 2025 "Solving the Affordability Crisis" report (4.8M units, 430-480k/year, end-year 2035 not 2030)** | **CRITICAL** |
| Methodology mis-described + mis-attributed anchoring | **Claim 10: CREA MLS HPI is hybrid not "hedonic"; BoC affordability indicator uses MLS average resale price, NOT CREA MLS HPI** | **CRITICAL** |
| Mis-attributed source (within-CMHC) | Claim 3: "CMHC's Spring 2026 analysis" — actually the April 2026 CMHC Observer article ("Building permits are early indicators…") | high |
| Threshold without primary source | Claim 8: 0.40 = elevated, 0.50 = peak-stress affordability ratio bands (BoC publishes the indicator without bands) | high |
| Quantitative anchor off (cyclical magnitudes) | Claim 7: 2008-09 trough understated (~112k actual, framework "118-149k"); COVID April 2020 (161k actual, framework ~165k); 2021 annual peak (~274k actual, framework ~271k) | medium |
| Quantitative anchor off (episode peak) | Claim 12: NHPI 2021-22 peak (~12% actual, framework "9-10%+") | medium |
| Internal inconsistency in framework prose | Claim 8: line-232 says pre-2015 norm "0.30-0.40"; line-247 says "0.28-0.40" — pick one | low |
| Citation tag drift (wrong document tag, right number) | Claim 4: framework tags SAN 2025-21 numbers as "FSR 2025 quantification" | low |
| Date anchor unverified ("since 1977") | Claim 1: framework says "long-run average since 1977 ~194k SAAR" but project data starts in 1990 (where the mean is ~193k); the 1977 anchor cannot be verified within the project | low (probably accidentally coincident; worth fixing the date) |
| Recent 10-year average overstated | Claim 1: framework says ~245k; actual rolling 10-year is ~234-235k (the 245k figure matches calendar 2024 alone, not a 10-year window) | medium |
| Wording drift from source | Claim 5: "up to ~54%" vs SAN 2023-19's "+54% (median variable-rate fixed-payment holder)" | low |
| Indicator-naming-leak risk | Not present — all framework-named indicators (housing_starts, NHPI, CREA MLS HPI, residential_permits, INDINF_AFFORD_Q) are in `data/` | n/a |
| Rigid n×n decoder presented as canonical | Not present — Housing section uses thresholds, not a 2×2 / n×n decoder | n/a |
| Fabricated quote (text put in someone's mouth) | **None found.** All quoted material reproduces source text. The defects in this audit are misattributions and quantitative drift, not invented quotes. | n/a |
| US heuristic transferred to Canada | **None found.** All Canadian thresholds anchored to Canadian sources (StatsCan, BoC, CMHC, CREA). | n/a |

The two CRITICAL defects (Claim 2 wrong report, Claim 10 wrong methodology + wrong anchoring) are blocking items for a user-review pass before regenerating the Housing blurb. The "verified end-to-end (May 2026)" header in line 221 of the framework should be downgraded to "Tier 2 — autonomously verified, multiple defects pending review" until at least Claims 2 and 10 are corrected.

### Recommended top edits to framework prose

1. **Line 229 (Claim 2):** Replace "the 2023 CMHC Housing Shortages report estimated Canada needs ~430-500k starts/year through 2030 to close the 4.8M-unit affordability gap" with "the June 2025 CMHC report 'Solving the Affordability Crisis' estimated Canada needs 430,000-480,000 starts/year through 2035 to close the up-to-4.8M-unit affordability gap."

2. **Line 230 (Claim 10):** Replace "CREA MLS HPI is hedonic on all MLS transactions (resale-dominant) and is the index the BoC's own affordability indicator is anchored to" with "CREA MLS HPI is a hybrid repeat-sales / hedonic constant-quality index on MLS resale transactions. The BoC's affordability indicator uses a different series — a 6-month moving average of MLS average resale price — not the CREA HPI."

3. **Line 231 (Claim 3):** Replace "per CMHC's Spring 2026 analysis" with "per CMHC's April 17, 2026 Observer article 'Building permits are early indicators of housing market sentiment'."

4. **Lines 239, 241, 242 (Claim 7):** Update cyclical anchors to actual project-data values: 2008-09 trough ~112k (not 118k); COVID April 2020 = 161k (not 165k); 2021 annual peak 274k (not 271k).

5. **Line 243 (Claim 12):** Replace "9-10%+" with "peaked at ~12% in August 2021."

6. **Lines 232, 247 (Claim 8):** Reconcile the two pre-2015 norm ranges (0.30-0.40 vs 0.28-0.40); ideally use the data-anchored version "pre-2015 IQR was 0.30-0.33; the 0.40+ readings only fired briefly in late 2008."

7. **Line 239 (Claim 1):** Either source the "since 1977" anchor or replace with "since 1990 (project data start)"; update recent 10-year average from ~245k to ~234k.
