# BoC Tracker — Project Handoff

This document captures the current state of the project. Written so a fresh session can continue without any prior context.

---

## 🚨 Gemini CLI Session Audit (2026-05-09 Evening)
**Agent:** Gemini CLI (Interactive Session)

This section logs a series of structural changes and identified regressions introduced during the evening session on 2026-05-09. **Action required:** Restoration of custom chart builders that were orphaned during the refactor.

### 1. Structural Changes (The "Deep-Dive Refactor")
- **Unified PageSpec Architecture:** Successfully migrated all 8 deep-dive pages from the legacy `DEEP_DIVES` list into the primary `PAGES` list in `build.py`. This ensures they share the same navigation, styling, and JS infrastructure as the main dashboard.
- **Secondary Y-Axis Support:** Extended the `LineConfig` and `MultiLineSpec` dataclasses to support `secondary_y`, `secondary_unit_label`, and `secondary_ticksuffix`. This was added specifically to support charts like "Indeed Job Postings vs. Official Vacancies."
- **Data Pipeline Expansion:** Added several new series to `fetch.py` (Youth/Prime-age UR, CORRA, ECB rates, 5Y/10Y/30Y GoC yields) and successfully ran a full fetch/build cycle.
- **StatsCan API Recovery:** Fixed a breaking 404 change in the StatsCan WDS API by updating all probe scripts (`analyses/*_vectors.py`) to use `POST` for metadata requests.

### 2. Regressions & Defects Introduced
- **DELETED/ORPHANED: Beveridge Curve:** The custom builder `_build_beveridge_curve_panel` (line 2474) is no longer being called. The `labour.html` deep-dive now contains a standard `MultiLineSpec` placeholder instead of the phase-space scatter plot.
- **ORPHANED: GDP Potential & Output Gap:** The specialized builders `_build_gdp_potential_panel` and `_build_output_gap_panel` are also orphaned. The `gdp.html` page uses simple `MultiLineSpec` stubs that lack the HP-filter logic of the originals.
- **ORPHANED: WTI–WCS Differential:** The native `_build_wcs_wti_panel` was replaced by a standard `MultiLineSpec` in `financial.html`, losing the specialized reference bands and layout.
- **Broken DEEP_DIVES Loop:** The `DEEP_DIVES` processing loop and `_assemble_deep_dive_page` call were removed from `main()`.

### 3. Regression status (updated 2026-05-10)

| Regression | Builder | Status |
|---|---|---|
| Beveridge Curve (`labour.html`) | `_build_beveridge_curve_panel` | **Being fixed — Charter agent, current session** |
| WTI–WCS Differential (`financial.html`) | `_build_wcs_wti_panel` | Remaining — fix in a follow-on session |
| GDP Potential & Output Gap (`gdp.html`) | `_build_gdp_potential_panel`, `_build_output_gap_panel` | Remaining — fix in a follow-on session |

**Do not revert the StatsCan API fix**; it is the only reason data fetching is currently working.

### 4. Parallel agent fleet framework (added 2026-05-10)

A human + Claude session reviewed this branch, confirmed the three regressions above, and introduced a structured parallel-agent framework for future multi-file work:

- **`markdown-files/FILE_OWNERSHIP.md`** — exclusive file zones per agent role (Fetcher, Charter, Auditor, Doc Writer, Deployer). Agents may not touch files outside their zone without coordinator approval.
- **`markdown-files/coordinator_template.md`** — coordinator prompt template for dispatching a parallel fleet: defines agent roles, dispatch instructions, and merge-review hand-off sequence.
- **`markdown-files/merge_review_prompt.md`** — merge-review prompt for the final consolidation step after parallel agents complete.

---

## What this project is

A personal data dashboard that tracks the economic indicators the Bank of Canada watches between its quarterly Monetary Policy Reports (MPRs). The output is a single interactive HTML file hosted publicly on GitHub Pages.

**Live URL:** https://jayzhaomurray.github.io/boc-tracker/
**GitHub repo:** https://github.com/jayzhaomurray/boc-tracker
**Owner GitHub handle:** jayzhaomurray

**Tech stack:** Python → Plotly → static HTML → GitHub Pages
**Data sources:** Statistics Canada WDS API, Bank of Canada Valet API, Federal Reserve (FRED) API, Alberta Economic Dashboard API

**Long-term vision:** `vision.md` has been archived to `markdown-files/archive/` and is not a first-read doc for session startup.

---

## What landed 2026-05-09

Four major milestones completed in a single day:

1. **Distribution conventions framework introduced and fully applied.** `markdown-files/distribution_conventions.md` codifies a five-tier ladder (typical / uncommon / pronounced / rare / extreme) at P50/P80/P95/P99 boundaries, binary BoC-band dual classification for BoC-band indicators, and per-indicator tail-axis + descriptor-pair metadata. Applied across all six framework sections in nine commits (see Phase commits table). Every framework indicator now has a calibrated empirical tier definition replacing asserted thresholds.
2. **CI auto-commit step fixed.** GitHub Actions `git-auto-commit-action` v5 was failing on Node.js 24 (the runner default as of 2026-05). Upgraded to v7 (`49d8f26`); CI builds are now green again.
3. **Deep-dive design doc landed.** `analyses/deep-dive-design-2026-05-09.md` covers all 8 deep-dives (6 section deep-dives + Trade + Demographics), 43 charts, 9 judgment calls resolved. Data-source probes (`analyses/data-source-probe-2026-05-09.md`, `analyses/lfs-gross-flows-probe-2026-05-09.md`) resolved the output gap, CORRA, CPI ex-indirect-tax, and TSX blockers.
4. **Hooks installed and validated.** Pre-commit checkpoint + edit-burst detector hooks are live; see CLAUDE.md Workflow conventions for rationale.

The convention sweep is the main analytical milestone: all six sections are now convention-aligned, all six verification logs updated, and blurb regen is now a clean operation (no stale anchors).

**Late-afternoon analytical milestones** (commits `15442ca`, `5a952d1`, `242ec83`): V/U fifth-pass research completed; Labour Claim 3 V/U bands relabelled to empirical descriptors (bottom-of-history / low / elevated / high / exceptionally high) with locked-in paragraph framing distinguishing BoC-likely-synthesis from wage-confirmed-synthesis. Policy Claim 10 (3×2 grid) dropped as the third rigid n×n decoder rejected. "Verification, not speculation" extended with general epistemic rule. Claims 3 and 10 marked Tier 3 resolved. New `reference/` folder convention for personal-reference documents (versioned PDFs, research artifacts).

---

## What landed 2026-05-09 (afternoon/evening session)

**Deep-dive flesh-out pass:**

- **Trade and Demographics placeholder pages added** (`trade.html`, `demographics.html`) — 5 placeholder sections each, fully wired into the nav bar. Dashboard is now 9 pages total: Overview + 8 deep-dives.
- **Beveridge curve rebuilt as native Plotly spec** in `build.py` (`_build_beveridge_curve_panel`); iframe removed from Labour deep-dive. Autorange on legend toggle via `plotly_restyle` hook.
- **HP filter potential GDP added to GDP deep-dive** — two charts: Actual vs Potential GDP (level, C$ trillions, λ=129,600) and Output Gap % (derived). Manual numpy fallback included; `statsmodels` added to `requirements.txt`.
- **`body_fn` pattern introduced in `DEEP_DIVES`** for pages with dynamically-built chart content (vs static `body` string).
- **Individual core measures chart added to Inflation deep-dive** (CpiSpec pattern, trim+median visible by default).
- **WCS–WTI spread chart added to Financial deep-dive** (reference bands at $10–15 normal range and $20 pipeline-constrained).
- **Mortgage renewal payment shock chart added to Housing deep-dive** as 6th chart (`MortgageShockSpec`; static data from BoC SAN 2025-21).

**Probe scripts ready (not yet run):**
- `analyses/gdp_deepdive_vectors.py` — capacity utilisation (Table 36-10-0007) and hours worked (Table 14-10-0035)
- `analyses/labour_deepdive_vectors.py` — LFS job-losers (Table 14-10-0125), youth/prime unemployment (Table 14-10-0287), EI beneficiaries (Table 14-10-0005)
- `analyses/trade_deepdive_vectors.py` — merchandise exports (Table 12-10-0011), bilateral CA–US trade (Table 12-10-0009)
- `analyses/demographics_deepdive_vectors.py` — population quarterly (Table 17-10-0009), age-group LFS (Table 14-10-0027)

Run these locally with `python analyses/<script>.py` before the next flesh-out pass. Each writes a `.md` results file. After results land, a Sonnet agent can add confirmed series to `fetch.py`, run the fetcher, and wire the remaining charts.

---

## Overnight checkpoint (2026-05-09 → 10)

User went to sleep around 04:00 with the prompt "do work overnight that requires the least input and judgment from me." Five phases landed; each independently committed so any phase's work can be reviewed in isolation. **The biggest finding is that Tier 2 verification of the four non-Labour-non-Inflation-non-Policy sections surfaced concrete defects that don't match project data — the "verified end-to-end (May 2026)" status flags in framework prose are now empirically wrong for at least three sections.**

### Phase commits (oldest first)

