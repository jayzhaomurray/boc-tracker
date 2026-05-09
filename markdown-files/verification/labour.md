# Verification log: Labour Market section

Per-claim source log for the Labour section of `analysis_framework.md`. Each claim in the framework should appear here with: (a) the framework prose verbatim, (b) the primary source(s) that back it, (c) a direct quote from the source where possible, (d) a verification verdict, (e) a provenance tier (see `_tiers.md`), and (f) any analyst notes.

This file is **not** in CLAUDE.md's "First moves" auto-load list — it's a working log for claim-by-claim review, kept separate from the framework prose to avoid bloating session-init context. The framework itself carries inline citations; this log carries the page-level evidence chain.

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

---

## Claim 1: Unemployment rate level and direction (estimated NAIRU ~6%)

### Provenance tier

**Tier 3 — user-verified 2026-05-09.** Original Tier-2 entry contained two fabricated BoC quotes that survived autonomous verification; user sign-off came only after sources were re-checked and the framework rewritten.

### Verification verdict

REVISED 2026-05-09. Original framework text contained two fabricated quotes attributed to the BoC ("accelerationist Phillips curves are no longer in its main models" and "the NAIRU concept is not applicable to a wider set of labour market measures"). Neither could be located in any BoC primary source. Framework rewritten to drop the fabrications, anchor on a verified Macklem quote, and explicitly adopt a peer-institution NAIRU anchor (IMF) with the BoC's stance noted as caveat.

### Final framework text (post-revision)

> The dashboard tracks unemployment against an estimated NAIRU of about 6%, anchored to the IMF's July 2024 Article IV Consultation for Canada. NAIRU is a concept, not an observable — estimated, slow-moving, and uncertain at the decimal. The BoC itself does not publish a NAIRU; Governor Macklem (Nov 2022) characterised maximum sustainable employment as "not directly measurable... more of a concept than a number," and SAN 2025-17 (June 2025) operationalises labour-market state through a multi-indicator benchmark range rather than a single number. The dashboard adopts a peer-institution anchor because the concept remains analytically useful — OECD publishes NAIRU explicitly in annex tables, ECB uses it as a named input to staff wage Phillips curves, the US Fed uses the term with active hedging (Kugler Feb 2025). CIBC (Jan 2026) flags that post-pandemic NAIRU may have moved structurally higher per the 2022–2024 immigration surge's skill-mismatch effects.

### Source 1 — IMF Canada 2024 Article IV Consultation (July 16, 2024)

**URL:** https://www.imf.org/en/publications/cr/issues/2024/07/16/canada-2024-article-iv-consultation-press-release-and-staff-report-551903

**Direct quote:** *"The unemployment rate has risen to 6.2 percent, slightly above the NAIRU, estimated at 6 percent... unemployment is expected to continue rising slowly, peaking at 6.4 percent toward the middle of the year before normalizing at the estimated NAIRU of 6 percent."*

**Methodology note:** IMF uses a Phillips curve / output-gap framework for NAIRU estimation in Article IV consultations. The 6% figure is post-pandemic and incorporates conditions through mid-2024. Whether the immigration-surge skill-mismatch effects are fully captured is not transparent in the published methodology.

**Verdict:** VERIFIED — primary source supports the 6% anchor.

### Source 2 — BoC Governor Macklem speech, Nov 10, 2022

**URL:** https://www.bankofcanada.ca/2022/11/restoring-labour-market-balance-and-price-stability/

**Direct quote on why no point estimate:** *"Maximum sustainable employment is not directly measurable and is determined largely by non-monetary factors that can change through time."* Macklem describes maximum sustainable employment as *"more of a concept than a number"* and uses Beveridge curve framings rather than NAIRU-based unemployment-gap analysis.

**Verdict:** VERIFIED — supports the framework's "BoC does not publish a NAIRU" framing and the verified Macklem quote in the revised prose.

### Source 3 — BoC SAN 2025-17 (June 2025)

**URL:** https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-17/

**Key finding:** The note contains zero mention of NAIRU. The word does not appear. The methodology uses HP filter, modified Hamilton filter, and model-based potential-output estimates. The single Phillips curve mention is contextual ("a flatter wage Phillips curve... for minimum wage workers") and does not constitute a framework-wide repudiation.

**Verdict:** VERIFIED — supports "BoC operationalises through multi-indicator benchmark" framing. Original framework's "Bank explicitly states accelerationist Phillips curves are no longer in its main models" wording is NOT verified by this paper.

### Source 4 — CIBC Economics, Andrew Grantham (Jan 15, 2026)

**URL:** https://thoughtleadership.cibc.com/article/canadian-labour-market-could-we-really-run-out-of-room-before-year-end/

**Direct quote — pre-pandemic baseline:** *"Our prior study into a labour-market based output gap placed NAIRU at a bit below 6% prior just ahead of the pandemic."*

**Direct quote — post-pandemic:** *"NAIRU likely moved higher subsequently, as structural changes caused by the pandemic as well as a big surge in the population resulted in a weaker relationship between skills and job availability."*

**Direct quote — current stance:** *"In reality, we will only really know where NAIRU lies when we see it — when broad wage inflation starts to accelerate again."* Grantham notes the 2024–2025 immigration policy pivot toward more-employable permanent residents *"should help reduce structural unemployment and lower the NAIRU rate over time."*

**Verdict:** VERIFIED — supports the framework's CIBC caveat language. CIBC explicitly declines to give a post-pandemic point estimate, so the framework should not invent one.

### Other-institution usage (justification for keeping NAIRU as a tracked concept)

- **OECD (Economic Outlook Statistical Annex):** Publishes NAIRU explicitly per country. Latest publicly accessible Canadian figure (CEIC mirror): 6.243% (2022 vintage). December 2025 annex paywalled.
- **ECB (Economic Bulletin Jan 2025):** *"the unemployment gap (calculated as a difference between the actual unemployment rate and the NAIRU estimate in the Eurosystem / ECB Staff projections)"* — used in augmented wage Phillips curves.
- **US Fed (Governor Kugler, Feb 20 2025 speech):** *"NAIRU (non-accelerating inflation rate of unemployment), which is thought to be the normal level of unemployment absent cyclical forces"*; *"the weight on the unemployment gap in the Phillips curve for the more recent period is very small."* URL: https://www.federalreserve.gov/newsevents/speech/kugler20250220a.htm

### Canadian private-sector context

- **RBC, BMO, TD, Scotia, NBF, Desjardins:** No publicly accessible quantitative NAIRU estimates. Pivot to "breakeven employment" (RBC framing) or qualitative slack discussion. Verified by web survey 2026-05-09.

### Open follow-ups (not blocking this claim's verdict)

- Direct read of Pierre Fortin (UQAM), CLEF Working Paper 070-2024 (May 2024) on regional Beveridge curves — relevant Canadian academic content, PDF couldn't be parsed by the sub-agent. URL: https://clef.uwaterloo.ca/wp-content/uploads/2024/05/CLEF-070-2024-EN.pdf
- A future labour-deep-dive page could re-estimate Canadian NAIRU using post-2022 data (Beveridge-curve or Phillips-curve regression), giving the dashboard a self-grounded estimate rather than a borrowed one. The 2024–2025 immigration policy pullback should reduce structural distortion in the data over time, making a re-estimate increasingly tractable.

---

## Claim 2: Utilization — employment rate and participation rate together

### Provenance tier

**Tier 3 — user-verified 2026-05-09.** User flagged the rigid 2×2 decoder as combinatorially incomplete; the autonomous Tier-2 version had codified it as if it were a primary-source rule.

### Verification verdict

REVISED 2026-05-09. Original framework prose codified a rigid four-quadrant decoder mapping joint employment+participation moves to four named states (*"falling employment with stable participation = layoffs absorbing slack; falling participation with stable employment = workers leaving the labour force; both falling = slack opening on both margins; both rising = the strongest tightening signal"*). The decoder had two structural problems that prompted revision:

