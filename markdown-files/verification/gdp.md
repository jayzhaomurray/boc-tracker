# Verification log: GDP & Activity section

Per-claim source log for the GDP & Activity section of `analysis_framework.md` (lines 156-184). Each claim in the framework should appear here with: (a) the framework prose verbatim, (b) the primary source(s) that back it, (c) a direct quote from the source where possible, (d) a verification verdict, (e) a provenance tier (see `_tiers.md`), and (f) any analyst notes.

This file is **not** in CLAUDE.md's "First moves" auto-load list — it's a working log for claim-by-claim review, kept separate from the framework prose to avoid bloating session-init context.

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

All entries below are Tier 2 (autonomously verified 2026-05-09; not user-reviewed) unless otherwise noted.

---

## Claim 1: Output gap -1.5% to -0.5% as of Q4 2025

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim, lines 168)

> Growth vs potential. The BoC's *operative* slack measure is the **output gap**, not a GDP growth threshold. As of Q4 2025 the BoC estimated the gap at -1.5% to -0.5% (well below potential), even as growth was positive.

### Verification verdict

**VERIFIED.** The Bank of Canada's January 2026 MPR explicitly publishes the Q4 2025 output gap range as -1.5% to -0.5%. The framework's claim is faithful.

### Source 1 — BoC Monetary Policy Report, January 2026 (Canadian conditions chapter)

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2026-01-28/canadian-conditions/

**Direct quote:** *"The current estimate of the output gap for the fourth quarter of 2025 is in the range of -1.5% to -0.5%."*

**Verdict:** VERIFIED — primary source matches the framework's range and quarter exactly.

### Source 2 — BoC Monetary Policy Report, April 2026 (Canadian conditions chapter)

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/canadian-conditions/

**Direct quote:** *"The output gap for the first quarter of 2026 is estimated to be in the range of -1.5% to -0.5%, unchanged from the January Report."*

**Verdict:** Cross-check — the same range was carried forward into Q1 2026, supporting the directional framing ("well below potential").

### Defects flagged

- **No fabricated quote.** Range matches verbatim.
- **No US-transferred heuristic.**
- **Minor sourcing note:** the framework cites the gap "as of Q4 2025" but doesn't name the MPR vintage (January 2026 MPR). Not a defect — acceptable shorthand — but adding the citation would tighten the prose.

### Open questions for user review

1. Should the framework explicitly cite "January 2026 MPR" as the source for the Q4 2025 estimate, given that the same range was carried into the April 2026 MPR for Q1 2026?

---

## Claim 2: Potential growth 1.2% (2026), 1.3% (2027) per April 2026 MPR Appendix

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim, lines 168, 175)

> Potential growth itself per April 2026 MPR Appendix: 1.2% (2026), 1.3% (2027) under BoC's central estimate

> Real GDP Y/Y around 1.2-1.5% ≈ running at potential (BoC April 2026 MPR central estimate: 1.2% 2026, 1.3% 2027

### Verification verdict

**VERIFIED.** The April 2026 MPR Appendix names both numbers verbatim.

### Source 1 — BoC Monetary Policy Report, April 2026 — Appendix on potential output and the nominal neutral rate

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2026-04-29/appendix/

**Direct quote:** *"Growth in potential output is expected to average 1.2% in 2026 before picking up modestly to 1.3% in 2027 and 1.5% in 2028."*

**Additional quote (TLP):** *"Growth in trend labour productivity averages about 1.4% over the projection horizon."*

**Verdict:** VERIFIED — both 2026 and 2027 numbers reproduce exactly.

### Defects flagged

- **No fabricated quote.**
- **Minor framing note:** the framework drops the 2028 figure (1.5%) which appears in the same sentence. Not a defect — abbreviation is acceptable — but including 2028 would give a fuller forward-look picture for blurb generation.

### Open questions for user review

1. Worth adding 2028 = 1.5% to the framework prose, since the appendix states it in the same sentence?

---

## Claim 3: SAN 2025-14 scenarios — 1.6%/yr (limited tariffs) vs 1.1%/yr (broad tariffs) 2025-2028

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim, lines 168, 175)