| Phase | Commit | What landed | Where to look |
|---|---|---|---|
| 0 | `b34bebe` | Three-tier provenance framework codified (Tier 1 generated / Tier 2 autonomous / Tier 3 user-verified). Existing claims retagged. | `markdown-files/verification/_tiers.md`; CLAUDE.md Workflow conventions block |
| 1 | `1219d80` | Labour Claims 4–10 Tier 2 entries in verification log. Two CRITICAL defects: Claim 8 fabricated MPR-Oct-2024 quote; Claim 10 propagation of US-transferred V/U heuristic Claim 3 rejected. | `markdown-files/verification/labour.md` |
| 2 | `165e7cc` | StatsCan zero-audit script + report. **No stale-zero bugs anywhere outside JVWS** — the COVID-gap defect was unique. 12 benign leading-NaN-padding mismatches; user picks resolution. | `analyses/statscan_zero_audit.py`, `analyses/statscan_zero_audit.md` |
| 3 | `33eb0cd` | Indeed Hiring Lab Canada fetcher wired into `fetch.py`. Daily + monthly-mean CSVs in `data/`. NOT chart-wired (deferred to 2026-05-10 design pass; needs MultiLineSpec secondary y-axis extension). | `fetch.py` `fetch_indeed_canada()`, `data/indeed_postings_ca.csv`, `data/indeed_postings_ca_monthly.csv` |
| 4 | `2a5fef7` | Tier 2 verification audits: Inflation, Policy, GDP, Housing, Financial. Each section gets a per-claim log file. **All five sections have defects.** Three sections have claims demonstrably wrong vs project data. | `markdown-files/verification/{inflation,policy,gdp,housing,financial}.md` |
| 5 | `e318b0c` | End-of-night status note + per-section verification log links wired into HANDOFF status block. | This file |
| 6 | `95c9ac5` | **Patch proposals across all six verification logs.** 44 mechanical patches drafted with copy-paste-able old_string / new_string pairs, ready for Edit-tool accept/reject. ~38 judgment items deferred. Restructures morning review from compose-from-scratch to fast accept/reject. | All `markdown-files/verification/*.md` files; "Proposed patches" subsection per claim |
| 7 | `ccf5244` | **Deep-dive site scaffolding.** Multi-page architecture wired into `build.py`: shared cross-page nav bar; 6 placeholder deep-dive pages (one per section); Beveridge curve embedded as a real iframe in the Labour deep-dive. Placeholder content per planned-content list. | `build.py` (`NAV`, `_build_nav_html`, `DEEP_DIVES`, `_assemble_deep_dive_page`); `policy.html`, `inflation.html`, `gdp.html`, `labour.html`, `housing.html`, `financial.html` at project root |
| 8 | `c994fb0` | **`distribution_conventions.md` introduced.** Five-tier ladder (typical / uncommon / pronounced / rare / extreme) at central 50/80/95/99% boundaries. Per-indicator metadata (tail axis, descriptor pair). Binary BoC-band frame for indicators with published BoC bands (inflation, policy rate vs neutral, output gap). Synonymic latitude within tier. New First-Moves doc; new "Preserve design rationale sparingly" workflow rule in CLAUDE.md. Designed via long discussion 2026-05-09 (research basis: Mosteller-Youtz 1990, IPCC, EU pharmacovigilance). | `markdown-files/distribution_conventions.md`; CLAUDE.md First Moves §5 + Workflow conventions; `analyses/bocfed_spread_distribution.py` (worked-example data); `analyses/bocfed_spread_38bp_test.md` (methodology drift evidence) |
| 9 | `3f020ad` | **Convention applied end-to-end on `bocfed_spread` (worked example).** Framework prose retuned; code retuned (`analyze.py` `_classify_bocfed` thresholds, banner). Verification log Claim 5 marked Tier 3. Old patch proposals superseded. | `markdown-files/analysis_framework.md`; `analyze.py`; `markdown-files/verification/policy.md` Claim 5 |
| 10 | `760b254` | **Convention applied to `can2y_overnight_spread`.** Vocabulary update; no threshold change needed (audit had found it VERIFIED). | `analysis_framework.md`; `markdown-files/verification/policy.md` Claim 4 |
| 11 | `49d8f26` | **CI fix: `git-auto-commit-action` v5 → v7.** Node.js 24 incompatibility was silently breaking nightly auto-commits. Green again. | `.github/workflows/update.yml` |
| 12 | `7c8b170` | **Convention applied to Inflation.** First BoC-band dual classification for an inflation indicator. Four-state breadth classification dropped (analyst synthesis; user Q1 decision). Unsourced thresholds retuned. | `analysis_framework.md`; `analyze.py`; `markdown-files/verification/inflation.md` |
| 13 | `e9f3240` | **Inflation Q1/Q2/Q3 user decisions applied.** Breadth dropped; core-vs-headline logic refined per user direction. | `analysis_framework.md`; `markdown-files/verification/inflation.md` |
| 14 | `d010e64` | **Convention applied to Financial Conditions.** USDCAD stress-corridor peaks corrected to match project data (1.4539). CAD pass-through ranges retuned. MPR/SAN mis-attribution resolved. | `analysis_framework.md`; `analyze.py`; `markdown-files/verification/financial.md` |
| 15 | `637f7bd` | **Convention applied to GDP & Activity.** BCC criteria corrected to canonical "amplitude, duration, scope." Housing-trough anchors corrected (April 2009 = 111.8k). Inventories threshold retuned to P80 (±3.55pp) from asserted ±3pp. Data-source probe doc landed. | `analysis_framework.md`; `analyze.py`; `analyses/gdp_distribution.py`; `analyses/data-source-probe-2026-05-09.md` |
| 16 | `7b80c79` | **Convention applied to Housing.** CMHC citation conflation resolved (2023 vs 2025 reports). CREA HPI methodology corrected. Cyclical anchors retuned against project data. | `analysis_framework.md`; `analyze.py`; `markdown-files/verification/housing.md` |
| 17 | `90bdb5d` | **Convention applied to Labour Market (final section).** Claim 8 fabricated quote removed. Claim 10 US-heuristic propagation removed. Real wage benchmark added per user direction. LFS gross-flows probe landed. | `analysis_framework.md`; `analyze.py`; `markdown-files/verification/labour.md`; `analyses/lfs-gross-flows-probe-2026-05-09.md` |
| 18 | `15442ca` | **End-of-day wrap: Policy Claim 10 dropped.** Policy Claim 10 (3×2 conditional grid) dropped per user decision; same construct class as Labour Claim 2 and Inflation Claim 3 (both previously rejected). Framework prose retains interpretive logic as paragraph framing; continuous tier handles magnitude. Verification log marked Tier 3. Labour-tightness research document landed: `analyses/labour_tightness_research_2026-05-09.md`. | `markdown-files/verification/policy.md`; `analysis_framework.md`; `analyses/labour_tightness_research_2026-05-09.md` |
| 19 | `5a952d1` | **V/U fifth-pass resolution applied.** Labour Claim 3 V/U bands relabelled to empirical descriptors (bottom-of-history / low / elevated / high / exceptionally high); paragraph framing locked in distinguishing BoC-likely-synthesis from wage-confirmed-synthesis. "Verification, not speculation" extended with general epistemic rule (state only dashboard observations; calibration anchors in background). Claims 3 and 10 marked Tier 3. | `markdown-files/verification/labour.md`; `analysis_framework.md` |
| 20 | `242ec83` | **HANDOFF refresh: prune stale Next Steps, integrate design-doc references.** Convention sweep item removed (complete); blurb regen item unblocked. Three post-refresh items added: RBA two-sided methodology, BOS labour-shortage indicator, real-wage-benchmark prose extension. | This file |

### Open judgment items (updated 2026-05-09)

All mechanical defects and factual corrections from the original five-section Tier 2 audit have been resolved via the convention sweep. Late-afternoon milestones resolved the two highest-priority items:

1. **Labour Claim 3 — V/U threshold bands.** **RESOLVED 2026-05-09 (Tier 3).** Bands relabelled to empirical descriptors (bottom-of-history / low / elevated / high / exceptionally high) with locked-in paragraph framing. Labour-tightness research confirmed three evidence anchors for the resolution. Verification log updated.
2. **Labour Claim 10 — V/U-line propagation.** **RESOLVED 2026-05-09 (Tier 3).** Claim 3 resolution unblocked Claim 10. Verification log updated.
3. **Policy — 3×2 conditional grid for `can2y_overnight_spread` × `action_state`.** **RESOLVED 2026-05-09 (Tier 3).** Dropped per user decision 2026-05-09; same construct class as Labour Claim 2 and Inflation Claim 3 (both previously rejected). Framework prose retains interpretive logic as paragraph framing; continuous tier handles magnitude.
4. **Output gap implementation.** Valet path confirmed (`INDINF_OUTGAPMPR_Q`, via data-source probe). User wants HP-filter-based potential GDP comparison added alongside. Awaiting implementation in `fetch.py` + framework wiring.
5. **Real wage benchmark.** Added to Labour framework per user direction during sweep; framework cites live computation but no current-state assessment exists yet (Tier 1 placeholder).

**Queued implementation work (no judgment needed, just implementation):**

- 12M→3M code change in `compute_labour_values` + chart spec + `_DERIVED_SERIES_SOURCES`. Framework updated in earlier sweep; code is not.
- `MultiLineSpec` secondary y-axis extension to wire the Indeed line into the Unemployment & Job Vacancies chart.
- Re-fetch other StatsCan series and accept leading-NaN rows (audit Option A) or tighten `fetch_statscan` to strip leading NaN only (Option B).

### Defect-class resolution (post-sweep, 2026-05-09)

| Defect class | Status |
|---|---|
| Fabricated quote / number (Labour Claims 1, 8) | **RESOLVED** — Claim 8 fabricated MPR quote removed; Claim 1 revised Tier 3 |
| Threshold values disagreeing with project data (Policy bocfed_spread, GDP housing-trough, Financial USDCAD, Housing anchors) | **RESOLVED** — All retuned per convention sweep; Tier 3 in per-section verification logs |
| Citation conflation (Housing CMHC, Financial MPR vs SAN, GDP BCC wording) | **RESOLVED** — Corrected in framework prose during sweep |
| Threshold values asserted without primary-source backing (Inflation 3 thresholds, Labour Claim 4, GDP inventories) | **RESOLVED** — All retuned to empirical P80 per convention; sources in distribution analysis files |
| Rigid n×n decoder (Inflation Claim 3 four-state breadth, Policy 3×2 grid) | Inflation Claim 3: **RESOLVED** — breadth classification dropped per user Q1 decision. Policy 3×2 grid: **RESOLVED** — dropped per user decision 2026-05-09; prose retains interpretive logic. |
| US heuristic transferred to Canada (Labour Claims 3, 10) | **RESOLVED** Tier 3 — both claims resolved 2026-05-09. Claim 3: bands relabelled to empirical descriptors with locked-in framing. Claim 10: unblocked by Claim 3 resolution. |
| Indicator-naming-leak risk (Labour Claim 9, Financial Claim 10) | Low priority; not addressed in sweep |

### What's now unblocked (2026-05-09 end of day)

The convention sweep clears the main blocker on blurb regen. All mechanical defects are resolved; framework prose is convention-aligned across all six sections. The four autonomous-draft blurbs (Labour, Financial, GDP, Housing) can now be regenerated without baking stale anchors.

Remaining blockers per section:
- **Labour**: Claim 3 V/U judgment still open; regenerating a blurb is safe (fabricated quotes removed), but the V/U bands language may need a follow-up pass.
- **Financial, GDP, Housing**: no open judgment items. Blurb regen is clean.

Recommended next-session order:
1. Resolve Labour Claim 3 V/U bands + Claim 10 propagation (dedicated session; bring the discussion thread).
2. Regen all four blurbs: `python analyze.py --section labour` / `financial` / `gdp` / `housing`. (CLI subscription path; no API key needed locally.)
3. Voice-iteration pass on the regenerated blurbs.
4. Implement deep-dives per `analyses/deep-dive-design-2026-05-09.md` — Policy page first (yield dependencies for Housing).

### Resume entry points