**1. Combinatorially incomplete.** The 2×2 codification names four states out of the 3 × 3 = 9 logical configurations (employment-rate move ∈ {falling, stable, rising}, participation-rate move ∈ {falling, stable, rising}). When data falls into one of the unaddressed five states, the framework forces a wrong assignment — exactly what the naive labour blurb did during 2026-05-09 testing (applied "layoffs pattern" to a 12M window where both employment and participation had fallen, which by the framework's own taxonomy is "slack opening on both margins," not "layoffs").

**2. The specific 2×2 codification is not from a primary source.** The underlying analytical move (read employment + participation together to distinguish layoff dynamics from labour-force-exit dynamics) is canonical labour-economics reasoning grounded in transition-flow analysis from the BoC, BLS, and standard texts. But the specific four-state matrix as written was the analyst's own synthesis, not a BoC-published rule.

### Final framework text (post-revision)

> Employment rate measures the share of the working-age population that's actually employed; participation rate measures the share that's in the labour force at all. The two encode different dimensions of labour-market state — employment captures how many people have jobs, participation captures how many are even available to work. Read against each other, the joint move surfaces dynamics the unemployment rate alone obscures: when employment is falling but participation holds, the move typically reflects layoffs adding to unemployment; when participation is falling but employment holds, the move typically reflects workers leaving the labour force (discouragement, retirement, or a labour-supply change). Treat these reads as starting hypotheses rather than final classifications — there are more configurations than canonical labels for them (3 × 3 = 9 logical states), small moves can be within noise, and the same configuration can mean different things in different cycles. Each rate is part of SAN 2025-17's multi-indicator benchmark — the BoC tracks them as separate channels rather than collapsing them into the unemployment rate.

### Source backing for retained material

**SAN 2025-17 (June 2025):** Verifies that the BoC's multi-indicator benchmark explicitly tracks employment rate and participation rate as separate channels rather than collapsing into the unemployment rate. (URL and direct quote in Claim 1 → Source 3.)

**Standard labour economics:** The "read employment + participation together to distinguish labour-demand from labour-supply moves" framing is canonical in transition-flow analysis. The economics is well-grounded — labour force = employed + unemployed; participation rate = labour force / working-age; employment rate = employed / working-age — so the joint moves encode flows between employed / unemployed / not-in-labour-force. References include BoC analytical papers on labour-market flows, the US BLS' published flow data, and standard labour economics texts. No single citable paper underpins the specific framing; this is the field's general analytical move.

### Untracked direct indicators (deep-dive material, NOT for blurb prose)

An earlier draft revision attempted to name direct-indicator triangulation in the bullet itself — LFS reason-for-unemployment (Table 14-10-0125, job-loser share) for layoffs; LFS R-indicators (R3, R7, R8) for discouragement / marginal attachment; long-term unemployment share (≥27 weeks) for persistent slack. These are valid analytical moves but the underlying series are not currently fetched. The user (2026-05-09) flagged that naming them in framework prose risks the model leaking *"would check this but the indicator is not currently fetched"* into user-facing blurb output.

Resolution: untracked-indicator discussion lives only in:
- HANDOFF item 5 (deep-dive Labour Market page, listed as tentative content)
- This verification log entry

The framework prose names only indicators that are present in the data block fed to the blurb prompt.

### Open follow-up

The global "Verification, not speculation" rule near the top of `analysis_framework.md` says main-page blurbs work from top-level aggregates only — never from individual sub-categories — and defers component-level decomposition to deep-dive pages. The user flagged 2026-05-09 that an experienced human writer can judge when a deep-dive tidbit *enriches* a high-level blurb vs. *clutters* it, but the model doesn't yet reliably exercise that judgment. The hard rule is the safe default for now. Worth revisiting when there's a more reliable way to confer that judgment — possibly via per-section allowlists, model improvements, or a separate "supplementary detail" instruction layer.

---

## Claim 3: Tightness — job vacancy rate + V/U ratio + V/U threshold bands

### Provenance tier

**Tier 3 (provisional) — user-engaged 2026-05-09; flagged for re-review 2026-05-10.** User actively challenged the V/U > 1 = tight heuristic, the BoC's-preferred framing, and the 12M MA smoothing choice; the revised version went through user push-back. The Tier-3 stamp will be confirmed (or revised again) at the 2026-05-10 review pass — until then, the entry is "engaged but not finalized," structurally still Tier 3 but with an explicit reopening flag. **DEFERRED (2026-05-09 convention sweep): user flagged for own re-review; thresholds not changed in this sweep.**

### Verification verdict

**REVISED 2026-05-09 — FLAGGED FOR USER RE-REVIEW 2026-05-10 BEFORE FINAL ACCEPTANCE.** The user explicitly wants to revisit this section tomorrow morning ("this is a crucial thing to get right"). The revision below is committed but provisional.

The original framework prose had three issues addressed in the revision:

**(A) "BoC's preferred composite read."** Original framework asserted V/U was the BoC's *preferred* tightness indicator. No primary source positions V/U as preferred over alternatives — the BoC uses V/U directionally inside a multi-indicator approach (per SAN 2025-17). Softened to *"one of the composite tightness indicators the BoC uses"* with a verified Macklem Nov 2022 anchor (he framed labour-market state via the Beveridge curve, which is V/U-based).

**(B) Threshold bands.** Original framework claimed *"V/U > 1 = tight, V/U < 1 = slack"*. This transferred a US JOLTS-era heuristic (US peaked at V/U ≈ 2 in 2022) to a structurally different Canadian series (Canadian peak ≈ 0.99 in 2022). Replaced with Canadian-specific empirical bands anchored to narrative tightness moments (2018–2019 BoC tightening cycle; 2022 post-COVID episode; 2015–2017 emergency-low period).

**(C) Smoothing methodology.** Framework specified 12M MA. Empirical analysis: Canadian vacancy NSA seasonal amplitude is ~8% of cyclical range, so 12M MA over-smooths and lags cyclical turns (the 2022 V/U peak hit 0.99 in June 2022 but registered in the 12M MA only in January 2023 — a 7-month lag). Recommendation: switch to 3M MA. Framework prose updated to reference 3M MA. **The corresponding code change in `analyze.py compute_labour_values` (12M → 3M for `vac_rate_12m` / `vac_level_12m` and the `vacancy_rate_12m_avg` / `vacancy_count_12m_avg_m` output keys, plus the `job_vacancy_rate_12m` / `job_vacancy_level_12m` derived chart series in `build.py`) is QUEUED for the 2026-05-10 review pass — so framework and dashboard rendering land coherently together.**

### Final framework text (post-revision; provisional pending 2026-05-10 review)

> **Tightness: job vacancy rate (3M MA) and the V/U ratio.** Vacancy data is monthly NSA (Table 14-10-0371; no SA series published). The dashboard uses a 3-month moving average to denoise — seasonal amplitude is small (~8% of cyclical range), so a 12-month MA over-smooths and lags cyclical turns (the 2022 peak hit V/U ≈ 0.99 in June 2022 but registered in 12M MA only in January 2023 at ~0.86, a 7-month lag). The V/U ratio — vacancies per unemployed person — is one of the composite tightness indicators the BoC uses (Macklem Nov 2022 framed labour-market state via the Beveridge curve, which is V/U-based). Theoretically, V/U = 1 is the labour-market efficiency point per Michaillat & Saez (2023, *u\* = √uv*). Canadian thresholds are calibrated empirically, not transferred from the US: V/U < 0.30 = slack; 0.30–0.45 = below balance (2015–2017); 0.45–0.60 = approaching balance / starting to be tight (2018–2019 anchor); 0.60–0.80 = tight (extrapolated); > 0.80 = exceptionally tight (2022 anchor). Beveridge curve position shifts (post-COVID outward shift visible in Canada per CIBC Jan 2026); fixed thresholds are dashboard simplifications.

### Source 1 — Statistics Canada Table 14-10-0371 (Job Vacancy and Wage Survey)

**URL:** https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410037101

**Verified facts:**
- Series begins 2015 (no longer historical record exists in StatsCan's published JVWS).
- Monthly vacancy rate / count published NSA only; no SA series exists. (Confirmed via cube metadata; no companion `_SA` vector available.)
- Vector 1212389365 = job vacancy rate; Vector 1212389364 = job vacancy count. Both registered in `data/` per HANDOFF.

**Implication for framework:** any tightness signal that requires longer history (cyclical comparison pre-2015) cannot be sourced from Canadian data. US JOLTS (1.5× longer, Dec 2000+) is the comparator we use for cyclical context.

### Source 2 — Michaillat & Saez (2023), "u\* = √uv"

**Citation:** Michaillat, Pascal; Saez, Emmanuel. *u\* = √uv*. NBER / journal version 2023.

**Theoretical claim:** the labour-market efficiency point is V/U = 1 — i.e. the rate at which there are as many vacancies as unemployed workers. At V/U = 1, search frictions don't systematically favour either side of the matching market. Above 1 = inefficiently tight; below 1 = inefficiently slack. The associated efficient unemployment rate is u\* = √(u·v).

**Use in framework:** treated as the *theoretical* anchor for V/U band design. The framework explicitly notes that fixed V/U thresholds are dashboard simplifications around this theoretical anchor — neither the BoC nor the Fed quotes specific V/U thresholds; both use V/U directionally.

**Verdict:** VERIFIED — primary literature supports the theoretical anchor.

### Source 3 — BoC Governor Macklem speech, Nov 10, 2022

**URL:** https://www.bankofcanada.ca/2022/11/restoring-labour-market-balance-and-price-stability/

**Direct quotes:**
- *"Canada's labour market is exceptionally tight."*
- *"...there are signs of excess demand."*
- Macklem framed labour-market state via the Beveridge curve (V/U-based), discussing the 2022 outward shift relative to pre-pandemic.

**Verdict:** VERIFIED — supports both "BoC uses V/U directionally" framing and the 2022 = "exceptionally tight" anchor for the > 0.80 V/U band.

### Source 4 — BoC Senior Deputy Governor Wilkins speech, Jan 8, 2019

**Source context:** Cited in the second narrative-anchoring sub-agent's findings. Quote on labour-market state circa late-2018 / early-2019 (the BoC's 2017–2019 tightening cycle):

**Direct quote:** *"...one of the highest levels of labour shortages since the Great Recession."*

**Computed Canadian V/U for this period (2018–2019 average using monthly NSA data, no smoothing):** V/U fluctuated in roughly 0.45–0.60 range. Unemployment was at or below the 6% IMF NAIRU lower bound — consistent with a labour market the BoC characterised as starting to be tight.

**Verdict:** VERIFIED narrative anchor for the 0.45–0.60 V/U band ("approaching balance / starting to be tight").

### Source 5 — CIBC Economics, Andrew Grantham (Jan 15, 2026)

**URL:** https://thoughtleadership.cibc.com/article/canadian-labour-market-could-we-really-run-out-of-room-before-year-end/

**Direct quote — post-pandemic Beveridge curve shift:** *"NAIRU likely moved higher subsequently, as structural changes caused by the pandemic as well as a big surge in the population resulted in a weaker relationship between skills and job availability."*

**Verdict:** VERIFIED — supports the framework's "Beveridge curve position shifts" caveat. Outward shift is also visually obvious in the Beveridge curve chart at `analyses/beveridge_curve_canada.html` (post-COVID points sit measurably above the pre-pandemic locus at the same unemployment rates).

### US comparison findings (Canadian thresholds calibrated empirically, not transferred from US)

**US JOLTS V/U history (Dec 2000+):**
- 2000–2007 cycle peak V/U ≈ 0.6–0.7
- 2018–2019 peak ≈ 1.0
- 2022 post-COVID peak ≈ 2.0 (a structurally distinct level not seen in Canadian data)

**Why structurally different:**
- Sectoral mix: Canada's employment is heavier in resources / public sector, lighter in tech / services where US 2022 vacancy demand spiked.
- Great Resignation: a US-specific phenomenon driven by stimulus + sectoral mix; Canadian quits never reached US-level magnitudes.
- Survey-coverage differences: JOLTS samples differently from JVWS; not 1:1 comparable in levels.

**Implication:** transferring US-calibrated V/U thresholds (e.g. "V/U > 1 = tight") to Canada systematically over-states tightness. Canadian peak V/U ≈ 0.99 in 2022, not 1+. The framework's threshold bands are calibrated to the *Canadian* range of historical observations.

### Smoothing methodology computation (E findings; computed 2026-05-09)

| Series | Computation | Result |
|---|---|---|
| Vacancy rate seasonal amplitude (median monthly NSA – 12M MA) | StatsCan Vector 1212389365, 2015–2026 | 0.082 (8.2% of cyclical range) |
| Vacancy rate cyclical amplitude (max – min, 12M MA) | Same series | 0.993 |
| 2022 V/U cyclical peak — raw NSA | Canadian peak | 0.99 (June 2022) |
| 2022 V/U cyclical peak — 12M MA | Same series, 12M smoothing | 0.86 (January 2023; 7-month lag behind raw peak) |
| 2022 V/U cyclical peak — 3M MA | Same series, 3M smoothing | ≈ 0.96 (August 2022; ~2-month lag — acceptable) |

**Decision:** 3M MA captures cyclical turns with acceptable lag while still removing the small NSA seasonal pattern. 12M MA's 7-month peak lag is large relative to the duration of policy-relevant cyclical episodes (2022 overheat lasted ~12 months; a 7-month detection lag means the dashboard signals "exceptionally tight" most of the way down).

### Open analytical question — flagged by user 2026-05-09 for revisit

**User skepticism (not an action item; logged for the 2026-05-10 review):**

> *"It is kind of funny that employers were complaining about labour shortages the whole time, even when V/U was so much lower. It's almost like, maybe they were so used to having such a massive pool of unemployed people that having any competition at all for workers, having to raise wages at all, read as a 'shortage' when it really wasn't. Like I am personally skeptical that the labour market was insanely tight from 0.5 all the way to 1 V/U. But as a diagnostic tool vs. my personal opinion, those are separate questions."*

**Analytical implication:** the 0.45–0.60 V/U band (anchored to Wilkins Jan 2019 "labour shortages since the Great Recession") may be over-conceding to the employer-narrative anchor. Employers used to a large unemployed pool (post-2008 era, Canadian unemployment 7%+) may interpret any wage pressure as "shortage" — a status-quo-bias signal rather than a structural-tightness signal. If the framework's "starting to be tight" band is effectively employer-baseline-expectation-driven rather than wage-pressure-driven, the diagnostic tool is partly endogenously calibrated to a complaint that was about something other than tight labour markets in the textbook sense.

**Why this matters but isn't being acted on tonight:** the user explicitly separated personal-skepticism from the diagnostic-tool framing, and asked that the framework reflect the diagnostic frame. Tomorrow's review can re-examine whether to (a) keep the band labels as-is (diagnostic frame matches the available narrative anchors), (b) relabel the 0.45–0.60 band to something less assertive than "starting to be tight" (e.g. "elevated relative to recovery baseline"), or (c) introduce a separate dashboard band for "wage-pressure-confirmed tight" requiring wage Y/Y > 3.5% to fire. Worth a structured discussion at the 2026-05-10 review.

### Recyclable artifact

**Beveridge curve chart:** `analyses/beveridge_curve_canada.py` and `analyses/beveridge_curve_canada.html`. Plotly static HTML. Period-coloured monthly trajectory (2015–2026), 3M MA on both axes, post-COVID outward shift visually obvious. **Candidate for the deep-dive Labour Market page** (HANDOFF item 5). Date range May 2015 – Feb 2026; U range 4.97–13.50%; V range 0–5.90%.

### JVWS COVID gap — bugfix and complementary-series plan (raised 2026-05-09 by user)

**The data bug.** The saved JVWS CSVs (`data/job_vacancy_rate.csv`, `data/job_vacancy_level.csv`) had `0.0` values for April–September 2020. StatsCan **suspended JVWS fieldwork** for those six months due to COVID — *Guide to the Job Vacancy and Wage Survey, 2024 ed.*: *"Data collection was suspended for the second and third quarter of 2020, due to the COVID-19 pandemic. As such, quarterly data is not available for the second and third quarter of 2020, and monthly data is not available for the months that make up these quarters (April-September 2020)."* No retrospective estimates were ever published; the gap is permanent. October 2020 was both the resumption date *and* the launch of the new monthly product (previously quarterly), so Table 14-10-0371-01 effectively starts October 2020 in monthly form. (Sources: StatsCan Guide 75-514-G; JVWS Summary of Changes; SDDS 5217.)

**Root cause and fix (applied 2026-05-09 in this commit).** The WDS API returns `value: null` with `statusCode: 1` ("data not available") for the gap months. The current `fetch_statscan` in `fetch.py` was correctly coercing nulls to NaN via `pd.to_numeric(errors="coerce")` — but then calling `.dropna()` before saving to CSV. That meant the *current* fetcher (since some past commit) would write 125 rows; but the saved CSVs had 132 rows with `0.0` because they were generated by an earlier vintage of the fetcher that handled nulls differently. Fix: removed `.dropna()` from `fetch_statscan` so NaN rows are preserved in CSVs, and re-fetched the two JVWS series. CSVs now have 131 rows with 6 NaN at the gap. Plotly auto-breaks lines at NaN; pandas rolling means handle NaN windows via `min_periods`; `asof()` already calls `.dropna()` internally and is NaN-safe. Verified `compute_labour_values` and `build.py` both run cleanly with the corrected data.

**The Beveridge curve chart was wrong.** The committed `analyses/beveridge_curve_canada.html` (commit 07e0996) plotted the `0.0` rows as real data points at V = 0% against U = 13.5%, creating a fake near-vertical excursion to the floor. Re-rendered with the corrected CSVs in this commit; the COVID-shock period now has 7 points (Mar 2020 + Oct 2020 – Mar 2021) instead of 13, because the joint-data inner-join correctly excludes Apr–Sep 2020 where vacancy data is missing. V range tightened from 0.00–5.90% to 1.93–5.90%; U range tightened from 4.97–13.50% to 4.97–8.90% (the COVID unemployment-spike months drop out of the Beveridge view because we have no V to pair with them — we never had).

**Indeed Hiring Lab Canada — complementary series (queued for 2026-05-10).** Indeed Hiring Lab publishes a **Canadian Job Postings Index** (Feb 1 2020 baseline = 100, daily SA, freely pullable from `github.com/hiring-lab/data` under CC BY 4.0). Coverage starts Feb 1 2020 — covers the entire JVWS blackout. Gap-period trajectory: trough −49% in early May 2020, recovered to −22% by Sept 4 2020. The BoC has used Indeed-Canada postings as a complementary read on the JVWS in **SAN 2021-18** ("Canadian job postings in digital sectors during COVID-19") and **SWP 2022-17** ("What COVID-19 May Leave Behind: Technology-Related Job Postings in Canada") — explicitly during the JVWS blackout. **Not a level substitute** (postings index, not vacancy rate; no employer-survey weighting). User decision (2026-05-09): **add Indeed as a toggleable line on the existing Unemployment & Job Vacancies chart**, not used in V/U calculations — purely visual. Implementation deferred to 2026-05-10:
- Add `indeed_postings_ca` to `fetch.py` (new fetcher; pulls from `https://raw.githubusercontent.com/hiring-lab/data/master/CA/aggregate_job_postings_CA.csv`, monthly resample for chart cadence)
- Extend `MultiLineSpec` (or add a per-line option) to support a secondary y-axis since Indeed's index unit doesn't share with vacancy rate (%) or vacancy level (millions)
- Add Indeed line to the Unemployment & Job Vacancies `MultiLineSpec`, default-off via legend toggle, dashed style

**Framework prose caveat (queued for 2026-05-10).** Add to the Tightness signal bullet: vacancy data has a permanent 6-month COVID hole (Apr–Sep 2020) where StatsCan suspended fieldwork; the COVID-period V/U trough is unobservable in JVWS and visible only in Indeed-Canada postings. Any "Canadian V/U full cyclical range" claim has this hidden caveat.

### Open follow-ups (not blocking this claim's verdict)

- **2026-05-10 review pass:** re-examine threshold band labels (esp. 0.45–0.60 "starting to be tight" anchor — see user skepticism above); finalize 12M→3M code change in `compute_labour_values` and `build.py` chart spec; decide whether the chart line label should be updated; add Indeed line + framework gap-caveat per the plan above.
- **Code change queued:** `analyze.py compute_labour_values` (12M → 3M); `analyze.py format_labour_values` (key renames); `build.py` Unemployment & Job Vacancies chart spec (derived series rename + comment update + Indeed line + secondary y-axis); `fetch.py` `_DERIVED_SERIES_SOURCES` (rename or add 3M variant; new Indeed fetcher). Coherent rollout: framework + code in one commit, regen labour blurb in next API-key-available pass.
- **CLEF 070-2024 (Fortin, regional Beveridge curves)** — also flagged in Claim 1 follow-ups; relevant here too, especially if regional Beveridge-curve heterogeneity informs whether national V/U thresholds even make sense as a single calibrated set.

---

## Claim 4: Cost pressure — Unit Labour Costs (Y/Y)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.** Ready for user verdict on 2026-05-10 review pass.

### Framework prose (verbatim from analysis_framework.md)

> **Cost pressure: unit labour costs (Y/Y).** ULC = wage growth minus productivity growth, by definition. It is the consolidated inflation-pressure read since 2% inflation is consistent with ULC growth around 2% at trend productivity. Compare ULC growth to the 2% target and to the wage measures: implied productivity = wage Y/Y minus ULC Y/Y. When implied productivity matches BoC's ~1% trend assumption (SAN 2025-14), wage growth and ULC are telling the same story; when implied productivity is well below 1%, wage gains are not being matched by output gains and ULC is the binding pressure on prices even when wages look moderate. Use LFS-Micro (composition-adjusted) as the cleaner wage input for this comparison.

Threshold bullets:

> **ULC Y/Y ≈ 2%** = consistent with the 2% inflation target at trend productivity; **ULC Y/Y > 3%** = labour-cost pressure inconsistent with target absent a productivity boom; **implied productivity (LFS-Micro Y/Y − ULC Y/Y) ≈ 1%** = aligned with BoC's trend assumption (SAN 2025-14), well below 1% = wage gains outrunning output.

### Verification verdict

**PARTIALLY VERIFIED — mix per sub-claim.** The ULC = wages-net-of-productivity framing is anchored in BoC publications. The "~1% trend productivity" is an inexact characterisation of SAN 2025-14, which puts trend labour productivity at **1.2% in Scenario 1 (baseline)** with a Scenario 2 (tariff-shock) downside of 0.2–0.8%. The 3% ULC threshold is **UNSOURCED** — analyst synthesis. The "LFS-Micro = cleaner wage input" claim is supported in substance but the BoC's own wording is "smoother" / "reduced volatility," not "cleaner."

### Source 1 — BoC Wages and costs: Definitions, graphs and data

**URL:** https://www.bankofcanada.ca/rates/indicators/capacity-and-inflation-pressures/wages-costs-definitions/

**Direct quote (ULC):** *"Unit labour cost is the labour cost per unit of output. It is calculated as the ratio of labour compensation to real value added."*
**Alternative framing on same page:** *"It is also the equivalent of the ratio of labour compensation per hour worked to labour productivity."*
**Direct quote (LFS-Micro):** *"The LFS-Micro is a measure of underlying wage growth derived from the Labour Force Survey (LFS) microdata. It removes the composition effects from the average hourly earnings in the LFS, yielding a wage measure with reduced volatility and a better relationship with labour market fundamentals."*

**Verdict:** VERIFIED — supports the identity (the BoC's ratio framing is mathematically equivalent to "wage growth minus productivity growth" in Y/Y log terms) and supports the LFS-Micro composition-adjustment claim. Does **not** explicitly link ULC to the 2% target on this page.

### Source 2 — SAN 2025-14, "Potential output in Canada: 2025 assessment"

**URL:** https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-14/

**Direct quotes (TLP figures):**
- Scenario 1 (baseline): 1.2% for each of 2025, 2026, 2027 (with prior April 2024 vintage in parentheses: 0.8, 0.9, 1.0).
- Scenario 2 (tariff shock): 2025 = 0.5%, 2026 = 0.2%, 2027 = 0.8%.
- *"TLP growth picks up in 2025 and remains relatively stable over the scenario horizon."*

**Verdict:** PARTIALLY VERIFIED — confirms SAN 2025-14 is the right citation, but the framework's "~1%" understates Scenario 1 (1.2%) and Scenario 2 is *tariff-shock-specific*, not a generic "structurally weak productivity" baseline. The note also makes **no statement** linking TLP to the 2% inflation target — that linkage is the analyst's, not SAN 2025-14's.

### Source 3 — SAN 2024-23, "Beyond the averages: Measuring underlying wage growth using Labour Force Survey microdata"

**URL:** https://www.bankofcanada.ca/2024/10/staff-analytical-note-2024-23/

**Direct quotes:**
- *"we introduce a new measure of underlying wage growth that we call LFS-Micro. This measure works within the limitations of the publicly available microdata from the LFS to calculate a measure of underlying wage growth that is separate from shifts in the composition of the Canadian workforce."*
- *"Compared with other measures, LFS-Micro provides a much smoother estimate of wage growth that is more representative of underlying wage pressures."*
- *"Wage growth is a key indicator that central banks monitor because labour costs are an important component of production costs and inflation."*

**Methodology note:** Uses Oaxaca-Blinder decomposition; composition-adjusted wage growth was 3.9% Jan–Aug 2024 vs. 5.1% headline raw LFS.

**Verdict:** VERIFIED for the composition-adjustment / underlying-wage-pressure claim. **The framework's word "cleaner" is not BoC vocabulary** — the SAN says "smoother" and "more representative of underlying wage pressures." The note **does not** describe LFS-Micro as the BoC's "preferred" measure; it presents it as a new staff tool.

### Source 4 — Macklem, "Toward a virtuous circle for productivity" speech, Nov 19, 2025

**URL:** https://www.bankofcanada.ca/2025/11/toward-a-virtuous-circle-for-productivity/

**Direct quotes:**
- *"The most important labour cost for a business isn't the hourly wage that it pays its workers. What matters more is what we refer to as unit labour costs—that is, how much it costs in wages to produce a single unit of output."*
- *"when wage growth is accompanied by an increase in productivity, it has less of an impact on unit labour costs, so it is less inflationary."*
- *"when productivity is strong, businesses can keep their prices stable even if they raise wages."*

**Verdict:** VERIFIED for the qualitative ULC = wages-net-of-productivity framing as BoC-stated. Does **not** quantify a wage-or-ULC threshold consistent with 2% inflation in this speech.

### Source 5 — Macklem MPR press conference opening statement, April 12, 2023

**URL:** https://www.bankofcanada.ca/2023/04/opening-statement-2023-04-12/

**Reported quote (widely cited via secondary sources, retrieved 2026-05-09):** *"Wage growth has been running at four to five per cent and unless there's a surprising acceleration in productivity, that's not consistent with two per cent inflation."*

**Methodology note:** Sub-agent retrieved this quote via web search of secondary sources; did not independently fetch the BoC opening-statement page to confirm the exact wording. **User should re-verify against the primary URL before quoting.**

**Verdict:** PROVISIONALLY VERIFIED — supports the qualitative claim that wage growth materially above trend productivity is "not consistent with" 2% inflation. The framework prose does not currently use this quote, but it is the strongest single primary-source anchor for the 2%-target linkage and could be added.

### Defects flagged

1. **Defect 3 (unsourced threshold) — `ULC Y/Y > 3%` bullet.** No BoC publication located states that ULC growth above 3% is the line for "labour-cost pressure inconsistent with target." Analyst synthesis dressed as canonical.
2. **"~1% trend productivity" understates SAN 2025-14.** Actual Scenario 1 is 1.2%; Scenario 2 dips to 0.2–0.8% under tariff shock. Recommend rewording to "~1.2% trend assumption (SAN 2025-14, Scenario 1; downside scenarios materially lower)."
3. **"Cleaner wage input" wording not in source.** SAN 2024-23 says "smoother" / "more representative." Minor vocabulary alignment.
4. **Implicit threshold "ULC ≈ 2% = consistent with 2% target" depends on assumed productivity.** With BoC's 1.2% TLP, an inflation-consistent wage path is ~3.2% and an inflation-consistent ULC is ~2% — so the identity holds, but the framework should make explicit that the "2% ULC = 2% inflation" framing already assumes the productivity number it later describes. Currently reads circularly.
5. **No fabricated quotes** in the prose itself.
6. **No US-transferred heuristic.** ULC = wage − productivity is a universal accounting identity.

### Open questions for user review

1. Soften "~1%" to "~1.2% (scenario-dependent)"? Or specify "Scenario 1 = 1.2%, downside scenarios as low as 0.2–0.8%"?
2. Drop the `ULC Y/Y > 3%` bullet, or anchor it. Either find a BoC source for that threshold or rewrite as analyst judgment.
3. Add the April 2023 Macklem opening-statement quote as the explicit anchor for the 2%-target linkage? It would close the gap that no primary source currently quantifies the wage-target relationship in the way the framework asserts.

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: Update "~1% trend productivity" to reflect SAN 2025-14 Scenario 1 = 1.2% with downside-scenario caveat**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
When implied productivity matches BoC's ~1% trend assumption (SAN 2025-14), wage growth and ULC are telling the same story; when implied productivity is well below 1%, wage gains are not being matched by output gains and ULC is the binding pressure on prices even when wages look moderate.
```

`new_string`:
```
When implied productivity matches BoC's trend assumption (SAN 2025-14 Scenario 1 baseline = 1.2%; downside scenarios materially lower), wage growth and ULC are telling the same story; when implied productivity is well below trend, wage gains are not being matched by output gains and ULC is the binding pressure on prices even when wages look moderate.
```

*Reason:* Aligns the framework with SAN 2025-14's actual baseline figure (1.2%) instead of the imprecise "~1%" rounding; flags that downside scenarios are scenario-specific rather than a generic structural claim.
*Source:* https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-14/ — Table A-1 reports trend labour productivity growth at 1.2% (Scenario 1, baseline, 2025) and 0.5% (Scenario 2, downside, 2025).

**Patch 2: Replace "cleaner wage input" with BoC's actual vocabulary ("smoother / more representative")**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
Use LFS-Micro (composition-adjusted) as the cleaner wage input for this comparison.
```

`new_string`:
```
Use LFS-Micro (composition-adjusted) as the smoother, more representative wage input for this comparison (SAN 2024-23).
```

*Reason:* "Cleaner" is not BoC vocabulary; SAN 2024-23 describes LFS-Micro as "smoother" and "more representative of underlying wage pressures." Aligning to the canonical wording.
*Source:* https://www.bankofcanada.ca/2024/10/staff-analytical-note-2024-23/ — *"Compared with other measures, LFS-Micro provides a much smoother estimate of wage growth that is more representative of underlying wage pressures."*

*Verification log change* (in this file): mark this claim's verdict line with "(patches 1–2 proposed 2026-05-09; awaiting user accept/reject)" prefix.

**Judgment item (no patch proposed):** ULC Y/Y > 3% threshold is unsourced — needs user decision on whether to drop the bullet, anchor it to a BoC source if one can be located, or rewrite as explicit analyst judgment.

---

## Claim 5: Wage growth across measures

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.** Ready for user verdict on 2026-05-10.

### Framework prose (verbatim)

> **Wage growth across measures (LFS all, LFS permanent, SEPH, LFS-Micro).** Look at dispersion: when measures cluster, the signal is consistent; when they diverge, the choice of measure matters. LFS-Micro typically runs *below* raw LFS in Canada because workforce composition has been shifting toward higher-paid workers (SAN 2024-23 reports composition-adjusted wage growth at 3.9% vs. raw LFS at 5.1% in early 2024). When LFS-Micro < raw LFS — the dominant Canadian pattern — the read is "composition is flattering the headline wage number," and the underlying wage dynamic is softer than raw averages suggest. The reverse case (LFS-Micro > raw LFS, indicating composition dragging the average down while underlying wages rise) is theoretically valid but historically rare for Canada.

Threshold bullet:

> **LFS-Micro typically below raw LFS in Canada** — when this holds, raw LFS overstates underlying wage pressure; when LFS-Micro is unexpectedly close to or above raw LFS, that itself is a signal worth flagging.

### Verification verdict

**PARTIALLY VERIFIED.** The SAN 2024-23 numbers, the directional claim, and the multi-year framing are directly supported. **However, the framework's enumeration of "the four measures" (LFS all, LFS permanent, SEPH, LFS-Micro) does NOT match the BoC's own Wages-and-costs page**, which lists LFS-AHE, SEPH-AHE, **National Accounts hourly wages**, and LFS-Micro — i.e., no separate "LFS permanent" line, and a National Accounts measure the framework omits. The "January–August 2024" window is loosely glossed as "early 2024." The composition shift is more narrowly attributable to *occupational mix* (rising share in high-wage occupations), not generic "higher-paid workers."

### Source 1 — SAN 2024-23 (Bounajm, Devakos, Galassi, October 2024)

**URL:** https://www.bankofcanada.ca/2024/10/staff-analytical-note-2024-23/
**Title:** "Beyond the averages: Measuring underlying wage growth using Labour Force Survey microdata"

**Direct quotes (retrieved 2026-05-09):**
- *"We find that composition-adjusted wage growth averaged 3.9% between January and August 2024…significantly below the average wage growth of 5.1%"*
- *"Most upward pressure in average wage growth…comes from changes in the occupational makeup of the labour market…increasing share working in high-wage occupations."*
- *"In general, LFS-Micro wage growth is lower than the LFS average wage growth measure over the full sample period."*
- *"This suggests that compositional changes in the labour market over the past few decades have generally contributed positively to wage growth."*

**Verdict:** VERIFIED for (a) the 3.9% / 5.1% pair, (b) the directional claim, (c) the composition framing — though the SAN's actual attribution is *occupational* composition, narrower than "workforce composition."

### Source 2 — BoC "Wages and costs: Definitions, graphs and data"

**URL:** https://www.bankofcanada.ca/rates/indicators/capacity-and-inflation-pressures/wages-costs-definitions/

**Measures listed verbatim:**
1. LFS-Micro
2. Labour Force Survey – Average Hourly Earnings ("Usual wages or salary of employees at their main job before taxes")
3. Survey of Employment, Payrolls and Hours – Average Hourly Earnings
4. National Accounts – Hourly Wages and Salaries

**Verdict:** **Contradicts the framework's enumeration.** The BoC's own canonical list does not contain a separate "LFS permanent employees" line, and it *does* contain a National Accounts hourly wages measure that the framework omits. SEPH is still listed — it has not been retired. The framework's "four measures" list appears to be analyst synthesis.

### Defects flagged

- **Defect 5 (rigid n-tuple decoder) / Defect 4 (mis-listed indicator):** The framework's "four measures" list reads as canonical but doesn't match the BoC's published taxonomy. "LFS permanent" is not a separate BoC headline measure; National Accounts hourly wages is, but the framework omits it.
- **No fabricated quotes** — 3.9% / 5.1% pair and directional language reproduce SAN 2024-23 accurately.
- **No US heuristic transfer.**
- **No unsourced threshold.**

### Open questions for user review

1. Reconcile the four-measure list with the BoC Wages-and-costs page: drop "LFS permanent," add "National Accounts hourly wages"? Or keep "LFS permanent" because the dashboard fetches it explicitly (project-state-driven rather than BoC-canonical)?
2. Tighten the composition framing to *"occupational composition has been shifting toward high-wage occupations"*?
3. Use the precise "January–August 2024" window instead of "early 2024"?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: Tighten "early 2024" to the precise SAN 2024-23 window "January–August 2024"**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
LFS-Micro typically runs *below* raw LFS in Canada because workforce composition has been shifting toward higher-paid workers (SAN 2024-23 reports composition-adjusted wage growth at 3.9% vs. raw LFS at 5.1% in early 2024).
```

`new_string`:
```
LFS-Micro typically runs *below* raw LFS in Canada because the occupational composition of the labour market has been shifting toward high-wage occupations (SAN 2024-23 reports composition-adjusted wage growth at 3.9% vs. raw LFS at 5.1% over January–August 2024).
```

*Reason:* Combines two mechanical fixes: (a) the SAN's actual time window is "between January and August 2024," not "early 2024"; (b) SAN 2024-23's attribution is *occupational* composition shifting toward *high-wage occupations*, not generic "higher-paid workers."
*Source:* https://www.bankofcanada.ca/2024/10/staff-analytical-note-2024-23/ — *"We find that composition-adjusted wage growth averaged 3.9% between January and August 2024…significantly below the average wage growth of 5.1%"* and *"Most upward pressure in average wage growth…comes from changes in the occupational makeup of the labour market…increasing share working in high-wage occupations."*

*Verification log change* (in this file): mark this claim's verdict line with "(patch 1 proposed 2026-05-09; awaiting user accept/reject)" prefix.

**Judgment item (no patch proposed):** Four-measure list ("LFS all, LFS permanent, SEPH, LFS-Micro") doesn't match BoC Wages-and-costs page (which has LFS-AHE, SEPH-AHE, National Accounts hourly wages, LFS-Micro). Needs user decision on whether to align with BoC taxonomy (drop "LFS permanent," add "National Accounts hourly wages") or keep the project-state list because the dashboard fetches `lfs_wages_permanent`.

---

## Claim 6: Wage growth vs. ~3% soft threshold

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.** Ready for user verdict on 2026-05-10.

### Framework prose (verbatim)

> **Wage growth vs. ~3% soft threshold.** The identity is target inflation = wage growth − productivity. With BoC trend productivity assumed at roughly 1% (SAN 2025-14 places it at ~1.2% in baseline scenarios but acknowledges Canada's structurally weak productivity, with downside scenarios at ~0.5%), wage growth above ~3% is broadly inconsistent with the 2% inflation target. The Bank does not publish a fixed 3% threshold but articulates the identity in MPRs ([October 2024 In Focus](https://www.bankofcanada.ca/publications/mpr/mpr-2024-10-23/in-focus-1/): "Nominal wage growth in Canada is around 4%, above the level of productivity growth plus 2% inflation"). Treat 3% as a soft anchor, not a hard line; recent productivity weakness pushes the implied threshold lower.

Threshold bullet:

> **Wage growth ≈ 3%** = soft threshold for consistency with the 2% inflation target, assuming ~1% trend productivity (BoC scenarios bracket 0.5–1.2% depending on environment). Recent productivity weakness pushes the implied threshold below 3%.

### Verification verdict

**VERIFIED with caveat.** Both numerical anchors (1.2% baseline, 0.5% downside in SAN 2025-14) and the MPR Oct 2024 In Focus quote are confirmed verbatim. The "3% soft threshold" is analyst synthesis derived from the identity, but the framework explicitly tells the reader the BoC doesn't publish 3% — honest synthesis.

### Source 1 — SAN 2025-14 (Abraham, Brouillette, Chernoff, Hajzler, Houle, Kim, Taskin, June 2025)

**URL:** https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-14/
**Title:** "Potential output in Canada: 2025 assessment"

**Direct content:** Table A-1 reports trend labour productivity growth at 1.2% (Scenario 1, baseline, 2025) and 0.5% (Scenario 2, downside, 2025); the previous April 2024 assessment carried 0.8%. Scenario 2 reflects "broad-based tariffs that reduce trade and create resource misallocation inefficiencies."

**Verdict:** Both numbers confirmed. **Caveat:** Scenario 2's downside is specifically a *tariff* scenario, not a generic "structurally weak productivity" baseline as the framework prose loosely implies.

### Source 2 — MPR October 2024, In Focus

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2024-10-23/in-focus-1/
**Title:** "The factors behind the rise in unemployment"

**Direct quote (verbatim):** *"Nominal wage growth in Canada is around 4%, above the level of productivity growth plus 2% inflation."*

**Verdict:** Quote confirmed verbatim. **Minor framing caveat:** the framework labels this "October 2024 In Focus" generically; the In Focus is actually titled "The factors behind the rise in unemployment," and the wage-productivity sentence is in its "Wage growth is expected to ease" subsection.

### Source 3 — Cross-check (BoC Wages-and-costs page; Macklem May 2023 speech)

**URLs:**
- https://www.bankofcanada.ca/rates/indicators/capacity-and-inflation-pressures/wages-costs-definitions/
- https://www.bankofcanada.ca/2023/05/staying-course-price-stability/

**Findings:** Wages-and-costs page does not name 3% as a threshold. Macklem May 2023 speech: *"persistent wage growth in the 4% to 5% range would make it difficult to achieve the 2% inflation target"* — supports the qualitative claim, doesn't anchor 3%.

**Verdict:** Supports the framework's negative claim ("BoC doesn't publish a 3% threshold").

### Defects flagged

- **Threshold sourcing — handled honestly.** The framework's "3% soft threshold" is analyst synthesis derived from the identity, but the framework tells the reader the BoC doesn't publish 3%. Not a defect; this is the right way to handle it.
- **Minor framing risk:** Citing SAN 2025-14's 0.5% as "Canada's structurally weak productivity" is loose — the 0.5% is the tariff-scenario downside. Tighten to "downside scenarios (e.g. broad-based tariffs) at ~0.5%."
- **Minor framing risk:** Hyperlink anchor "October 2024 In Focus" is generic; consider naming the In Focus title.
- **No fabricated quote.** MPR Oct 2024 quote is verbatim.
- **No US heuristic transfer.**

### Open questions for user review

1. Specify that the 0.5% downside is the tariff-scenario number, not a generic structural-weakness estimate?
2. Re-label the In Focus link with its actual title ("The factors behind the rise in unemployment")?
3. The "recent productivity weakness pushes the implied threshold lower" line is analyst inference. Add explicit "(analyst inference from the identity)" tag, or is the surrounding "treat 3% as a soft anchor, not a hard line" wording sufficient?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: Clarify SAN 2025-14 0.5% downside is tariff-scenario-specific, not generic**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
With BoC trend productivity assumed at roughly 1% (SAN 2025-14 places it at ~1.2% in baseline scenarios but acknowledges Canada's structurally weak productivity, with downside scenarios at ~0.5%), wage growth above ~3% is broadly inconsistent with the 2% inflation target.
```

`new_string`:
```
With BoC trend productivity assumed at roughly 1% (SAN 2025-14 places it at ~1.2% in the Scenario 1 baseline; downside scenarios such as the broad-based-tariff Scenario 2 fall to ~0.5%), wage growth above ~3% is broadly inconsistent with the 2% inflation target.
```

*Reason:* SAN 2025-14's 0.5% number is the Scenario 2 (broad-based tariff shock) figure, not a generic structural-weakness estimate. The current prose loosely conflates the two.
*Source:* https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-14/ — Scenario 2 reflects "broad-based tariffs that reduce trade and create resource misallocation inefficiencies"; Table A-1 reports TLP at 1.2% (Scenario 1) and 0.5% (Scenario 2, 2025).

**Patch 2: Specify the October 2024 In Focus link with its actual title**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
The Bank does not publish a fixed 3% threshold but articulates the identity in MPRs ([October 2024 In Focus](https://www.bankofcanada.ca/publications/mpr/mpr-2024-10-23/in-focus-1/): "Nominal wage growth in Canada is around 4%, above the level of productivity growth plus 2% inflation").
```

`new_string`:
```
The Bank does not publish a fixed 3% threshold but articulates the identity in MPRs ([MPR October 2024 In Focus, "The factors behind the rise in unemployment"](https://www.bankofcanada.ca/publications/mpr/mpr-2024-10-23/in-focus-1/): "Nominal wage growth in Canada is around 4%, above the level of productivity growth plus 2% inflation").
```

*Reason:* The In Focus has a specific title ("The factors behind the rise in unemployment") and the wage-productivity sentence sits in its "Wage growth is expected to ease" subsection. Naming the In Focus correctly is a one-line precision fix.
*Source:* https://www.bankofcanada.ca/publications/mpr/mpr-2024-10-23/in-focus-1/ — In Focus titled "The factors behind the rise in unemployment"; quote *"Nominal wage growth in Canada is around 4%, above the level of productivity growth plus 2% inflation"* verified verbatim.

*Verification log change* (in this file): mark this claim's verdict line with "(patches 1–2 proposed 2026-05-09; awaiting user accept/reject)" prefix.

---

## Claim 7: Wage growth vs. services CPI

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Patch 1 applied 2026-05-09: citation updated from "Macklem April 2023" to MPR July 2024 In Focus 'Drivers of inflation in core goods and services.' Not user-reviewed.** Ready for user verdict on 2026-05-10.

### Framework prose (verbatim)

> **Wage growth vs. services CPI.** The BoC tracks wage growth as a leading indicator for services inflation persistence (Macklem April 2023; SAN 2024-23). When wage growth persistently exceeds services CPI, this indicates labour cost pressures are not yet fully reflected in prices — consistent with incomplete pass-through, lagged price adjustment, or margin compression. Note that "margin absorption" is *our* shorthand; the BoC's framing is the more nuanced one above. The composition-adjusted LFS-Micro shows the strongest correlation with services-ex-shelter (SAN 2024-23).

Threshold bullet:

> **Wage growth > services CPI** = leading indicator that labour-cost pressures are not yet fully passing through to services prices.

### Verification verdict

**PARTIALLY VERIFIED, with citation drift and synthesised mechanisms.** The LFS-Micro / services-ex-shelter correlation claim from SAN 2024-23 is verified verbatim. **The "Macklem April 2023" attribution for the leading-indicator framing is weak** — neither the April 12 MPR opening statement nor the April 18 House of Commons opening statement explicitly describes wages as a "leading indicator" for services inflation. The cleanest BoC source for that framing is **MPR July 2024 In Focus on drivers of core inflation**, which the framework should cite instead. The mechanisms list ("incomplete pass-through, lagged price adjustment, margin compression") is framework synthesis — none of these phrases appear in either SAN 2024-23 or April 2023 Macklem statements.

### Source 1 — SAN 2024-23 (LFS-Micro / services-ex-shelter)

**URL:** https://www.bankofcanada.ca/2024/10/staff-analytical-note-2024-23/

**Direct quote:** *"Theoretically, changes in wage growth should be closely related to changes in inflation because labour is a key production input. LFS-Micro has a substantially strong correlation with measures of inflation. In particular, it shows the strongest correlation with services excluding shelter, which is a component of the consumer price index (CPI) basket of goods and services that is usually labour intensive."*

**Verdict:** VERIFIED for the correlation claim. Note: the SAN frames this descriptively (correlation observed in historical data); it does **not** claim a leading/predictive relationship and contains no language about "leading indicator," pass-through, margin compression, or persistence. The framework's leading-indicator gloss is an extrapolation.

### Source 2 — Macklem MPR press conference opening statement, April 12, 2023

**URL:** https://www.bankofcanada.ca/2023/04/opening-statement-2023-04-12/

**Direct quotes:**
- *"Continued strong demand for services and the still-tight labour market are putting upward pressure on many services prices."*
- *"Services price inflation and wage growth need to moderate."*

**Verdict:** PARTIALLY SUPPORTS, does not say "leading indicator." Concurrent-pressure framing.

### Source 3 — Macklem House of Commons opening statement, April 18, 2023

**URL:** https://www.bankofcanada.ca/2023/04/opening-statement-180423/

**Direct quotes:** *"wages continue to grow in the 4% to 5% range"*; *"Continued strong demand and the tight labour market are putting upward pressure on many services prices"*; *"services price inflation and wage growth need to moderate"*

**Verdict:** Same as Source 2 — concurrent-pressure framing, no explicit leading-indicator framing.

### Source 4 — MPR July 2024, "Drivers of inflation in core goods and services" (the actually-supportive citation the framework should be using)

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2024-07/in-focus-1/

**Direct quotes:**
- *"While this measure of wage growth has been volatile, it has fallen from its peak. This suggests that inflation in services excluding shelter will moderate if wage growth continues to ease."*
- *"Microdata from the Labour Force Survey (LFS) also suggest that elevated growth in labour costs may have been putting upward pressure on inflation."*

**Verdict:** **This IS leading-indicator framing** ("if wages ease, services-ex-shelter will moderate"). It is the cleanest BoC source for the framework's claim. **Recommend swapping the citation.**

### Defects flagged

- **Defect type 4 (mis-attributed source):** The "Macklem April 2023" attribution does not contain the specific leading-indicator framing the prose implies. Reasonable inference from "wages need to moderate" but not what the speech actually says.
- **Defect type 5 (analyst synthesis presented as canonical):** "Incomplete pass-through, lagged price adjustment, or margin compression" is framework-synthesised. The framework already hedges "margin absorption" but does not similarly hedge the three-mechanism list itself.
- **No fabricated quotes** — the framework paraphrases rather than placing words in Macklem's mouth.
- **No US heuristic transfer.**

### Open questions for user review

1. Swap the "Macklem April 2023" citation for **MPR July 2024 In Focus on core inflation drivers**, which contains explicit leading-indicator language?
2. Hedge the three-mechanism list as analyst synthesis, like "margin absorption" already is?
3. SAN 2024-23's correlation is **contemporaneous, not leading**. Keep the leading-indicator framing or shift to a correlation framing for the SAN-citation half?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: Swap Macklem April 2023 attribution for MPR July 2024 In Focus on drivers of core inflation**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
**Wage growth vs. services CPI.** The BoC tracks wage growth as a leading indicator for services inflation persistence (Macklem April 2023; SAN 2024-23).
```

`new_string`:
```
**Wage growth vs. services CPI.** The BoC tracks wage growth as a leading indicator for services inflation persistence ([MPR July 2024 In Focus, "Drivers of inflation in core goods and services"](https://www.bankofcanada.ca/publications/mpr/mpr-2024-07/in-focus-1/); SAN 2024-23).
```

*Reason:* Neither Macklem's April 12 MPR opening statement nor his April 18 House of Commons opening statement contains explicit leading-indicator framing — both use concurrent-pressure language ("services price inflation and wage growth need to moderate"). MPR July 2024 In Focus on drivers of core inflation contains the explicit leading-indicator construction ("inflation in services excluding shelter will moderate if wage growth continues to ease"), making it the correct citation.
*Source:* https://www.bankofcanada.ca/publications/mpr/mpr-2024-07/in-focus-1/ — *"While this measure of wage growth has been volatile, it has fallen from its peak. This suggests that inflation in services excluding shelter will moderate if wage growth continues to ease."*

*Verification log change* (in this file): mark this claim's verdict line with "(patch 1 proposed 2026-05-09; awaiting user accept/reject)" prefix.

**Judgment item (no patch proposed):** Three-mechanism list ("incomplete pass-through, lagged price adjustment, or margin compression") is framework synthesis with no source. Needs user decision on whether to hedge it like "margin absorption" already is, drop it, or leave it as the framework's own analytical scaffolding.

**Judgment item (no patch proposed):** SAN 2024-23's correlation is contemporaneous, not leading. Needs user decision on whether to keep the leading-indicator framing for both citations or split the framing between MPR July 2024 (leading) and SAN 2024-23 (contemporaneous correlation).

---

## Claim 8: Real wages = wage Y/Y minus headline CPI Y/Y

### Provenance tier

**Tier 3 — resolved 2026-05-09. Fabrication confirmed by user. Patch 1 applied 2026-05-09: fabricated quote deleted, replaced with actual MPR Oct 2024 sentence; expanded to per-measure framing with live tier classifications in `analyze.py`.**

### Framework prose (verbatim)

> **Real wages: wage Y/Y minus headline CPI Y/Y.** Standard BoC framing (MPR October 2024: "1.6% annual real wage gains since 2023"). Headline CPI is the standard deflator; positive real wages = workers gaining purchasing power; negative = falling behind inflation.

Threshold bullet:

> **Real wage > 0** = workers gaining purchasing power; **real wage < 0** = losing it.

### Verification verdict

**UNSOURCED, with one likely-fabricated quote.** The bare arithmetic definition is uncontroversial, but the specific MPR Oct 2024 quote does not appear in the document, and the "standard BoC framing" / "headline CPI is the standard deflator" assertions are overstated.

### Source 1 — MPR October 2024 (overview / Canadian conditions / outlook chapters)

**URLs:**
- https://www.bankofcanada.ca/publications/mpr/mpr-2024-10-23/
- https://www.bankofcanada.ca/publications/mpr/mpr-2024-10-23/canadian-conditions/
- https://www.bankofcanada.ca/publications/mpr/mpr-2024-10-23/canadian-outlook/

**Sub-agent search:** the exact phrase *"1.6% annual real wage gains since 2023"* and any "1.6%" figure attached to real wages.

**Found:** the only "1.6%" in the October 2024 MPR HTML chapters retrieved is **headline CPI inflation in September 2024**: *"Inflation declined to 1.6% in September."* The MPR's actual real-wage framing compares real wages to **productivity**, not to a 2023 baseline: *"real wage growth — an important factor in the costs of producing many of these services — remains elevated when compared with growth in productivity."*

**Verdict:** **The framework's quoted "1.6% annual real wage gains since 2023" attributed to MPR October 2024 was not found in the HTML chapters.** Sub-agent could not text-extract the PDF; cannot 100% rule out a chart caption / footnote. Most likely the figure conflates the September 2024 headline-CPI figure (1.6%) with real wages.

### Source 2 — BoC "Wages and costs: Definitions" indicator page

**URL:** https://www.bankofcanada.ca/rates/indicators/capacity-and-inflation-pressures/wages-costs-definitions/

**Finding:** Defines nominal wage measures (LFS-Micro, LFS AHE, SEPH AHE, National Accounts hourly wages, ULC). Contains **no definition of "real wages"** and **does not specify a deflator** — neither headline nor core CPI is named as the standard.

**Verdict:** Does not support the framework's "headline CPI is the standard deflator" claim.

### Source 3 — MPR October 2024 framing of real wages

**URL:** https://www.bankofcanada.ca/publications/mpr/mpr-2024-10-23/canadian-conditions/

**Direct quote:** *"real wage growth — an important factor in the costs of producing many of these services — remains elevated when compared with growth in productivity."*

**Verdict:** When the BoC discusses real wages in Oct 2024, the comparator is **productivity**, not a 2023 baseline. The framework's claim is not the BoC's framing in this report.

### Defects flagged

1. **CRITICAL: Defect type 1 (fabricated quote).** *"1.6% annual real wage gains since 2023"* attributed to MPR October 2024 was not found in any HTML chapter retrieved. High suspicion of fabrication or conflation with the September 2024 headline-CPI figure. **This is the most serious defect identified across Claims 4–10.** User to confirm against the PDF before any decision.
2. **Defect type 3 (unsourced threshold / convention):** "Headline CPI is the standard deflator" is not supported by the BoC's wages-and-costs page, which doesn't specify a deflator. The BoC's published real-wage discussions compare to productivity, not a single CPI-deflated number.
3. **Defect type 5 (analyst synthesis presented as canonical):** "Standard BoC framing" overstates the case.
4. **No US heuristic transfer.**

### Open questions for user review

1. **Critical:** confirm the MPR October 2024 quote *"1.6% annual real wage gains since 2023"* exists somewhere (PDF chart caption / footnote), or remove it as fabricated.
2. Soften "headline CPI is the standard deflator" to "headline CPI is one common deflator; the BoC also discusses real wages relative to productivity"?
3. Keep the bare "real wage > 0 = gaining purchasing power" framing, or add the productivity-comparator framing the BoC actually uses in MPRs?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: Delete the un-located "1.6% annual real wage gains since 2023" quote and reword without it**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
**Real wages: wage Y/Y minus headline CPI Y/Y.** Standard BoC framing (MPR October 2024: "1.6% annual real wage gains since 2023"). Headline CPI is the standard deflator; positive real wages = workers gaining purchasing power; negative = falling behind inflation.
```

`new_string`:
```
**Real wages: wage Y/Y minus headline CPI Y/Y.** Headline CPI is one common deflator; the BoC also discusses real wages relative to productivity (MPR October 2024: *"real wage growth — an important factor in the costs of producing many of these services — remains elevated when compared with growth in productivity"*). Positive real wages = workers gaining purchasing power; negative = falling behind inflation.
```

*Reason:* Combines two mechanical fixes: (a) the *"1.6% annual real wage gains since 2023"* quote was not located in MPR October 2024 HTML chapters and is likely a fabrication or conflation with the September 2024 headline-CPI figure (1.6%) — deleting per fabricated-quote handling; (b) the BoC's published real-wage discussions in MPR October 2024 explicitly use productivity as the comparator, not a 2023-baseline real-wage gain, so substituting the actual MPR sentence preserves the BoC anchor without inventing one. The "headline CPI is *one* common deflator" softening is required because the BoC Wages-and-costs page does not name a standard deflator.
*Source:* https://www.bankofcanada.ca/publications/mpr/mpr-2024-10-23/canadian-conditions/ — verbatim quote *"real wage growth — an important factor in the costs of producing many of these services — remains elevated when compared with growth in productivity."*

*Verification log change* (in this file): mark this claim's verdict line with "(patch 1 proposed 2026-05-09; awaiting user accept/reject — replaces fabricated quote)" prefix.

---

## Claim 9: Coverage gaps (what the framework doesn't track but BoC does)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.** Ready for user verdict on 2026-05-10.

### Framework prose (verbatim)

> **What this framework doesn't track but BoC explicitly does.** Average hours worked (NSA-only monthly; flagged for the next labour scope review), involuntary part-time rate (annual cadence too coarse for this dashboard), newcomer and youth unemployment composition, and regional decompositions (Toronto/Vancouver vs. rest of Canada). Each is part of how BoC reads the labour market. The remaining omissions are narrower than they used to be — utilization (employment rate, participation rate), tightness (vacancies, V/U), and cost pressure (ULC) are now wired in — but conclusions touching demographic composition or regional dispersion should still be flagged as partial.

### Verification verdict

**PARTIALLY VERIFIED.** Three of four named gaps (avg hours, involuntary PT, newcomer/youth) are clearly tracked by BoC — verified against SAN 2024-8 (predecessor benchmark paper) and the June 2024 Macklem speech. **The "Toronto/Vancouver vs. rest of Canada" framing is NOT verified as BoC-canonical** — see defect below. The "now wired in" claim is verified against `data/`. SAN 2025-17's actual demographic decomposition is broader than the framework's pairing suggests.

### Source 1 — SAN 2024-8, "Benchmarks for assessing labour market health: 2024 update" (Apr 30, 2024)

**URL:** https://www.bankofcanada.ca/2024/04/staff-analytical-note-2024-8/

**Finding:** Table 1 lists average hours worked (total impact 0.17 pp on inflation) and involuntary part-time rate (0.37 pp), described as *"a signal that people want to work more hours but there is insufficient demand."*

**Verdict:** VERIFIED — both indicators are explicit benchmark-dashboard members in the predecessor of SAN 2025-17.

### Source 2 — SAN 2025-17, "Benchmarks for assessing labour market health: 2025 update"

**URL:** https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-17/

**Finding:** Average hours worked and involuntary PT appear as *anticipated trade-impact channels* (*"A reduction in average hours worked is likely"*; *"This will likely increase the number of workers involuntarily working part-time"*) rather than in the headline benchmark charts. Demographic decomposition tracked: youth (15–24, by gender), prime-age (25–54, by gender), older (55+, by gender), public vs. private, low/mid/high-wage. Newcomers not separately analysed in this update; **no province/CMA breakdown.**

**Verdict:** PARTIAL — confirms BoC continues to use these as channels, but the 2025 note de-emphasises them relative to SAN 2024-8.

### Source 3 — Macklem, "Making the labour market work for everyone" (Jun 2024)

**URL:** https://www.bankofcanada.ca/2024/06/making-labour-market-work-everyone/

**Direct quotes:** *"the unemployment rate for newcomers to Canada is rising much faster than the overall rate"*; *"the unemployment rate for youth is almost 2 percentage points higher than it was in 2019"*.

**Regional finding:** This speech contains **no** regional decomposition — no Toronto, Vancouver, province, or CMA references beyond the speech location.

**Verdict:** VERIFIED for newcomer + youth as BoC-tracked channels.

### Source 4 — BoC Labour Market Definitions page

**URL:** https://www.bankofcanada.ca/rates/indicators/capacity-and-inflation-pressures/labour-market-definitions/

**Finding:** The BoC's headline indicators page lists unemployment rate, LMI composite, participation, employment growth, BOS labour shortage, BOS intensity of shortages. Average hours, involuntary PT, newcomer/youth, and regional breakdowns are NOT on this canonical page.

**Verdict:** Mixed — confirms these are second-tier indicators in BoC's published apparatus, which softens "BoC explicitly does" but does not contradict it.

### Source 5 — Project state check (`data/`)

**Verdict on "now wired in" claim:** VERIFIED. `data/` contains `employment_rate.csv`, `participation_rate.csv`, `job_vacancy_rate.csv`, `job_vacancy_level.csv`, `unit_labour_cost.csv`. V/U computed from `job_vacancy_level.csv` and `unemployment_level.csv`.

### Defects flagged

1. **Toronto/Vancouver vs. rest of Canada is NOT BoC-canonical.** Across SAN 2025-17, SAN 2024-8, the Macklem June 2024 speech, and the Labour Market Definitions page, no BoC labour-market regional decomposition along Toronto / Vancouver lines was found. BoC tends to decompose by age × gender × education × wage tier × sector, not geographically. **Likely analyst synthesis** (or accidentally imported from CMHC's Toronto/Vancouver supply-gap framing in the Housing section, where it is canonical). Same defect class as Claim 3's V/U > 1 = tight — heuristic asserted as canonical when the source is silent.
2. **"Average hours worked... NSA-only monthly" parenthetical may be inaccurate.** Worth a primary-source check before keeping.
3. **Indicator-naming-leak risk (per Claim 2 protocol):** Claim 9's prose names "average hours worked" and "involuntary part-time rate" while explicitly stating they are NOT tracked. Two readings: (a) safe because the prose is in framework not in a blurb prompt context, the model reads "doesn't track but BoC does" as a list to avoid claiming; (b) re-introduces the risk if any future blurb-prompt-injection forwards this section without disclaimer. **User's call.** Recommend the safer demotion (move named list to verification log only) unless user wants to keep the named list visible at framework level.
4. **"Each is part of how BoC reads the labour market" overstates headline-tier status.** The Labour Market Definitions page does not list these. They appear in SANs and speeches — real BoC content but not the headline indicator suite. Soften.
5. **No fabricated quotes** — the Macklem June 2024 quotes are verbatim.
6. **No US heuristic transfer.**

### Open questions for user review

1. Toronto/Vancouver framing — pasted-in placeholder from Housing section, or intended Labour-side citation? If the latter, primary source needed; if the former, replace with the actual BoC framing (no specific city pair, or the BOS regional-breakdown if it can be cited).
2. Demote the named "avg hours / involuntary PT" list to verification log only, per the Claim 2 indicator-naming-leak precedent? (Recommended.)
3. Specify SAN 2025-17 decomposition (gender × age × education × wage tier × public/private) instead of generic "demographic composition"?

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: Drop unsourced "Toronto/Vancouver vs. rest of Canada" regional pairing**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
newcomer and youth unemployment composition, and regional decompositions (Toronto/Vancouver vs. rest of Canada).
```

`new_string`:
```
newcomer and youth unemployment composition, and subnational variation.
```

*Reason:* No BoC labour-market source located decomposes along Toronto/Vancouver vs. rest-of-Canada lines — checked across SAN 2025-17, SAN 2024-8, the Macklem June 2024 speech, and the Labour Market Definitions page. BoC labour decompositions run age × gender × education × wage tier × sector, not by city. Likely accidentally imported from the Housing section's CMHC framing. Replacing with the generic "subnational variation" preserves the partial-coverage flag without asserting a specific city pair as canonical. (User may prefer a different replacement — flagged.)
*Source:* https://www.bankofcanada.ca/2025/06/staff-analytical-note-2025-17/ (no province/CMA breakdown); https://www.bankofcanada.ca/2024/06/making-labour-market-work-everyone/ (no Toronto/Vancouver references); https://www.bankofcanada.ca/rates/indicators/capacity-and-inflation-pressures/labour-market-definitions/ (no regional breakdown listed). Replacement is a deletion of the unsupported pairing rather than a swap to a sourced alternative; the user may prefer to substitute a specific BoC regional framing if one exists (e.g., BOS regional breakdown).

*Verification log change* (in this file): mark this claim's verdict line with "(patch 1 proposed 2026-05-09; awaiting user accept/reject)" prefix.

**Judgment item (no patch proposed):** "Average hours worked... NSA-only monthly" parenthetical accuracy needs primary-source check before keeping. User's call.

**Judgment item (no patch proposed):** Indicator-naming-leak risk — the prose names "average hours worked" and "involuntary part-time rate" while saying they are not tracked. Per Claim 2's precedent, user may want to demote the named list to verification log only. Not a clear-cut mechanical fix.

**Judgment item (no patch proposed):** "Each is part of how BoC reads the labour market" overstates headline-tier status (these are SAN/speech indicators, not on the Labour Market Definitions page). Softening is judgment about how strongly to characterize.

---

## Claim 10: What to surface (synthesis paragraph)

### Provenance tier

**Tier 2 — autonomously verified 2026-05-09. Not user-reviewed.** Ready for user verdict on 2026-05-10. **Contains a propagation defect from user-verified Claim 3 that needs immediate fix — see flag below.** **DEFERRED (2026-05-09 convention sweep): user explicitly requested deferral; V/U propagation logic not touched in this sweep.**

### Framework prose (verbatim)

> **What to surface:** Lead with what the labour market is *doing* — tightening, loosening, holding — anchored on the unemployment rate level + direction, framed against BoC's qualitative characterizations rather than a fixed NAIRU. Use the utilization pair (employment + participation) to distinguish layoff dynamics from labour-force-exit dynamics when their moves diverge. Surface tightness via the V/U ratio when it's clearly off balance — V/U well below 1 reinforces a slack read, V/U near or above 1 reinforces a tight read. Characterize wage growth: dispersion across measures, whether the central tendency is above or below the ~3% soft threshold, and whether LFS-Micro is meaningfully below raw LFS (the dominant Canadian pattern). Use ULC as the consolidated cost-pressure read when wages and productivity are telling different stories — implied productivity at or near 1% means wages and prices are roughly aligned with target; implied productivity well below 1% means ULC is the binding inflation pressure even when wages look moderate. Surface the wage-vs-services-CPI relationship as a leading indicator for services inflation persistence — the BoC-validated framing, not the older "margin absorption" shorthand. Note real wages when the gap is large in either direction. When demographic or regional decomposition would change the read, flag that the framework's view is partial.

### Verification verdict

**CONTESTED — contains a known-defect line that user-verified Claim 3 explicitly rejected.** Most of the synthesis paragraph is consistent with verified Claims 1–8, but the V/U sentence (*"V/U well below 1 reinforces a slack read, V/U near or above 1 reinforces a tight read"*) re-asserts the US-transferred heuristic that Claim 3's user-verification eliminated.

### PROMINENT FLAG — V/U threshold contradiction (propagation defect)

The synthesis paragraph contradicts user-verified Claim 3.

- **Synthesis says:** *"V/U well below 1 reinforces a slack read, V/U near or above 1 reinforces a tight read."*
- **User-verified Claim 3 (post-revision, Tier 3 provisional):** *"V/U < 0.30 = slack; 0.30–0.45 = below balance; 0.45–0.60 = approaching balance / starting to be tight; 0.60–0.80 = tight; > 0.80 = exceptionally tight."*

The "near or above 1 = tight" line in the synthesis paragraph is the **exact US-transferred heuristic** Claim 3 explicitly identified, sourced (US JOLTS 2022 peak ≈ 2.0 vs. Canadian 2022 peak ≈ 0.99), and rejected. The synthesis paragraph likely pre-dates the Claim 3 revision (or the revision didn't propagate). **Recommend immediate edit before any blurb regen.** Replacement options:

> *"Surface tightness via the V/U ratio against its Canadian-calibrated bands — V/U below 0.30 reinforces a slack read; 0.45–0.60 marks the BoC-tightening-cycle band; above 0.80 marks 2022-style exceptional tightness."*

Or, more compact:

> *"Surface tightness via the V/U ratio against its Canadian-calibrated bands (Claim 3 thresholds) — directionally informative, with the standing caveat that the Beveridge curve's position has shifted post-COVID."*

### Per-item mapping to verified claims

| Synthesis guidance | Verified claim anchor | Verdict |
|---|---|---|
| "Lead with what labour market is *doing*" | stylistic | OK |
| "Anchored on unemployment rate level + direction" | Claim 1 | VERIFIED |
| "Framed against BoC's qualitative characterizations rather than a fixed NAIRU" | Claim 1 | VERIFIED with subtle issue: synthesis under-uses the IMF 6% soft anchor that Claim 1 keeps active |
| "Use utilization pair to distinguish layoff vs. labour-force-exit when moves diverge" | Claim 2 | VERIFIED |
| **"V/U well below 1 = slack; near or above 1 = tight"** | Claim 3 | **CONTESTED — propagation defect** |
| "Wage dispersion, ~3% soft threshold, LFS-Micro below raw LFS" | Claims 4–6 | provisional OK; consistent with framework prose |
| "ULC as cost-pressure read, implied productivity ~1%" | Claim 4 | provisional OK |
| "Wage-vs-services-CPI as leading indicator, not 'margin absorption' shorthand" | Claim 7 | provisional OK |
| "Real wages when gap is large in either direction" | Claim 8 | provisional OK |
| "Demographic / regional decomposition flag as partial" | Claim 9 | VERIFIED with regional-framing caveat |

### Defects flagged

1. **PRIMARY: V/U "near or above 1 = tight" propagation defect.** US-transferred heuristic re-asserted. **Must fix before next blurb regen.**
2. **Subtle: "rather than a fixed NAIRU" reads as if NAIRU is dropped entirely.** Claim 1 keeps the IMF 6% as a soft anchor and instructs the model to use it. Suggest: *"...framed against BoC's qualitative characterizations alongside the IMF ~6% soft reference, neither used as a hard threshold."*
3. **No fabricated quotes** in the synthesis paragraph itself.
4. **No un-fetched indicators named.** All indicators referenced are in `data/`.
5. **No rigid n×n decoder** — Claim 2's revision to "starting hypotheses" is preserved as "when their moves diverge."

### Open questions for user review

1. **Approve V/U-line replacement wording.** Two options proposed above; user picks (or rewrites). **Blocking item for tomorrow's review.**
2. Soften "rather than a fixed NAIRU" to preserve the IMF 6% soft anchor as an active signal?
3. After fix, this can move to Tier 3.

### Proposed patches (mechanical only — judgment items deferred)

**Patch 1: Replace V/U "near or above 1 = tight" with Canadian-calibrated bands per user-verified Claim 3**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
Surface tightness via the V/U ratio when it's clearly off balance — V/U well below 1 reinforces a slack read, V/U near or above 1 reinforces a tight read.
```

`new_string`:
```
Surface tightness via the V/U ratio against its Canadian-calibrated bands (Claim 3 thresholds) — V/U below 0.30 reinforces a slack read; 0.45–0.60 marks the BoC-tightening-cycle band; above 0.80 marks 2022-style exceptional tightness. Directionally informative, with the standing caveat that the Beveridge curve's position has shifted post-COVID.
```

*Reason:* The current synthesis sentence re-asserts the US-transferred V/U ≈ 1 heuristic that user-verified Claim 3 explicitly rejected. Canadian V/U is structurally lower (2022 peak ≈ 0.99 vs. US ≈ 2.0). Replacement uses the Canadian bands the user already signed off on for Claim 3; this is the propagation fix flagged as CRITICAL in the cross-claim defects index.
*Source:* User-verified Claim 3 (Tier 3 provisional) post-revision wording: *"V/U < 0.30 = slack; 0.30–0.45 = below balance; 0.45–0.60 = approaching balance / starting to be tight; 0.60–0.80 = tight; > 0.80 = exceptionally tight."* Underlying BoC anchors via Claim 3: Wilkins Jan 8, 2019 speech (https://www.bankofcanada.ca/2019/01/choosing-our-path-investing-canadians-prosperity/) for the 2018–2019 tightening band; Macklem Nov 10, 2022 speech (https://www.bankofcanada.ca/2022/11/economic-progress-report-restoring-price-stability/) for "exceptionally tight" 2022 anchor.

**Patch 2: Soften "rather than a fixed NAIRU" to preserve the IMF 6% soft anchor**

*Framework prose change* in `markdown-files/analysis_framework.md`:

`old_string`:
```
anchored on the unemployment rate level + direction, framed against BoC's qualitative characterizations rather than a fixed NAIRU.
```

`new_string`:
```
anchored on the unemployment rate level + direction, framed against BoC's qualitative characterizations alongside the IMF ~6% soft reference, neither used as a hard threshold.
```

*Reason:* The current "rather than a fixed NAIRU" reads as if NAIRU is dropped entirely from the synthesis, but user-verified Claim 1 keeps the IMF ~6% as an active soft reference. The replacement preserves Claim 1's framing and prevents the synthesis from contradicting the upstream verified anchor.
*Source:* User-verified Claim 1 (Tier 3) — IMF Article IV Consultation, July 2024 (https://www.imf.org/en/Publications/CR/Issues/2024/07/16/Canada-2024-Article-IV-Consultation-Press-Release-Staff-Report-551817) as the institutional anchor for ~6% NAIRU; framework Claim 1 instructs "Treat ~6% as a soft reference, not a threshold."

*Verification log change* (in this file): mark this claim's verdict line with "(patches 1–2 proposed 2026-05-09; awaiting user accept/reject — patch 1 closes the CRITICAL propagation defect)" prefix.

---

## Cross-claim defects index (Tier 2 audit, Claims 4–10)

| Defect class | Where found | Severity |
|---|---|---|
| Fabricated quote | Claim 8: *"1.6% annual real wage gains since 2023"* attributed to MPR Oct 2024, not located in HTML chapters | **CRITICAL** |
| US heuristic transferred to Canada | Claim 10: *"V/U near or above 1 reinforces a tight read"* — propagation from pre-Claim-3-revision wording | **CRITICAL — must fix before next blurb regen** |
| Threshold without primary source | Claim 4: ULC > 3% bullet | high |
| Mis-attributed source | Claim 7: "Macklem April 2023" should be MPR July 2024 In Focus | high |
| Mis-listed indicator (canonical taxonomy mismatch) | Claim 5: framework's four-measure list omits National Accounts hourly wages, includes "LFS permanent" not in BoC's published list | medium |
| Analyst synthesis presented as canonical | Claim 7: three-mechanism list ("incomplete pass-through, lagged price adjustment, margin compression"); Claim 9: "Toronto/Vancouver vs. rest of Canada" regional framing | medium |
| Number understatement | Claim 4 / Claim 6: "~1%" vs SAN 2025-14 Scenario 1 = 1.2%; downside is tariff-scenario-specific not generic | medium |
| Indicator-naming-leak risk | Claim 9: names avg hours / involuntary PT in framework prose while saying not tracked | low (judgment call) |

The two CRITICAL defects (Claim 8 fabricated quote, Claim 10 V/U propagation) are blocking items for the 2026-05-10 review pass.
