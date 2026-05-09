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

**Tier 3 (provisional) — user-engaged 2026-05-09; flagged for re-review 2026-05-10.** User actively challenged the V/U > 1 = tight heuristic, the BoC's-preferred framing, and the 12M MA smoothing choice; the revised version went through user push-back. The Tier-3 stamp will be confirmed (or revised again) at the 2026-05-10 review pass — until then, the entry is "engaged but not finalized," structurally still Tier 3 but with an explicit reopening flag.

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

## Subsequent claims

To be added as we work through the framework:
- Claim 4: Cost pressure (ULC Y/Y; LFS-Micro + ULC pairing; implied productivity ≈ 1% rule)
- Claim 5: Wage growth across measures (LFS-Micro vs raw LFS pattern)
- Claim 6: Wage growth vs ~3% soft threshold
- Claim 7: Wage growth vs services CPI (BoC framing vs older "margin absorption" shorthand)
- Claim 8: Real wages = wage Y/Y minus headline CPI Y/Y
- Claim 9: What this framework doesn't track (avg hours, involuntary PT, demographic decomposition, regional)

Plus the seven threshold bullets and the "What to surface" synthesis paragraph.
