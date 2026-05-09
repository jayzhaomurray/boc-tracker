# BoC Tracker: Project Evolution and Current State

**As of 2026-05-09 | https://jayzhaomurray.github.io/boc-tracker/**

---

## 1. Project Overview

The BoC Tracker is a personal data dashboard that tracks the economic indicators the Bank of Canada monitors between its quarterly Monetary Policy Reports. It is hosted publicly on GitHub Pages, auto-refreshes daily from public data APIs, and presents practitioner-grade analytical commentary alongside interactive charts — all without a server, database, or JavaScript framework. Every chart is generated in Python (Plotly) and embedded as a static HTML file.

The project was built by Jay Zhao-Murray in collaboration with Claude (Anthropic) over a series of sessions beginning in early May 2026. The git history records each discrete iteration, making the project's analytical and technical decision-making fully auditable.

The dashboard answers six plain-English questions, one per section, framed as the Bank of Canada itself frames them:

| Section | Question |
|---|---|
| Monetary Policy | What is the BoC doing right now? |
| Inflation | Is the BoC's mandate — the 2% target — being met? |
| GDP & Activity | Is the economy at potential? |
| Labour Market | Is there slack? How tight is the labour market? |
| Housing | Is the most rate-sensitive sector amplifying or dampening policy? |
| Financial Conditions | What external winds are pushing on inflation, growth, and the CAD? |

The implicit composite question is: where does Canada stand relative to the BoC's goals, and what is likely to shape the next policy decision? But the six sub-questions are the working surface — each section earns its place by directly helping the reader answer its own question.

The live URL is https://jayzhaomurray.github.io/boc-tracker/. The source repository is at https://github.com/jayzhaomurray/boc-tracker.

---

## 2. Architecture in Plain Language

The pipeline runs in three stages:

**Fetch (`fetch.py`)** pulls raw data daily from four public APIs: Statistics Canada's WDS endpoint (CPI series, LFS employment, wages, GDP, housing starts, building permits), the Bank of Canada's Valet API (overnight rate, core inflation measures, 2-year GoC yield, balance sheet, inflation expectations, LFS-Micro composition-adjusted wages, FAD calendar), the Federal Reserve's FRED API (US 2-year Treasury, USD/CAD, WTI, Brent, fed funds), and the Alberta Economic Dashboard (Western Canada Select crude). Each series is saved as a CSV in `data/`. The fetch step is the only one that makes network calls. A `--wait` flag allows the StatsCan crons to retry until the 8:30 AM ET release appears in the API response.

**Analyze (`analyze.py`)** reads the saved CSVs alongside an internal analytical brief (`analysis_framework.md`), computes structured data values for each section (current readings, thresholds, tier classifications), then calls Claude Opus via the Anthropic SDK to generate a 3–4 sentence prose blurb per section. A second LLM call acts as a self-review pass, checking the blurb for factual errors (sign conventions, attribution, dates, magnitudes) before writing results to `data/blurbs.json`. The framework is the load-bearing document: it defines the question each section answers, the signals to evaluate, the threshold values and their provenance, and explicit rules about what to surface in plain-language prose.

**Build (`build.py`)** reads the CSVs and `blurbs.json`, then assembles `index.html` from configuration objects (spec dataclasses) that define every chart's data series, transforms, defaults, legend behavior, and section assignments. The build step is fully offline. All chart transforms (Year/Year, Month/Month, 3M Annualised Rate, Level) are pre-baked into Plotly traces at build time; toggle buttons swap trace visibility via Plotly `restyle`, and the y-axis range recomputes live in JavaScript from whatever traces are currently visible.

A GitHub Actions workflow (`update.yml`) runs on three cron schedules — two at 8:30 AM ET to cover the StatsCan release window across DST transitions, one at 11:00 AM ET for BoC daily yields — and pushes the rebuilt dashboard back to `main`, which triggers GitHub Pages redeploy automatically.

The current dashboard has 20 charts across six sections, all on a single overview page (`index.html`). Scaffold deep-dive pages (one per section) were added in May 2026 as placeholder HTML files wired into the shared navigation bar.

---

## 3. Phases of Development

The project progressed through roughly six identifiable phases, each anchored to specific commits.

