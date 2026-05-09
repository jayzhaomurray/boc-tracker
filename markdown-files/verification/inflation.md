# Verification log: Inflation section

Per-claim source log for the Inflation section of `analysis_framework.md` (lines 53–86). Each claim appears here with: (a) the framework prose verbatim, (b) the primary source(s) that back it, (c) a direct quote from the source where possible, (d) a verification verdict, (e) a provenance tier (see `_tiers.md`), and (f) defects flagged + open questions for user review.

This file is **not** in CLAUDE.md's "First moves" auto-load list — it's a working log for claim-by-claim review.

**Provenance tiers (see `_tiers.md` for full glossary):**
- **Tier 1 — Generated.** Claude-written, no verification.
- **Tier 2 — Autonomously verified.** Claude / sub-agent ran sources, the user did NOT review.
- **Tier 3 — User-verified.** User pushed back on framings, accepted/rejected/revised per claim.

**Verification verdict glossary (orthogonal to tier):**

- **VERIFIED** — direct quote from a primary source supports the framework claim.
- **PARTIALLY VERIFIED** — primary source supports the substance but the framework's specific framing or numbers extend beyond the source.
- **CONTESTED** — primary sources disagree, or the BoC's position differs from broader analyst consensus.
- **UNSOURCED — analyst judgment** — the claim is the analyst's framing, not a direct primary-source claim. Should be marked as such in framework prose if kept.
- **PENDING** — not yet researched.

**Audit-wide note.** This audit is performing the same kind of pass that surfaced fabricated quotes, US-transferred heuristics, and unsourced thresholds in the Labour section. The framework header at line 55 states *"VERIFICATION STATUS: verified end-to-end (May 2026). Analytical claims audited against primary sources / our own data; thresholds anchored to empirical distributions."* The Tier 1 framing in `_tiers.md` warns explicitly: *"Tier 2 is the most dangerous tier because it looks authoritative on the surface (sources cited, structured verdict glossary, primary-source URLs) but has not been challenged."* Treat the section's "verified end-to-end" header as a Tier 2 self-claim until this Tier 2 audit is reviewed by the user.

---

## Claim 1: 2% target and 1–3% control range

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim)

> 2% = BoC target
> 1–3% = BoC control range

### Verification verdict

**VERIFIED.** Both anchors are explicit BoC canon.

### Source 1 — BoC "Inflation" core-functions page

**URL:** https://www.bankofcanada.ca/core-functions/monetary-policy/inflation/

**Direct quote:** *"The Bank of Canada aims to keep inflation at the 2 per cent midpoint of an inflation-control target range of 1 to 3 per cent."*

**Verdict:** VERIFIED.

### Defects flagged

None.

### Open questions for user review

None.

---

## Claim 2: 0.17%/month neutral threshold (precisely 0.165%) — algebraic identity

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim)

> Is M/M momentum consistent with 2% annualized? ~0.17%/month is the neutral threshold (precisely 0.165%). Sustained prints above 0.3% signal acceleration; sustained prints below 0.1% signal deceleration.

> ~0.17%/month ≈ 2% annualized

### Verification verdict

**VERIFIED for the algebraic identity. Acceleration / deceleration thresholds (0.3% / 0.1%) are UNSOURCED — analyst synthesis.**

### Source 1 — Algebraic computation (independently verified 2026-05-09)

**Identity:** the geometric monthly rate that compounds to 2% annualized is `(1.02)^(1/12) - 1 = 0.001652 = 0.1652%/month`.

**Computation receipts:**
- Geometric: `(1 + 0.001652)^12 - 1 = 0.019982 ≈ 2.00%` ✓
- Linear approximation: `2/12 = 0.1667%/month`
- "0.17%" is the linear approximation rounded to 2 decimals; "0.165%" is the geometric exact value rounded to 3 decimals.

**Verdict:** VERIFIED. The math checks out. The framework's "(precisely 0.165%)" parenthetical is the geometric value; "~0.17%" is the rounded linear approximation. Both are correct expressions of the same identity.

### Source 2 — Acceleration / deceleration thresholds (0.3% above, 0.1% below)

**Search result:** No BoC primary source located stating that 0.3%/month is the acceleration threshold or 0.1%/month the deceleration threshold. The BoC discusses M/M momentum directionally in MPRs and opening statements but does not, to this auditor's review, publish bright-line monthly thresholds.