> SAN 2025-14 Scenario 1 (limited tariffs) averages 1.6%/yr 2025-2028, Scenario 2 (broad tariffs) 1.1%/yr.

> SAN 2025-14 scenarios bracket 1.1-1.6%/year

### Verification verdict

**VERIFIED.** Sub-agent verified both averages against the SAN 2025-14 page on the BoC site.

### Source 1 — BoC Staff Analytical Note 2025-14, "Potential output in Canada: 2025 assessment" (June 2025)

**URL:** https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-14/

**Verified facts (retrieved 2026-05-09):**
- Scenario 1 (limited tariffs) average annual potential output growth 2025-2028: **1.6%**
- Scenario 2 (broad tariffs) average annual potential output growth 2025-2028: **1.1%**
- Scenario 1 2026 potential output: 1.3%; 2027: 1.4%
- Scenario 2 2026 potential output: 0.4%; 2027: 1.0%
- Scenario 1 2026 TLP: 1.2%; 2027: 1.2%
- Scenario 2 2026 TLP: 0.2%; 2027: 0.8%

**Scenario 1 characterization (verbatim from page):** *"elevated trade policy uncertainty that starts to fade at the end of 2026"* and *"limited US tariffs of 25% on Canadian steel and aluminum exports and the associated 25% on $29.8 billion of Canadian imports of US goods"*

**Scenario 2 builds on Scenario 1:** *"25% US tariffs on Canadian and Mexican motor vehicles and parts"* plus *"12% US tariffs on all other goods imported from Canada and Mexico"*

**Verdict:** VERIFIED for both averages. Note: SAN 2025-14 was published in June 2025, so the April 2026 MPR Appendix supersedes it as the BoC's most current central potential-output view. Both should not be presented as parallel "current" numbers — the MPR is the more recent vintage.

### Defects flagged

- **Minor freshness note:** April 2026 MPR is the more recent vintage. Framework cites both alongside each other, which is fine for showing scenario range, but a session reading the framework should know which is the current central case.
- **No fabricated quote.**
- **No US-transferred heuristic.**

### Open questions for user review

1. Should the framework explicitly note SAN 2025-14 (June 2025) is the older vintage now superseded by April 2026 MPR for the central case? Or is the parallel framing useful for showing the scenario uncertainty range?

---

## Claim 4: C.D. Howe Business Cycle Council methodology — "depth, duration, breadth"; declared no recession in 2022-2023

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim, line 178)

> Recession framing: Canada's authoritative recession-dating body is the **C.D. Howe Institute Business Cycle Council**, NOT a "two consecutive negative quarters" rule. Council methodology requires a "pronounced, pervasive, and persistent decline" assessed on **depth, duration, and breadth** (across sectors and indicators including employment). The Council declared no recession in 2022-2023 despite weak quarters because depth/breadth criteria were not met. A single severe broad-based quarter can qualify; a shallow prolonged contraction may not. Reference C.D. Howe BCC methodology rather than the two-negative-quarters shorthand.

### Verification verdict

**PARTIALLY VERIFIED — with substantive terminology defect.** The substance (BCC is the Canadian recession-dating body; rejected 2022-2023 recession; uses three dimensions; explicitly considers breadth across industries and employment) is fully supported by C.D. Howe primary sources. **However, the framework's explicit naming of the three criteria as "depth, duration, and breadth" is NOT the BCC's actual terminology — the canonical wording is "amplitude, duration, and scope."** "Depth" and "breadth" are reasonable synonyms but the framework presents them as a direct quotation of the BCC's methodology. The "pronounced, pervasive, and persistent" phrase has the right three words but the wrong order (BCC says "pronounced, persistent, and pervasive").

### Source 1 — C.D. Howe Business Cycle Council Methodology page

**URL:** https://cdhowe.org/publication/business-cycle-council-methodology/

