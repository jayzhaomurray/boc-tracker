# BoC Tracker — Project Handoff

This document captures the current state of the project. Written so a fresh session can continue without any prior context.

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
| 7 | this commit | **Deep-dive site scaffolding.** Multi-page architecture wired into `build.py`: shared cross-page nav bar; 6 placeholder deep-dive pages (one per section); Beveridge curve embedded as a real iframe in the Labour deep-dive. Placeholder content per planned-content list. | `build.py` (`NAV`, `_build_nav_html`, `DEEP_DIVES`, `_assemble_deep_dive_page`); `policy.html`, `inflation.html`, `gdp.html`, `labour.html`, `housing.html`, `financial.html` at project root |

### Highest-priority items for the morning review

The cross-section findings reveal a **defect-class pattern**: the same Tier-2-verified framework that the user is currently auditing claim-by-claim for Labour has analogous defects in every other section. The user's choice to introduce the three-tier framework was prescient — Tier 2 is real but not equivalent to Tier 3.

**Immediate-fix candidates** (defects where the framework prose is demonstrably wrong against project data; can be corrected without research):

1. **Policy** — `bocfed_spread` thresholds in framework + `analyze.py` line ~581 disagree with project data. Median is **62.5bp**, not 38bp; ±100bp marks top 18%, not top 10%; ±150bp marks top 10%, not top 5%. Same defective thresholds appear in two places (framework prose + analyze.py code) — code and prose agree with each other but disagree with the data. (`verification/policy.md` Claim 3.)
2. **Housing** — Citation conflation. Framework's *"2023 CMHC Housing Shortages report estimated Canada needs ~430-500k starts/year through 2030 to close the 4.8M-unit affordability gap"* mixes two reports: 2023 report says 3.5M units by 2030; 4.8M / 430-480k figures come from June 2025 "Solving the Affordability Crisis" report targeting 2035. (`verification/housing.md` Claim 2.)
3. **Financial** — USDCAD stress-corridor peaks don't match project data: framework says "March 2020 (1.466)" but actual `data/usdcad.csv` peak was 1.4539. (`verification/financial.md` Claim 2.)
4. **GDP** — C.D. Howe BCC criteria mis-named: framework says *"depth, duration, breadth"* with literal quote *"pronounced, pervasive, and persistent decline"*; canonical wording is *"amplitude, duration, scope"* with *"pronounced, persistent, and pervasive"*. (`verification/gdp.md` Claim 4.)
5. **Labour** — Claim 8: *"1.6% annual real wage gains since 2023"* attributed to MPR October 2024 was not located in any HTML chapter retrieved. Likely fabrication or conflation with the September 2024 headline-CPI figure (1.6%). User to confirm against the PDF or remove. (`verification/labour.md` Claim 8.) Plus Claim 10 V/U-line propagation defect.

**Deeper analytical items** (defects where the right answer needs user judgment):