**Verdict:** UNSOURCED — analyst synthesis. The 2% identity is exact; the asymmetric 0.3 / 0.1 bands around it are not BoC-published. They are intuitive (0.3%/month ≈ 3.66% annualized = above the 1–3% control range top; 0.1%/month ≈ 1.21% annualized = below the control range midpoint), but the framework presents them without that derivation and without an analyst-judgment hedge.

### Defects flagged

1. **Defect type 3 (threshold without primary source).** The "above 0.3% = acceleration / below 0.1% = deceleration" bullet is the analyst's calibration, not a BoC convention. Should be hedged or annotated. Same defect class as Labour Claim 4's `ULC > 3%`.
2. **No fabricated quote.** Algebraic identity is independently verifiable.
3. **No US-transferred heuristic.** Math is universal.

### Open questions for user review

1. Hedge the 0.3% / 0.1% bands as analyst calibration, or anchor them to a BoC source. (E.g.: *"0.3%/month ≈ 3.7% annualized = above the BoC's 3% control-range ceiling"* — derives the threshold from Claim 1 rather than asserting it freestanding.)
2. The "(precisely 0.165%)" parenthetical is technically correct but lightly pedantic given that 0.17% is already a rounding choice. Keep, drop, or replace with the linear `2/12 = 0.1667%` explanation?

---

## Claim 3: Four-state CPI breadth classification (broad-based pressure / softening / clustered / polarized)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim)

> CPI breadth: classify the breadth signal into one of four states using the deviations from the 1996–2019 historical averages. Define `tilt = (above-3% share deviation) − (below-1% share deviation)`. The four states are:
> - **Broad-based pressure** — share above 3% elevated *and* share below 1% depressed (positive tilt). Many components running hot, few cold.
> - **Broad-based softening** — share above 3% depressed *and* share below 1% elevated (negative tilt). Many cold, few hot.
> - **Clustered near target** — both shares near their historical norms (small tilt, both deviations near zero). Most components in the 1–3% middle range.
> - **Polarized** — both shares elevated. Rare; some components hot *and* some cold simultaneously, with few in the middle.

### Verification verdict

**UNSOURCED — analyst synthesis.** The BoC publishes share-above-3% and share-below-1% as breadth indicators and discusses them descriptively, but no BoC publication located uses a four-state classification with these labels.

### Source 1 — BoC MPR October 2025, In Focus: "Assessing underlying inflation"

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2025-10-29/in-focus-1/

**Direct quotes (relevant breadth passages, full extraction):**
- *"The share of CPI components growing faster than 3% and the share growing below 1% suggest inflation of around 2% to 2½%"*
- *"The distribution of price changes stayed slightly skewed to the upside, which signals elevated inflation for several CPI components."*
- *"Underlying inflation is not a formula, nor can it be measured with precision. Rather, it is determined by assessing a collection of inflation indicators, including measures of core inflation and measures of the breadth of inflation, and by analyzing individual categories of the consumer price index (CPI)."*

**Verdict:** the BoC uses share-above-3% / share-below-1% as a *single descriptive assessment tool* — "assessing... breadth of inflation" — without categorical state labels. No four-state typology.

### Source 2 — Other BoC indicator pages