**Direct quotes (retrieved 2026-05-09):**
- *"to identify a recession three dimensions need to be considered simultaneously: amplitude, duration, and scope"*
- *"a 0.1 percent quarterly decline in aggregate economic activity is a necessary but not sufficient condition"* (amplitude criterion)
- *"a decline in aggregate economic activity lasting at least one quarter is a necessary minimum"* (duration criterion)
- *"how widespread a downturn is"* (scope criterion, measured via diffusion indices)
- The Council *"does not follow hard-and-fast rules on these dimensions"*
- On the two-negatives shorthand: the Council does not endorse the rule; their flexibility allows for weakness in contiguous quarters *"but not necessarily by outright decline."* This implicitly rejects the strict two-negatives rule but does NOT explicitly state "we reject the two-consecutive-negative-quarters rule" anywhere I could locate.

**Verdict:** The methodology canonically names the three dimensions as **amplitude, duration, and scope** — not "depth, duration, and breadth." The substantive claim (three dimensions, qualitative judgment, explicit consideration of breadth/scope across industries) is correct.

### Source 2 — "So Far, So Good" Communiqué (March 2024) — declared no recession in 2022-2023

**URL:** https://cdhowe.org/publication/so-far-so-good-cd-howe-institute-business-cycle-council-declares-recession/

**Direct quotes:**
- *"The latest available data show that the Canadian economy did not fulfil these conditions in 2022 or 2023."*
- The negative quarters were *"not persistent enough to be called recessions"*; they were *"bracketed by quarters of growth"* and showed *"positive"* cumulative growth over two-quarter periods.
- GDP declines were *"mild at 0.1 percent for each quarter"*, failing the magnitude test.
- One diffusion index *"dropped just below 50, to 48.9, in the fourth quarter of 2022"*, but employment *"increased in both quarters"* of contraction — the breadth criterion was not satisfied.
- Framework summary phrase from the communiqué: declines must be *"pronounced, persistent and pervasive"* — note the BCC's order is **persistent before pervasive**, framework prose has them in reverse order.

**Verdict:** VERIFIED — supports the "Council declared no recession in 2022-2023" claim. Confirms the *"pronounced, persistent, and pervasive"* canonical phrase (with "persistent" before "pervasive").

### Source 3 — Business Cycle Council main page

**URL:** https://cdhowe.org/council/business-cycle-council/

**Confirms:** The methodology was updated *"to reflect the importance of the breadth of a downturn"* (December 2019, sixth report). This is the only place "breadth" appears as the BCC's own word; "scope" remains the canonical methodology-document term.

### Defects flagged

1. **Defect type 5 (analyst synthesis presented as canonical wording).** The framework names the three criteria as **"depth, duration, and breadth."** The BCC's canonical wording is **"amplitude, duration, and scope."** "Breadth" appears in BCC communiqués as a concept but "scope" is the methodology term. "Depth" never appears in the methodology — "amplitude" is the BCC's word. This is presented in framework prose as if it were a direct citation of BCC methodology when it is, at minimum, a paraphrase.
2. **Word-order issue.** Framework reads *"pronounced, pervasive, and persistent decline"*. The BCC's canonical phrase is *"pronounced, persistent, and pervasive."* If the prose presents the phrase in quotation marks (and it does — the framework wraps the phrase in literal quotes), the word order should match.
3. **The "two consecutive negative quarters rule explicitly rejected" claim.** The BCC does not explicitly reject the two-negatives rule in its publicly available methodology page. They reject the *application* of a strict mechanical rule by emphasising flexibility ("not necessarily by outright decline"). The framework's phrasing — that the BCC is "NOT a 'two consecutive negative quarters' rule" — is true in the sense that the BCC doesn't use such a rule, but framing it as an "explicit rejection" overstates the BCC's posture.
4. **The "depth/breadth criteria were not met" gloss for 2022-2023.** Per the communiqué, what wasn't met was actually persistence (declines bracketed by growth) AND breadth (employment grew through both contracting quarters) — but the magnitude was at the edge (0.1%). The framework says "depth/breadth criteria were not met"; cleaner would be "persistence and breadth criteria were not met." Minor mis-summary.
5. **No fabricated quote.** "Pronounced, pervasive, and persistent" appears in BCC publications; the issue is word-order consistency.
6. **No US-transferred heuristic** — the framework appropriately distinguishes BCC from NBER (NBER is implied but not named in this section).