- **Open judgment items** — see "Open judgment items" above. Labour Claim 3 V/U is the highest-priority unresolved item.
- **Blurb regen** — all four autonomous-draft sections are now ready: `python analyze.py --section <labour|financial|gdp|housing>`.
- **Deep-dive implementation** — `analyses/deep-dive-design-2026-05-09.md` is the spec. Policy page first.
- **Convention sweep log** — `git log --oneline c994fb0..90bdb5d` shows the full sweep in chronological order.
- **Per-section verification logs** — `markdown-files/verification/{labour,inflation,policy,gdp,housing,financial}.md`. All mechanical patches applied; open items marked.
- **`markdown-files/verification/_tiers.md`** — canonical glossary for the three-tier framework.

---

## File structure

```
boc-tracker/
├── fetch.py                ← pulls data from APIs, saves CSVs to data/
├── analyze.py              ← reads framework + data, calls Claude Opus, writes data/blurbs.json
├── build.py                ← reads CSVs + blurbs.json, builds index.html
├── requirements.txt        ← requests, pandas, plotly, anthropic
├── README.md               ← project overview; portfolio-facing
├── .gitignore              ← __pycache__/, *.pyc, .claude/, probe_*.py, table-*.json
├── index.html              ← generated output; do not edit by hand
├── policy.html             ← Policy deep-dive (7 live charts); generated by build.py
├── inflation.html          ← Inflation deep-dive; 1 live chart (core individual measures) + 4 placeholder stubs; generated by build.py
├── gdp.html                ← GDP deep-dive; 2 live charts (real GDP vs potential, output gap) + 4 placeholder stubs; generated by build.py
├── labour.html             ← Labour deep-dive; 1 live chart (Beveridge curve) + 7 placeholder stubs; generated by build.py
├── housing.html            ← Housing deep-dive; 5 live charts + 1 static reference chart (mortgage renewal shock); generated by build.py
├── financial.html          ← Financial deep-dive; 1 live chart (WTI−WCS differential) + 5 placeholder stubs; generated by build.py
├── trade.html              ← Trade & External Sector deep-dive (5 placeholder sections); generated by build.py
├── demographics.html       ← Demographics & Labour Supply deep-dive (5 placeholder sections); generated by build.py
├── reference/              ← personal-reference documents (PDFs, Word docs, research artifacts; gitignored)
├── data/                   ← all fetched CSVs + generated blurbs (source-of-truth for build.py)
│   ├── CPI series: cpi_all_items.csv (SA v41690914), cpi_all_items_nsa.csv (NSA v41690973),
│   │     cpi_food.csv, cpi_energy.csv, cpi_goods.csv, cpi_services.csv, cpi_shelter.csv,
│   │     cpi_trim.csv, cpi_median.csv, cpi_common.csv, cpix.csv, cpixfet.csv
│   ├── cpi_components.csv        ← wide CSV: 60 depth-3 components × ~500 months
│   ├── cpi_breadth_mapping.json  ← component metadata: vector IDs, basket weights, names
│   ├── Labour series: unemployment_rate.csv, unemployment_level.csv, employment_rate.csv,
│   │     participation_rate.csv, job_vacancy_rate.csv (monthly NSA v1212389365),
│   │     job_vacancy_level.csv (monthly NSA, scaled to millions), unit_labour_cost.csv,
│   │     lfs_wages_all.csv, lfs_wages_permanent.csv, seph_earnings.csv, lfs_micro.csv
│   ├── Policy / financial series: overnight_rate.csv, overnight_rate_daily.csv, fed_funds.csv,
│   │     yield_2yr.csv, yield_5yr.csv, yield_10yr.csv, yield_30yr.csv, us_2yr.csv,
│   │     corra_daily.csv, usdcad.csv, wti.csv, brent.csv, wcs.csv,
│   │     indeed_postings_ca.csv (daily SA), indeed_postings_ca_monthly.csv (monthly mean derived)
│   │     [pending FRED retry: ecb_rate.csv, boe_rate.csv, rba_rate.csv — FRED timed out 2026-05-09]
│   ├── BoC Balance Sheet: boc_total_assets.csv, boc_goc_bonds.csv, boc_settlement_balances.csv
│   ├── Inflation expectations: infl_exp_consumer_1y.csv, infl_exp_consumer_5y.csv,
│   │     bos_dist_below1.csv, bos_dist_1to2.csv, bos_dist_2to3.csv, bos_dist_above3.csv,
│   │     infl_exp_above3.csv
│   ├── GDP / Activity series: gdp_monthly.csv, gdp_quarterly.csv,
│   │     gdp_total_contribution.csv, gdp_contrib_*.csv (6: consumption, investment, govt,
│   │     exports, imports, inventories), gdp_industry_*.csv (4: goods, services,
│   │     manufacturing, mining_oil)
│   ├── Housing series: housing_starts.csv, new_housing_price_index.csv,
│   │     residential_permits.csv, crea_mls_hpi.csv, housing_affordability.csv,
│   │     mortgage_rate_5yr.csv, crea_resales.csv, crea_snlr.csv,
│   │     crea_resales_toronto.csv, crea_resales_vancouver.csv, crea_resales_calgary.csv,
│   │     units_under_construction.csv
│   └── blurbs.json               ← generated by analyze.py; section_id -> {as_of, model, text}
├── analyses/                ← one-off research scripts and reference data; NOT run by pipeline
│   ├── trim_vs_median_skewness.py        ← empirical test on a framework claim
│   ├── trim_vs_median_skewness_results.csv
│   ├── trim_vs_median_skewness_plot.png
│   ├── boc_speech_breadth_reference.csv  ← BoC's own published breadth chart data
│   ├── bocfed_spread_distribution.py / .csv / .png  ← worked example for distribution_conventions.md
│   ├── bocfed_spread_38bp_test.md        ← methodology drift evidence
│   ├── can2y_overnight_spread_distribution.py / .csv / .png
│   ├── financial_distribution.py / .csv  ← USDCAD distribution analysis
│   ├── gdp_distribution.py / .csv        ← inventories + housing-trough distribution
│   ├── inflation_distribution.py / .csv
│   ├── housing_distribution.py / .csv
│   ├── labour_distribution.py / .csv
│   ├── beveridge_curve_canada.py / .html ← Plotly Beveridge curve; candidate lead chart for Labour deep-dive
│   ├── deep-dive-design-2026-05-09.md    ← full design for all 8 deep-dives (43 charts, 9 judgment calls resolved)
│   ├── data-source-probe-2026-05-09.md   ← output gap, CORRA, CPI ex-indirect-tax, TSX confirmations
│   ├── lfs-gross-flows-probe-2026-05-09.md ← LFS gross-flows methodology probe
│   ├── housing_deepdive_probe_2026_05_09.py / housing_deepdive_probe_results_2026_05_09.md ← Housing deep-dive data availability probe
│   ├── housing_deepdive_probe2_2026_05_09.py / housing_deepdive_probe2_results_2026_05_09.md ← Housing deep-dive second probe (CREA CMA series)
│   └── project-evolution-2026-05-09.md / .html / .pdf ← project evolution narrative
└── markdown-files/          ← reference docs and this handoff
    ├── HANDOFF.md
    ├── analysis_framework.md             ← internal analytical brief for blurb generation
    ├── chart_style_guide.md              ← formatting principles + workflow rules (first-read)
    ├── dashboard_purpose.md              ← what the dashboard exists to answer (first-read)
    ├── distribution_conventions.md       ← five-tier ladder for indicator readings (first-read; adopted 2026-05-09)
    ├── blurb_quality_log.md              ← May 2026 testing-session lessons + open questions
    └── archive/                          ← superseded / deprioritised planning docs
        ├── vision.md
        ├── reading_guide.md
        ├── gdp_inventories_research.md
        ├── boc_mpr_charts_inventory.md
        ├── boc_mpr_tracking_priority.md
        └── boc_mpr_data_methodology.md
```

The `analyses/` folder is for one-off research and reference data. Scripts there are run manually, never by `fetch.py` or `build.py`. Each analysis is a self-contained `.py` file that reads from `data/` and writes its own outputs (CSV/PNG) into `analyses/`. Any `probe_*.py` files at the project root were cleaned up — none remain there. The `.gitignore` still blocks `probe_*.py` at root; new probes should go in `analyses/` with descriptive names.

---

## How to run

```bash
# Step 1: download fresh data from APIs (run when you want to update data)
$env:FRED_API_KEY = "<your-key>"                          # PowerShell; or set persistently via [Environment]::SetEnvironmentVariable
python fetch.py

# Step 2 (optional but recommended): regenerate the dashboard blurbs
# Local path: if `claude` CLI is installed and authenticated, no API key needed.
python analyze.py                                         # writes data/blurbs.json
# CI / forced SDK path: set ANTHROPIC_API_KEY and CLAUDE_AUTH_MODE=api
# $env:ANTHROPIC_API_KEY = "sk-ant-..."
# $env:CLAUDE_AUTH_MODE = "api"

# Step 3: regenerate the dashboard HTML from saved CSVs + blurbs
python build.py

# Step 4: view locally
start index.html          # Windows
open index.html           # Mac
```

`build.py` is offline. Only `fetch.py` and `analyze.py` make network calls.

The `--wait` flag on `fetch.py` activates a retry loop for StatsCan series: compares the latest date in the API response to the saved CSV; if no update is detected it sleeps 30 seconds and retries (up to 10 times). Used by the 8:30 AM ET scheduled runs; not needed for the BoC daily run.

`analyze.py --print-only` computes the section's data values and previews the prompt without calling the API. Useful for inspecting the inputs the model will see. `analyze.py --section <id>` selects which section to (re)generate; default is `inflation` (currently the only wired section).

---

## Data APIs

### Statistics Canada WDS

**Endpoint:** `POST https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods`
**Body:** `[{"vectorId": <int>, "latestN": <int>}]` — array even for one vector

Response is a JSON array; access via `payload[0]`. To find a vector ID: hit `getCubeMetadata` for the product ID (or use one of the discovery probes archived under `analyses/` if you write a new one). **Do not trust the surface table number** — vector 41690914 was historically labelled "table 18-10-0006-01, NSA" in our own comments but is actually in the seasonally adjusted table 18-10-0006. Always verify with `getSeriesInfoFromVector`.

### Bank of Canada Valet API

**Endpoint:** `GET https://www.bankofcanada.ca/valet/observations/{series_key}/json`
**Query params:** `start_date=YYYY-MM-DD`

Browse all series keys at https://www.bankofcanada.ca/valet/lists/series/json. API docs: https://www.bankofcanada.ca/valet/docs.

### Federal Reserve (FRED) API

**Endpoint:** `GET https://api.stlouisfed.org/fred/series/observations`
**Query params:** `series_id`, `observation_start`, `api_key`, `file_type=json`
**Key:** stored in env var `FRED_API_KEY` (also a GitHub Actions secret). Free registration at fred.stlouisfed.org.
Missing values are returned as `"."` (string) and filtered out in `fetch_fred()`.

### Alberta Economic Dashboard API