- **BoC Inflation page** (https://www.bankofcanada.ca/core-functions/monetary-policy/inflation/): describes core measures and the look-through approach; no four-state breadth typology.
- **BoC Key inflation indicators and the target range** (https://www.bankofcanada.ca/rates/indicators/key-variables/key-inflation-indicators-and-the-target-range/): same — defines core measures, does not classify breadth into states.
- **Web search** for `"Bank of Canada" CPI breadth "four states" OR "four categories" classification "broad-based"`: no relevant hits.

**Verdict:** the four-state typology is not BoC canon.

### Source 3 — Project-internal computation (`analyze.py`)

**File:** `C:\Users\jayzh\Documents\boc-tracker\analyze.py` lines 88–110.

**Finding:** the 1996–2019 historical-average baseline is computed internally on dashboard CPI-component data, then used to define `breadth_above3_dev`, `breadth_below1_dev`, and `breadth_tilt`. The state labels are framework prose; the numerical inputs are dashboard-computed.

**Verdict:** the empirical baseline is project-internal and reasonable. The four-state *labelling* on top of it is analyst synthesis — a useful organising scheme for blurb output, but not a BoC-published rule.

### Defects flagged

1. **Defect type 5 (rigid n×n decoder presented as canonical).** Same class as Labour Claim 2's original 2×2 utilization decoder. The four-state typology is presented declaratively ("**The four states are:**") with no analyst-synthesis hedge. The labels are intuitive but they are framework framings, not BoC publications.
2. **Defect type 3 (threshold-style framing without primary source).** "Tilt = above-3% deviation − below-1% deviation" is a derived statistic with no BoC anchor; it is an analyst-defined index. Whether this is a defect or a useful simplification depends on how the framework labels it.
3. **Combinatorial coverage check.** The four states cover four of the nine logical 3×3 combinations (above-3% deviation ∈ {depressed, near-norm, elevated} × below-1% deviation ∈ {depressed, near-norm, elevated}). The "polarized" state names {above elevated, below elevated}; "clustered" names {above near-norm, below near-norm}; "pressure" names {above elevated, below depressed}; "softening" names {above depressed, below elevated}. The remaining five configurations — e.g. {above near-norm, below elevated} (mild-cold tilt) or {above elevated, below near-norm} (mild-hot tilt) — have no named state. Same combinatorial-incompleteness issue Labour Claim 2 flagged for the 2×2 decoder. The "tilt" magnitude does some implicit work in distinguishing edges, but the prose still reads as if the four states partition the space.
4. **No fabricated quote.**
5. **No US-transferred heuristic** — uses Canadian historical data.

### Open questions for user review

1. Hedge the four-state typology as analyst synthesis (e.g. "The dashboard classifies the breadth signal into one of four analyst-defined states..."). Same fix Labour Claim 2 received.
2. Either (a) acknowledge the five unnamed configurations as falling on transitions between named states, or (b) replace with a continuous tilt-only framing where labels apply only beyond a tilt threshold.
3. The 1996–2019 reference period — is this the right window? Pre-1991-target era is excluded (good); post-2020 inflation surge is excluded (so deviations from this baseline read the post-2020 episode as elevated, which is the intended diagnostic). Worth confirming as deliberate.

---

## Claim 4: Tight band = all core measures within ~0.5pp of each other

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim)

> Is the band of core measures tight or wide? A tight band means the measures are telling a consistent story. A wide band means the choice of measure matters.

> Tight band = all core measures within ~0.5pp of each other

### Verification verdict

**UNSOURCED — analyst judgment.** The qualitative claim ("when measures cluster, the signal is consistent") is uncontroversial labour-economics-style reasoning. The specific 0.5pp threshold is not BoC-published.

### Source 1 — Targeted searches

- BoC Inflation page, Key inflation indicators page, MPR October 2025 In Focus on underlying inflation — none cite a 0.5pp cross-measure dispersion threshold for "tight" core-measure agreement.
- Web search for `Bank of Canada "core measures" "within" "percentage points" tight band` — no relevant hits.

### Source 2 — Loose precedent

The BoC describes the multi-measure approach in the Oct 2025 MPR In Focus: *"underlying inflation... is determined by assessing a collection of inflation indicators, including measures of core inflation."* This supports cross-measure triangulation but doesn't quantify a "tight" threshold.

### Defects flagged

1. **Defect type 3 (threshold without primary source).** The 0.5pp threshold is analyst calibration. Same class as Labour Claim 4's `ULC > 3%`.
2. **No fabricated quote.**
3. **No US heuristic transfer.**

### Open questions for user review

1. Hedge the 0.5pp threshold as analyst calibration, or anchor it. The threshold is reasonable for the post-2017 Canadian core-measure trio (CPI-trim, CPI-median, CPI-common) but is not BoC-published.
2. Note that the framework's `Data` line lists five core measures (cpi_trim, cpi_median, cpi_common, cpix, cpixfet) but the "preferred" trio per the BoC is just three. CPIX and CPIXFET are alternative measures, not in the BoC's preferred trio. The 0.5pp claim "all core measures" is more demanding when applied to all five.

---

## Claim 5: Headline-core gap > 0.3pp = look at food / energy / services for the driver

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim)

> Is headline CPI above or below core, and what is driving the gap? When headline diverges from core by more than ~0.3pp, look at food Y/Y and energy Y/Y to identify the driver. State the actual food and energy Y/Y numbers; do not guess at attribution. Goods Y/Y vs services Y/Y can also be informative if the gap is not in food or energy.

> Headline-core gap > 0.3pp = look at food/energy/services for the driver

### Verification verdict