### Open questions for user review

1. Replace the "depth, duration, and breadth" phrasing with the canonical **"amplitude, duration, and scope"** (the BCC's own methodology document terms)?
2. Fix the word order: *"pronounced, persistent, and pervasive"* (BCC canonical) instead of *"pronounced, pervasive, and persistent."*
3. Soften the "two-consecutive-quarters rule explicitly rejected" framing to "the BCC does not use a mechanical two-consecutive-quarters rule" — accurate without overclaiming an explicit rejection?
4. Update the 2022-2023 explanatory gloss from "depth/breadth criteria not met" to "persistence and breadth criteria not met (declines were 0.1% per quarter, bracketed by growth, employment grew through both)."

---

## Claim 5: 2008-09 housing trough ~118-149k annualized; COVID April 2020 monthly SAAR ~165k

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09 against project data. Not user-reviewed.**

### Framework prose (verbatim, line 241 — note: this is the Housing-section bullet inside the audit scope as a cross-reference)

> Housing starts < 180k SAAR = recessionary territory. 2008-09 recession bottomed at ~118-149k annualized; COVID April 2020 monthly SAAR was ~165k. Below 180k signals acute construction contraction.

### Verification verdict

**PARTIALLY VERIFIED — both numbers are slightly off project-data ground truth.** The 2008-09 trough actually went lower than 118k, and the COVID April 2020 figure is closer to 161k than 165k.

### Source 1 — Project data: `data/housing_starts.csv`

**Verified facts (computed 2026-05-09 from the project's own CSV):**

| Period | Reported value (SAAR, thousands) |
|---|---|
| 2008-12 | 150.305 |
| 2009-01 | 132.314 |
| 2009-02 | 115.722 |
| 2009-03 | 141.138 |
| **2009-04 (trough)** | **111.781** |
| 2009-05 | 127.857 |
| 2009-06 | 142.729 |
| 2009-07 | 137.567 |
| 2008-09 trough range (low–high during the worst 6-7 months) | ~112k–~149k |
| 2020-04 (COVID trough) | **161.004** |
| 2020-05 | 192.551 |
| 2020-06 | 213.167 |

**Verdict:** PARTIALLY VERIFIED.
- The framework's "118-149k" lower bound understates the actual 2008-09 trough; April 2009 hit 111.781k, which rounds to ~112k. The 118k floor in framework prose may have come from a 3-month average or a different vintage. The high end (~149k) is consistent with the broader 2008-12-through-2009-07 envelope.
- The framework's "~165k" for COVID April 2020 is off; the project's own CSV has 161.004k, which rounds to ~161k. The 165k figure may come from a different vintage (CMHC has revised housing starts series over time) or be a rounding-up to the nearest 5k. Either way, it doesn't match the data the dashboard ships with.

### Defects flagged

1. **Defect type 3 (numerical anchor doesn't match project data).** "118-149k" lower bound and "~165k" COVID figure don't match the project's CSV. Recommend updating to either:
   - Tighter: "~112-150k" 2008-09 trough range; "~161k" COVID April 2020.
   - Or generalize: "~110-150k" / "~160-165k" (acknowledging vintage uncertainty).
2. **No fabricated quote.**
3. **No US-transferred heuristic.**

### Open questions for user review

1. Update the framework's housing-trough numbers to match the project's CSV exactly, or tolerate ~5k of rounding for narrative simplicity?
2. Should the framework note these are the project's CSV-vintage numbers (CMHC has historical revisions), or treat them as authoritative?

---

## Claim 6: Inventories swing > ±3 pp threshold

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim, lines 169, 179)

> The residual is typically small (~0.05pp non-AR; well within rounding); a sustained large residual signals StatsCan revised something meaningful. Which component is contributing most, which is dragging? Common patterns: ... inventory-driven (often noise; recent swings have been -4.2pp), ...

> Inventories swing > ±3 pp = likely a distortion of the underlying demand signal (Q4 2025 was -4.2pp; ±2pp is too tight given recent volatility). When inventories dominate, focus on **final domestic demand** as the cleaner read.

### Verification verdict

**UNSOURCED — analyst judgment.** The "±3 pp" threshold is not from a BoC, StatsCan, or other primary source. It's analyst calibration based on observed Canadian volatility — which is reasonable, but the framework should flag it as such.

### Source 1 — Project data: `data/gdp_contrib_inventories.csv`

**Verified Q4 2025 value:** Last row reads `2025-10-01,-4.238`. Framework's "-4.2pp" is correct (rounding).

**Recent inventory contribution swings (2024Q1 onward):**

| Quarter | Inventory contribution (pp, AR) |
|---|---|
| 2024-Q1 | +0.255 |
| 2024-Q2 | +1.211 |
| 2024-Q3 | -0.397 |
| 2024-Q4 | -3.99 |
| 2025-Q1 | +1.915 |
| 2025-Q2 | +4.145 |
| 2025-Q3 | -2.123 |
| **2025-Q4** | **-4.238** |

The recent envelope spans roughly ±4pp, supporting the framework's claim that "±2pp is too tight given recent volatility."

**Verdict:** The Q4 2025 -4.2pp number is correct. The "±3pp threshold" is analyst calibration informed by recent observed swings, not a primary-source threshold.

### Source 2 — Searched for BoC / StatsCan threshold guidance

No BoC or StatsCan publication located that names ±3pp (or any numerical pp threshold) as the cutoff for "inventory-driven distortion." The standard analytical move (separate inventories from final domestic demand) is canonical, but the specific ±3pp band is the dashboard's own calibration.

### Defects flagged

1. **Defect type 3 (unsourced threshold).** "±3 pp" is not in any BoC publication. It's the analyst's empirical calibration based on recent Canadian quarterly observations (envelope ~±4pp in 2024-2025). Framework should either:
   - Mark it explicitly as analyst calibration: *"±3pp (dashboard calibration based on recent observed envelope; not a BoC-published threshold)"*
   - Or rephrase to remove the appearance of a primary-source number.
2. **No fabricated quote.**
3. **No US-transferred heuristic** — the threshold is calibrated to Canadian data.

### Open questions for user review

1. Mark "±3pp" explicitly as analyst calibration in the framework prose?
2. Is the threshold band still useful as a soft rule of thumb, or should it be replaced with a rolling-stdev-based dynamic threshold?

---

## Claim 7: BoC's mandate is price stability, not growth management

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim, line 182)

> Connect to monetary policy carefully: **the BoC's mandate is price stability, not growth management** — restrictive policy aims to bring inflation back to the 2% target, with slower growth as the transmission effect, not the objective.

### Verification verdict

**VERIFIED with caveat.** The BoC's primary monetary policy framework is the inflation-control target. **However, the 2021 Renewal of the framework added a supporting objective for "maximum sustainable employment"** that the framework prose elides. The "price stability, not growth management" framing is essentially correct but slightly more absolute than the BoC's actual posture since 2021.

### Source 1 — BoC Core Functions: Monetary Policy

**URL:** https://www.bankofcanada.ca/core-functions/monetary-policy/

**Direct quotes:**
- *"The goal of Canada's monetary policy is to promote the economic and financial well-being of Canadians. Experience shows the best way to achieve this goal is by keeping inflation low and stable."*
- *"At the heart of Canada's monetary policy framework is the inflation-control target, which is the 2% midpoint of the 1%–3% control range."*
- *"Predictable inflation allows Canadians to make spending and investment decisions with confidence, encourages longer-term investment in Canada's economy, and contributes to sustained job creation and greater productivity."*

### Source 2 — 2021 Framework Renewal (cited via Core Functions page)

**Finding:** The 2021 framework renewal added a supporting objective: monetary policy should *"continue to support maximum sustainable employment."* This remains secondary to the primary goal of stable, low inflation.

### Defects flagged

1. **Minor framing risk:** "Mandate is price stability, not growth management" is mostly right, but since 2021 the BoC has an explicit secondary employment objective. The framework's hard-line dichotomy ("price stability, NOT growth management") loses this nuance. A more accurate framing: *"primary mandate is price stability via the 2% inflation target; the 2021 renewal added a supporting maximum-sustainable-employment objective; growth management per se is not the goal — slower growth is the transmission channel for restrictive policy, not the objective."*
2. **No fabricated quote.**
3. **No US-transferred heuristic.**

### Open questions for user review

1. Soften "price stability, not growth management" to acknowledge the 2021 maximum-sustainable-employment supporting objective?

---

## Claim 8: Final domestic demand convention — consumption + government + GFCF; excludes inventories and net trade

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim, line 170)

