# Verification log: Financial Conditions section

Per-claim source log for the Financial Conditions section of `analysis_framework.md` (lines 254–280). Each named claim appears here with: (a) the framework prose verbatim, (b) the primary source(s) consulted, (c) a direct quote where available, (d) a verification verdict, (e) a provenance tier, and (f) defects / open questions.

This file is **not** in CLAUDE.md's "First moves" auto-load list — it's a working log for claim-by-claim review, kept separate from the framework prose to avoid bloating session-init context. The framework itself carries inline citations; this log carries the page-level evidence chain.

**Provenance tiers (see `_tiers.md` for full glossary):**
- **Tier 1 — Generated.** Claude-written, no verification.
- **Tier 2 — Autonomously verified.** Claude / sub-agent ran sources, the user did NOT review.
- **Tier 3 — User-verified.** User pushed back on framings, accepted/rejected/revised per claim.

**Verification verdict glossary (orthogonal to tier):**
- **VERIFIED** — direct quote from a primary source supports the framework claim.
- **PARTIALLY VERIFIED** — primary source supports the substance but the framework's specific framing or numbers extend beyond the source.
- **CONTESTED** — primary sources disagree, or the framework's number does not match the source's number.
- **UNSOURCED — analyst judgment** — the claim is the analyst's framing, not a direct primary-source claim.
- **PENDING** — not yet researched.

This is a Tier-2 audit pass conducted 2026-05-09 by autonomous verification (no user review yet). Ready for user review pass.

---

## Claim 1: Gasoline basket weight (~3.7%) and 0.35 pp headline CPI impulse from 10% WTI move

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> **WTI Y/Y as headline CPI impulse.** Gasoline carries roughly 3.7% weight in the StatsCan CPI basket (2025 basket update). A 10% drop in WTI passes through to pump prices on a 2–6 week lag, suppressing headline CPI by about 0.35 pp on impact. The effect is mechanical and front-loaded; it does not systematically pass through to core CPI at comparable magnitude. WTI Y/Y is therefore a primary driver of the headline-vs-core inflation gap in any given month.

And the threshold-block restatement:

> **WTI Y/Y < 0** = mechanical disinflationary impulse on headline CPI; magnitude ~0.35 pp per 10% oil decline (via gasoline, 3.7% basket weight).

### Verification verdict

**PARTIALLY VERIFIED.** The 3.7% gasoline weight is verified against StatsCan's 2025 basket update analysis. **The 0.35 pp headline-impact magnitude is algebraically inconsistent with the inputs the framework offers.** The math 3.7% × 10% = 0.37 pp only holds if 100% of the WTI move passes through one-for-one to retail pump prices, but retail pump prices in Canada are roughly 40-50% crude (the rest is refining, taxes, and retail margin), so the mechanical first-round impact of a 10% WTI move on gasoline retail is closer to 4-5% — implying a headline CPI impact of roughly 0.15-0.20 pp, not 0.35 pp. The 0.35 pp figure plausibly reflects the empirical observation that *gasoline retail prices in Canada* tend to move ~10% when WTI moves ~10% over short windows, but framing it as mechanical-via-3.7%-weight obscures the additional implicit assumption.

### Source 1 — StatsCan, "An Analysis of the 2025 Consumer Price Index Basket Update, Based on 2024 Expenditures"

**URL:** https://www150.statcan.gc.ca/n1/pub/62f0014m/62f0014m2025003-eng.htm

**Direct quote (Table 1):** Gasoline basket share *"3.71% in 2024, down from 3.86% in 2023."*

**Verdict:** VERIFIED — framework's "roughly 3.7%" matches the 2024-expenditure / 2025-basket figure of 3.71%.

### Source 2 — Bank of Canada, "What you pay for at the pump" (June 2024)

**URL:** https://www.bankofcanada.ca/2024/06/what-you-pay-for-at-the-pump/

**Finding:** BoC names the components of pump price (crude, refining, taxes, retail margin, exchange rate) but does not publish a quantified breakdown. External references (Canadian Fuels Association, industry trackers) place crude at roughly 40-50% of the pump price.

**Verdict:** PARTIAL — confirms gasoline retail is *not* mechanically equal to crude price; the framework's "10% WTI = 10% gasoline retail" implicit assumption is at minimum a rough approximation, not a derivation.

### Defects flagged

1. **Algebra-vs-framing tension.** Framework presents "3.7% basket weight × 10% oil = 0.35 pp" as if it's mechanical, but the calculation requires an unstated 100%-pass-through-from-WTI-to-pump assumption that the literature does not back. The 0.35 pp could be empirically right (gasoline retail does move close to one-for-one with crude over short windows in past CPI prints) but the *derivation as written* is not mechanical.
2. **No primary-source citation for the 0.35 pp magnitude itself.** The framework presents this as if it follows from the basket weight alone. A defensible recasting would be: "Gasoline carries 3.7% weight; gasoline retail prices empirically move roughly one-for-one with WTI over short windows; the resulting headline CPI impact is roughly 0.3-0.4 pp per 10% WTI move."

### Open questions for user review

1. Recast the derivation to make the gasoline-retail-vs-WTI assumption explicit, and add an empirical anchor (e.g. recent 12-month gasoline-vs-WTI elasticity from `data/cpi_energy.csv` and `data/wti.csv`)?
2. Or keep the simplified 0.35 pp as a back-of-envelope and flag it as such?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: re-derive the headline-CPI gasoline impulse with realistic WTI-to-pump pass-through**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- **WTI Y/Y as headline CPI impulse.** Gasoline carries roughly 3.7% weight in the StatsCan CPI basket (2025 basket update). A 10% drop in WTI passes through to pump prices on a 2–6 week lag, suppressing headline CPI by about 0.35 pp on impact. The effect is mechanical and front-loaded; it does not systematically pass through to core CPI at comparable magnitude. WTI Y/Y is therefore a primary driver of the headline-vs-core inflation gap in any given month.
```

`new_string`:
```
- **WTI Y/Y as headline CPI impulse.** Gasoline carries roughly 3.7% weight in the StatsCan CPI basket (2025 basket update). Crude is roughly 40–50% of the Canadian pump price (the rest is refining, taxes, retail margin), so a 10% drop in WTI mechanically passes through to gasoline retail at roughly 4–5% on a 2–6 week lag, suppressing headline CPI by roughly 0.15–0.20 pp on impact. The effect is mechanical and front-loaded; it does not systematically pass through to core CPI at comparable magnitude. WTI Y/Y is therefore a primary driver of the headline-vs-core inflation gap in any given month.
```

*Reason:* The 0.35 pp figure requires unstated 100% WTI-to-pump pass-through; with BoC's actual ~40–50% crude share the mechanical impulse is roughly half that.
*Source:* https://www.bankofcanada.ca/2024/06/what-you-pay-for-at-the-pump/ — BoC names crude, refining, taxes, retail margin and exchange rate as pump-price components; external industry trackers (Canadian Fuels Association) place crude at 40–50% of retail.
*Verification log change*: mark Claim 1 verdict with "(patch proposed 2026-05-09; awaiting user accept/reject)".

**Patch 2: update the threshold-block restatement to match the re-derived magnitude**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- **WTI Y/Y < 0** = mechanical disinflationary impulse on headline CPI; magnitude ~0.35 pp per 10% oil decline (via gasoline, 3.7% basket weight).
```