**PARTIALLY VERIFIED.** The qualitative move (when headline ≠ core, decompose by food / energy / goods / services) is canonical BoC reasoning. The 0.3pp threshold for the gap is UNSOURCED.

### Source 1 — BoC Inflation page

**URL:** https://www.bankofcanada.ca/core-functions/monetary-policy/inflation/

**Direct quote:** *"The Bank seeks to look through such transitory movements in total CPI inflation and focusses on 'core' inflation measures that better reflect the underlying trend of inflation."*

**Verdict:** supports the qualitative principle (headline can deviate from core for transitory reasons; core is the underlying trend). Does not quantify a gap threshold.

### Source 2 — MPR October 2025 In Focus

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2025-10-29/in-focus-1/

**Relevant quote:** *"Measures of core inflation are typically used to filter out these types of volatile price changes and capture the more stable, underlying trend."*

**Verdict:** supports the food/energy decomposition reasoning at the qualitative level. No 0.3pp threshold.

### Source 3 — MPR July 2024 In Focus on core inflation drivers

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2024-07/in-focus-1/

**Verdict:** the BoC routinely decomposes core into goods vs. services in its MPR In Focus pieces. Supports the goods/services secondary-decomposition step. No 0.3pp threshold.

### Defects flagged

1. **Defect type 3 (threshold without primary source).** The 0.3pp gap threshold is analyst calibration. Same class as Labour Claim 4's `ULC > 3%` and the 0.5pp tight-band threshold above.
2. **The qualitative principle is well-grounded** — decomposing headline-core gaps into food / energy / goods / services is exactly the BoC's framing in Oct 2025 In Focus and July 2024 In Focus.
3. **No fabricated quote.**
4. **No US heuristic transfer.**

### Open questions for user review

1. Hedge the 0.3pp threshold as analyst calibration. Reasonable rule of thumb; not BoC canon.
2. The framework instruction *"State the actual food and energy Y/Y numbers; do not guess at attribution"* is a strong anti-hallucination instruction and is well-formed. No defect there.

---

## Claim 6: BoC CSCE consumer 1y / 5y framing — "5y is the long-run anchor and the more important one for assessing whether expectations have slipped"

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim)

> **Inflation expectations: are they anchored at 2%?** Consumer 1-year-ahead (CSCE) reflects near-term expectations; the 5-year-ahead measure is the long-run anchor and the more important one for assessing whether expectations have slipped.

### Verification verdict

**PARTIALLY VERIFIED.** The BoC describes long-term inflation expectations as "anchored" in monetary-policy communications, supporting the long-run anchor framing. The framework's stronger claim that the 5y is "the more important one" (relative to 1y) is analyst synthesis — defensible and consistent with central-bank-economics convention, but not a verbatim BoC ranking.

### Source 1 — CSCE Q1 2026 release

**URL:** https://www.bankofcanada.ca/2026/04/canadian-survey-of-consumer-expectations-first-quarter-of-2026/

**Direct quote (1y context):** *"Inflation expectations for these horizons have changed little over the past 12 months and are still above the survey's historical average."*

**Direct quote (5y context):** *"Long-term inflation expectations declined slightly from 12 months ago."*

**Verdict:** the BoC distinguishes the horizons in its quarterly write-ups. The word "anchor" does not appear in this Q1 2026 release.

### Source 2 — BoC SWP 2025-5, "Anchored Inflation Expectations: What Recent Data Reveal"

**URL (paper):** https://www.bankofcanada.ca/2025/01/staff-working-paper-2025-5/
**URL (PDF):** https://www.bankofcanada.ca/wp-content/uploads/2025/01/swp2025-5.pdf

**Verdict:** **paper title verified — direct text not retrieved.** WebFetch returned only the BoC abstract page metadata (paper title, authors, date) and not the body PDF text. The paper's existence and title support the framework's "anchored" framing semantically; the *specific* claim that the 5y is the BoC's preferred "long-run anchor" needs body-text verification before being elevated to Tier 3.

### Source 3 — BoC Expectations: Definitions, graphs and data

**URL:** https://www.bankofcanada.ca/rates/indicators/capacity-and-inflation-pressures/expectations/

**Sub-agent attempt:** WebFetch returned only navigation metadata; the page's substantive content (definition text, anchor framing) was not retrieved. Could not confirm whether this BoC definitions page describes the 5y as the long-run anchor.