**Endpoint:** `GET https://api.economicdata.alberta.ca/data?table=OilPrices`
No auth required. Returns ~700 records covering several oil grades. WCS is filtered by `Type == "WCS"`. **Watch for trailing whitespace in JSON keys** — the API returns `"Type "` (with space) on some records; we strip keys before filtering.

---

## Current series

| CSV filename | Source | Identifier | Description | Frequency |
|---|---|---|---|---|
| `cpi_all_items` | StatsCan | Vector 41690914 | All-items CPI, Canada, **SA** (Table 18-10-0006-01) | Monthly |
| `cpi_all_items_nsa` | StatsCan | Vector 41690973 | All-items CPI, Canada, **NSA** (Table 18-10-0004-01) | Monthly |
| `cpi_food` | StatsCan | Vector 41690974 | Food CPI, Canada, NSA (Table 18-10-0004-01) | Monthly |
| `cpi_energy` | StatsCan | Vector 41691239 | Energy CPI, Canada, NSA (Table 18-10-0004-01) | Monthly |
| `cpi_goods` | StatsCan | Vector 41691222 | Goods CPI, Canada, NSA (Table 18-10-0004-01) | Monthly |
| `cpi_services` | StatsCan | Vector 41691230 | Services CPI, Canada, NSA (Table 18-10-0004-01) | Monthly |
| `cpi_shelter` | StatsCan | Vector 41691050 | Shelter CPI, Canada, NSA (Table 18-10-0004-01) | Monthly |
| `cpi_trim` | BoC Valet | `CPI_TRIM` | CPI-trim, Y/Y % | Monthly |
| `cpi_median` | BoC Valet | `CPI_MEDIAN` | CPI-median, Y/Y % | Monthly |
| `cpi_common` | BoC Valet | `CPI_COMMON` | CPI-common, Y/Y % | Monthly |
| `cpix` | BoC Valet | `ATOM_V41693242` | CPIX (excl. 8 volatile), Y/Y % | Monthly |
| `cpixfet` | BoC Valet | `STATIC_CPIXFET` | CPIXFET (excl. food & energy), Y/Y % | Monthly |
| `cpi_components` | StatsCan | 60 vectors (see mapping JSON) | Wide CSV: one column per CPI component | Monthly |
| `unemployment_rate` | StatsCan | Vector 2062815 | Unemployment rate, Canada, SA | Monthly |
| `unemployment_level` | StatsCan | Vector 2062814 | Unemployment count, Canada 15+, SA — Table 14-10-0287-01; scale 0.001 (thousands → millions of persons) | Monthly |
| `employment_rate` | StatsCan | Vector 2062817 | Employment rate (employment/working-age population), Canada 15+, SA — Table 14-10-0287-01 | Monthly |
| `participation_rate` | StatsCan | Vector 2062816 | Participation rate (labour force/working-age population), Canada 15+, SA — Table 14-10-0287-01 | Monthly |
| `job_vacancy_rate` | StatsCan | Vector 1212389365 | Job vacancy rate, Canada total economy, **NSA** — Table 14-10-0371-01; monthly NSA (no monthly SA series exists); series begins 2015. 12M MA derived line (`job_vacancy_rate_12m`) used as chart default | Monthly |
| `job_vacancy_level` | StatsCan | Vector 1212389364 | Job vacancies count, Canada total, NSA — Table 14-10-0371-01; scale 0.000001 (persons → millions so it shares an axis with `unemployment_level`); series begins 2015 | Monthly |
| `unit_labour_cost` | StatsCan | Vector 1409159 | Unit labour costs, business sector, Canada, SA index (2017=100) — Table 36-10-0206-01 | Quarterly |
| `lfs_wages_all` | StatsCan | Vector 105812645 | LFS avg hourly wages, all employees, SA | Monthly |
| `lfs_wages_permanent` | StatsCan | Vector 105812715 | LFS avg hourly wages, permanent employees, SA | Monthly |
| `seph_earnings` | StatsCan | Vector 79311153 | SEPH avg weekly earnings, all employees, SA | Monthly |
| `lfs_micro` | BoC Valet | `INDINF_LFSMICRO_M` | BoC LFS-Micro, composition-adjusted Y/Y | Monthly |
| `overnight_rate` | BoC Valet | `STATIC_ATABLE_V39079` | BoC overnight rate target | Monthly |
| `fed_funds` | FRED (special) | See below | Fed funds target midpoint | Mixed |
| `yield_2yr` | BoC Valet | `BD.CDN.2YR.DQ.YLD` | 2Y GoC benchmark bond yield | Daily |
| `yield_5yr` | BoC Valet | `BD.CDN.5YR.DQ.YLD` | 5Y GoC benchmark bond yield | Daily |
| `yield_10yr` | BoC Valet | `BD.CDN.10YR.DQ.YLD` | 10Y GoC benchmark bond yield | Daily |
| `yield_30yr` | BoC Valet | `BD.CDN.LONGBOND.DQ.YLD` | 30Y GoC benchmark bond yield | Daily |
| `corra_daily` | BoC Valet | `AVG.INTWO` | CORRA (Canadian Overnight Repo Rate Average) | Daily |
| `us_2yr` | FRED | `DGS2` | US 2Y Treasury constant maturity | Daily |
| `usdcad` | FRED | `DEXCAUS` | CAD per USD (USD/CAD; higher = weaker CAD) | Daily |
| `wti` | FRED | `DCOILWTICO` | WTI crude oil, USD/barrel | Daily |
| `brent` | FRED | `DCOILBRENTEU` | Brent crude oil, USD/barrel | Daily |
| `wcs` | Alberta API | `OilPrices` table, Type=WCS | Western Canada Select, USD/barrel | Monthly |
| `ecb_rate` | FRED | `ECBDFR` | ECB deposit facility rate | Monthly — **CSV pending FRED retry** |
| `boe_rate` | FRED | `IRSTCB01GBM156N` | Bank of England policy rate | Monthly — **CSV pending FRED retry** |
| `rba_rate` | FRED | `IRSTCB01AUM156N` | Reserve Bank of Australia policy rate | Monthly — **CSV pending FRED retry** |
| `indeed_postings_ca` | Indeed Hiring Lab (CC BY 4.0) | `github.com/hiring-lab/data` `CA/aggregate_job_postings_CA.csv`, "total postings" SA | Indeed Job Postings Index, Canada, daily SA, baseline Feb 1 2020 = 100. Pre-aggregated monthly mean is saved as `indeed_postings_ca_monthly.csv`. **Tier 2 (autonomous) data source — not yet user-reviewed; chart wiring pending 2026-05-10 design pass (needs MultiLineSpec secondary y-axis for the index unit).** Covers JVWS COVID gap (Apr-Sep 2020); BoC has used Indeed-Canada in SAN 2021-18 and SWP 2022-17. | Daily |
| `gdp_monthly` | StatsCan | Vector 65201210 | Monthly real GDP, all industries, chained 2017 $, SAAR — C$ trillions | Monthly |
| `gdp_industry_goods` | StatsCan | Vector 65201211 | Monthly real GDP, goods-producing industries, chained 2017 $, SAAR — C$ trillions | Monthly |
| `gdp_industry_services` | StatsCan | Vector 65201212 | Monthly real GDP, services-producing industries, chained 2017 $, SAAR — C$ trillions | Monthly |
| `gdp_industry_manufacturing` | StatsCan | Vector 65201263 | Monthly real GDP, manufacturing, chained 2017 $, SAAR — C$ trillions | Monthly |
| `gdp_industry_mining_oil` | StatsCan | Vector 65201236 | Monthly real GDP, mining/quarrying/oil & gas extraction, chained 2017 $, SAAR — C$ trillions | Monthly |
| `gdp_total_contribution` | StatsCan | Vector 79448580 | Total GDP at market prices, contribution to annualized Q/Q growth, percentage points (Table 36-10-0104, SAAR) — overlay line on the GDP Growth Contributions chart | Quarterly |
| `housing_starts` | StatsCan | Vector 52300157 | CMHC housing starts, Canada total, SAAR (thousands) — Table 34-10-0158-01 | Monthly |
| `new_housing_price_index` | StatsCan | Vector 111955442 | NHPI, Canada total, Dec 2016=100, NSA — Table 18-10-0205-01 | Monthly |
| `residential_permits` | StatsCan | Vector 1675119646 | Total residential building permits, value SA, current C$ thousands — Table 34-10-0292-01 | Monthly |
| `crea_mls_hpi` | BoC Valet | `FVI_CREA_MLS_HPI_CANADA` | CREA MLS HPI benchmark, all of Canada, index 2019=100; BoC Financial Vulnerability Indicators; available 2014–present | Monthly |
| `housing_affordability` | BoC Valet | `INDINF_AFFORD_Q` | BoC housing affordability index (ratio of mortgage payment to income); available 2000–present | Quarterly |
| `mortgage_rate_5yr` | BoC Valet | `V80691335` | 5-year conventional mortgage rate; weekly; 1897 rows | Weekly |
| `crea_resales` | BoC Valet | `FVI_CREA_HOUSE_RESALE_INDEXED_CANADA` | CREA national resales, indexed; 146 rows | Monthly |
| `crea_snlr` | BoC Valet | `FVI_CREA_HOUSE_SALES_TO_NEW_LISTINGS_CANADA` | CREA Sales-to-New-Listings Ratio, %; 146 rows | Monthly |
| `crea_resales_toronto` | BoC Valet | `FVI_HOUSE_RESALES_12M_TORONTO` | CREA resales, Toronto CMA, 12M; 48 rows | Monthly |
| `crea_resales_vancouver` | BoC Valet | `FVI_HOUSE_RESALES_12M_VANCOUVER` | CREA resales, Vancouver CMA, 12M; 48 rows | Monthly |
| `crea_resales_calgary` | BoC Valet | `FVI_HOUSE_RESALES_12M_CALGARY` | CREA resales, Calgary CMA, 12M; 48 rows | Monthly |
| `units_under_construction` | StatsCan | Vector 52300170 | Units under construction, Canada total, SAAR — Table 34-10-0158-01; 145 rows. **Tier 2 pending — vector inferred from magnitude; verify with `getSeriesInfoFromVector` before treating as authoritative.** | Monthly |