- **Labour Claim 3 V/U thresholds** — flagged for user re-review per Tuesday's "save the revision but i still want to go over it again tomorrow morning."
- **Inflation Claim 3** — four-state breadth classification (broad-based pressure / softening / clustered / polarized) is analyst synthesis presented as canonical (same defect class as Labour Claim 2's 2×2 utilization decoder). Cover only 4 of 9 logical breadth-deviation states. Propagates into Inflation Claim 10 ("What to surface").
- **Policy** — 3×2 conditional grid for `can2y_overnight_spread` × `action_state` is analyst synthesis. Same construct class as Labour Claim 2's rejected 2×2 decoder.
- **Housing** — CREA MLS HPI methodology mis-described as "hedonic" (actually hybrid repeat-sales + hedonic); BoC affordability indicator's anchor mis-stated.

**Queued (deferred from earlier commits, still valid):**

- 12M→3M code change in `compute_labour_values` + chart spec + `_DERIVED_SERIES_SOURCES`. Framework has been updated; code is not.
- `MultiLineSpec` secondary y-axis extension to wire the Indeed line into the Unemployment & Job Vacancies chart.
- Re-fetch other StatsCan series and accept the leading-NaN rows (audit Option A) or tighten `fetch_statscan` to strip leading NaN only (Option B).

### Defect-class index across all six sections

| Defect class | Sections affected | Severity |
|---|---|---|
| Fabricated quote / number | Labour (Claim 1, Claim 8) | CRITICAL — must fix before any blurb regen |
| Threshold values that disagree with project data | Policy (bocfed_spread), GDP (housing-trough anchors), Financial (USDCAD peaks), Housing (cyclical anchors) | CRITICAL |
| Citation conflation (right facts, wrong source) | Housing (2023 vs 2025 CMHC reports), Financial (MPR Jan 2025 vs SAN 2025-2), GDP (C.D. Howe BCC wording), Labour Claim 7 (Macklem Apr 2023 vs MPR July 2024 In Focus) | high |
| Threshold values asserted without primary-source backing | Inflation (3 thresholds), Labour Claim 4 (ULC > 3%), GDP (inventories ±3pp) | medium |
| Rigid n×n decoder presented as canonical | Labour Claim 2 (resolved Tier 3); Inflation Claim 3 (open); Policy 3×2 grid (open) | medium |
| US heuristic transferred to Canada | Labour Claim 3 (resolved Tier 3); Labour Claim 10 (propagation, open) | high |
| Indicator-naming-leak risk | Labour Claim 9, Financial Claim 10 | low (judgment call) |

The "VERIFICATION STATUS: verified end-to-end (May 2026)" header in `analysis_framework.md` is now empirically wrong for at least Policy, GDP, Financial, and Housing. **Recommend the user decide tomorrow whether to (a) downgrade those headers to "Tier 2 audit identified defects; see verification/<section>.md" before any further blurb regen, or (b) leave them as-is and rely on the per-section audit logs for ground truth.** I left framework prose untouched overnight — the headers reflect the May 8 status, not the post-audit state.

### What I deliberately did NOT do overnight

- Did not edit `markdown-files/analysis_framework.md` framework prose. The audits surfaced defects but the user's original "save and revisit tomorrow" framing for Labour Claim 3 implied the prose-level decisions are user-only.
- Did not regen any blurbs. `data/blurbs.json` for the four autonomous-draft sections (Labour, Financial, GDP, Housing) is still Tier 1; tomorrow's framework decisions should land before any regen.
- Did not run `python fetch.py` to re-pull the StatsCan CSVs (would have surfaced the leading-NaN issue from the audit). Held for user resolution choice.
- Did not extend `MultiLineSpec` for the Indeed dual-axis chart wiring. Architectural change with judgment on schema design.
- Did not push to remote yet — pushing is on user discretion. (Five commits ready: `b34bebe`, `1219d80`, `165e7cc`, `33eb0cd`, `2a5fef7`, plus this one.)

### Morning review workflow (use this for the 2026-05-10 review pass)

The 44 mechanical patches in the verification logs are designed for accept/reject batching, not compose-from-scratch review. Recommended approach:

1. **Mechanical batch first.** Open the cross-claim defect-class index above. For each CRITICAL / high-severity entry that has a "Proposed patches" subsection in its verification log, scan the proposed patch (`old_string` + `new_string` + source URL + direct quote) and accept or reject. Each takes ~30–60 seconds. Goal: clear all mechanical patches in one focused session.
2. **Apply via Edit tool.** Patches are formatted to feed straight into Edit (`old_string` / `new_string`). For accepted patches, run Edit on `analysis_framework.md` (or `analyze.py` for the bocfed_spread code patch). Mark the verification log entry as Tier 3 with date.
3. **Judgment items in a separate session.** Items flagged "Judgment item (no patch proposed)" — analyst-synthesised decoders, unsourced thresholds, indicator-naming-leak risk — need different cognitive mode. Do these in a dedicated review where you have headspace to weigh tradeoffs. Don't interleave with mechanical accept/reject — context-switching between mechanical and judgment work doubles the friction.
4. **Defer Labour Claim 3 (V/U) to its own dedicated session.** It's already flagged for re-review with a specific user-skepticism question (whether 0.45–0.60 is genuine tightness or status-quo-bias employer baseline). Treat as a third batch.
5. **After patches land, regen blurbs** for the four Tier 1 sections (Labour, Financial, GDP, Housing) using the corrected framework prose. The autonomous-draft blurbs in `data/blurbs.json` predate every framework change since they were generated.

### Resume entry points

- **Start with the defect-class index above** — pick which CRITICAL items to address first.
- **Read commits in order** if you want to see the night's logical progression: `git log --oneline b34bebe..HEAD`
- **Per-section verification logs** at `markdown-files/verification/{labour,inflation,policy,gdp,housing,financial}.md` carry the page-level evidence chain. Each Tier 2 claim with mechanical defects has a "Proposed patches" subsection.
- **`markdown-files/verification/_tiers.md`** is the canonical glossary for the three-tier framework.

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
├── policy.html             ← deep-dive scaffolding (placeholder); generated by build.py
├── inflation.html          ← deep-dive scaffolding (placeholder)
├── gdp.html                ← deep-dive scaffolding (placeholder)
├── labour.html             ← deep-dive scaffolding (placeholder); embeds Beveridge curve via iframe
├── housing.html            ← deep-dive scaffolding (placeholder)
├── financial.html          ← deep-dive scaffolding (placeholder)
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
│   │     yield_2yr.csv, us_2yr.csv, usdcad.csv, wti.csv, brent.csv, wcs.csv,
│   │     indeed_postings_ca.csv (daily SA), indeed_postings_ca_monthly.csv (monthly mean derived)
│   ├── BoC Balance Sheet: boc_total_assets.csv, boc_goc_bonds.csv, boc_settlement_balances.csv
│   ├── Inflation expectations: infl_exp_consumer_1y.csv, infl_exp_consumer_5y.csv,
│   │     bos_dist_below1.csv, bos_dist_1to2.csv, bos_dist_2to3.csv, bos_dist_above3.csv,
│   │     infl_exp_above3.csv
│   ├── GDP / Activity series: gdp_monthly.csv, gdp_quarterly.csv,
│   │     gdp_total_contribution.csv, gdp_contrib_*.csv (6: consumption, investment, govt,
│   │     exports, imports, inventories), gdp_industry_*.csv (4: goods, services,
│   │     manufacturing, mining_oil)
│   ├── Housing series: housing_starts.csv, new_housing_price_index.csv,
│   │     residential_permits.csv, crea_mls_hpi.csv, housing_affordability.csv
│   └── blurbs.json               ← generated by analyze.py; section_id -> {as_of, model, text}
├── analyses/                ← one-off research scripts and reference data; NOT run by pipeline
│   ├── trim_vs_median_skewness.py        ← empirical test on a framework claim
│   ├── trim_vs_median_skewness_results.csv
│   ├── trim_vs_median_skewness_plot.png
│   └── boc_speech_breadth_reference.csv  ← BoC's own published breadth chart data
└── markdown-files/          ← reference docs and this handoff
    ├── HANDOFF.md
    ├── analysis_framework.md             ← internal analytical brief for blurb generation
    ├── chart_style_guide.md              ← formatting principles + workflow rules (first-read)
    ├── dashboard_purpose.md              ← what the dashboard exists to answer (first-read)
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
$env:ANTHROPIC_API_KEY = "sk-ant-..."                    # PowerShell; set once
python analyze.py                                         # writes data/blurbs.json

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
| `us_2yr` | FRED | `DGS2` | US 2Y Treasury constant maturity | Daily |
| `usdcad` | FRED | `DEXCAUS` | CAD per USD (USD/CAD; higher = weaker CAD) | Daily |
| `wti` | FRED | `DCOILWTICO` | WTI crude oil, USD/barrel | Daily |
| `brent` | FRED | `DCOILBRENTEU` | Brent crude oil, USD/barrel | Daily |
| `wcs` | Alberta API | `OilPrices` table, Type=WCS | Western Canada Select, USD/barrel | Monthly |
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

**Derived series (computed in `_add_derived_series`, not stored as CSVs):** `bocfed_spread`, `can2y_overnight_spread`, `can_us_2y_spread` (yield spreads); `nhpi_yoy` and `crea_mls_hpi_yoy` (Y/Y %); `nhpi_rebased` and `crea_mls_hpi_rebased` (both rebased to Jan 2020 = 100, for the Housing Prices Index toggle); `housing_starts_3m` and `housing_starts_12m` (rolling means, for the Housing Starts legend-as-toggles); `residential_permits_b` (residential_permits / 1e6, i.e. C$ billions); `job_vacancy_rate_12m` (12M rolling mean of monthly NSA job vacancy rate); `job_vacancy_level_12m` (12M rolling mean of monthly NSA job vacancy level, in millions of persons). Source CSVs are registered in `_DERIVED_SERIES_SOURCES` dict so the data loader knows to load them.

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
    charts: list                       # ChartSpec | MultiLineSpec | StackedBarSpec | WageSpec | CpiSpec | CoreInflationSpec | CpiBreadthSpec
    sections: dict = field(default_factory=dict)   # {chart_index: section_id}
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
```

Most charts default to 10Y window; the GDP Contributions stacked bar defaults to 2Y because the per-quarter component swings only really tell their story over a recent window. All six sections currently have blurbs in `data/blurbs.json` (inflation and policy are user-iterated; the other four are autonomous-draft pending iteration).

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
- **Policy section data architecture:** action-state classification uses a daily series (`overnight_rate_daily`, V39079, since 2009) + FAD calendar (`data/fad_calendar.json` from BoC iCal feed + `data/fad_history.json` static bootstrap). The chart still uses monthly `overnight_rate` for longer history.
- **Internal naming note:** `compute_external_values` / `format_external_values` in `analyze.py` and `financial` in `PageSpec.sections` refer to the same domain (Financial Conditions); the `external` name is a historical artifact.

---

## What is not yet implemented

- [ ] **`ANTHROPIC_API_KEY` secret not set in repo Settings** — workflow code is in place; requires the user to add the secret at https://github.com/jayzhaomurray/boc-tracker/settings/secrets/actions. Until set, blurbs stay at the last manually-seeded values; CI runs green.
- [ ] **GDP blurb predates `compute_gdp_values` rewiring** — `compute_gdp_values` was rewired to `gdp_total_contribution` (v79448580) in commit `b51bef0`; the saved blurb in `data/blurbs.json` predates this. Regeneration blocked on `ANTHROPIC_API_KEY`.
- [ ] **Labour blurb predates `compute_labour_values` rewiring** — `compute_labour_values` was rewired in commit `945fa8f` to surface utilization, V/U ratio, and ULC; the saved blurb predates this. Regeneration blocked on `ANTHROPIC_API_KEY`.
- [ ] **Regenerate housing blurb against the rewired framework** — `compute_housing_values` was rewired in May 2026 to include CREA MLS HPI and housing affordability (mirrors the labour / GDP wiring commits 945fa8f / b51bef0). The saved blurb in `data/blurbs.json` predates the rewiring. Regeneration blocked on `ANTHROPIC_API_KEY` (or the Claude Code subscription workaround).
- [ ] **Average hours worked + involuntary part-time rate** — flagged as coverage gaps in the labour framework but deferred. Avg hours (V3411411) is NSA-only monthly (would need 12M MA); involuntary PT (table 14-10-0029) is annual-only. Decision pending on whether to add either.
- [ ] **Output gap as a live indicator** — BoC publishes a live range each MPR (currently -1.5% to -0.5%); GDP section references it but doesn't fetch it.
- [ ] **Mortgage rate spreads / mortgage debt-service ratio** — flagged in the housing framework's coverage gaps; tracked by BoC FSR but not loaded.
- [ ] **Multiple pages / navigation bar** — infrastructure ready; only relevant after chart count grows further.
- [ ] **Custom domain**

---

## Next steps, in priority order

### 1. Set `ANTHROPIC_API_KEY` in repo Secrets to activate full automation

The single switch that turns the dashboard from "data-and-charts auto-update; blurbs hold at last manual seed" into "everything auto-updates nightly." Add the secret at https://github.com/jayzhaomurray/boc-tracker/settings/secrets/actions. After setting it, manually dispatch the workflow once to confirm blurbs regenerate.

### 2. User iteration on autonomous-draft blurbs (Labour, Financial, GDP, Housing)

Labour Market and Financial Conditions blurbs were generated overnight May 8, 2026; GDP and Housing verified May 8 but also autonomous-draft. Monetary Policy and Inflation went through user iteration and are ground-truth voice. The other four need the same treatment — iterate against the framework writing principles (plain language, semantic preservation, action-state verbs, no journey phrasing, takeaway-first). Before iterating GDP and Labour, wire their blurbs against the rewired compute functions (items above).

### 3. Regenerate all four autonomous-draft blurbs once `ANTHROPIC_API_KEY` is set

Labour, Financial Conditions, GDP, and Housing blurbs are autonomous drafts generated May 8, 2026. All four compute functions have since been rewired (GDP: commit b51bef0; Labour: commit 945fa8f; Housing: May 2026 CREA/affordability wiring). Regenerating all four in one pass once the API key is available will align the blurbs with the rewired compute functions and give the user a clean starting point for the voice-iteration pass (item 2 above).

### 4. Eventually: deep-dive Monetary Policy page

A separate page for practitioner-grade detail that doesn't fit on the overview:
- Yield curve term structure (5Y, 10Y, 30Y; 2Y vs 10Y spread for recession indicator)
- Real rates (nominal yields minus inflation expectations)
- CORRA tracking target
- Forward guidance / MPR forecast comparison
- Balance sheet decomposition (maturity, BoC holdings as % of total GoC debt outstanding)
- Cross-central-bank balance sheet comparison

### 5. Eventually: deep-dive Labour Market page

All entries below are **tentative** — surfaced during the framework verification pass on 2026-05-09 and earlier labour scoping discussions. The verification log at `markdown-files/verification/labour.md` carries the discussion that motivated several of them.

**Direct-indicator triangulation for the framework's joint-move read.** The overview-page Labour framework reads employment-rate and participation-rate moves together to infer dynamics (layoffs, discouragement, slack). The 9-state combinatorial space means the inference often forces wrong assignments. Direct indicators that would verify or refute specific inferences:
- LFS reason-for-unemployment (StatsCan Table 14-10-0125) — job-loser share as a direct layoff signal
- LFS R-indicators (R3, R7, R8 etc.) — broader unemployment / discouragement / part-time-for-economic-reasons
- Long-term unemployment share (≥27 weeks) — direct persistent-slack signal
- EI initial claims / beneficiaries (StatsCan Table 14-10-0010 family) — real-time labour-loss read

**Own NAIRU estimation.** The overview-page anchor is currently the IMF's July 2024 estimate (~6%) — a borrowed figure with limited transparency on whether it captures the 2022–2024 immigration-surge skill-mismatch effects. A self-grounded estimate using post-2022 Canadian data (Beveridge-curve regression or Phillips-curve regression with population-growth controls) would materially improve precision. The 2024–2025 immigration policy pullback should reduce structural distortion in the data over time, making a re-estimate increasingly tractable.

**Beveridge curve chart (already built, ready to recycle).** `analyses/beveridge_curve_canada.html` (built 2026-05-09) is a Plotly Beveridge curve for Canada — vacancy rate (3M MA) vs unemployment rate (3M MA), monthly, period-coloured (pre-pandemic, COVID shock, post-COVID overheat, cooling, recent slack). Post-COVID outward shift visually obvious. Source script: `analyses/beveridge_curve_canada.py`. The matching-efficiency / labour-force-composition shift the Labour framework's V/U-bands caveat references is what this chart shows directly. Strong candidate as the lead chart for the deep-dive labour page.

**Other candidate content:**
- Sectoral employment moves (manufacturing layoffs vs services resilience; trade-exposed sectors during tariff cycles)
- Hours worked (NSA monthly with 12M MA — deferred from the May 2026 overview add-pass for data-quality reasons)
- Involuntary part-time rate (annual cadence; deferred similarly)
- Demographic decompositions (newcomer vs Canadian-born; youth 15–24 vs prime-age 25–54 unemployment)
- Regional decompositions (provincial labour-market dispersion; Toronto / Vancouver / Calgary employment patterns)

### 6. Multi-page split (eventually)

When chart count grows further, split into themed pages (policy, inflation, labour, housing deep-dives). **Scaffolding landed 2026-05-09 (commit `ccf5244`)** — `policy.html`, `inflation.html`, `gdp.html`, `labour.html`, `housing.html`, `financial.html` exist as placeholder pages with shared cross-page nav. Real-chart migration into these pages is pending (each placeholder section names what would go there).

### 6b. Skills worth packaging when triggered (not pre-emptively)

These were considered 2026-05-09 against the project's actual failure modes (see `~/.claude/projects/...../memory/infrastructure_match_failure_mode.md`). Each is conditional on a specific evolution:

- **`/add-chart`** — trigger: scaling deep-dive page real charts. The 6 placeholder deep-dive pages will need real charts; estimate 40+ total at full build-out. When that work begins, package a skill that scaffolds ChartSpec + PAGES entry + `_DERIVED_SERIES_SOURCES` registration following established patterns.
- **`/audit-section`** — trigger: re-auditing on a cadence (annually as BoC publications update — new MPRs, SANs, FSRs). The Tier 2 audit prompt template was used 5× on 2026-05-09; if re-audit becomes recurring, packaging it pays back. Lower priority than `/add-chart` since cadence isn't established yet.
- **Hooks: ~never become high-value** for this project (content-bound failure mode, not code-shape). One narrow exception: a data-shape validator on `fetch.py` to catch fetcher regressions like the JVWS stale-zero bug. Set up only if bitten again.

### 7. Charts still on the wishlist

| Chart | Data |
|---|---|
| Headline CPI + CPI ex-indirect-taxes overlay | StatsCan / BoC Valet |
| Employment by sector reliant on US exports | StatsCan LFS Table 14-10-0023 + IO tables |
| Goods exports excluding gold | StatsCan Table 12-10-0011 |
| BOS hiring intentions / pass-through | BoC quarterly BOS publication |

---

## Parked / blocked items

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

7. **`ANTHROPIC_API_KEY` required for `analyze.py`** — without it, `analyze.py` prints computed values + a clear error and exits with code 1. CI skips blurb regeneration with a `::warning::` annotation; the last committed `data/blurbs.json` holds current blurbs.

8. **Author display name** — `AUTHOR_DISPLAY_NAME = "jayzhaomurray"` in `build.py`.

9. **Vector ID label drift** — the `cpi_services` comment was historically wrong (claimed table 18-10-0006-01, actually 18-10-0004-01); `cpi_all_items` was mislabelled NSA but is actually SA. Both fixed. **Verify any new vector ID against cube metadata (`getSeriesInfoFromVector`) before adding it.**