**Verdict:** PENDING — primary source not text-extractable on this run.

### Source 4 — General BoC framing in monetary-policy communications

**Verbal content (web search synthesis 2026-05-09):** *"Longer-term inflation expectations remain anchored"* is a recurring BoC monetary-policy phrasing in MPRs and opening statements.

**Verdict:** supports the framework's "anchor" language at the general level. The framework's specific ranking (5y > 1y in importance for slippage diagnosis) is consistent with central-bank-economics convention but is analyst paraphrase, not verbatim BoC.

### Defects flagged

1. **No fabricated quote** — the framework does not put words in BoC's mouth on this point.
2. **Mild defect type 5 (analyst synthesis presented as canonical).** "The 5-year-ahead measure is the long-run anchor and the more important one" reads declaratively. The BoC's framing — "long-term inflation expectations remain anchored" — supports the spirit but does not explicitly rank 5y above 1y for slippage diagnosis.
3. **Source-text gap.** Two of the most relevant primary sources (BoC Expectations definitions page, SWP 2025-5 PDF body) were not text-extractable on this audit. Recommend a manual user pass on those before promoting this claim to Tier 3.
4. **No US heuristic transfer.**

### Open questions for user review

1. Soften the ranking ("the long-run anchor" → "a long-run anchor measure"; "the more important one" → "more diagnostic of anchor slippage")?
2. User to manually retrieve BoC Expectations definitions page text and SWP 2025-5 body to confirm the BoC's exact framing.
3. CSCE methodology note (per the BoC overview page): the CSCE is a quarterly rotating-panel survey of ~2,000 households, conducted Feb / May / Aug / Nov. The framework correctly says "quarterly" in the data line.

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: soften the 5y-vs-1y ranking from declarative to anchor-diagnostic framing**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
Consumer 1-year-ahead (CSCE) reflects near-term expectations; the 5-year-ahead measure is the long-run anchor and the more important one for assessing whether expectations have slipped.
```

`new_string`:
```
Consumer 1-year-ahead (CSCE) reflects near-term expectations; the 5-year-ahead measure is the long-run anchor measure and is more diagnostic of whether expectations have slipped.
```

*Reason:* The BoC's recurring monetary-policy phrasing — *"Longer-term inflation expectations remain anchored"* — and the title of SWP 2025-5 ("Anchored Inflation Expectations: What Recent Data Reveal") support the *"long-run anchor"* framing in spirit but do not explicitly rank the 5y above the 1y. The original wording *"the long-run anchor and the more important one"* asserts a definitive ranking the BoC does not publish; *"a long-run anchor measure"* + *"more diagnostic of"* preserves the analytical point without the overstatement.

*Source:* BoC Staff Working Paper 2025-5, *"Anchored Inflation Expectations: What Recent Data Reveal"* (https://www.bankofcanada.ca/2025/01/staff-working-paper-2025-5/) — paper title verifies the BoC's "anchored" framing. BoC monetary-policy communications recurringly use *"Longer-term inflation expectations remain anchored"* (web search synthesis 2026-05-09 across MPRs / opening statements). Neither source ranks 5y above 1y as "more important," so the patch removes the rank assertion while keeping the anchor framing.

*Verification log change* (in this file): mark verdict with "(patch proposed 2026-05-09; awaiting user accept/reject)".

---

## Claim 7: BOS ABOVE3 ~54% in late 2023 to ~11% in Q1 2026

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim)

> BOS ABOVE3 (% of firms expecting inflation > 3% over the next 2 years) is the business-side anchor diagnostic — went from ~54% in late 2023 to ~11% in Q1 2026, so this is currently a re-anchoring story. Material drift in the 5-year-ahead consumer measure or a sustained climb in BOS ABOVE3 would signal anchor slippage.

### Verification verdict

**VERIFIED.** Both endpoints check out against BoC primary data, and the wording "% of firms expecting inflation > 3% over the next 2 years" matches the BoC's exact survey-question wording.

### Source 1 — BoC Business Outlook Survey Data page

**URL:** https://www.bankofcanada.ca/publications/bos/business-outlook-survey-data/

**Direct quote (survey question wording):** *"Over the next two years, what do you expect the annual rate of inflation to be, based on the consumer price index?"*

**Direct data (Q1 2026 series tail):** *"Above 3 per cent (% of firms): 11"* (Q1 2026); 16 (Q4 2025); 23 (Q1 2025).

**Verdict:** Q1 2026 endpoint (11%) verified at primary source. The framework's "% of firms expecting inflation > 3% over the next 2 years" exactly matches the BoC's series label and survey-question wording.

### Source 2 — BoC Business Outlook Survey, Q4 2023

**URL:** https://www.bankofcanada.ca/2024/01/business-outlook-survey-fourth-quarter-of-2023/

**Sub-agent retrieval (web search synthesis 2026-05-09):** *"54% of firms expect inflation to remain above 3% for the next two years (compared to 53% in Q3)."* This was returned by web search referencing the Q4 2023 BoC release. WebFetch on the Q4 2023 release page itself did not surface the specific 54% figure in the rendered HTML — likely the figure lives in a chart annotation or footnote rather than body text. **The 54% figure is therefore VERIFIED via secondary aggregation of the BoC release, not via direct quote from the release HTML.**

**Verdict:** the late-2023 endpoint (54%) is consistent with the BoC's published Q4 2023 release per multiple secondary references; the user may want to confirm against the BoC Business Outlook Survey historical-data CSV (`https://www.bankofcanada.ca/publications/bos/business-outlook-survey-data/`'s downloadable dataset) for the exact Q4 2023 number.