**Derived series (computed in `_add_derived_series`, not stored as CSVs):** `bocfed_spread`, `can2y_overnight_spread`, `can_us_2y_spread` (yield spreads); `nhpi_yoy` and `crea_mls_hpi_yoy` (Y/Y %); `nhpi_rebased` and `crea_mls_hpi_rebased` (both rebased to Jan 2020 = 100, for the Housing Prices Index toggle); `housing_starts_3m` and `housing_starts_12m` (rolling means, for the Housing Starts legend-as-toggles); `residential_permits_b` (residential_permits / 1e6, i.e. C$ billions); `job_vacancy_rate_12m` (12M rolling mean of monthly NSA job vacancy rate); `job_vacancy_level_12m` (12M rolling mean of monthly NSA job vacancy level, in millions of persons); `yield_10y_2y_spread` (10Y minus 2Y GoC yield spread); `real_overnight_rate` (ex-post real overnight rate: overnight rate target minus trailing CPI Y/Y); `real_2yr_monthly` (ex-post real 2Y yield: 2Y GoC yield minus trailing CPI Y/Y); `mortgage_5yr_goc_5yr_spread` (weekly 5-year conventional mortgage rate minus daily 5Y GoC bond yield, merged via merge_asof — Housing deep-dive chart 2 toggle). Source CSVs are registered in `_DERIVED_SERIES_SOURCES` dict so the data loader knows to load them.

**`fed_funds` construction:** `FEDFUNDS` monthly effective rate (1990–Dec 2008) prepended to `(DFEDTARU + DFEDTARL) / 2` daily midpoint (Dec 2008–present). Built by `fetch_fed_funds_target()`.

---

## GitHub Actions workflow

`.github/workflows/update.yml` — three scheduled triggers plus `workflow_dispatch`:

```
30 12 * * *   → 8:30 AM EDT (summer) — StatsCan release window
30 13 * * *   → 8:30 AM EST (winter) — StatsCan release window
 0 15 * * *   → 11:00 AM EDT / 10:00 AM EST — BoC daily yields
```

The DST problem: no single UTC time is 8:30 AM ET year-round. Two cron lines handle this — one fires early (harmless on the other season), one fires exactly right.

Both StatsCan crons use `python fetch.py --wait`; the BoC cron uses `python fetch.py` (one-shot). `FRED_API_KEY` is passed from a configured GitHub Actions secret.

The workflow has a "Generate section blurbs" step that loops over all six section IDs and calls `python analyze.py --section <id>`. It gates on `ANTHROPIC_API_KEY` being present in repo Secrets — if not set, emits a `::warning::` annotation and skips; CI stays green.

---

## Architecture: spec dataclasses

All chart and page configuration lives in the `PAGES` list at the bottom of `build.py`. To add a chart, add a spec to a page's `charts` list. To add a page, add a `PageSpec` to `PAGES`.

### ChartSpec

Single-series chart with a transform toggle. Used for static or simple charts (e.g. unemployment_rate).

```python
@dataclass
class OverlayConfig:
    series: str    # CSV filename without .csv
    label: str     # legend label
    color: str     # hex color

@dataclass
class ChartSpec:
    series: str               # CSV filename without .csv
    title: str
    frequency: str            # daily | weekly | monthly | quarterly | annual | irregular
    color: str
    static: bool = False      # if True, no transform buttons
    default_transform: str = "level"
    default_years: int | None = None
    footnote: str = ""
    overlays: list = []       # list[OverlayConfig]; optional; default empty
```

When `overlays` is non-empty, the builder adds N×T additional traces (N overlays × T transforms), all `visible="legendonly"` by default. The transform buttons use `xformClickOverlay` (instead of `xformClick`) to switch transforms while respecting which overlays are currently active. A legend bar below the chart has one button per overlay (off by default) plus a button for the primary series. The `toggleOverlayTrace` JS function toggles the overlay trace matching the currently active transform. Currently used on the Real GDP (monthly) chart for industry sub-aggregate overlays.

Trace layout: indices `0..T-1` = main series transforms; indices `T..2T-1` = overlay 0 transforms; `2T..3T-1` = overlay 1; etc.

### CoreInflationSpec

Composite chart: shaded range band across 5 core measures + headline CPI Y/Y line + individual toggles for trim and median. Built by `_build_core_inflation_panel`. Trace map: 0/1 = range bounds, 2 = headline, 3 = trim, 4 = median.

### CpiBreadthSpec

Share-above-3% / share-below-1% chart, expressed as deviation from the 1996–2019 historical average. Built by `_build_cpi_breadth_panel`. Computation:
- Source: `data/cpi_components.csv` × weights from `cpi_breadth_mapping.json`
- Drop components whose first valid date is after 1995-01-01 (one component currently)
- For each month, Y/Y for each component → weighted share above 3% and below 1%
- Subtract 1996–2019 average (pre-COVID inflation-targeting era)
- Calibration: 2022 peak (+46 pp) matches BoC's published version (see `analyses/boc_speech_breadth_reference.csv`) within 1 pp

### LineConfig and MultiLineSpec

Generic multi-line chart with per-line legend toggle. Used for Policy Rates, 2Y Yields, Oil Prices.

```python
@dataclass
class LineConfig:
    series: str
    label: str
    color: str
    visible: bool = True
    smooth: bool = True   # False keeps raw data in smooth mode (e.g. monthly WCS on a daily oil chart)

@dataclass
class MultiLineSpec:
    title: str
    lines: list                  # list[LineConfig]
    ticksuffix: str = "%"
    hoverformat: str = ".2f"
    default_years: int | None = None
    line_shape: str = "linear"            # "linear" or "hv" (step)
    smooth_window: int | None = None      # if set, adds Level / Nd Avg toggle
    date_fmt: str = "%b %Y"
    footnote: str = ""
    ymin: float | None = None             # hard floor for y-axis (e.g. 0 for oil to handle negative-print anomalies)
```

When `smooth_window` is set, the builder creates 2N traces (raw 0..N-1, smoothed N..2N-1). `mlXformClick` switches between sets; `mlToggle` preserves which lines are active across switches. Legend gets `id="leg-{div_id}"`.

When `ymin=0`, `rangemode="nonnegative"` is set on the y-axis to clamp the floor.

### StackedBarSpec

Stacked bar chart with per-series legend toggles. Used for the GDP Growth Contributions chart. Reuses `LineConfig` for inputs. Uses Plotly `barmode="relative"` so positive bars stack above zero and negative bars stack below — correct for contribution-to-growth charts where components swing both ways. Y-axis range is computed from the union of stack-sum bounds and per-series bounds, so toggling a hidden trace on doesn't blow out the axis. No transforms; data is treated as already in display units (pp).

### WageSpec

Composite chart: range band across four wage measures + individual toggles for each + Services CPI overlay. Built by `_build_wage_panel`. Trace map:
- 0/1: range bounds across LFS-all, LFS-permanent, SEPH, LFS-Micro
- 2–5: the four wage measures
- 6: Services CPI Y/Y (overlay, dashed red)

Services CPI is clipped to start at the earliest valid wage date so Max view doesn't show 50 years of services-only data.

### CpiLine and CpiSpec

Multi-series CPI chart: each line is computed in all four transforms (Level, M/M, 3M AR, Y/Y). N lines × 4 transforms = N × 4 traces. Built by `_build_cpi_panel`. Visibility = (active transform) AND (line legend toggle on). Default: Y/Y view, 10Y window, only the first line (Headline SA) visible.

```python
@dataclass
class CpiLine:
    series: str
    label: str
    color: str
    visible: bool = False

@dataclass
class CpiSpec:
    title: str
    lines: list                       # list[CpiLine]
    footnote: str = ""
    default_transform: str = "yoy"
    default_years: int | None = 10
```

The current PAGES uses seven lines: Headline (SA), Headline (NSA), Food, Energy, Shelter, Goods, Services. The sub-aggregates plus headline give the framework everything it needs to verify the food/energy/shelter contribution to any headline-vs-core gap directly from the chart.

JS state per chart: `div._cpiTransform` (0–3) and `div._cpiVisible` (array of N booleans). `_cpiInitVisible` seeds the visible array from the initial Plotly trace visibility on first interaction. `_cpiApplyVisibility` recomputes the visible array for all N×4 traces from those two pieces of state.

### PageSpec

```python
@dataclass
class PageSpec:
    title: str
    tagline: str
    output_file: str
    charts: list                       # ChartSpec | MultiLineSpec | StackedBarSpec | WageSpec | CpiSpec | CoreInflationSpec | CpiBreadthSpec | MortgageShockSpec
    sections: dict = field(default_factory=dict)   # {chart_index: section_id}
    is_deep_dive: bool = False
```

`sections` maps a chart index to a section identifier defined in `SECTION_HEADINGS`. When `build_page` reaches that index, it prepends a section heading and (if a blurb exists in `data/blurbs.json`) the blurb above the chart panel. All six section headings are placed today (`{0: "policy", 3: "inflation", 8: "gdp", 10: "labour", 14: "housing", 18: "financial"}`). All six sections have generated blurbs in `data/blurbs.json`.

### Current PAGES definition (20 charts, 6 section headings, 6 blurbs)