> Final domestic demand = consumption + government consumption + gross fixed capital formation; inventories and net trade are excluded by definition (StatsCan / BoC convention).

### Verification verdict

**VERIFIED.** StatsCan defines final domestic demand exactly this way; the inventories and net-trade exclusions are explicit.

### Source 1 — Statistics Canada GDP press release (Q2 2025)

**URL:** https://www150.statcan.gc.ca/n1/daily-quotidien/250829/dq250829a-eng.htm

**Direct quote:** *"Final domestic demand, which represents total final consumption expenditures and investment in fixed capital, was up 0.9% in the second quarter of 2025, following a decline of 0.2% in the first quarter."*

**Methodology note:** "Total final consumption expenditures" includes both household and government final consumption — so the framework's "consumption + government consumption + gross fixed capital formation" is correct in substance. StatsCan's tighter wording rolls household + government into a single "total final consumption expenditures" term, which the framework prose unrolls for clarity. Inventories and net trade are tracked as separate components (see same release: "Business non-farm inventories accumulated at a faster pace…").

**Verdict:** VERIFIED — the framework's expanded version reproduces StatsCan's identity correctly.

### Defects flagged

- **No fabricated quote.**
- **No US-transferred heuristic.**
- **No unsourced threshold.**

### Open questions for user review