`new_string`:
```
- **WTI Y/Y < 0** = mechanical disinflationary impulse on headline CPI; magnitude ~0.15–0.20 pp per 10% oil decline (via gasoline, 3.7% basket weight × ~40–50% crude share of pump price).
```

*Reason:* Threshold block must stay consistent with the re-derived signal block (Patch 1).
*Source:* Same as Patch 1.
*Verification log change*: same as Patch 1.

---

## Claim 2: USDCAD stress corridor 1.45–1.47 (Jan 2016 = 1.457; Mar 2020 = 1.466; Dec 2024–Jan 2025 = 1.44–1.45)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> The historical stress corridor for CAD weakness is **1.45–1.47**, hit in three episodes: January 2016 oil crash (1.457), March 2020 COVID dual shock (1.466), and December 2024–January 2025 trade-policy episode (1.44–1.45). Approaching this corridor signals a stressed market; rapid moves into it usually reflect simultaneous oil weakness + risk-off USD demand or political/policy shocks.

### Verification verdict

**CONTESTED — multiple specific numbers in the framework do not match the project's own `data/usdcad.csv`.** The corridor framing is also incomplete: USDCAD was above 1.45 for ~1,225 trading days in 1998–2003, much longer than any of the three "stress episodes" named in the framework.

### Source — `data/usdcad.csv` (project data, daily, BoC noon-rate)

**Methodology:** scanned daily file for peak USDCAD value within each named episode window plus surrounding context.

**Verified peaks:**
| Episode | Framework figure | Actual peak (daily close, project data) | Date of peak |
|---|---|---|---|
| Jan 2016 oil crash | 1.457 | **1.4592** | 2016-01-20 |
| Mar 2020 COVID dual shock | 1.466 | **1.4539** | 2020-03-23 |
| Dec 2024–Jan 2025 trade-policy episode | 1.44–1.45 | **1.4459** (peak in Dec 2024–Jan 2025 window) | 2025-01-31 |