### Source 3 — Project-internal data series

The dashboard fetches `infl_exp_above3` from BoC Valet (per the framework's Data line — "BOS: % of firms expecting inflation > 3% over next 2 years, quarterly"). This is the BoC's published series; the dashboard reads it directly. `analyze.py` uses `expectations_bos_above3` as `ie_above3.iloc[-1]`. Project-internal data corroborates the framework's directional claim.

### Defects flagged

1. **No fabricated quote.**
2. **No US heuristic transfer.**
3. **No threshold without primary source** — the figures are quoted directionally ("~54%", "~11%"), and both anchor at primary BoC data.
4. **Minor source-extraction gap.** The Q4 2023 endpoint was not surfaced verbatim from the BoC release HTML; the 54% figure was confirmed via web-search aggregation citing the same release. User may want to download the BoC BOS historical CSV and confirm the exact Q4 2023 value (likely 54 per the secondary references; possibly 53 if the framework conflated with Q3 2023).

### Open questions for user review

1. Confirm the late-2023 anchor against the BoC BOS historical CSV. Q4 2023 = 54 per web-search-aggregated reporting on the Q4 2023 release; Q3 2023 = 53. Framework says "~54% in late 2023" which is consistent with either Q3 or Q4 2023.
2. The framing "currently a re-anchoring story" is analyst inference but is reasonable given the trajectory (54 → 23 → 16 → 11 across Q4 2023 → Q1 2025 → Q4 2025 → Q1 2026). No defect.

---

## Claim 8: BoC's "own convention" of preferring core over headline

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim)

> Defer to core measures over headline as the more representative read on persistent inflation, since this is the BoC's own convention.

### Verification verdict

**VERIFIED.** The BoC describes the look-through-to-core approach as its operating practice in multiple primary sources. The framework's "BoC's own convention" wording is well-grounded.

### Source 1 — BoC Inflation page

**URL:** https://www.bankofcanada.ca/core-functions/monetary-policy/inflation/

**Direct quote:** *"In setting monetary policy, the Bank seeks to look through such transitory movements in total CPI inflation and focusses on 'core' inflation measures that better reflect the underlying trend of inflation."*

**Direct quote:** *"Since January 2017, the Bank's preferred core inflation measures are CPI-trim, CPI-median, and CPI-common."*

**Verdict:** VERIFIED — the BoC explicitly designates core measures as "preferred" and frames the look-through to core as policy practice.

### Source 2 — BoC CPI page

**URL:** https://www.bankofcanada.ca/rates/price-indexes/cpi/

**Verdict:** the page header is "Preferred measures of core inflation" — making the "preferred" framing a primary-source designation, not analyst gloss.

### Source 3 — MPR October 2025 In Focus on underlying inflation

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2025-10-29/in-focus-1/

**Direct quote:** *"Measures of core inflation are typically used to filter out these types of volatile price changes and capture the more stable, underlying trend."*

**Direct quote (multi-tool framing):** *"Underlying inflation is not a formula, nor can it be measured with precision. Rather, it is determined by assessing a collection of inflation indicators, including measures of core inflation and measures of the breadth of inflation, and by analyzing individual categories of the consumer price index (CPI)."*