None — claim is cleanly verified.

---

## Claim 9: Q4 2025 inventories swing of -4.2pp (verifiable from project data)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09 against project data. Not user-reviewed.**

### Framework prose (verbatim, lines 169, 179)

> recent swings have been -4.2pp

> Q4 2025 was -4.2pp

### Verification verdict

**VERIFIED.** Last row of `data/gdp_contrib_inventories.csv` reads `2025-10-01,-4.238`, which rounds to -4.2pp.

### Source 1 — Project data: `data/gdp_contrib_inventories.csv`

**Verified row (retrieved 2026-05-09):**
```
2025-10-01,-4.238
```

The framework's "-4.2pp" is the correctly-rounded headline value.

**Verdict:** VERIFIED.

### Defects flagged

- **No fabricated quote.**
- **No US-transferred heuristic.**
- **No unsourced threshold.**

### Open questions for user review

None — claim is cleanly verified.

---

## Claim 10: BoC publishes four output gap measures (MPR central, historical real-time, EMVF, IF)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim, line 180)

> Output gap > 0 (positive) = excess demand, inflationary pressure; output gap < 0 = excess slack, disinflationary. The BoC publishes four separate gap measures (MPR central, historical real-time, Extended Multivariate Filter, Integrated Framework) — uncertainty is wide; don't treat any single estimate as precise.

### Verification verdict

**VERIFIED.** The BoC's Product Market Definitions page lists exactly these four measures.

### Source 1 — BoC Product market: Definitions, graphs and data

**URL:** https://www.bankofcanada.ca/rates/indicators/capacity-and-inflation-pressures/product-market-definitions/

**Verified facts:** The page lists four output-gap series:
1. **Current MPR Output Gap** (*"contains the estimates embedded in the most recently published Monetary Policy Report"*)
2. **Historical MPR Output Gap** (*"a series containing historical estimates made in real-time, without any revision"*)
3. **Extended Multivariate Filter (EMVF)** (mechanical methodology; *"generally free of judgement or anecdotal evidence"*)
4. **Integrated Framework (IF)** (mechanical methodology, alongside EMVF)

**Verdict:** VERIFIED — the framework's four-measure enumeration matches the BoC's own taxonomy.

### Note on framework's "BoC's gap is not loaded" caveat