**Phase 1 — MVP scaffolding (initial commit: `34e70a2`).**
The first commit on 2026-05-06 was a three-chart BoC Tracker: a CPI chart, a bond yield chart, and a policy rate chart. The architecture already separated `fetch.py` and `build.py`. Commits in the following 24 hours added transform toggles (Level / M/M / 3M AR / Y/Y), range selectors, a custom live y-axis system, and the categorical color palette documented in the chart style guide.

**Phase 2 — Chart layer expansion (commits through `c5e11ca`).**
Within the first two days, the dashboard grew to nine charts covering the full six-section structure: CPI breadth deviation chart (weighted share of components above 3% / below 1%, calibrated against the BoC's own published breadth data); wage growth range band; GDP monthly level with industry overlays; GDP quarterly contribution stacked bar; USD/CAD; oil prices (WTI / Brent / WCS). The CPI breadth chart methodology — deviations from the 1996–2019 pre-COVID average, 59 components weighted by basket shares — was calibrated to reproduce the BoC's own published breadth chart within 1 percentage point at the 2022 peak. The blurb pipeline (`analyze.py` with self-review pass) was added in this phase, wiring the analytical framework to the dashboard's text.

**Phase 3 — Data layer and framework writing (commits through `b51bef0`).**
The analytical framework (`analysis_framework.md`) was written as a per-section brief during this phase, anchoring every threshold and analytical claim to a BoC primary source — Staff Analytical Notes, MPRs, Financial Stability Reports, official communications. The Monetary Policy section was the first to reach practitioner-grade: the neutral-rate band (2.25–3.25% from the Bank's 2024 r* update), the BoC–Fed spread tiers, the Canada 2Y–overnight spread as a market-expectations read with explicit caveats about term-premium noise, and the balance sheet operational timeline (QE April 2020, reinvestment phase, passive QT from April 2022, QT end January 2025, floor-system maintenance $20–60B target). The meeting-resolution action-state classifier — which determines whether the BoC is currently "on hold," "cutting," or "hiking" by reading the daily overnight rate series (BoC Valet V39079) against the FAD calendar — was introduced here. Labour Market, Financial Conditions, GDP, and Housing frameworks were drafted in autonomously-run overnight sessions and initially marked as hypothesis-grade.

**Phase 4 — Labour framework verification and blurb iteration (commits through `932b800`).**
The Labour Market section was the first to undergo the claim-by-claim user-review cycle that later became the template for all sections. The original draft contained two fabricated quotes attributed to the BoC (on NAIRU and Phillips curve methodology) that had survived the initial autonomous pass — a finding that directly motivated the three-tier provenance framework introduced later. The V/U tightness bands were revised after a user-skepticism challenge about whether the 0.45–0.60 "approaching balance" band reflected genuine data or status-quo-bias employer baseline. The composition-adjusted LFS-Micro wage measure (BoC SAN 2024-23) was wired into the wage band chart and the analytical framework, providing a cleaner underlying wage read than raw LFS.

**Phase 5 — Architecture polish and deep-dive scaffolding (commits through `ccf5244`).**
The Indeed Hiring Lab Canada postings index was added to `fetch.py` as a daily-SA job postings series (filling the COVID gap in Statistics Canada's Job Vacancy and Wage Survey). The BoC Balance Sheet chart was added with three series (total assets, GoC bonds, settlement balances) and the operational timeline as annotation context. The A/B testing harness (`experiments/`) was built to compare blurb quality across framework vs. no-framework and across different prompt configurations. Deep-dive scaffolding — a shared cross-page navigation bar and six placeholder deep-dive HTML pages, with the Beveridge curve embedded as a real iframe in the Labour deep-dive — was added in commit `ccf5244`, marking the transition toward a multi-page site.

**Phase 6 — Verification audit, provenance framework, and distribution conventions (commits `b34bebe` through `7c8b170`).**
This is the most analytically substantial phase and is covered in detail in the following two sections.

---

## 4. The May 2026 Verification Audit

On the night of 2026-05-08 to 2026-05-09, a structured verification pass was run across all six analytical framework sections. The findings transformed the project's epistemic architecture.

### The three-tier provenance framework

The audit's first output was formalising a three-tier content-provenance system (`markdown-files/verification/_tiers.md`, commit `b34bebe`):

**Tier 1 — Generated.** Claude produced the content with no verification step. Default tier for any new content. Suitable for first-draft material; not suitable for citing as fact in downstream work.

**Tier 2 — Autonomously verified.** Claude or a sub-agent ran a structured verification pass — located primary sources, captured direct quotes, identified methodology gaps, compared claims against external evidence. The user did NOT review the conclusions. Tier 2 is characterised as "the most dangerous tier because it looks authoritative on the surface but has not been challenged." It is susceptible to cherry-picked sources, sub-agent hallucinations, confirmation-bias source selection, and heuristics transferred from other contexts without flagging.

**Tier 3 — User-verified.** The user actively engaged with the content: pushed back on framings, challenged sources, requested re-checks, and gave explicit accept/reject/revise feedback per claim. The highest-confidence tier. Still not infallible, but the active challenge process catches the failure modes Tier 2 misses.

All existing framework prose was retagged under this system. The Labour Market and Financial Conditions frameworks, generated autonomously overnight before this audit, were tagged Tier 1. The earlier autonomous verification passes on Monetary Policy, Inflation, GDP, Housing, and Financial were tagged Tier 2. Claims the user had actively reviewed (Labour Claims 1–3; the Inflation and Monetary Policy blurb voice) were tagged Tier 3.

### What the audit found

Per-claim verification logs were produced for all six sections. The findings were worse than expected: every section had defects, and the "VERIFICATION STATUS: verified end-to-end (May 2026)" header on four sections was empirically wrong.

The defects clustered into identifiable classes:

**Fabricated quotes and numbers (CRITICAL).** The Labour section's Claim 8 attributed "1.6% annual real wage gains since 2023" to MPR October 2024, but no such quote could be located in any retrieved HTML chapter from that MPR. The figure plausibly originated as a conflation with the September 2024 headline CPI figure (also 1.6%). An earlier pass had already caught two fully fabricated quotes on NAIRU attributed to the BoC (Claim 1 of Labour, resolved Tier 3 after user review). Fabrications surviving an autonomous verification pass is exactly the failure mode that Tier 2 is documented to be susceptible to.

**Threshold values contradicted by project data (CRITICAL).** The `bocfed_spread` tier thresholds in `analysis_framework.md` and in `analyze.py` had been calibrated against daily data since 2009 but labelled as "since 1996 monthly." The Financial section's USDCAD stress-corridor peak was stated as "1.466 (March 2020)" but the actual peak in `data/usdcad.csv` was 1.4539. The Housing section's long-run starts average was anchored to "since 1977" but the project's CSV starts in 1990, and the stated recent 10-year average of ~245k starts overstated the actual 10-year mean of ~234k by roughly 10,000 units, with the 245k figure appearing to correspond to calendar 2024 alone. The GDP section had C.D. Howe Business Cycle Council methodology terms mis-stated as "depth, duration, breadth" when the canonical wording is "amplitude, duration, scope" with the BCC's own descriptor "pronounced, persistent, and pervasive."

**Citation conflation (high severity).** The Housing section's CMHC housing-gap reference mixed two different reports: the 2023 CMHC Housing Shortages report estimated 3.5M units by 2030 under a certain scenario, while the 4.8M-unit figure and the 430–500k/year starts target come from a June 2025 "Solving the Affordability Crisis" report targeting 2035. The Financial section incorrectly attributed certain CAD-driver decompositions to MPR January 2025 when the relevant analysis was in Staff Analytical Note 2025-2.

**Rigid analytical decoders presented as canonical.** The Inflation breadth section classified the breadth signal into four states (broad-based pressure, broad-based softening, clustered near target, polarized), but this typology was analyst synthesis covering only 4 of the 9 logical 3×3 deviation states. The Policy section's 3×2 conditional grid for `can2y_overnight_spread` × `action_state` was similarly analyst synthesis that the framework prose did not mark as such. An earlier user review had already flagged and resolved the Labour section's 2×2 utilization decoder as the same defect class.

**US heuristics transferred to Canada without flagging.** The original Labour Claim 3 applied V/U tightness thresholds calibrated to the US JOLTS survey to Canadian Job Vacancy and Wage Survey data — two surveys with materially different coverage and structural characteristics. The 2022 peak V/U in Canada was ~0.99 versus ~2.0 in the US, reflecting sectoral mix, survey-coverage differences, and Great Resignation dynamics that were US-specific. The claim was revised to Canadian-calibrated bands with explicit cross-country caveats, and marked Tier 3 after user sign-off.

### The morning-review workflow

The audit produced 44 mechanical patch proposals across all six verification logs, formatted as `old_string` / `new_string` pairs ready for direct application via the Edit tool, each accompanied by the primary-source URL and direct quote that motivates the change. The design intent was to restructure the user's morning review from composing corrections from scratch to a fast accept/reject pass through pre-built patches. The verification logs also identify approximately 38 "judgment items" — deferred items where the correct answer requires user judgment (unsourced thresholds, competing analytical framings, indicator-naming choices) — separated into a distinct review batch to avoid interleaving mechanical corrections with higher-stakes analytical decisions.

---

## 5. The Distribution Conventions Framework

The `bocfed_spread` threshold defect — calibrated against daily data since 2009 but labelled "monthly since 1996" — exposed a structural problem that went beyond a single wrong number. The underlying issue was that any analyst writing framework prose can introduce empirical thresholds without documenting what those thresholds are actually measuring. A threshold stated as "high = above 100 bp (historical)" does not reveal whether "historical" means monthly or daily, which time window, what the N is, or whether the calculation is symmetric or absolute-value. Silent methodology drift is invisible until an audit compares the stated label against the actual data.

The response was `markdown-files/distribution_conventions.md` (commit `c994fb0`), introduced through a design discussion on 2026-05-09. The document establishes a five-tier vocabulary and a methodology-disclosure requirement for every empirical threshold in the framework.

Note: the original markdown was written through commit `7c8b170` (Inflation convention sweep). The convention sweep completed across all six sections the same day; those results are described in the updated §5 and §6 below.

### The five-tier ladder

The convention standardises how indicator readings are described relative to their historical distribution:

| Tier | Share of all observations |
|---|---|
| Typical | central 50% |
| Uncommon | next 30% out (P50–P80) |
| Pronounced | next 15% out (P80–P95) |
| Rare | next 4% out (P95–P99) |
| Extreme | most extreme 1% |

The boundary choices — P50, P80, P95, P99 — are anchored to three independent calibrated-language frameworks: the Mosteller-Youtz 1990 survey of probability-word meanings, the IPCC likelihood scale, and the EU pharmacovigilance adverse-event frequency categories. All three converge on a tighter-at-extremes ladder of similar shape. Equal-sized buckets (quartiles, quintiles) were rejected because "rare" and "extreme" carry inherent low-frequency content in everyday English that a top-25% threshold would contradict.

### Per-indicator metadata requirements

Every indicator introduced to the framework must specify two pieces of metadata at its definition:

**Tail axis:** what is actually being percentile-ranked. For two-tailed signed values (BoC–Fed spread can be positive or negative), the tail axis is the absolute magnitude `|spread|`. For target-anchored indicators like CPI, the tail axis is deviation from the 2% target: `|CPI Y/Y - 2%|`. The tail axis makes the distribution calculation unambiguous and replicable.

**Descriptor pair:** the natural English words for "high" and "low" at the Pronounced tier and above, calibrated to the indicator's direction. Inflation indicators use "hot / soft"; labour-market tightness uses "tight / slack"; spreads use "high / low"; volume/flow indicators use "strong / weak."

For indicators where the BoC publishes an authoritative band or target (inflation at 1–3%, policy rate vs. the 2.25–3.25% neutral band, the output gap), the convention requires dual classification: the binary BoC frame (in-band or outside-band, using the BoC's published edge) and the empirical five-tier ladder. Prose surfaces whichever frame is analytically salient. Inside-band readings typically need only the BoC frame; far-outside readings typically need only the empirical tier because the band breach is already the headline.

### The methodology-disclosure rule

Every threshold citation in framework prose must state the window, resolution, tail axis, and sample size. The model phrase is: `(median |spread| 62.5 bp, monthly month-start, since 1996, N=364)`. This makes silent methodology drift structurally impossible: you cannot cite a threshold without revealing what it actually measures.

Thresholds are to be recomputed annually, ideally pre-MPR, with the recompute date documented in framework prose so staleness is visible.

### Worked examples — full sweep completed

The convention sweep ran across all six sections on 2026-05-09, completing the catalog in `distribution_conventions.md`.

The **`bocfed_spread`** — absolute monthly spread in basis points, since 1996, N=364 — has thresholds: typical ≤62.5 bp (P50), uncommon to 100 bp (P80), pronounced to 187 bp (P95), rare to 231 bp (P99), extreme above 231 bp. The 38 bp discrepancy between the old thresholds and the recomputed ones was diagnosed in `analyses/bocfed_spread_38bp_test.md`: the prior thresholds used daily data since 2009, while the correct baseline is monthly month-start since 1996. Monthly data has lower variance than daily (the tails are narrower because noise averages out), and the 2009 start date excluded the 1996–2008 pre-GFC era in which the spread was structurally closer to zero. Both effects pushed the prior thresholds upward — what looked like a "pronounced" reading under the old calibration would actually be at the P65–P70 level in the correct distribution.

The **`can2y_overnight_spread`** — absolute monthly spread since 2001, N=304 — has thresholds: typical ≤32 bp, uncommon to 71 bp, pronounced to 120 bp, rare to 179 bp, extreme above 179 bp. The small-N caveat applies: at N=304 the extreme tier (top 1%, about three observations) is sparsely populated, making the extreme threshold sensitive to single new outliers.

The **Inflation section** (`7c8b170`, then extended in `e9f3240`) produced the most extensive worked example. `analyses/inflation_distribution.py` (N=315, January 2000 to March 2026) computed empirical tiers for headline CPI deviation, M/M momentum, core band width, headline-core gap, and two expectation series. Key findings: the prior "notable" headline-core divergence threshold of 0.3 pp sits at the 27th percentile (fires in 73% of months); the defensible "uncommon divergence" trigger is P50 = 0.55 pp and "clearly material" is P80 = 1.05 pp. The prior "tight" core dispersion threshold of 0.5 pp sat at P35. Commit `e9f3240` resolved three user-judgment calls from the audit: (Q1) the 5-year consumer inflation expectations series gets dual classification (BoC binary band frame plus empirical tier on `|x - 2%|`); (Q2) `CPI-common` was retained in the catalog with an explicit caveat that the BoC dropped it from its preferred set in 2022 after large pandemic-era historical revisions; (Q3) the four-state breadth typology was replaced by a continuous tier on `|tilt|` with a descriptor pair (pressure / softening), using N=364 monthly observations — P50 = 10.88 pp, P80 = 18.76 pp, P95 = 37.72 pp.

The **Financial Conditions section** (`d010e64`) swept USDCAD deviation, oil-price deviation, and the BoC-Fed spread simultaneously. The USDCAD data error surfaced in the audit — stress-corridor peak incorrectly stated as "March 2020 (1.466)" when `data/usdcad.csv` shows the actual peak was 1.4539 — was corrected as part of this sweep.

The **GDP section** (`637f7bd`) applied tiers to the output-gap proxy (GDP-trend deviation, since the project lacks a live output gap series), capacity utilization, and GDP Y/Y. The C.D. Howe BCC methodology was corrected from "depth, duration, breadth" to the canonical "amplitude, duration, scope" with the evaluative descriptor "pronounced, persistent, and pervasive."

The **Housing section** (`7b80c79`) swept four indicators: starts 12-month MA deviation (N=424, 1990+), NHPI Y/Y deviation (N=531, 1982+), CREA HPI Y/Y deviation (N=134, small-N caveat, 2015+), and affordability ratio deviation (N=104, quarterly, small-N). Two critical citation corrections also landed: the CMHC citation conflation (2023 Housing Shortages report at 3.5M units by 2030 separated from the June 2025 "Solving the Affordability Crisis" report at 4.8M units / 430–480k per year / 2035 target); and the CREA HPI methodology description corrected from "hedonic" to "hybrid repeat-sales/hedonic constant-quality index on MLS resale."

The **Labour Market section** (`90bdb5d`) completed the sweep and simultaneously resolved several outstanding verification items. ULC Y/Y and four real-wage measures (LFS-all, LFS-permanent, SEPH, LFS-Micro) each received empirical tiers from `analyses/labour_distribution.py`. Labour Claim 8 — the fabricated "1.6% annual real wage gains since 2023" quote attributed to MPR October 2024, which no retrieved MPR chapter could locate — was resolved: the user accepted Outcome C (remove the quote; replace with the BoC's actual real-wage framing from the same MPR, which compares real wages to productivity). The real-wage read is now computed live (nominal wage Y/Y minus headline CPI Y/Y across all four measures) rather than dependent on a year-old quote. This section marks the first time the Labour framework has been Tier 3 on wage methodology.

### Design notes preserved in the document

The convention document includes a "Design notes" section recording the non-obvious calls behind the rules — a practice introduced to prevent the same tradeoffs from being re-argued in future sessions. These cover the choice of English labels over numeric tiers (three independent calibrated-language frameworks settle on labelled tiers), the decision to use central-X% framing rather than symmetric absolute deviation for skewed distributions, and the rationale for binary BoC-band classification rather than a three-state (in / outside / far-outside) scheme (the BoC publishes band edges, not "far-outside" thresholds, so three-state would invent calibration the BoC did not publish).

---

## 6. Current State as of End of Day 2026-05-09

### What was completed during the day

The day's work brought the analytical framework to a state that is materially more defensible than where it started. The headline developments:

**Convention sweep — all six sections complete.** As of commit `90bdb5d`, every framework section has empirical tier thresholds computed from the project's own CSVs, with the methodology-disclosure string (window, resolution, tail axis, N) embedded in framework prose. This is the hardest-to-reverse structural improvement: thresholds now have auditable provenance and cannot silently drift. Total indicators tiered: 2 (Policy, already done) + 7 (Inflation) + 4 (GDP) + 4 (Housing) + 4 (Financial) + 5 (Labour) = 26 indicators with tier classifications.

**Critical fabrication resolved.** Labour Claim 8's fabricated MPR quote (Tier 2 audit finding, outstanding since the previous session) was resolved by user decision: quote removed; real-wage read now computed live from data. The live computation is strictly more defensible than a point-in-time MPR quote that could have been misread even if real.

**Factual corrections committed.** CMHC citation conflation (Housing), USDCAD peak value error (Financial), C.D. Howe BCC methodology wording (GDP), CREA HPI methodology description (Housing) — all four corrected in their respective sweep commits.

**GitHub Actions fixed.** The nightly cron was failing at the auto-commit step due to a deprecated Node.js 20 environment in `git-auto-commit-action` v5. Commit `49d8f26` upgraded to v7 (Node.js 24). Root cause confirmed via `gh run logs`. The auto-update pipeline is running again.

**HANDOFF auth-path drift corrected.** An earlier doc inconsistency between the CI path (API key) and the local path (Claude Code subscription) was resolved in commit `7d76cba`.

### What is still outstanding

The convention sweep and verification patches did not resolve everything. The remaining open items fall into three batches, which the HANDOFF morning-review workflow now structures explicitly:

**Mechanical patches still pending.** Several mechanical corrections from the audit remain unapplied: the Claim 7 citation update (Macklem April 2023 -> MPR July 2024 In Focus, which landed in the Labour sweep), the verification header downgrades in GDP / Housing / Financial sections (still marked "verified end-to-end" despite known defects), and assorted minor framing corrections across the six logs. The HANDOFF morning-review recommendation is to batch these as accept/reject passes through the pre-written `old_string` / `new_string` pairs rather than composing corrections from scratch.

**Judgment items deferred.** The Policy section's 3×2 conditional grid for `can2y_overnight_spread × action_state`; the Labour V/U 0.45–0.60 "approaching balance" band anchor narrative (whether this threshold reflects genuine data or status-quo-bias); the outstanding Claim 3 (V/U tightness) re-review where the user's challenge about the band calibration remains open.

**Code changes not yet wired.** The Indeed Hiring Lab postings index is fetched and in `data/` but not charted — blocked on a secondary y-axis extension to `MultiLineSpec`. The `compute_labour_values` function in `analyze.py` still uses a 12-month MA for the job vacancy rate; the framework was updated to a 3-month MA (to avoid the 7-month lag at cyclical turns) but the code has not been updated to match.

**Blurb regeneration pending.** The four autonomous-draft blurbs (Labour, GDP, Housing, Financial) predate the convention sweep and all factual corrections. They should be regenerated after the remaining mechanical patches land. The Inflation and Monetary Policy blurbs are Tier 3 and do not need regeneration.

### What is queued next

**Deep-dive page real content.** A full design for all eight deep-dive pages was produced on 2026-05-09 and is committed at `analyses/deep-dive-design-2026-05-09.md`. The design covers 43 proposed charts across the six existing sections plus two new pages (Trade and Demographics), with per-chart data series, spec types, tradeoffs, and cross-page data-fetch dependencies. Nine judgment calls were documented and resolved within the design session rather than being left open, reducing the next implementation session's front-loaded decision cost. Key resolved calls: output gap series confirmed via BoC Valet key `INDINF_OUTGAPMPR_Q` (discovered during data-source probes); CPI ex-indirect-taxes confirmed via BoC Valet key `MPR_2025M04_CPI_TAX_S1`; CORRA confirmed at `CORRA_WEIGHTED_MEAN_RATE` (not `AVG.INTWO` as previously hypothesized); Canadian IG credit spread not available in Valet, fallback is US ICE BofA IG spread `BAMLC0A0CM` on FRED; TSX Composite confirmed only via `yfinance` / `^GSPTSE` (Valet key `SAN_LEBM180118_CHART2D_A_TSX` is an impulse-response artifact, not index data; FRED `SPTSXINL` returns 404). Data-source probe results are in `analyses/data-source-probe-2026-05-09.md`.

**LFS gross flows — low feasibility.** A probe of StatsCan's published table catalog (`analyses/lfs-gross-flows-probe-2026-05-09.md`) confirmed that the 3×3 E/U/NLF gross-flows matrix the BoC uses in MPR Chart 23 is not a published table. The BoC computes it from confidential LFS microdata by linking consecutive monthly files via dwelling/household identifiers that are stripped from the public microdata release. Three paths exist for approximation: a StatsCan custom tabulation request, RDC application (not suitable for a live dashboard), or a residual accounting identity using published LFS stocks and the "activity prior to unemployment" monthly series (Table 14-10-0123). The last path is the most tractable; it was documented as the concrete next step if the Labour deep-dive chart is pursued.

**Market-implied rate path.** Still blocked on the absence of a free Canadian OIS or CRA-futures data feed. TMX has no public API; BoC Valet has no implied-rate series. The 2Y term-premium framework in the Monetary Policy section is a partial substitute, with explicit caveats about when the spread is and is not interpretable as a rate-path signal.

**CI authentication.** The GitHub Actions workflow requires `ANTHROPIC_API_KEY` as a repo secret for blurb regeneration in CI. The local development path uses Claude Code's subscription authentication (`claude` CLI). The workaround is documented in `fetch.py`'s run instructions; no structural change is needed, but the auth path split is something a new session should be aware of.

---

## 7. Appendix: Canonical Documents and References

**Canonical first-read documents** (in load order per `CLAUDE.md`):

1. `markdown-files/dashboard_purpose.md` — the six sub-questions each section answers; the filter for what belongs on the overview vs. deep-dive vs. out of scope.
2. `markdown-files/HANDOFF.md` — current state, file structure, data series table, architecture, Next Steps. The session-startup document.
3. `markdown-files/chart_style_guide.md` — formatting principles and the §8 exception/revision protocol.
4. `markdown-files/analysis_framework.md` — the internal analytical brief driving blurb generation. Per-section questions, signals, thresholds.
5. `markdown-files/distribution_conventions.md` — the five-tier ladder, methodology-disclosure requirements, per-indicator reference catalog.

**Verification logs:** `markdown-files/verification/{_tiers,policy,inflation,gdp,labour,housing,financial}.md`

**Analyses (one-off research scripts):** `analyses/bocfed_spread_distribution.py`, `analyses/can2y_overnight_spread_distribution.py`, `analyses/inflation_distribution.py`, `analyses/labour_distribution.py`, `analyses/bocfed_spread_38bp_test.md`, `analyses/beveridge_curve_canada.html`, `analyses/statscan_zero_audit.md`, `analyses/deep-dive-design-2026-05-09.md`, `analyses/data-source-probe-2026-05-09.md`, `analyses/lfs-gross-flows-probe-2026-05-09.md`

**External reference:** `boc-tracker_assessment_2026-05-09.pdf` (project root, gitignored) — a portfolio-facing assessment of the project generated on 2026-05-09. It covers: technical summary (1,100 lines of Python, four APIs, 65 CSVs, 20 charts, A/B testing harness); analytical positioning (practitioner-aligned, BoC-framing, refuses directionally-correct reads); and a calibrated set of comparisons placing the project relative to typical solo dashboards, hackathon projects, capstone theses, the BoC's own MPR site, and junior macro-analyst automation tools. The framing that the project "sits at the intersection of competent solo side project and junior-analyst automation tool" with the analytical depth carrying it for macro-research-adjacent portfolio use is preserved in the assessment; that document is the right home for that framing, which is out of scope for this technical evolution record.

**Live dashboard:** https://jayzhaomurray.github.io/boc-tracker/

**GitHub repository:** https://github.com/jayzhaomurray/boc-tracker

**Commit range covered by this document:** `34e70a2` (initial commit, 2026-05-06) through `90bdb5d` (distribution conventions applied to Labour Market section, completing the full six-section sweep, 2026-05-09).