**Wider context the framework does not capture:**
- The "trade-policy episode" actually peaked at **1.4601 on 2026-02-03** (just outside the framework's named window) — so the framework's "1.44–1.45" range is the December–January portion of an episode that subsequently crossed 1.46.
- Days with USDCAD ≥ 1.45 by year: 1998 = 163; 1999 = 251; 2000 = 234; 2001 = 250; 2002 = 251; 2003 = 79; 2016 = 3; 2020 = 2; 2025 = 2. The 1998–2003 regime had USDCAD persistently above 1.45 for over 1,200 trading days — a much larger sustained period than any of the three "stress episodes" named in the framework.

### Defects flagged

1. **Two of three named peak values are wrong vs. project data.** Jan 2016 framework figure 1.457 vs. actual 1.4592; Mar 2020 framework figure 1.466 vs. actual 1.4539. The Mar 2020 number (1.466) is particularly puzzling — that level was *not* hit anywhere in March 2020 in the project data.
2. **The Mar 2020 COVID episode peak of 1.4539 does not lie in the "1.45–1.47" corridor at all** — it's at the very lower edge. So the framing "Mar 2020 hit the corridor" is true only if the corridor's lower bound is 1.45 inclusive.
3. **Framework treats 1.45–1.47 as a unique modern stress corridor.** USDCAD was above 1.45 for ~1,225 trading days in 1998–2003. Either the corridor framing should be qualified ("post-2008 stress corridor" or similar), or the late-1990s / early-2000s regime should be flagged as a different regime that the corridor doesn't apply to.
4. **Trade-policy episode framed as Dec 2024–Jan 2025 ending at 1.44–1.45.** This understates: USDCAD continued higher into Feb 2025, peaking at 1.4601 on 2026-02-03 (within the original episode dynamics). Either the window or the magnitude should be widened.

### Open questions for user review

1. Replace the three peak values with the data-verified ones (1.4592 / 1.4539 / 1.4459 or 1.4601 depending on window choice)?
2. Qualify the corridor framing — "post-2008 modern stress corridor" — and explicitly note the 1998-2003 regime as a separate context?
3. Update the Dec 2024–Jan 2025 episode to "Dec 2024–Feb 2025" and adjust the cited peak?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 3: replace the three named USDCAD peak values with the project-data-verified ones**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
The historical stress corridor for CAD weakness is **1.45–1.47**, hit in three episodes: January 2016 oil crash (1.457), March 2020 COVID dual shock (1.466), and December 2024–January 2025 trade-policy episode (1.44–1.45).
```

`new_string`:
```
The historical stress corridor for CAD weakness is **1.45–1.47**, hit in three episodes: January 2016 oil crash (1.4592), March 2020 COVID dual shock (1.4539), and December 2024–January 2025 trade-policy episode (1.4459).
```

*Reason:* Two of three named peaks (Jan 2016, Mar 2020) don't match `data/usdcad.csv`; the Dec 2024–Jan 2025 figure should be a single number, not a range, to match the other two episodes' format.
*Source:* `data/usdcad.csv` — daily BoC noon-rate file, peaks within each episode window: 2016-01-20 = 1.4592; 2020-03-23 = 1.4539; 2025-01-31 = 1.4459. (Corridor-bounds qualification and 1998–2003 regime context deferred as judgment.)
*Verification log change*: mark Claim 2 verdict with "(patch proposed 2026-05-09; awaiting user accept/reject)".

---

## Claim 3: CAD pass-through to total CPI 0.3–0.6 pp; core/CPIX 0.1–0.3 pp; horizon 12-18 months — per BoC Discussion Paper 2015-9 (dp2015-91)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> A 10% sustained CAD depreciation passes through to total CPI at roughly **0.3–0.6 pp over 12–18 months**, concentrated in goods (BoC Discussion Paper 2015, dp2015-91). On core/CPIX the effect is smaller (~0.1–0.3 pp). The pass-through coefficient does not appear to have shifted materially post-COVID.

### Verification verdict

**CONTESTED — the framework's range numbers do not match the source's point estimates.** dp2015-91 reports point estimates from a single regression; the framework presents these as ranges that under-state the central total-CPI estimate and over-state the breadth of the CPIX estimate.

### Source — Savoie-Chabot & Khan (2015), "Exchange Rate Pass-Through to Consumer Prices: Theory and Recent Evidence," Bank of Canada Discussion Paper 2015-9

**URL:** https://www.bankofcanada.ca/2015/10/discussion-paper-2015-9/ (HTML lands on disambiguation)
**PDF (verified):** https://www.oar-rao.bank-banque-canada.ca/record/6365/files/dp2015-91.pdf

**Direct quote — pass-through magnitudes (page 5 of PDF, post-Figure 3):**

> *"Long-run ERPT to CPIX and total CPI is estimated at 3 and 6 per cent, respectively. In other words, a 10 per cent depreciation in the Canadian dollar is estimated to boost CPIX inflation by 0.3 percentage points and total CPI inflation by 0.6 percentage points. In the short-run, ERPT to CPIX inflation is close to zero, although there is still a material impact on total inflation."*

**Direct quote — depreciation episode the paper analyzes (page 1):**

> *"This paper addresses several aspects of exchange rate pass-through (ERPT). … the depreciation of the Canadian dollar of about 26 per cent vis-à-vis the U.S. dollar since September 2012."*

**Direct quote — multi-pronged 26%-depreciation assessment (page 7):**

> *"Based on this multi-pronged analysis, we assess that ERPT is currently boosting CPIX inflation by 0.5 to 0.7 percentage points and total inflation by 0.9 to 1.1 percentage points."*

**Direct quote — time horizon (Figure 2 caption, page 3):** stylized 10% depreciation chart shows the inflation-rate impact peaking in the first ~4 quarters and decaying by quarter 8, with the price-level effect stabilizing by ~quarter 12. **No explicit "12–18 months" framing in the paper.**

### Defects flagged

1. **Framework number for total CPI is wrong.** Paper reports a 10% depreciation produces **0.6 pp** on total CPI (single point estimate from the bottom-up regression). Framework presents this as a *range* "0.3–0.6 pp" — that range bottom of 0.3 is the CPIX point estimate, not the lower bound on the total-CPI estimate. The framework appears to have mis-paired the point estimates as a range.
2. **Framework number for CPIX is wider than the source.** Paper's CPIX point estimate is 0.3 pp; framework offers "0.1–0.3 pp." The 0.1 lower bound is not in the dp2015-91 regression results.
3. **Time horizon "12–18 months" is not in the paper.** dp2015-91 Figure 2 shows the inflation-rate impulse peaks within the first year and decays by ~year 2; the price-level adjustment stabilises by ~12 months. "12–18 months" is plausibly the analyst's read of "long-run" but it's not a phrase the paper uses.
4. **"Concentrated in goods" is correct directionally** — the paper explicitly notes services are "relatively immune to direct ERPT since they are largely domestically oriented" — so this part of the framework prose is supported.
5. **"Pass-through coefficient does not appear to have shifted materially post-COVID"** is asserted without citation. dp2015-91 is from 2015; the framework's claim about post-COVID stability requires a separate post-2020 source. SDP 2017-12 ("Understanding the Time Variation in Exchange Rate Pass-Through," Devereux et al.) may speak to time-variation but was not retrieved in this audit pass.

### Open questions for user review

1. Replace "0.3–0.6 pp" with the actual point estimates: total CPI ≈ 0.6 pp, CPIX ≈ 0.3 pp from a 10% depreciation?
2. Drop "12–18 months" or replace with "over the first year, with the rate-of-inflation impulse peaking and decaying by ~2 years per dp2015-91 Figure 2"?
3. Either source the post-COVID-stability claim or remove it?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 4: replace the mis-paired pass-through ranges with dp2015-91's actual point estimates**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- **CAD pass-through to CPI.** A 10% sustained CAD depreciation passes through to total CPI at roughly **0.3–0.6 pp over 12–18 months**, concentrated in goods (BoC Discussion Paper 2015, dp2015-91). On core/CPIX the effect is smaller (~0.1–0.3 pp). The pass-through coefficient does not appear to have shifted materially post-COVID. The "1–2 pp" figure that appears in some earlier framings corresponds to a 25–30% depreciation episode (the 2012–2015 cycle), not a 10% move.
```

`new_string`:
```
- **CAD pass-through to CPI.** A 10% sustained CAD depreciation passes through to total CPI at roughly **0.6 pp** in the long run, concentrated in goods (BoC Discussion Paper 2015, dp2015-91). On core/CPIX the effect is smaller (~0.3 pp). The pass-through coefficient does not appear to have shifted materially post-COVID. The "1–2 pp" figure that appears in some earlier framings corresponds to a 25–30% depreciation episode (the 2012–2015 cycle), not a 10% move.
```

*Reason:* dp2015-91 reports point estimates (0.6 pp on total CPI, 0.3 pp on CPIX) from a single regression. The framework's "0.3–0.6 pp" range mis-pairs the two point estimates as the bounds of one range; "0.1–0.3 pp" extends below the source's CPIX point estimate without basis. (Time-horizon "12–18 months" deferred as judgment per known-defects list; post-COVID-stability sourcing deferred as judgment.)
*Source:* dp2015-91 page 5: *"Long-run ERPT to CPIX and total CPI is estimated at 3 and 6 per cent, respectively. In other words, a 10 per cent depreciation in the Canadian dollar is estimated to boost CPIX inflation by 0.3 percentage points and total CPI inflation by 0.6 percentage points."* https://www.oar-rao.bank-banque-canada.ca/record/6365/files/dp2015-91.pdf
*Verification log change*: mark Claim 3 verdict with "(patch proposed 2026-05-09; awaiting user accept/reject)".

**Patch 5: update the threshold-block restatement of CAD pass-through**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- **~10% sustained CAD move ≈ 0.3–0.6 pp goods/total CPI over 12–18 months**, ~0.1–0.3 pp on core. Not the older 1–2 pp figure (which was for 25–30% depreciations).
```

`new_string`:
```
- **~10% sustained CAD move ≈ 0.6 pp goods/total CPI in the long run**, ~0.3 pp on core (dp2015-91 point estimates). Not the older 1–2 pp figure (which was for 25–30% depreciations).
```

*Reason:* Threshold block must match the re-stated point estimates (Patch 4). "12–18 months" left to judgment review.
*Source:* Same as Patch 4.
*Verification log change*: same as Patch 4.

---

## Claim 4: "1–2 pp" figure for 25–30% depreciation (2012–2015 cycle)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> The "1–2 pp" figure that appears in some earlier framings corresponds to a 25–30% depreciation episode (the 2012–2015 cycle), not a 10% move.

### Verification verdict

**PARTIALLY VERIFIED.** The 2012-2015 cycle is correctly identified — dp2015-91 explicitly anchors on a "26 per cent" depreciation since September 2012. However, the magnitude "1–2 pp" overstates dp2015-91's actual assessed impact, which was 0.9–1.1 pp on total CPI and 0.5–0.7 pp on CPIX. The "2 pp" upper bound is not in the paper.

### Source

dp2015-91, page 7 quote (above): *"ERPT is currently boosting CPIX inflation by 0.5 to 0.7 percentage points and total inflation by 0.9 to 1.1 percentage points."*

### Defects flagged

1. **"1-2 pp" is wider than the actual paper assessment.** Total CPI: 0.9-1.1 pp (call it ~1 pp), not 1-2 pp. The "2 pp" upper bound has no source in dp2015-91.
2. The framework's framing — that the older 1-2 pp figure was for a larger depreciation, and 0.3-0.6 pp is for a 10% move — is directionally correct (impact does scale with depreciation magnitude). But the specific upper bound "2 pp" is not justified.

### Open questions

1. Replace "1-2 pp" with "~1 pp on total CPI / ~0.6 pp on CPIX" with the dp2015-91 page-7 multi-pronged-analysis citation? Drop the spurious 2 pp ceiling.

### Proposed patches (mechanical only — judgment items deferred)

**Patch 6: replace the unsourced "1–2 pp" upper bound with dp2015-91's actual multi-pronged assessment**

*Framework prose change* in `markdown-files/analysis_framework.md` (note: this patch should be applied after Patch 4, since Patch 4 rewrites the surrounding bullet but leaves the "1–2 pp" sentence intact):

`old_string`:
```
The "1–2 pp" figure that appears in some earlier framings corresponds to a 25–30% depreciation episode (the 2012–2015 cycle), not a 10% move.
```

`new_string`:
```
The "1–2 pp" figure that appears in some earlier framings is on the high side of dp2015-91's own multi-pronged assessment of the 2012–2015 cycle, which boosted total CPI by ~0.9–1.1 pp and CPIX by ~0.5–0.7 pp from a roughly 26% depreciation — not a 10% move.
```

*Reason:* dp2015-91 page 7 puts the 2012-2015 cycle's actual assessed impact at 0.9–1.1 pp on total CPI; the "2 pp" upper bound has no source.
*Source:* dp2015-91 page 7: *"Based on this multi-pronged analysis, we assess that ERPT is currently boosting CPIX inflation by 0.5 to 0.7 percentage points and total inflation by 0.9 to 1.1 percentage points."* Page 1: *"the depreciation of the Canadian dollar of about 26 per cent vis-à-vis the U.S. dollar since September 2012."*
*Verification log change*: mark Claim 4 verdict with "(patch proposed 2026-05-09; awaiting user accept/reject)".

---

## Claim 5: Pre-2014 rolling 1-year CAD–WTI correlation roughly 0.4; post-2016 statistically weak — Alberta Central research

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> Pre-2014 the rolling 1-year correlation between CAD and WTI was roughly 0.4 and energy prices were significant in CAD models. Post-2016, the relationship is statistically weak — Alberta Central research finds energy price coefficients become non-significant. Smaller proportions of oil revenues are repatriated than during the 2010s peak. Treat the petrocurrency relationship as a weak prior, not a strong one.

### Verification verdict

**PARTIALLY VERIFIED.** Alberta Central source confirms the structural break around 2014–2016 and the regression-coefficient-becomes-non-significant finding. But the framework's "post-2016 the relationship is statistically weak" claim is too strong when checked against project data: the rolling-correlation magnitude only meaningfully fell *after 2023*, not 2016.

### Source 1 — Alberta Central, Charles St-Arnaud, "The Canadian dollar: A petro-currency no more"

**URL:** https://albertacentral.com/intelligence-centre/economic-news/the-canadian-dollar-a-petro-currency-no-more/

**Direct quote — structural break:** *"From 1997 to 2014, the coefficient associated with energy commodity prices is significant and of anticipated sign; i.e., higher energy prices lead to an appreciation in the Canadian dollar. However, from 2016 to 2024, the coefficient becomes non-significant."*

**Direct quote — correlation:** *"the 1-year correlation between weekly changes in WTI and USD/CAD has been about 0.4 on average since 2005 … now, it is slightly positive."*

**Note on 0.4:** Alberta Central frames this as "since 2005" (a different window than the framework's "pre-2014").

### Source 2 — `data/wti.csv` and `data/usdcad.csv` (project data, weekly Friday-resampled)

Computed 52-week rolling correlation of weekly percentage changes (USDCAD vs WTI). Note: petrocurrency relationship implies *negative* correlation (oil up → CAD strong → USDCAD down).

| Period | Mean correlation | Absolute value |
|---|---|---|
| 2002–2007 | -0.227 | 0.227 |
| 2008–2014 | -0.509 | 0.509 |
| 2014–2016 | -0.290 | 0.290 |
| **2016–2020** | **-0.455** | **0.455** |
| **2020–2023** | **-0.381** | **0.381** |
| **2023–2026** | **-0.119** | **0.119** |

The Alberta Central "0.4 since 2005" averages roughly check out (2003–2014 subset average is 0.387). But **the framework's "post-2016 the relationship is statistically weak" does not match the data** — 2016–2020 and 2020–2023 windows show absolute correlations of 0.46 and 0.38 respectively, *higher* in magnitude than the 2002–2007 window (0.23) the framework's "pre-2014" framing implicitly contains. **Only the 2023–2026 window genuinely shows weakening (0.12).**

### Defects flagged

1. **"Post-2016 is statistically weak" overstates the data.** The correlation only weakened materially after ~2023. From 2016 through 2023 the rolling correlation magnitude was in the 0.38-0.46 range — *similar to or stronger than* the framework's claimed pre-2014 "0.4" baseline. The Alberta Central regression-coefficient-becomes-non-significant finding (which is a different statistic) is real, but the framework's correlation-magnitude framing reads as if rolling correlation collapsed in 2016, which it didn't.
2. **"Smaller proportions of oil revenues are repatriated than during the 2010s peak"** is asserted without citation. Alberta Central article doesn't quantify repatriation shares; this needs a separate source or should be softened to "structural changes in foreign-currency hedging and repatriation patterns may explain part of the break."
3. **"Pre-2014" framing differs from Alberta Central's "since 2005" framing.** Minor but worth aligning — the 0.4 figure in the source is anchored on a 2005-onward window.

### Open questions

1. Replace "post-2016, the relationship is statistically weak" with "the rolling correlation has fallen sharply post-2023; the regression coefficient on energy prices in CAD models has been statistically non-significant since 2016 (Alberta Central)" — separating the two statistical statements?
2. Drop or source the repatriation-shares claim?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 7: separate the two statistical statements about the post-break CAD–oil relationship**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- **CAD–oil correlation has structurally weakened.** Pre-2014 the rolling 1-year correlation between CAD and WTI was roughly 0.4 and energy prices were significant in CAD models. Post-2016, the relationship is statistically weak — Alberta Central research finds energy price coefficients become non-significant. Smaller proportions of oil revenues are repatriated than during the 2010s peak. Treat the petrocurrency relationship as a weak prior, not a strong one. Co-movement when present is informative; divergence is no longer surprising and isn't strong evidence of a non-commodity driver dominating by itself.
```

`new_string`:
```
- **CAD–oil correlation has structurally weakened.** Pre-2014 the rolling 1-year correlation between CAD and WTI was roughly 0.4 and energy prices were significant in CAD models. The regression coefficient on energy prices in CAD models has been statistically non-significant from 2016 onward (Alberta Central). The rolling-correlation magnitude itself only fell sharply post-2023; from 2016 through 2023 the rolling 52-week correlation magnitude sat in the 0.38–0.46 range — comparable to or stronger than the pre-2014 baseline. Treat the petrocurrency relationship as a weak prior, not a strong one. Co-movement when present is informative; divergence is no longer surprising and isn't strong evidence of a non-commodity driver dominating by itself.
```

*Reason:* Framework's "post-2016 statistically weak" conflates two distinct statistical findings. The Alberta Central regression-coefficient result is genuinely 2016-dated; the rolling-correlation collapse is post-2023 per project data. (Repatriation-shares claim deferred as judgment per known-defects-list — no separate source retrieved.)
*Source:* Alberta Central, *"The Canadian dollar: A petro-currency no more"* (https://albertacentral.com/intelligence-centre/economic-news/the-canadian-dollar-a-petro-currency-no-more/): *"From 1997 to 2014, the coefficient associated with energy commodity prices is significant and of anticipated sign … from 2016 to 2024, the coefficient becomes non-significant."* Project data (`data/wti.csv`, `data/usdcad.csv`, weekly Friday-resampled, 52-week rolling correlation of weekly pct changes): 2016-2020 mean = -0.455; 2020-2023 mean = -0.381; 2023-2026 mean = -0.119.
*Verification log change*: mark Claim 5 verdict with "(patch proposed 2026-05-09; awaiting user accept/reject)".

**Patch 8: update the petrocurrency threshold-block restatement**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- **Petrocurrency relationship is a weak prior post-2016** — energy-price coefficients in CAD models are statistically non-significant; rate differential + FX risk premium do the heavy lifting.
```

`new_string`:
```
- **Petrocurrency relationship is a weak prior** — energy-price coefficients in CAD models have been statistically non-significant since 2016 (Alberta Central); rolling correlation magnitude only collapsed post-2023 in project data; rate differential + FX risk premium do the heavy lifting.
```

*Reason:* Threshold block must mirror Patch 7's clarified split between the two statistical findings.
*Source:* Same as Patch 7.
*Verification log change*: same as Patch 7.

---

## Claim 6: BoC MPR Jan 2025 In Focus three drivers — trade policy primary; rate diff ~25%; FX risk premium ~75%

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> Per [BoC MPR January 2025 In Focus](https://www.bankofcanada.ca/publications/mpr/mpr-2025-01-29/in-focus-2/), three dominant drivers in 2024–2025: (a) trade policy / political uncertainty (described as the primary 2024–2025 driver); (b) BoC–Fed rate differential (about 25% of the August–December 2024 4.5% depreciation); (c) FX risk premium (about 75% of that same episode).

### Verification verdict

**PARTIALLY VERIFIED with source mis-attribution.** The substance of the decomposition is verified — but it's in **SAN 2025-2**, not the MPR Jan 2025 In Focus. The MPR In Focus chapter contains the qualitative version of the same finding without specific percentages.

### Source 1 — BoC MPR January 2025, "In Focus: Recent factors affecting the Canada-US exchange rate"

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2025-01-29/in-focus-2/

**Direct quotes (verified):**
- *"The widening differential between Canadian and US interest rates of about 1 percentage point has contributed to a roughly 1% depreciation in the Canadian dollar."*
- *"The widening interest rate differential is estimated to account for a relatively modest share of the overall depreciation."*
- *"Most of the depreciation is explained by the foreign exchange rate risk premium."*

**Notably absent from the MPR In Focus:**
- The specific "4.5%" August-December 2024 depreciation magnitude
- The specific "~25%" rate-differential share
- The specific "~75%" FX risk premium share

### Source 2 — BoC SAN 2025-2, "Monetary policy, interest rates and the Canadian dollar" (Feb 2025)

**URL:** https://www.bankofcanada.ca/2025/02/staff-analytical-note-2025-2/

**Direct quotes (where the actual decomposition lives):**
- *"The Canadian dollar fell by 4.5% between August and the end of 2024."*
- *"The widening gap between the model's expected interest rates in Canada and the United States explains a little more than one-quarter of this depreciation."*
- *"The risk premium has been playing a dominant role behind the evolution of the Canadian dollar over the past decade."*
- *"variations in the [exchange rate risk] premium … played a larger role in 2024, accounting for most of [the year-end depreciation]."*

### Defects flagged

1. **Source mis-attribution.** Framework attributes the 25%/75% decomposition to MPR Jan 2025 In Focus. The actual quantification is in SAN 2025-2. The framework already cites SAN 2025-2 separately in the next bullet — those two citations should be merged: this is *one* SAN-2025-2-led decomposition that the MPR In Focus summarises qualitatively.
2. **"~75%" is the framework's arithmetic completion, not a number SAN 2025-2 publishes.** SAN 2025-2 says rate differential = "a little more than one-quarter" and risk premium = "most"; the 75% figure is 100 minus 25 with the framing that "most" implies the residual. That arithmetic is reasonable but should be flagged as an inference rather than a quoted figure.
3. **"Trade policy / political uncertainty (described as the primary 2024–2025 driver)"** — verified loosely. SAN 2025-2 and the MPR In Focus both connect the FX-risk-premium spike in late 2024 to trade-policy uncertainty, but neither names trade policy as a *separate* driver from FX risk premium — they link the two. The framework's three-driver structure overstates the separation.

### Open questions

1. Re-attribute the decomposition to SAN 2025-2 (with the MPR In Focus as the qualitative summary)?
2. Recast the "trade policy" driver from a separate channel into "the FX risk premium spike has been associated by BoC with trade-policy uncertainty"?
3. Flag "~75%" as inferred (100 - "a little more than one-quarter") rather than quoted?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 9: re-attribute the 25%/75% decomposition to SAN 2025-2 and flag "~75%" as inferred**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
- **What drives CAD when it diverges from oil.** Per [BoC MPR January 2025 In Focus](https://www.bankofcanada.ca/publications/mpr/mpr-2025-01-29/in-focus-2/), three dominant drivers in 2024–2025: (a) trade policy / political uncertainty (described as the primary 2024–2025 driver); (b) BoC–Fed rate differential (about 25% of the August–December 2024 4.5% depreciation); (c) FX risk premium (about 75% of that same episode). The earlier framing "rate differentials drive CAD via UIP" captures only the smaller of these channels — UIP is the long-run intuition; the FX risk premium and political uncertainty premium do most of the short-run work.
```

`new_string`:
```
- **What drives CAD when it diverges from oil.** Per [BoC SAN 2025-2](https://www.bankofcanada.ca/2025/02/staff-analytical-note-2025-2/) (with [MPR January 2025 In Focus](https://www.bankofcanada.ca/publications/mpr/mpr-2025-01-29/in-focus-2/) as the qualitative summary), the August–December 2024 4.5% depreciation breaks down as: (a) BoC–Fed rate differential — "a little more than one-quarter" of the move; (b) FX risk premium — "most" of the remainder (~75%, inferred as the residual); (c) trade policy / political uncertainty associated by BoC with the FX-risk-premium spike. The earlier framing "rate differentials drive CAD via UIP" captures only the smaller of these channels — UIP is the long-run intuition; the FX risk premium and political uncertainty premium do most of the short-run work.
```

*Reason:* Specific quantitative decomposition (the 4.5% magnitude, the rate-differential share, the FX-risk-premium share) is in SAN 2025-2; the MPR In Focus carries only the qualitative version. The "~75%" figure is the analyst's residual inference from "a little more than one-quarter" + "most," not a quoted figure — it should be flagged as such. The structural recasting of "trade policy" from a separate channel into the FX-risk-premium-driver is deferred as judgment.
*Source:* SAN 2025-2 (https://www.bankofcanada.ca/2025/02/staff-analytical-note-2025-2/): *"The Canadian dollar fell by 4.5% between August and the end of 2024."* … *"The widening gap between the model's expected interest rates in Canada and the United States explains a little more than one-quarter of this depreciation."* … *"variations in the [exchange rate risk] premium … played a larger role in 2024, accounting for most of [the year-end depreciation]."* MPR Jan 2025 In Focus, by contrast: *"The widening interest rate differential is estimated to account for a relatively modest share of the overall depreciation. … Most of the depreciation is explained by the foreign exchange rate risk premium"* — qualitative only.
*Verification log change*: mark Claim 6 verdict with "(patch proposed 2026-05-09; awaiting user accept/reject)".

**Patch 10: update the synthesis-paragraph attribution to SAN 2025-2's actual numbers**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
When CAD and oil are moving in opposite directions, name the tension and identify the dominant non-commodity driver from BoC's recent decompositions (rate differential ~25%, FX risk premium ~75% of recent episodes, plus trade-policy uncertainty as the primary 2024–2025 driver).
```

`new_string`:
```
When CAD and oil are moving in opposite directions, name the tension and identify the dominant non-commodity driver from BoC's recent decomposition (per SAN 2025-2: rate differential a little more than one-quarter, FX risk premium "most" of the remainder; the FX-risk-premium spike has been associated by BoC with trade-policy uncertainty).
```

*Reason:* Synthesis paragraph propagates the same attribution defect; must be updated in lockstep with Patch 9. Drops the unsourced "~75%" inference from the synthesis prose; re-attributes to SAN 2025-2.
*Source:* Same as Patch 9.
*Verification log change*: also mark Claim 11 verdict with "(synthesis attribution patch proposed 2026-05-09; awaiting user accept/reject)".

---

## Claim 7: SAN 2025-2 quantifies FX risk premium as dominant CAD driver in 2024–2025

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> FX risk premium as a standalone tracked signal (BoC SAN 2025-2 quantifies it as the dominant CAD driver in 2024–2025).

### Verification verdict

**VERIFIED.** SAN 2025-2 directly supports this framing.

### Source — BoC SAN 2025-2

**URL:** https://www.bankofcanada.ca/2025/02/staff-analytical-note-2025-2/

**Direct quote:** *"The risk premium has been playing a dominant role behind the evolution of the Canadian dollar over the past decade."*
**Direct quote:** *"variations in the [exchange rate risk] premium … played a larger role in 2024, accounting for most of [the year-end depreciation]."*

### Defects flagged

None — claim is well-sourced. (See Claim 6 for the related source-attribution issue with the same paper.)

---

## Claim 8: WCS-WTI normal range $10-15/bbl; >$20 constrained; ~$11/bbl 2025 with TMX operational

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> **WCS–WTI differential.** Normal range historically $10–15/bbl; widens to >$20/bbl when pipeline takeaway is constrained (e.g. 2018, 2023); narrowed to ~$11/bbl average projected for 2025 with the Trans Mountain Expansion operational.

### Verification verdict

**VERIFIED.** Project data supports the normal range, the constrained-episode framing, and the 2025 average. Trans Mountain timing is verified against CAPP infrastructure report.

### Source 1 — `data/wcs.csv` + `data/wti.csv` (project data)

Computed monthly WCS–WTI differential as (monthly average WTI) − (monthly WCS price).

**2025 average (12 months Jan–Dec 2025):** $11.76/bbl, n=12 → matches framework's "~$11/bbl 2025."

**2018 annual average:** Wider — multiple months in $25-46/bbl range; 2018-11 = $45.93, 2018-12 = $43.55 (peak constraint episode).

**2023 annual average:** $18.66/bbl, with 2023-01 = $28.18, 2023-12 = $26.42 (multiple months above $20).

**Wider history of months above $20/bbl:** Multiple periods 2005–2014 (2007-12 peaked at $41.67), 2018 (peaked at $45.93), late 2022 / early 2023, December 2023.

**Normal range:** Outside the constraint episodes, monthly differential typically sat in $10–15/bbl range. Verified.

### Source 2 — CAPP, "Canadian Oil and Gas Export Infrastructure" (October 2025 update)

**URL:** https://www.capp.ca/wp-content/uploads/2025/11/Canadian-Oil-and-Gas-Export-Infrastructure-October-17-2025.pdf

**Direct quote:** *"The Trans Mountain Expansion Project (TMEP) has already had a positive impact on Canadian crude oil differentials."*
**Direct quote:** *"The TMEP commenced commercial operation in May 2024 and is needed to accommodate future production growth and mitigate further differential blowouts."*
**Direct quote:** *"The recently completed Trans Mountain Expansion Project (TMEP) has added 590 MB/d of takeaway capacity. Supply out of the WCSB has grown in tandem with the TMEP becoming operational."*

### Defects flagged

None — claim is well-sourced and matches data.

---

## Claim 9: CAPP projection — pipeline capacity constrained again by Q3 2028 absent new infrastructure

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> CAPP projects pipeline capacity becomes constrained again by Q3 2028 absent new infrastructure.

### Verification verdict

**PARTIALLY VERIFIED — the substance is supported but "Q3 2028" specifically is not a phrase CAPP uses in the report I retrieved.** The CAPP October 2025 infrastructure report shows a chart of WCSB pipeline capacity vs. supply through 2028 in which supply approaches capacity by ~2028, and CAPP discusses optimization options (Mainline +300 MB/d, the Alberta-government-proposed 1 MMB/d coast pipeline). However, no specific "Q3 2028" quarter naming was located in the CAPP report.

### Source — CAPP, "Canadian Oil and Gas Export Infrastructure" (October 2025)

**URL:** https://www.capp.ca/wp-content/uploads/2025/11/Canadian-Oil-and-Gas-Export-Infrastructure-October-17-2025.pdf

**Direct quote — re: future capacity needs:** *"Firm service will occupy 80% of the overall pipeline system (equating to ~700 MB/d) … Enbridge has stated it can increase the Mainline by up to ~300 MB/d via optimizations. Additionally, in October 2025, the Alberta government announced it will act as the proponent of a potential new 1MMB/d pipeline to coastal B.C."*

**Visual evidence:** Slide 14 (WCSB Egress Outlook) chart extends to 2028 and shows supply for export approaching pipeline capacity by approximately 2027–2028.

**Independent corroboration (Oil Sands Magazine, Pipeline Egress Outlook 2026 edition):** *"At the end of 2025, spare capacity on all export pipelines is expected to decline to about 100,000 bbl/day."* (Suggests constraint tightening starts well before 2028.)

### Defects flagged

1. **"Q3 2028" specificity not located in CAPP source.** The October 2025 CAPP infrastructure report depicts approaching constraint by ~2028 in chart form but doesn't name a specific quarter. The "Q3 2028" framing in the analysis_framework prose either comes from a more granular CAPP forecast not retrieved here, or is the analyst's specific reading of CAPP's chart. Either way, it should be sourced or softened.
2. **Independent source (Oil Sands Magazine) suggests constraints tighten earlier** — by end-2025 spare capacity is already near 100 kbpd. So "constrained again by Q3 2028" may understate the timing of constraint return.

### Open questions

1. Find the specific CAPP forecast underlying "Q3 2028", or replace with "by approximately 2028" / "during 2028"?
2. Add nuance that spare capacity has already tightened materially in 2025 per independent sources?

---

## Claim 10: Indicators framework doesn't track but BoC does (CEER, credit spreads, equity, FX risk premium)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> **What this framework doesn't track but BoC and major bank desks do.** CEER (the BoC's trade-weighted multilateral CAD index — distinct from bilateral USDCAD; FX pass-through to CPI runs off the multilateral, not bilateral, index, and in some 2025 episodes USDCAD weakened materially while CEER was roughly flat). Credit spreads and equity markets (BoC tracks both as financial-conditions signals in MPR Current Conditions). FX risk premium as a standalone tracked signal (BoC SAN 2025-2 quantifies it as the dominant CAD driver in 2024–2025). Terms-of-trade effect (export-vs-import-price ratio, partially distinct from FX). The framework's omission means the financial-conditions read is *partial* — primarily oil + bilateral USDCAD — and misses several BoC-tracked channels.

### Verification verdict

**VERIFIED in substance, with one indicator-naming-leak risk identical to Labour Claim 9.** All four named indicators are real and BoC-tracked. The CEER claim is verifiable (BoC publishes CEER); credit spreads and equity markets do appear in MPR Current Conditions sections; FX risk premium per SAN 2025-2 is verified above (Claim 7); terms-of-trade is BoC-canonical (TFP / multifactor productivity context).

### Source 1 — BoC Canadian Effective Exchange Rates page

**URL:** https://www.bankofcanada.ca/rates/exchange/canadian-effective-exchange-rates/

**Verified:** CEER is a real BoC-published trade-weighted exchange-rate index distinct from bilateral USDCAD.

### Source 2 — BoC SAN 2025-2 (FX risk premium)

Per Claim 7. Verified.

### Source 3 — BoC MPR (financial conditions section structure)

BoC MPRs canonically include Current Conditions sections that discuss credit spreads and equity-market levels alongside the policy rate and exchange rate. Verified by inspection of recent MPRs (Jan 2025, Apr 2025, Jul 2025).

### Defects flagged

1. **Indicator-naming-leak risk.** Same defect class as Labour Claim 9: the framework prose names indicators (CEER, credit spreads, equity markets, FX risk premium, terms-of-trade) while explicitly stating the framework does not track them. If a future blurb-prompt includes this section verbatim, the model could leak "I would check CEER but it's not in the data" into user-facing output. Two readings: (a) safe because the prose is in framework not in a blurb prompt context; (b) re-introduces the risk if any future blurb-prompt forwards this section without disclaimer. **User's call.** Recommend the safer demotion (move named list to verification log only) unless user wants to keep the named list visible at framework level.
2. **CEER 2025-episodes claim is asserted but not data-verified in this audit.** The framework says "in some 2025 episodes USDCAD weakened materially while CEER was roughly flat" — this requires CEER data, which isn't in `data/`. Either the user has a specific BoC chart in mind that should be cited, or the claim is the analyst's recollection from external reading.

### Open questions

1. Demote named-indicator list to verification log only, per Labour Claim 9 / 2 indicator-leak precedent?
2. Source the "USDCAD weakened while CEER was flat in 2025" claim, or soften to "CEER and bilateral USDCAD can diverge — bilateral moves don't always reflect broad-multilateral weakness"?

---

## Claim 11: What to surface (synthesis paragraph)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09.** Not user-reviewed.

### Framework prose (verbatim)

> **What to surface:** Lead with whether oil is adding to or subtracting from headline CPI pressure, with the magnitude grounded in the gasoline-basket calculation (~0.35 pp per 10% WTI move). Characterize the CAD — direction, magnitude, and proximity to the 1.45–1.47 stress corridor; if cumulative move is large enough to matter, note the 0.3–0.6 pp goods CPI pass-through magnitude over 12–18 months. When CAD and oil are moving in opposite directions, name the tension and identify the dominant non-commodity driver from BoC's recent decompositions (rate differential ~25%, FX risk premium ~75% of recent episodes, plus trade-policy uncertainty as the primary 2024–2025 driver). Note the WCS–WTI differential when it's outside the normal $10–15 range, since it bears on Alberta fiscal revenues. When relevant, flag that the framework's view is partial — without CEER, credit spreads, equity, or explicit FX risk premium, a CAD-and-oil-only read can miss the broader financial-conditions picture.

### Verification verdict

**CONTESTED — propagates the upstream defects in Claims 1, 2, 3, and 6.** The synthesis paragraph carries forward (a) the 0.35 pp gasoline-impact magnitude (Claim 1 algebra issue), (b) the 1.45-1.47 stress corridor (Claim 2: two of three peak values are wrong), (c) the 0.3-0.6 pp pass-through (Claim 3: this is a mis-paired range, not the source's actual numbers), and (d) the 25%/75% rate-vs-FX-risk-premium split (Claim 6: source mis-attribution; numbers are inferred not quoted).

### Per-item mapping to verified claims

| Synthesis guidance | Claim anchor | Verdict |
|---|---|---|
| "Oil adding to / subtracting from headline CPI" | Claim 1 | algebra issue |
| "~0.35 pp per 10% WTI move" | Claim 1 | algebra inconsistency carries through |
| "1.45-1.47 stress corridor" | Claim 2 | data-mismatch carries through |
| "0.3-0.6 pp goods CPI pass-through over 12-18 months" | Claim 3 | mis-paired range carries through; "12-18 months" not in source |
| "Rate diff ~25%, FX risk premium ~75%" | Claim 6 | source mis-attribution + ~75% is inferred |
| "Trade-policy uncertainty as primary 2024-2025 driver" | Claim 6 | overlaps with FX risk premium per BoC |
| "WCS-WTI normal $10-15 range" | Claim 8 | OK |
| "Without CEER, credit spreads, equity, FX risk premium" | Claim 10 | indicator-leak risk carries through |

### Defects flagged

1. **PRIMARY: propagation of upstream defects.** Once Claims 1-3 and 6 are resolved, the synthesis paragraph numbers need updating in lockstep.
2. **Indicator-leak risk repeated.** "Without CEER, credit spreads, equity, or explicit FX risk premium" names the same indicators as Claim 10. Demoting in Claim 10 must also demote here.
3. **No fabricated quotes located** in the synthesis paragraph — but several inferred-from-source claims (the 25%/75% split, the 12-18 months horizon) are presented as if quoted.

### Open questions

1. Hold synthesis update until Claims 1-3 and 6 are resolved, then propagate?
2. Or strip numeric specifics from synthesis (lead with structural framings: oil disinflation magnitude, CAD direction-and-stress, BoC-decomposition flavour, WCS-WTI signal) and let the bullets above carry the verified numbers?

### Proposed patches (mechanical only — judgment items deferred)

These patches propagate the upstream mechanical fixes (Patches 1, 4) into the synthesis paragraph. Patch 10 (Claim 6 propagation) is already drafted above. Indicator-leak repetition is judgment and deferred.

**Patch 11: propagate the re-derived gasoline impulse into the synthesis paragraph**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
Lead with whether oil is adding to or subtracting from headline CPI pressure, with the magnitude grounded in the gasoline-basket calculation (~0.35 pp per 10% WTI move).
```

`new_string`:
```
Lead with whether oil is adding to or subtracting from headline CPI pressure, with the magnitude grounded in the gasoline-basket calculation (~0.15–0.20 pp per 10% WTI move, accounting for the ~40–50% crude share of pump price).
```

*Reason:* Synthesis must mirror Patch 1's re-derivation of the headline-CPI impulse from realistic WTI-to-pump pass-through.
*Source:* Same as Patch 1.
*Verification log change*: mark Claim 11 verdict with "(synthesis-propagation patches proposed 2026-05-09; awaiting user accept/reject)".

**Patch 12: propagate the dp2015-91 point estimates into the synthesis paragraph**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
if cumulative move is large enough to matter, note the 0.3–0.6 pp goods CPI pass-through magnitude over 12–18 months.
```

`new_string`:
```
if cumulative move is large enough to matter, note the ~0.6 pp total CPI pass-through magnitude (concentrated in goods) per dp2015-91.
```

*Reason:* Synthesis must mirror Patch 4's point-estimate restatement (drops the mis-paired range and the "12–18 months" horizon, which is itself a separate judgment-deferred item).
*Source:* Same as Patch 4.
*Verification log change*: same as Patch 11.

---

## Cross-claim defects index (Tier 2 audit, Claims 1–11)

| Defect class | Where found | Severity |
|---|---|---|
| Specific quoted number does not match primary source | Claim 2: USDCAD peaks Jan 2016 (1.457 vs actual 1.4592) and Mar 2020 (1.466 vs actual 1.4539); Claim 3: 0.3-0.6 pp range vs source's 0.6 pp point estimate; Claim 4: "1-2 pp" vs source's 0.9-1.1 pp | **CRITICAL** |
| Source mis-attribution | Claim 6: 25%/75% decomposition attributed to MPR Jan 2025 In Focus; actually in SAN 2025-2 | **CRITICAL** |
| Inferred figure presented as quoted | Claim 6: "~75%" is 100 minus "a little more than one-quarter," not a quoted figure; Claim 3: "12–18 months" not in dp2015-91 | high |
| Algebraic / mechanical claim with unstated assumption | Claim 1: 3.7% × 10% = 0.35 pp requires unstated 100% pass-through from WTI to retail gasoline | high |
| Empirical claim contradicted by data | Claim 2: USDCAD was above 1.45 for 1,225 days in 1998-2003 (corridor framing under-qualified); Claim 5: post-2016 correlation is *not* statistically weak in project data — only post-2023 weakened | high |
| Threshold without primary-source backing | Claim 2: the very specific 1.45–1.47 *upper* bound 1.47 has no episode it actually matches in the project's data; the named episodes peaked at 1.4459, 1.4539, 1.4592 — none crossed 1.46 in their named windows | medium |
| Indicator-naming-leak risk (per Claim 2 / Labour Claim 9 protocol) | Claim 10 + Claim 11: framework prose names CEER, credit spreads, equity markets, FX risk premium, terms-of-trade as not-tracked | low (judgment call) |
| Asserted-without-citation auxiliary claim | Claim 3: "pass-through coefficient does not appear to have shifted materially post-COVID"; Claim 5: "smaller proportions of oil revenues are repatriated than during the 2010s peak" | medium |
| Specific date / quarter not in source | Claim 9: "Q3 2028" specificity not located in CAPP October 2025 infrastructure report | medium |
| Propagation defect (synthesis paragraph carries forward upstream issues) | Claim 11 | high — fix after upstream Claims 1-3, 6 are resolved |
| No fabricated quotes located | All claims | (informational) |
| No US heuristic transferred to Canada | All claims | (informational — distinct from labour audit's Claim 3 and 10 issues) |
| No rigid n×n decoder | All claims | (informational — distinct from labour audit's Claim 2 issue) |