The framework explicitly flags (line 168) that the dashboard does not load BoC's published gap estimates. This is honestly disclosed and is consistent with the failure-mode caveat about not naming un-fetched indicators. The four measures are *named* but not *cited as data points the dashboard reads from* — they're cited as evidence that "uncertainty is wide" rather than as a tracked series. This is the right way to handle it.

### Defects flagged

- **No fabricated quote.**
- **No US-transferred heuristic.**
- **No unsourced threshold.**
- **Coverage gap honestly disclosed** — the framework appropriately notes the dashboard does not load these series.

### Open questions for user review

1. Should there be a future task to actually wire one or more of the BoC's four gap series into the dashboard (closing the coverage gap)? Currently flagged but not actioned.

---

## Claim 11: "Two consecutive negative quarters" rule explicitly rejected

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.**

### Framework prose (verbatim, line 178 — overlap with Claim 4)

> Recession framing: Canada's authoritative recession-dating body is the C.D. Howe Institute Business Cycle Council, NOT a "two consecutive negative quarters" rule.

### Verification verdict

**PARTIALLY VERIFIED.** The BCC does not *use* the two-consecutive-quarters rule, but it also does not *explicitly reject* it in its publicly available methodology page. The framework's framing is closer to "the BCC doesn't apply this rule" than to "explicitly rejected" — both are defensible characterisations of the BCC's actual methodology.

### Source 1 — BCC Methodology page

**URL:** https://cdhowe.org/publication/business-cycle-council-methodology/

**Findings (no direct rejection of two-quarters rule):**
- The methodology never names "two consecutive negative quarters" as a rule it explicitly rejects.
- However, it states the Council *"does not follow hard-and-fast rules on these dimensions"* and that weakness can be expressed as *"contiguous quarters, but not necessarily by outright decline,"* allowing for stagnation periods that wouldn't qualify under a strict negative-print rule.
- These collectively constitute an *implicit* rejection — the Council's flexibility-based methodology is incompatible with a strict mechanical rule.

### Source 2 — BCC 2022-2023 communiqué (handled in Claim 4)

The Council declared no recession in 2022-2023 despite multiple quarters of weakness, illustrating that they don't apply the two-quarters rule mechanically. This is operational evidence — not a verbal rejection.

### Defects flagged