**Verdict:** supports the substance. **Subtle nuance:** the BoC frames core measures as part of a *collection* of indicators used to assess underlying inflation, not as the single preferred read in isolation. The framework's *"Defer to core measures over headline as the more representative read on persistent inflation"* is consistent with this but slightly stronger than "core is one of several tools in a basket." Recommend the framework wording be read as "for the question of *underlying / persistent* trend, core is the BoC's first-line read" — which is what the BoC actually does — rather than "core is always the preferred number."

### Source 4 — Macklem, "The path to price stability" (Dec 2023) and adjacent speeches

**URL:** https://www.bankofcanada.ca/2023/12/path-price-stability/

**Verbal content (web search synthesis 2026-05-09):** Macklem repeatedly framed the policy stance around needing *"to see more easing in our measures of core inflation"* (Oct 2023 House Finance opening) and similar look-to-core language across 2023–2024 communications.

**Verdict:** supports the look-to-core convention as practical BoC policy framing.

### Defects flagged

1. **No fabricated quote.**
2. **No US heuristic transfer.**
3. **Minor framing nuance (not a defect):** the BoC frames core as part of a *collection* of underlying-inflation indicators (Oct 2025 In Focus), rather than as the single preferred read in isolation. The framework's "defer to core over headline as the more representative read on *persistent* inflation" wording is consistent with the BoC's framing — the qualifier "persistent" carries the work — but is one phrase away from over-claiming. No fix needed.

### Open questions for user review

None.

---

## Claim 9: M/M and 3M AR computed on SA series; Y/Y identical SA / NSA

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim)

> M/M and 3M AR are computed on the SA cpi_all_items series; Y/Y is identical between SA and NSA.

### Verification verdict

**VERIFIED in principle (algebraic / methodological).** The Y/Y identity is approximate, not exact, but is canonical statistical practice.

### Source 1 — Algebra

For a 12-month-period seasonal pattern, X12-ARIMA / SEATS seasonal adjustment factors recur on a 12-month cycle. The Y/Y log change `ln(P_t) − ln(P_{t-12})` cancels the seasonal factor when factors are stable — so SA Y/Y ≈ NSA Y/Y to a very close approximation. The two are not exactly identical (seasonal-adjustment programs allow factors to evolve; revision passes can shift them slightly), but for practical reporting the framework's "identical between SA and NSA" claim is the standard simplification.

**Verdict:** VERIFIED with the standard simplification. M/M and 3M AR computed on SA is correct (raw NSA M/M would be dominated by seasonal noise).

### Defects flagged

None.

### Open questions for user review

None.

---

## Claim 10: What to surface (synthesis paragraph)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim)

> **What to surface:** Open with a takeaway that synthesizes the picture (sentence 1). Anchor on headline CPI Y/Y (sentence 2), with core context if it changes the read. Bring in supporting evidence — breadth, M/M, 3M AR — in order of importance. When headline and core diverge, name the driver using the verified food or energy Y/Y figure rather than the framework's hypothetical "energy or food is masking" language. Defer to core measures over headline as the more representative read on persistent inflation, since this is the BoC's own convention.

> When citing breadth in the blurb, lead with the state name (*broad-based pressure*, *broad-based softening*, *clustered near target*, or *polarized*). The two-threshold comparison is for evaluating the signal internally; the blurb output uses the synthesis. When both threshold signals point the same way, cite one of them as evidence and drop the other — the second is redundant. When the two signals disagree (polarized state, or a transition where one has normalized but the other has not), cite both since they are telling different stories. Phrase the components as "running well above target" / "running well below target" rather than "above 3%" / "below 1%" — the precise threshold belongs on the chart, not in the prose.

### Verification verdict

**INTERNALLY CONSISTENT — propagates the unhedged Claim 3 four-state typology.** The synthesis is largely a stylistic / blurb-construction guide, well-formed, and the headline-then-core sequencing aligns with the BoC's framing in MPR opening statements (BoC opens on headline, then tracks core as the persistent-trend read). No fabricated quotes. The one carry-through defect: the four state labels (Claim 3) are repeated declaratively here, so any hedge applied to Claim 3 should propagate.

### Source 1 — BoC MPR opening statements (template comparison)

**URL examples:**
- https://www.bankofcanada.ca/2024/10/opening-statement-2024-10-23/
- https://www.bankofcanada.ca/2026/04/opening-statement-2026-04-29/