```
PageSpec("Bank of Canada Tracker", sections={0: "policy", 3: "inflation", 8: "gdp", 10: "labour", 14: "housing", 18: "financial"}, ...)
  ── MONETARY POLICY (heading + blurb) ──
  MultiLineSpec            — Policy Rates (BoC overnight + Fed funds + BoC−Fed spread toggle, hv step, neutral-rate band 2.25–3.25%, 10Y default)
  MultiLineSpec            — 2-Year Yields (Canada + US + Canada 2Y−Overnight spread toggle + Canada 2Y−US 2Y spread toggle, smooth toggle, 10Y default)
  MultiLineSpec            — BoC Balance Sheet (Total assets + GoC bonds visible + Settlement balances toggle; weekly; CAD billions; 10Y default)
  ── INFLATION (heading + blurb) ──
  CoreInflationSpec        — Core Inflation (range band + headline + trim/median toggle)
  CpiSpec                  — CPI Components (7 lines × 4 transforms, Y/Y default, 10Y default; line order: Headline SA, Headline NSA, Food, Energy, Shelter, Goods, Services; Shelter is between Energy and Goods)
  CpiBreadthSpec           — CPI Breadth (deviation from 1996–2019 avg)
  MultiLineSpec            — Consumer Inflation Expectations (CSCE consumer 1y/5y, 10Y default)
  MultiLineSpec            — Business Inflation Expectations (BOS 4-bucket distribution: <1%, 1–2%, 2–3%, >3% + ">3% most-current vintage" toggle off by default; 10Y default)
  ── GDP & ACTIVITY (heading + blurb) ──
  ChartSpec                — Real GDP (monthly, C$ trillions, 4 transforms, 4 industry overlays via OverlayConfig, level default, 10Y default; conditional unit swap: in Level mode, if the main total series is toggled off via the legend and only industry overlays are visible, the y-axis subtitle and overlay values switch from trillions to billions — industries naturally read in billions, not fractional trillions. Configured via `overlay_level_alt_unit_label="C$ billions"` and `overlay_level_alt_scale=1000.0` on the ChartSpec.)
  StackedBarSpec           — GDP Growth Contributions (6 components stacked + Headline GDP (AR) line overlay from vector 79448580, barmode=relative, 2Y default; subtitle = "Percentage-point contributions to annualized Q/Q growth"; footnote calls out the StatsCan-daily ÷4 convention and the residual = non-profits + statistical discrepancy; x-axis uses quarterly tick labels "Q1 2025" etc. — implemented via explicit tickvals/ticktext because Plotly's bundled d3-time-format does not implement %q)
  ── LABOUR MARKET (heading + blurb) ──
  MultiLineSpec            — Unemployment & Job Vacancies (combined; primary=Rate (%), alt=Level (millions of persons) via button-bar toggle; legend toggles each series. Vacancies are monthly NSA — no SA series exists — so the default-visible vacancy line is a 12M MA derived series (`job_vacancy_rate_12m` / `job_vacancy_level_12m`); raw NSA available as a legend toggle. 10Y default; Beveridge tightness pair)
  WageSpec                 — Wage Growth (range band + 4 measures + Services CPI overlay)
  MultiLineSpec            — Labour Utilization (Employment rate + Participation rate, monthly SA, level only; 10Y default)
  ChartSpec                — Unit Labour Costs (business sector, quarterly SA, default Y/Y; 10Y default)
  ── HOUSING (heading + blurb) ──
  MultiLineSpec            — Housing Starts (three legend-as-toggle lines: Level off, 3M Avg on, 12M Avg on; no transform toggles; thousands SAAR; 10Y default)
  MultiLineSpec            — Housing Prices (NHPI + CREA MLS HPI; Y/Y default with Y/Y ↔ Index button-bar toggle; both rebased to Jan 2020 = 100 in Index view; 10Y default)
  ChartSpec                — Residential Building Permits (level default; C$ billions SA via residential_permits_b derived series; Max default — data starts Jan 2018)
  ChartSpec                — Housing Affordability (BoC INDINF_AFFORD_Q; quarterly ratio; static, 10Y default)
  ── FINANCIAL CONDITIONS (heading + blurb) ──
  MultiLineSpec            — Oil Prices (WTI + Brent + WCS, smooth toggle, ymin=0, 10Y default)
  ChartSpec                — USD/CAD (daily, 10Y default)

PageSpec("Labour Market — Deep Dive", is_deep_dive=True, output_file="labour.html", ...)
  Beveridge Curve (1 live chart — native Plotly, period-coloured scatter, `_build_beveridge_curve_panel`) + 7 placeholder stubs

PageSpec("GDP & Activity — Deep Dive", is_deep_dive=True, output_file="gdp.html", ...)
  Actual vs Potential GDP / Output Gap % (2 live charts — HP filter λ=129,600, numpy fallback) + 4 placeholder stubs

PageSpec("Inflation — Deep Dive", is_deep_dive=True, output_file="inflation.html", ...)
  Individual Core Measures (1 live chart — CpiSpec, trim+median visible by default) + 4 placeholder stubs

PageSpec("Financial Conditions — Deep Dive", is_deep_dive=True, output_file="financial.html", ...)
  WCS–WTI Spread (1 live chart — reference bands at $10–15 normal and $20 pipeline-constrained) + 5 placeholder stubs

PageSpec("Housing Market — Deep Dive", is_deep_dive=True, output_file="housing.html", ...)
  6 live charts: CREA Sales Activity, Mortgage Rate vs 5Y GoC, Units Under Construction, Resales by CMA, Housing Starts Supply Context, Mortgage Renewal Payment Shock (MortgageShockSpec, BoC SAN 2025-21)

PageSpec("Monetary Policy — Deep Dive", is_deep_dive=True, output_file="policy.html", ...)
  MultiLineSpec            — GoC Yield Curve (2Y/5Y/10Y/30Y; smooth toggle; daily)
  MultiLineSpec            — 2Y–10Y Spread (derived: yield_10y_2y_spread; smooth toggle; daily)
  MultiLineSpec            — Real Rates (ex-post: overnight rate and 2Y yield minus trailing CPI Y/Y; monthly)
  MultiLineSpec            — CORRA vs Target (CORRA daily vs overnight rate target; smooth toggle; 2Y default)
  MultiLineSpec            — BoC Assets (total assets + GoC bonds; weekly; CAD billions)
  MultiLineSpec            — BoC Liabilities (settlement balances; weekly; CAD billions)
  MultiLineSpec            — Peer Central Banks (BoC + Fed live; ECB/BoE/RBA pending FRED retry; hv step)

PageSpec("Trade & External Sector — Deep Dive", is_deep_dive=True, output_file="trade.html", ...)
  [5 placeholder sections: Goods Exports by Category, Canada–US Bilateral Trade Balance, Goods Exports Excluding Gold, Terms of Trade, Export Shares by Partner]

PageSpec("Demographics & Labour Supply — Deep Dive", is_deep_dive=True, output_file="demographics.html", ...)
  [5 placeholder sections: Population Growth by Component, Net International Migration, Working-Age Population and Dependency Ratio, Labour Force by Age Group, Population Projections vs Actual]

PageSpec("Housing Market — Deep Dive", is_deep_dive=True, output_file="housing.html", ...)
  MultiLineSpec            — CREA Sales Activity (SNLR % primary; Resales Index toggle; monthly; 10Y default)
  MultiLineSpec            — 5-Year Mortgage Rate vs 5-Year GoC Bond (mortgage rate + GoC 5Y; spread toggle; weekly/daily; smooth toggle; 10Y default)
  ChartSpec                — Units Under Construction (v52300170 Tier 2; SAAR thousands; monthly; 10Y default)
  MultiLineSpec            — Resale Activity by CMA (Toronto/Vancouver/Calgary 12M rolling; monthly; 10Y default)
  MultiLineSpec            — Housing Starts — CMHC Supply Target Context (3M Avg visible; Level/12M Avg toggles; thousands SAAR; 10Y default)
  MortgageShockSpec        — Mortgage Renewal Payment Shock (static horizontal bar; hardcoded BoC SAN 2025-21 data; no transforms; section heading: Mortgage Renewal Shock)
```

Most charts default to 10Y window; the GDP Contributions stacked bar defaults to 2Y because the per-quarter component swings only really tell their story over a recent window. All six sections currently have blurbs in `data/blurbs.json` (inflation and policy are user-iterated; the other four are autonomous-draft pending iteration).

New spec class added 2026-05-09: **MortgageShockSpec** — static bar chart for hardcoded payment-shock data (BoC SAN 2025-21). No transforms, no date range buttons, no data fetching. Currently used on the Housing deep-dive Mortgage Renewal Shock section.

---

## Architecture: transformation system

### Frequency table

| Frequency | Available transforms | Button labels |
|---|---|---|
| `daily` | `level`, `rolling_20d` | Level, 20d Avg |
| `weekly` | `level`, `rolling_4w`, `yoy` | Level, 4W Avg, Y/Y |
| `monthly` | `level`, `mom`, `ar_3m`, `yoy` | Level, M/M, 3M AR, Y/Y |
| `quarterly` | `level`, `qoq`, `qoq_ar`, `yoy` | Level, Q/Q, Q/Q AR, Y/Y |
| `annual` | `level`, `yoy` | Level, Y/Y |
| `irregular` | `level` | Level |

### Transform formulas

| Key | Formula |
|---|---|
| `level` | raw series |
| `rolling_20d` | `v.rolling(20).mean()` |
| `rolling_4w` | `v.rolling(4).mean()` |
| `mom` | `v.pct_change(1) * 100` |
| `ar_3m` | `((v / v.shift(3)) ** 4 - 1) * 100` |
| `qoq` | `v.pct_change(1) * 100` |
| `qoq_ar` | `((v / v.shift(1)) ** 4 - 1) * 100` |
| `yoy` | `v.pct_change(N) * 100` where N = 12/52/4/1 by frequency |

### How toggles are implemented

All transforms are pre-computed at build time and embedded as separate Plotly traces. Only the default is initially visible. Toggle buttons use Plotly `restyle` to swap visibility. Buttons are plain HTML, not Plotly `updatemenus`. **No live calculation of trace values at click time** (transforms are pre-baked); **y-axis range and tick density are computed live in JS** so toggling a series updates the axis to fit only what's visible.

**JavaScript functions:**
- `xformClick(btn, chartId, idx)` — radio-style transform switch for ChartSpec
- `rangeClick(btn, chartId, years)` — set date range for one chart
- `gcRange(years, btn)` — override date range across all charts
- `toggleTrace(btn, chartId, indices)` — generic trace show/hide (CoreInflation, CpiBreadth); calls `_refreshYAxis` after
- `mlXformClick(btn, chartId, mode, lineCount)` / `mlToggle(...)` — MultiLineSpec smooth-mode handling; `mlToggle` calls `_refreshYAxis`
- `cpiXformClick(btn, chartId, transformIdx, ticksuffix)` / `cpiLineToggle(btn, chartId, lineIdx)` / `_cpiApplyVisibility(div)` / `_cpiInitVisible(div)` — CpiSpec state machine
- `_computeYRange(div, xStartMs, xEndMs)` / `_niceDtick(ymin, ymax, target)` / `_dtickFormat(dt)` / `_refreshYAxis(chartId)` / `_applyComputedYAxis(div, update, yr)` — live y-axis computation helpers

State per chart is stored on the div element: `div._mlMode`, `div._cpiTransform`, `div._cpiVisible`.

### Y-axis scaling: live computation from visible traces

Build-time pre-computed Y_RANGES were removed because they baked the union of all traces — toggling a volatile series off (e.g. Energy on the CPI chart) still left the axis compressed by its swings. Replaced with a live JS computation:

- `_computeYRange(div, xStart, xEnd)` scans `div.data` for traces where `visible !== false` and finds the y min/max within the x window. Returns `[ymin - pad, ymax + pad]` with `pad = max(span * 0.08, 0.1)`. Respects a chart-level y-floor (e.g. 0 for oil) carried in the page-level `Y_FLOORS` map.
- `_niceDtick(ymin, ymax, target=5)` returns a round-down "nice" tick interval (1, 2, 2.5, 5 × 10^k) sized so at least `target` ticks fit in the displayed range.
- `_dtickFormat(dt)` returns a tickformat string whose precision matches the dtick so all ticks display the same number of decimal places.
- `applyRange(chartId, years)` is the entry point — sets the x range, computes y range from visible traces, applies dtick + tickformat. For `years === null` (Max view), `xaxis.autorange` is true and y is computed from all visible data.
- `_refreshYAxis(chartId)` re-runs `applyRange` for whatever date window is currently active. Called from every visibility-changing handler (`toggleTrace`, `mlToggle`, `cpiLineToggle`).
- `DEFAULT_RANGES` still initializes each chart's window on `DOMContentLoaded`, which calls `applyRange` and so seeds the axis correctly.

### Y-axis tick density and decimal consistency

Current approach in `build.py`:

- **`_nice_dtick(ymin, ymax, target=5)`** — round-DOWN nice tick interval (1, 2, 2.5, 5 × 10^k) sized so at least `target` ticks fit in the displayed range.
- **`_dtick_format(dtick)`** — tickformat string whose precision matches the dtick value, so all ticks display the same number of decimal places.
- For multi-series charts (MultiLineSpec, WageSpec, CoreInflation, CpiBreadth): dtick is computed from the **displayed range** (data + padding), not raw data. `tick0=0` anchors the tick grid to integer multiples.
- For ChartSpec: no fixed dtick — uses `nticks=7` instead, because different transforms (Level vs M/M) have wildly different scales and a global dtick is wrong for at least one.

### Color palette

The full color palette and rules for when to use each are codified in `markdown-files/chart_style_guide.md` §4. HANDOFF doesn't duplicate to avoid drift; check the style guide as the source of truth.

---

## Architecture: HTML generation

`build.py` assembles the full HTML page as a single string:

```
<!DOCTYPE html>
  <head> CSS </head>
  <body>
    site-header (title, tagline, last-updated)
    global-controls (All charts — 2Y / 5Y / 10Y / Max)
    [section divider+blurb if this index starts a section, then chart panel] × N
    about section
    <script> JS including ALL_CHARTS, DEFAULT_RANGES, Y_FLOORS </script>
  </body>
```

Each chart panel:
```
<div class="section-divider">                ← only when starting a section
  <div class="section-heading">…</div>
  <div class="section-blurb">…</div>
</div>

<div class="chart-panel">
  <div class="chart-header">
    <div class="chart-title">…</div>
    <div class="chart-controls">[transform buttons] [sep] [range buttons]</div>
  </div>
  [Plotly div]
  <div class="chart-legend">…</div>   ← only on multi-trace charts
  <div class="chart-footnote">…</div> ← if footnote set
</div>
```

Plotly JS is loaded from CDN for the first chart only (subsequent panels pass `include_plotlyjs=False`). `displayModeBar` is disabled.

**X-date compaction.** `_compact_x_dates(fig)` runs before every `fig.to_html(...)`. Plotly's default serialization of pandas Timestamp x arrays produces `"YYYY-MM-DDT00:00:00.000000"` (28 chars per entry); for date-only data this trailing time component is pure noise. The helper rewrites each trace's x to `YYYY-MM-DD` strings, cutting `index.html` from ~6.0 MB to ~3.7 MB (~38%). Y values are already encoded as Plotly typed arrays (`bdata` blocks). The JS uses `new Date(x).getTime()` which parses both formats identically, so live y-axis and hover are unaffected. **If a future chart needs intraday x values, skip the helper for that figure** — it will round all timestamps to midnight.

The About section lists all four data sources (StatsCan, BoC Valet, FRED, Alberta Economic Dashboard).

---

## Analysis framework and blurb pipeline

The analytical framework (`markdown-files/analysis_framework.md`) is the internal brief for blurb generation — per-section questions, signals, thresholds. Blurbs are generated by `analyze.py`, which reads the framework + CSV data, calls `claude-opus-4-7`, and writes `data/blurbs.json`. `build.py` injects the section heading + blurb above the chart at the index named in `PageSpec.sections`.

All six sections (`policy`, `inflation`, `gdp`, `labour`, `housing`, `financial`) have:
- A `compute_*_values` + `format_*_values` pair in `analyze.py`
- A verified framework section in `analysis_framework.md` (explicit VERIFIED status flags with BoC primary-source citations)
- A generated blurb in `data/blurbs.json`

**Verification status (updated 2026-05-09 04:00; see `markdown-files/verification/_tiers.md` for tier definitions and per-section logs for findings):**