1. **Minor framing precision:** "NOT a 'two consecutive negative quarters' rule" implies the BCC explicitly rejects the rule. The BCC uses a different methodology entirely; there's no published "we reject this" statement. Cleaner phrasing: *"the BCC does not use the two-consecutive-quarters rule; it uses a multi-dimensional methodology assessing amplitude, duration, and scope."*
2. **No fabricated quote.**
3. **No US-transferred heuristic** — the BCC is explicitly Canadian; the framework correctly distinguishes from NBER (though NBER isn't named in this section).

### Open questions for user review

1. Soften "explicitly rejected" framing to "does not use" or "does not rely on"?

---

## Cross-claim defects index

Aggregating defects across all 11 claims by failure-mode type. Failure-mode taxonomy from the audit prompt:

1. **Fabricated quotes** attributed to real BoC speakers / publications.
2. **US-economic heuristics transferred to Canada without empirical recalibration.**
3. **Threshold values asserted without primary-source backing.**
4. **Naming un-fetched indicators in framework prose.**
5. **Rigid n×n decoders presented as canonical when they're analyst synthesis.**

### Defect 1 — fabricated quotes

**None located.** No quote in the GDP & Activity section of the framework was fabricated against a real BoC publication. This is a cleaner result than the Labour-section audit, which surfaced multiple fabrications. The closest issue is the BCC's "depth, duration, and breadth" phrase — which is presented in framework prose as if it were the BCC's methodology terminology when it is actually a paraphrase (canonical: "amplitude, duration, and scope"). This is closer to a paraphrasing-as-quotation defect than an outright fabrication.

### Defect 2 — US-transferred heuristics

**None located.** The framework correctly anchors recession dating to C.D. Howe BCC (Canada-specific) rather than NBER (US). Potential output growth, output gap, scenario averages, and inventory thresholds are all calibrated to Canadian data. The framework's careful hedging on the "two consecutive negatives" rule (often a US shorthand) is appropriate.

### Defect 3 — Threshold values asserted without primary-source backing

**Two defects flagged:**

- **Claim 5** — 2008-09 housing trough lower bound (118k) doesn't match project data (actual trough = 111.781k in April 2009); COVID April 2020 figure (165k) doesn't match project data (161.004k). Both are project-data ground-truth mismatches rather than BoC-source mismatches, but the framework presents them as anchors.
- **Claim 6** — "Inventories swing > ±3 pp" threshold is the analyst's calibration based on recent Canadian volatility (envelope ~±4pp in 2024-2025), not a BoC or StatsCan published threshold. Reasonable as a rule of thumb but should be marked as analyst calibration.

### Defect 4 — Naming un-fetched indicators in framework prose

**Honestly disclosed; no defect.** The framework explicitly flags (line 168) that BoC's output gap is not loaded into the dashboard. The four output-gap measures are named (Claim 10) but cited as evidence of uncertainty rather than as tracked series. This is the right way to handle a coverage gap: name + flag, don't pretend.

### Defect 5 — Rigid n×n decoders presented as canonical

**Two soft instances:**

- **Claim 4** — The "depth, duration, breadth" three-criteria framing is presented as the BCC's canonical wording but is actually a paraphrase. Analyst synthesis dressed as primary-source terminology.
- **Claim 4** — The "pronounced, pervasive, and persistent" phrase is in the right spirit but the wrong word order (BCC canonical: "pronounced, persistent, and pervasive").

### Top three defects (priority for revision)

1. **C.D. Howe BCC criteria mis-naming (Claim 4).** Framework names the three criteria as **"depth, duration, and breadth"**; BCC canonical is **"amplitude, duration, and scope."** Framework also reverses the "persistent / pervasive" word order in the BCC's headline phrase. Material because the framework presents these as primary-source citations, lending false authority to the analyst's paraphrase. **Fix: replace with canonical BCC wording verbatim.**

2. **Housing-trough numerical anchors don't match project data (Claim 5).** Framework's "118-149k" 2008-09 trough lower bound is too high (actual: 111.781k in April 2009); COVID April 2020 SAAR is given as "~165k" but project CSV shows 161.004k. Material because these are anchors used for the "below 180k = recessionary" threshold calibration. **Fix: tighten to "~112-150k" and "~161k" to match the project's CSV vintage.**

3. **"Inventories swing > ±3pp" threshold is unsourced analyst calibration (Claim 6).** Threshold is presented in framework prose without a "(analyst calibration)" tag, even though it's the dashboard's own empirical envelope calibration rather than a BoC/StatsCan-published number. Material because it sits alongside primary-source-backed thresholds (output gap > 0) and reads as if it carries the same weight. **Fix: add explicit "(dashboard calibration; not a BoC-published threshold)" tag, or replace with a rolling-stdev dynamic threshold.**

### Lower-priority defects flagged in individual claim entries

- **Claim 7** — "BoC's mandate is price stability, NOT growth management" elides the 2021 maximum-sustainable-employment supporting objective. Soften framing.
- **Claim 11** — "Two-consecutive-negatives rule explicitly rejected" overstates the BCC's posture (they don't use it; they don't explicitly reject it in print). Soften to "does not use."
- **Claim 4** — "depth/breadth criteria not met" 2022-2023 gloss; cleaner is "persistence and breadth criteria not met" given the communiqué's actual reasoning.
- **Claim 3** — SAN 2025-14 (June 2025) is now superseded by April 2026 MPR for the central case; framework cites both in parallel without a freshness indicator.

### Audit-scope notes

- All numerical anchors that could be verified against project data were verified (Q4 2025 inventories: ✓; housing trough range: partial mismatch; COVID April 2020: partial mismatch).
- The audit could not access the BCC's Communiqué PDF directly (binary PDF couldn't be parsed) but cross-verified its content via the C.D. Howe HTML pages and search results.
- The audit could not access the January 2026 MPR PDF directly (binary PDF couldn't be parsed) but cross-verified the Q4 2025 output gap range via the HTML version of the Canadian Conditions chapter.