**Pattern:** the BoC typically opens with headline CPI, brings in core as the underlying-trend read, and decomposes by component when headline-core diverge. The framework's *"Anchor on headline CPI Y/Y... with core context if it changes the read"* matches this template.

**Verdict:** the synthesis structure is well-aligned with BoC convention.

### Defects flagged

1. **Carry-through from Claim 3.** The four state names are reused verbatim. If Claim 3 is hedged as analyst synthesis (recommended), the same hedge should propagate here.
2. **The "verification, not speculation" instruction** (*"name the driver using the verified food or energy Y/Y figure rather than the framework's hypothetical 'energy or food is masking' language"*) is a strong anti-hallucination instruction. Well-formed.
3. **No fabricated quote.**
4. **No US heuristic transfer.**
5. **No un-fetched indicators named** — every indicator referenced (breadth, M/M, 3M AR, food Y/Y, energy Y/Y, goods Y/Y, services Y/Y, core measures, BOS ABOVE3, CSCE 1y / 5y) is in the framework's Data line and is in the dashboard data block.

### Open questions for user review

1. After Claim 3 is hedged, propagate the same hedge here.

---

## Cross-claim defects index (Tier 2 audit, Inflation Claims 1–10)

| Defect class | Where found | Severity |
|---|---|---|
| Fabricated quote | None located in this section | none |
| US heuristic transferred to Canada | None located in this section | none |
| Threshold without primary source | Claim 2: 0.3%/month acceleration and 0.1%/month deceleration thresholds | medium |
| Threshold without primary source | Claim 4: 0.5pp tight-band threshold | medium |
| Threshold without primary source | Claim 5: 0.3pp headline-core gap threshold | medium |
| Rigid n×n decoder presented as canonical | Claim 3: four-state breadth typology (covers 4 of 9 logical configurations of the 3×3 deviation grid) | high |
| Analyst synthesis presented as canonical | Claim 6: "5y is the long-run anchor and the more important one" — BoC framing supports the spirit, not the specific ranking | low |
| Source-text gap (PENDING follow-up) | Claim 6: BoC Expectations definitions page and SWP 2025-5 PDF body not text-extracted on this run; framework's "anchor" framing is supported by BoC monetary-policy communications generally but not pinned to a specific definitional source | low — user to retrieve |
| Source-text gap (PENDING follow-up) | Claim 7: Q4 2023 BOS ABOVE3 = 54 figure surfaced via web-search aggregation of the BoC release rather than direct HTML-body quote; downloadable BoC CSV would close this gap | low — user to retrieve |
| Indicator-naming-leak risk | None — all indicators named in framework prose are in the data block | none |
| Number understatement | None located | none |

**Comparison to Labour audit:** the Inflation section is in materially better shape than the Labour section was at the equivalent Tier 2 stage. The most serious defects in Labour — fabricated quotes (Claims 1, 8) and a directly US-transferred heuristic (Claim 3 V/U > 1 = tight) — are absent here. The Inflation section's defects are concentrated in unsourced calibration thresholds (0.3%/month, 0.1%/month, 0.5pp, 0.3pp) and the four-state breadth typology presented as canonical. These are the Labour-audit "Defect type 3" (threshold without primary source) and "Defect type 5" (rigid decoder) classes — not "Defect type 1" (fabrication) or "Defect type 2" (US transfer).

**Top three priority items for the 2026-05-10 user-review pass:**
1. **Claim 3** — hedge or rework the four-state breadth typology. This is the highest-impact defect because the four state names propagate into Claim 10 and from there into blurb output.
2. **Claim 2** — anchor or hedge the 0.3% / 0.1% acceleration / deceleration thresholds. They can probably be derived from the 1–3% control range (0.3%/month ≈ 3.7% annualized = above the BoC ceiling) rather than asserted freestanding.
3. **Claims 4 & 5** — same treatment for the 0.5pp (tight band) and 0.3pp (headline-core gap) thresholds. Either anchor or hedge.

The framework's existing line-55 self-claim (*"VERIFICATION STATUS: verified end-to-end (May 2026). Analytical claims audited against primary sources / our own data; thresholds anchored to empirical distributions"*) overstates the current state. After this audit, the section should be downgraded to "Tier 2 — autonomously verified" until the user-review pass converts surviving claims to Tier 3. The Labour-audit precedent is to drop the unhedged "verified end-to-end" header and let the verification log carry the per-claim provenance.