- **Inflation** — see `markdown-files/verification/inflation.md`. Tier 2 audit identified defects: four-state breadth classification is analyst synthesis presented as canonical (same defect class as Labour Claim 2's 2×2 decoder); three unsourced calibration thresholds (M/M acceleration / deceleration bands; tight-band 0.5pp; headline-core gap 0.3pp). No fabricated quotes. Blurb is Tier 3 (user-iterated).
- **Monetary Policy** — see `markdown-files/verification/policy.md`. Tier 2 audit identified critical defects: `bocfed_spread` thresholds in framework + analyze.py disagree with project data (median 62.5bp not 38bp; ±100bp marks top 18% not 10%); 2Y term-premium "0–40 bp / 20–60 bp" magnitudes have no surfaced primary-source backing; 3×2 conditional decoder for `can2y_overnight_spread` × `action_state` is analyst synthesis. No fabricated quotes. Blurb is Tier 3 (user-iterated).
- **Labour Market** — see `markdown-files/verification/labour.md`. **Tier 3 for Claims 1–2; Tier 3 (provisional, re-review 2026-05-10) for Claim 3; Tier 2 for Claims 4–10.** Two CRITICAL defects in Tier 2 entries: Claim 8 fabricated MPR-Oct-2024 quote (*"1.6% annual real wage gains since 2023"* not located); Claim 10 propagation of US-transferred V/U heuristic that user-verified Claim 3 explicitly rejected. Blurb is Tier 1 (autonomous draft).
- **Financial Conditions** — see `markdown-files/verification/financial.md`. Tier 2 audit identified critical defects: USDCAD stress-corridor peaks don't match project data (March 2020 peak claimed 1.466; actual 1.4539); CAD pass-through ranges mis-paired vs dp2015-91 point estimates; MPR Jan 2025 vs SAN 2025-2 source mis-attribution; algebraic inconsistency in 0.35pp/10% WTI claim. Blurb is Tier 1 (autonomous draft).
- **GDP & Activity** — see `markdown-files/verification/gdp.md`. Tier 2 audit identified defects: C.D. Howe BCC criteria mis-named (framework says "depth, duration, breadth"; canonical wording is "amplitude, duration, scope"); housing-trough anchors don't match project data (claim 118-149k; actual April 2009 low 111.8k); ±3pp inventories threshold unsourced. No fabricated quotes; no US-heuristic transfers. Blurb is Tier 1 (autonomous draft).
- **Housing** — see `markdown-files/verification/housing.md`. Tier 2 audit identified critical defects: 2023 vs 2025 CMHC report citation conflation (4.8M-unit gap and 430-500k/yr through 2030 — actually the 2030 target is 3.5M from the 2023 report; the 4.8M / 430-480k / 2035 numbers are the June 2025 report); CREA MLS HPI mis-described as "hedonic" (actually hybrid repeat-sales + hedonic); BoC affordability anchor mis-stated; cyclical anchors off vs project data. Blurb is Tier 1 (autonomous draft).

**Tier 2 → Tier 3 risk (now empirically confirmed).** The 2026-05-09 audit pass found Tier 2 defects in every section, including claims demonstrably wrong against project data in three sections (Policy, GDP, Financial) and in Housing's 2023-vs-2025 CMHC report conflation. The "VERIFICATION STATUS: verified end-to-end (May 2026)" header in `analysis_framework.md` is empirically wrong for at least Policy, GDP, Financial, and Housing. Each per-section verification log carries the full evidence chain and a cross-claim defects index for prioritized morning review.

**Blurb voice quality:** Inflation and Monetary Policy blurbs went through user iteration cycles and represent ground-truth voice (Tier 3). Labour Market, Financial Conditions, GDP, and Housing blurbs were generated autonomously May 8, 2026 against Tier-2-verified frameworks — Tier 1 prose; expect revision at next review.

**Pipeline notes:**
- `data/blurbs.json` shape: `{section_id: {as_of, model, text}}`.
- `analyze.py --print-only` previews prompt + values without calling the API.
- `analyze.py --section <id>` selects a single section to regenerate.
- After blurb generation, a self-review pass (`review_blurb()`) runs a factual-correctness checklist; flagged blurbs save with `review_flags` for user review rather than blocking.
- **Auth paths for `call_claude()`:** default prefers the `claude` CLI subprocess (subscription path -- no API key needed if `claude` is on PATH and authenticated). Falls back to the Anthropic SDK if `ANTHROPIC_API_KEY` is set. Override via `CLAUDE_AUTH_MODE=cli` or `CLAUDE_AUTH_MODE=api`. CI uses the SDK path (`CLAUDE_AUTH_MODE=api` or no CLI on runner); local regen uses the CLI path. A future session reading this: local `python analyze.py --section <id>` works today without any API key.
- **Policy section data architecture:** action-state classification uses a daily series (`overnight_rate_daily`, V39079, since 2009) + FAD calendar (`data/fad_calendar.json` from BoC iCal feed + `data/fad_history.json` static bootstrap). The chart still uses monthly `overnight_rate` for longer history.
- **Internal naming note:** `compute_external_values` / `format_external_values` in `analyze.py` and `financial` in `PageSpec.sections` refer to the same domain (Financial Conditions); the `external` name is a historical artifact.

---

## What is not yet implemented

- [ ] **`ANTHROPIC_API_KEY` secret — optional future upgrade, shelved** — the current steady state is the CLI subscription path: `python analyze.py --section <id>` works locally any time `claude` is on PATH and authenticated, billed against the user's plan, no API key needed. Setting the secret in repo Settings would additionally enable nightly CI blurb regen via the Anthropic SDK path, but adds per-call cost. The cost tradeoff has been decided in favour of the current approach; this is not a blocker or a priority. If circumstances change (e.g. the CLI auth path becomes unreliable in CI, or the project scales up), revisit at https://github.com/jayzhaomurray/boc-tracker/settings/secrets/actions.
- [ ] **GDP blurb predates `compute_gdp_values` rewiring** — `compute_gdp_values` was rewired to `gdp_total_contribution` (v79448580) in commit `b51bef0`; the saved blurb in `data/blurbs.json` predates this. Queued for regen after framework patches land (see Next Steps item 3); available locally via CLI path.
- [ ] **Labour blurb predates `compute_labour_values` rewiring** — `compute_labour_values` was rewired in commit `945fa8f` to surface utilization, V/U ratio, and ULC; the saved blurb predates this. Queued for regen after framework patches land; available locally via CLI path.
- [ ] **Regenerate housing blurb against the rewired framework** — `compute_housing_values` was rewired in May 2026 to include CREA MLS HPI and housing affordability (mirrors the labour / GDP wiring commits 945fa8f / b51bef0). The saved blurb in `data/blurbs.json` predates the rewiring. Queued for regen after framework patches land; available locally via CLI path.
- [ ] **Average hours worked + involuntary part-time rate** — flagged as coverage gaps in the labour framework but deferred. Avg hours (V3411411) is NSA-only monthly (would need 12M MA); involuntary PT (table 14-10-0029) is annual-only. Decision pending on whether to add either.
- [ ] **Output gap as a live indicator** — BoC publishes a live range each MPR (currently -1.5% to -0.5%); GDP section references it but doesn't fetch it.
- [ ] **Mortgage rate spreads / mortgage debt-service ratio** — flagged in the housing framework's coverage gaps; tracked by BoC FSR but not loaded.
- [ ] **ECB/BoE/RBA rate CSVs not yet fetched** — FRED timed out during 2026-05-09 Policy deep-dive fetch session; `ecb_rate.csv`, `boe_rate.csv`, `rba_rate.csv` are absent. The Peer Central Banks chart currently shows BoC + Fed only. Run `python fetch.py` (with `FRED_API_KEY` set) to complete the fetch; no code changes needed.
- [ ] **Custom domain**

---

## Next steps, in priority order

### 1. ✅ Build scaffolding for Trade and Demographics deep-dive pages

**DONE 2026-05-09.** `trade.html` and `demographics.html` added with 5 placeholder sections each; nav bar now has 9 pages total.

### 2. ✅ Fix Beveridge curve chart; build HP-filter potential GDP

**DONE 2026-05-09.** Beveridge curve rebuilt as native Plotly spec (`_build_beveridge_curve_panel`); iframe removed. HP filter potential GDP (λ=129,600) + output gap % added to `gdp.html`. numpy fallback included; `statsmodels` added to `requirements.txt`.

### 3. Flesh out all deep-dive pages (automated)

All 8 deep-dive pages get real charts per `analyses/deep-dive-design-2026-05-09.md`. Current live chart counts per page:

- **Policy** — 7 live charts (complete per design doc)
- **Housing** — 6 live charts (original 5 + mortgage renewal payment shock)
- **Labour** — 1 live chart (Beveridge curve, native Plotly)
- **GDP** — 2 live charts (Actual vs Potential GDP, Output Gap %)
- **Inflation** — 1 live chart (individual core measures, CpiSpec)
- **Financial** — 1 live chart (WCS–WTI spread)
- **Trade** — 0 live charts (5 placeholder sections)
- **Demographics** — 0 live charts (5 placeholder sections)

**Immediate next action:** Run the 4 probe scripts locally to confirm vector IDs, then dispatch a Sonnet agent to add confirmed series to `fetch.py`, run the fetcher, and wire the remaining charts:
- `python analyses/gdp_deepdive_vectors.py`
- `python analyses/labour_deepdive_vectors.py`
- `python analyses/trade_deepdive_vectors.py`
- `python analyses/demographics_deepdive_vectors.py`

Each script writes a `.md` results file. Wire charts only after results confirm series availability.

### 4. Manual review pass

User goes through each populated deep-dive page and requests specific adjustments, chart removals, or replacements.

### 5. Framework and blurb work

- Regenerate the four autonomous-draft blurbs (Labour, Financial, GDP, Housing) — framework patches all landed 2026-05-09; this is unblocked. Run `python analyze.py --section <id>` locally (CLI subscription path; no API key needed).
- User iteration on regenerated blurbs: voice, analytical framing, takeaway-first structure.
- Remaining open framework items:
  - **RBA two-sided labour methodology** — replicate for Canada. The intent is to cover BOTH demand-side AND supply-side signals as the RBA does ([RBA Bulletin April 2024](https://www.rba.gov.au/publications/bulletin/2024/apr/assessing-full-employment-in-australia.html)). Substantive gap: no Canadian economy-wide voluntary quit-rate series; closest path is LFS gross flows (Table 14-10-0125). Full mapping in memory at `~/.claude/projects/.../memory/project_rba_methodology.md`.
  - **BOS labour-shortage indicators** — the dashboard currently does not pull BOS labour-shortage series; this is why V/U band labels were retitled to purely empirical descriptors. Probe Valet for `BOS`, `LABOUR_SHORTAGE`, `BOS_*`; if found, add to `fetch.py` and integrate into Labour section.
  - **Real-wage benchmark prose extension** — make the wage-pressure cross-check rule explicit in the Labour Thresholds block (currently only in the V/U paragraph framing). Small edit.

### 7b. Skills worth packaging when triggered (not pre-emptively)

These were considered 2026-05-09 against the project's actual failure modes (see `~/.claude/projects/...../memory/infrastructure_match_failure_mode.md`). Each is conditional on a specific evolution:

- **`/add-chart`** — trigger: scaling deep-dive page real charts. The 6 placeholder deep-dive pages will need real charts; estimate 40+ total at full build-out. When that work begins, package a skill that scaffolds ChartSpec + PAGES entry + `_DERIVED_SERIES_SOURCES` registration following established patterns.
- **`/audit-section`** — trigger: re-auditing on a cadence (annually as BoC publications update — new MPRs, SANs, FSRs). The Tier 2 audit prompt template was used 5× on 2026-05-09; if re-audit becomes recurring, packaging it pays back. Lower priority than `/add-chart` since cadence isn't established yet.
- **Hooks: ~never become high-value** for this project (content-bound failure mode, not code-shape). One narrow exception: a data-shape validator on `fetch.py` to catch fetcher regressions like the JVWS stale-zero bug. Set up only if bitten again.

### 7c. Automate the CLI auth path in CI (future project, low priority)

`claude setup-token` produces a long-lived OAuth token. Storing it as a GitHub Actions secret (e.g. `CLAUDE_CODE_OAUTH_TOKEN`) and adding a workflow step to install the Claude CLI and export the token would route nightly blurb regen through the Max subscription instead of the paid API. Caveats: Max plan rate limits apply to CLI usage; headless CI behaviour of the CLI is less battle-tested than the SDK path; actual API cost for this dashboard is pennies per month, so this is nice-to-have, not urgent.

### 8. Charts still on the wishlist

| Chart | Data |
|---|---|
| Headline CPI + CPI ex-indirect-taxes overlay | StatsCan / BoC Valet |
| Employment by sector reliant on US exports | StatsCan LFS Table 14-10-0023 + IO tables |
| Goods exports excluding gold | StatsCan Table 12-10-0011 |
| BOS hiring intentions / pass-through | BoC quarterly BOS publication |

---

## Parked / blocked items

### WCS–WTI spread (Financial Conditions blurb)

**Status:** Placeholder only. Current WCS source (Alberta Economic Dashboard) is monthly and lagged; the live spread in `compute_external_values` mixes monthly-average WCS against a single daily WTI value — not directly comparable. The distribution thresholds in `distribution_conventions.md` were calibrated from monthly WCS vs. monthly WTI (correct pairing), but the live compute is not that. Blurb prose is instructed to omit the spread until resolved.

**What would unblock it:** A free daily (or at least weekly) WCS series. Alberta Economic Dashboard is the only accessible free source and it publishes monthly. TMX / Refinitiv / Bloomberg carry daily differentials but are paid.

### Market-Implied Rate Path chart

**Status:** Investigated May 2026. Blocked on free programmatic access to Canadian implied-rate data.

**Goal:** Forward curve drawn as a dotted continuation of the historical BoC overnight rate, showing the market's expected policy rate at each future date — practitioner-grade replacement for the current "2Y minus overnight" rough proxy.

**Why it's blocked:**
- BoC Valet has no OIS / swap / forward-rate series.
- TMX CRA (3-Month CORRA) futures are the right instrument but no public API exists; scraping m-x.ca would violate TMX Datalinx redistribution restrictions.
- Yahoo Finance carries CME ZQ / SR3 but not CRA. US-only forward path is the wrong centerpiece.
- CME DataMine, paid aggregators out of scope for a free personal dashboard.

**What was incorporated instead:** The 2Y term-premium literature from this investigation sharpened the framework. `analysis_framework.md` Monetary Policy now codifies BoC ACM-model term-premium magnitudes and regime distortions. The 2-Year Yields chart footnote carries the short version.

**Unblocks the chart:** a paid feed (Bloomberg / Refinitiv / TMX Datalinx); BoC publishing a CORRA-OIS series via Valet; or a free aggregator emerging. A possible smaller upgrade: if the BoC FSI 2Y term-premium series is queryable via Valet, a term-premium-adjusted 2Y toggle on the existing chart would be a modest single-point estimate.

---

## Known issues and open questions

1. **`fed_funds` frequency mixing** — CSV is monthly pre-2009, daily post-2009. Step-function rendering on Policy Rates handles it visually. No problems in practice.

2. **Hover format for level series** — `_hover_template()` infers suffix from transform. Unemployment level shows "6.70" with no `%`. Add a `hover_format` field to ChartSpec if a chart looks wrong.

3. **Build-time dtick + tickformat are overwritten by JS** — panel functions still call `fig.update_yaxes(dtick=..., tickformat=...)` at build time, but `applyRange` recomputes both on `DOMContentLoaded`. Build-time settings serve as initial values until JS fires. Could be cleaned up.

4. **CPI breadth basket weights** — 2024-vintage hardcoded in `data/cpi_breadth_mapping.json`. When StatsCan publishes a new basket (~every 2 years), regenerate. Write a fresh probe in `analyses/` next time.

5. **`DFEDTAR` unavailable** — FRED's daily single fed-funds target series returns HTTP 500. Pre-2009 history uses monthly `FEDFUNDS` (effective rate) instead.

6. **CPI chart NSA toggle in Y/Y view** — Headline (SA) and Headline (NSA) Y/Y are essentially identical in Y/Y view. Default has NSA off; the toggle is useful in M/M view where SA matters.

7. **`analyze.py` auth-path resolution** — `call_claude()` resolves auth in this order: (1) `CLAUDE_AUTH_MODE=api` forces the SDK path and requires `ANTHROPIC_API_KEY`; (2) `CLAUDE_AUTH_MODE=cli` forces the CLI subprocess path; (3) default: prefer `claude` CLI if on PATH, fall back to SDK if `ANTHROPIC_API_KEY` is set, otherwise raise. Locally, if `claude` is installed and authenticated, no API key is needed. The SDK path is used in CI (GitHub Actions runner has no `claude` CLI) and gates on the `ANTHROPIC_API_KEY` secret; if absent, the workflow emits `::warning::` and skips regen.

8. **Author display name** — `AUTHOR_DISPLAY_NAME = "jayzhaomurray"` in `build.py`.

9. **Vector ID label drift** — the `cpi_services` comment was historically wrong (claimed table 18-10-0006-01, actually 18-10-0004-01); `cpi_all_items` was mislabelled NSA but is actually SA. Both fixed. **Verify any new vector ID against cube metadata (`getSeriesInfoFromVector`) before adding it.**

10. **Hook `if` filter mis-firing.** The `pre-commit-checkpoint.sh` hook fires the system-reminder on any Bash tool call, not just `git commit`-prefixed commands. The configured `if "Bash(git commit*)"` permission-rule filter isn't gating the hook firing as expected. Worth investigating — either the filter syntax needs adjustment or the hook execution logic doesn't honour the if clause for system-reminder injection. Doesn't block work; just adds noise.
