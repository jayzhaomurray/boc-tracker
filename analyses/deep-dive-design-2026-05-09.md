# Deep-Dive Page Design — 2026-05-09

Eight deep-dive pages, chart-by-chart. Design only; implementation is deferred. Each section covers: page question, current placeholder content, proposed chart list, tradeoffs, and cross-page dependencies. Trade and Demographics include new-data-fetch appendices.

---

## 1. Policy — Monetary Policy Deep Dive

**Page-level question:** What is the full shape and operational context of the BoC's policy stance — across the yield curve, in real-rate terms, in balance-sheet detail, and relative to peer central banks?

**Existing placeholder content (from `DEEP_DIVES` in `build.py`):** Six sections — yield curve term structure, real rates, CORRA tracking, forward guidance vs MPR projections, balance sheet decomposition, cross-central-bank comparison. All placeholder text.

**Proposed chart list:**

| # | Title | Data series | Spec type | Justification |
|---|---|---|---|---|
| 1 | GoC Yield Curve (2Y / 5Y / 10Y / 30Y) | Existing: `yield_2yr`. NEW: `yield_5yr` (BoC Valet `BD.CDN.5YR.DQ.YLD`), `yield_10yr` (`BD.CDN.10YR.DQ.YLD`), `yield_30yr` (`BD.CDN.LONG.DQ.YLD`) | MultiLineSpec, smooth toggle | Overview shows 2Y only; the term structure shape — flat, inverted, steep — encodes cycle expectations the 2Y alone cannot show. The 2Y–10Y spread has inverted ahead of every Canadian recession since the 1990s. |
| 2 | 2Y–10Y Spread (recession signal) | Derived from `yield_2yr` and `yield_10yr` (both already fetched once chart 1 lands) | ChartSpec, Y/Y not useful — level only | Separate panel for the spread because the scale difference with yield levels makes toggle on the yield curve chart visually poor. The 2024–25 inversion was the deepest since 1990. |
| 3 | Real Rates (nominal minus expectations) | Existing: `yield_2yr`, `infl_exp_consumer_1y`, `infl_exp_consumer_5y`. Derived: `real_rate_2y_1y` = yield_2yr − CSCE 1y | MultiLineSpec | Policy rate relative to neutral is the overview's lens; real rates are the additional dimension — the same nominal rate is more restrictive when inflation falls. The 2y-minus-1y-expectations real rate is defensible and uses already-fetched series. |
| 4 | CORRA vs Target | NEW: `corra_daily` (BoC Valet `AVG.INTWO`) | ChartSpec, daily | CORRA drift from target is the floor-system operational health signal. Post-April-2022 floor-system declaration, CORRA should trade at or just above the deposit rate; persistent drift signals balance-sheet tension. |
| 5 | Balance Sheet Decomposition | Existing: `boc_total_assets`, `boc_goc_bonds`, `boc_settlement_balances`. Derived: non-GoC component = total − GoC bonds | MultiLineSpec | Overview shows total assets, GoC bonds, and settlement balances as lines; the deep-dive reframes them as a stacked decomposition showing GoC bonds, non-GoC (T-bills + repos + other), and compares against the pre-COVID ~$120B baseline and QE peak ~$575B (March 2021). Renders the balance-sheet rundown story more clearly than three parallel lines. |
| 6 | Cross-Central-Bank Policy Rates | Existing: `overnight_rate`, `fed_funds`. NEW: `ecb_rate` (FRED `ECBDFR`, deposit facility rate, weekly), `boe_rate` (FRED `BOERUKQ`, quarterly, or BoE API) | MultiLineSpec, hv step | Shows whether BoC's divergence from the Fed is replicated across peers or is Canada-specific. The 2024 BoC-leads-Fed-on-cuts story is visible in isolation on the overview; the peer context is what the deep-dive adds. |

**Notes on tradeoffs:**
- Chart 3 (real rates): using CSCE 1y consumer expectations as the deflator is a proxy — it reflects household expectations, not the market-implied real rate from TIPS/RRBs. Real return bond yields are available via BoC Valet (`BD.CDN.RRB10YR.DQ.YLD`) but come with their own liquidity distortions. User to decide: CSCE-deflated (simpler, uses existing series) vs. RRB-derived (theoretically cleaner, needs one new fetch). The placeholder text mentions TIPS cross-check; that requires one new FRED series (`DFII10`).
- Chart 6: BoE rate data at quarterly cadence (FRED `BOERUKQ`) is too coarse for a rate-cycle comparison. The Bank of England API (`https://www.bankofengland.co.uk/boeapps/database/`) provides monthly; adds a new fetcher. ECB `ECBDFR` is weekly via FRED — usable. Recommend ECB + Fed (already have) for now; add BoE if user wants fuller peer set.
- Balance sheet decomposition as a stacked bar vs. the current multi-line: StackedBarSpec would require the non-GoC component to be derived and stored as a separate CSV. Medium implementation cost; strong visual payoff.

**Cross-page dependencies:** Chart 1 fetches yield_5yr and yield_10yr; yield_10yr feeds directly into Policy chart 2. No overlap with other deep-dives.

---

## 2. Inflation — Inflation Deep Dive

**Page-level question:** What specific components are driving Canada's inflation, how persistent is the current inflation state, and have long-run expectations moved materially from the 2% anchor?

**Existing placeholder content:** Five sections — headline + ex-indirect-taxes, sub-component decomposition, persistence/breadth distribution, core measures individually, expectations decomposition. All placeholder.

**Proposed chart list:**

| # | Title | Data series | Spec type | Justification |
|---|---|---|---|---|
| 1 | Headline CPI + Ex-Indirect-Taxes | Existing: `cpi_all_items`. NEW: `cpi_ex_indirect_tax` — StatsCan Valet series for CPI excluding indirect taxes (BoC Valet `ATOM_V41693271` or StatsCan v41693271) | MultiLineSpec or ChartSpec with overlay | Carbon-tax repeal in early 2025 carved ~0.6 pp from headline; this pair separates policy-driven from underlying inflation impulse. The overview CPI chart has no ex-indirect-taxes line — this is the non-redundant addition. |
| 2 | Core Measures — Individual Time Series | Existing: `cpi_trim`, `cpi_median`, `cpi_common`, `cpix`, `cpixfet` | CpiSpec (existing class handles N lines × 4 transforms) | Overview CoreInflationSpec collapses the five into a range band + trim/median toggles. The deep-dive shows each measure as its own line with Y/Y transforms, making turning-point disagreements between measures visible. Data already fetched. |
| 3 | CPI Component Contributions (top-10 by weight × Y/Y) | Existing: `cpi_components.csv` (60 components), `cpi_breadth_mapping.json` (weights) | StackedBarSpec (new builder function needed: monthly horizontal/vertical stacked bar of weighted contributions) | The overview CpiBreadthSpec shows the aggregate breadth signal; the deep-dive shows which specific components are contributing most to headline Y/Y. Rotation from shelter to transportation in 2025 is the analytical point. This requires a new rendering function — flagged as medium implementation cost. |
| 4 | Consumer Inflation Expectations — Long-Run Anchor | Existing: `infl_exp_consumer_1y`, `infl_exp_consumer_5y`. NEW: `real_return_bond_10y` (BoC Valet `BD.CDN.RRB10YR.DQ.YLD`) as a market-based long-run anchor | MultiLineSpec | Overview shows consumer 1y and 5y. Adding the real-return-bond-derived 10y breakeven (RRB yield subtracted from nominal 10Y) gives the market-based anchor alongside the survey-based one. Long-run anchor slippage is the most consequential signal; the two-source comparison is practitioner-grade. |
| 5 | Component Y/Y Distribution (histogram by month) | Existing: `cpi_components.csv`, `cpi_breadth_mapping.json` | NEW spec: histogram panel (not in current spec dataclasses) | Distributional view of where components cluster in a given month. Width and tail behaviour change materially across the cycle; the 2022 episode had components past 10% Y/Y. This cannot be done in any existing spec — needs a new static figure type or a client-side histogram builder. Lowest priority of the five — flag as a judgment item. |

**Notes on tradeoffs:**
- Chart 3 (component contributions): building a contribution-to-headline stacked bar from 60 components is substantial. A simpler interim: a table (top 10 contributors + shares) rendered as HTML rather than Plotly. The user should decide: proper Plotly stacked bar (new spec, ~150 lines in build.py) vs. static HTML table (quicker, less visual). Either way, the data is already in `data/`.
- Chart 5 (histogram): no existing Plotly spec handles this. Options are (a) pre-compute a set of histogram traces at build time for the last N months, (b) render as a static PNG via a one-off analysis script. Defer to a separate design pass once charts 1–4 are implemented.
- CPI ex-indirect-taxes vector ID needs verification via `getSeriesInfoFromVector`. The BoC Valet key `STATIC_CPIXFET` excludes food and energy but not indirect taxes. The correct series is StatsCan Table 18-10-0004-01 or the BoC's published CPIX-excluded-indirect-taxes series; needs a lookup probe before committing a vector ID.

**Cross-page dependencies:** Chart 4 fetches `real_return_bond_10y`; this series is also a candidate for Policy chart 3 (real rates). Fetch once, use in both pages.

---

## 3. GDP & Activity — GDP Deep Dive

**Page-level question:** What is the gap between where Canada's economy is and where it could be — and which specific productivity and capacity channels explain it?

**Existing placeholder content:** Five sections — output gap (live BoC range), productivity decomposition, capacity utilization, hours worked, BoC potential-output decomposition. All placeholder.

**Proposed chart list:**

| # | Title | Data series | Spec type | Justification |
|---|---|---|---|---|
| 1 | BoC Output Gap (published quarterly range) | NEW: manual/static — BoC publishes four gap measures quarterly in MPR Appendix + "Indicators of Capacity and Inflation Pressures" page; no Valet key confirmed. Would require either a scraper or a manually-maintained static array. | ChartSpec or static figure | The output gap is the operative slack measure for monetary policy, explicitly flagged as a coverage gap in `analysis_framework.md`. Even a manually maintained series updated each MPR would be more useful than nothing. |
| 2 | Capacity Utilization — Manufacturing + Total | NEW: `capacity_utilization_mfg` (StatsCan Table 36-10-0007, vector to be confirmed; quarterly) | ChartSpec, quarterly Y/Y + level | Manufacturing utilization is the most cyclically informative capacity read; below 80% = slack, above 85% = tight per conventional benchmarks. Fully non-redundant with the overview (not tracked anywhere currently). |
| 3 | Labour Productivity (Real GDP per Hour Worked) | Existing: `gdp_monthly` (SAAR, monthly). NEW: `hours_worked_monthly` (StatsCan Table 14-10-0035, aggregate hours worked, monthly NSA — or LFS total actual hours v2062881) | Derived ChartSpec: gdp / hours, Y/Y | Overview tracks GDP growth. Productivity = output per hour; the two can diverge sharply (2022–2024 episode). This is the cleanest read on Canadian competitiveness weakness Macklem flagged in his Nov 2024 speech. |
| 4 | GDP by Industry — Extended Decomposition | Existing: `gdp_industry_goods`, `gdp_industry_services`, `gdp_industry_manufacturing`, `gdp_industry_mining_oil` | ChartSpec with overlays (existing OverlayConfig pattern) | Overview has these four as toggleable overlays on the total GDP chart. The deep-dive gives them their own panel with Y/Y as default, making sector-level cycle turns visible without the overlay toggle gymnastics. Data already fetched. |
| 5 | Final Domestic Demand vs Headline GDP | Existing: `gdp_contrib_consumption`, `gdp_contrib_investment`, `gdp_contrib_govt`, `gdp_total_contribution` | MultiLineSpec (derived: FDD line = consumption + investment + govt contribution, computed at build time) | The analysis framework flags FDD as the cleanest "underlying" demand read; inventory swings can mask it. Overview shows the contributions stacked bar but not FDD as a standalone series. Low implementation cost — derived from already-fetched series. |

**Notes on tradeoffs:**
- Chart 1 (output gap): no programmatic fetch path is confirmed for the BoC's published gap estimates. The most pragmatic path is a hardcoded data array updated manually each MPR (four times per year) — low maintenance burden for high analytical value. Alternatively, the gap could be scraped from the BoC's Indicators of Capacity and Inflation Pressures page (HTML table), but scraper maintenance is fragile. User to decide: static array (simple) vs. scraper (automated but fragile).
- Chart 3 requires hours-worked data. LFS aggregate hours (v2062881, Table 14-10-0035) is monthly but NSA-only, which was the reason it was deferred from the overview in May 2026. The 12M MA denoising strategy used for job vacancies applies here too. Same decision point deferred from before; the deep-dive is the right place to resolve it.
- Chart 4 overlaps with the overview's industry toggles. The justification is different framing (Y/Y dedicated panel vs level with toggle), but the user should confirm this earns its place vs. being redundant.

**Cross-page dependencies:** `hours_worked_monthly` fetched for chart 3 here feeds directly into Labour deep-dive. Fetch once; share the CSV.

---

## 4. Labour Market — Labour Deep Dive

**Page-level question:** What do direct indicators say about the specific mechanisms driving Canada's labour-market slack — layoffs vs discouragement, demographic composition, regional dispersion?

**Existing placeholder content:** Nine sections — Beveridge curve (already a real embedded iframe), LFS reason for unemployment, R-indicators (R3/R7/R8), long-term unemployment, EI claims, hours worked, demographic decomposition, regional decomposition, Indeed postings. Beveridge curve is implemented; all others are placeholder.

**Proposed chart list:**

| # | Title | Data series | Spec type | Justification |
|---|---|---|---|---|
| 1 | Beveridge Curve | Already built (`analyses/beveridge_curve_canada.html`) | Existing iframe embed | The structural matching-efficiency shift post-COVID is the central visual. Already live. |
| 2 | LFS Reason for Unemployment — Job-Loser Share | NEW: StatsCan Table 14-10-0125; vectors for job-loser, job-leaver, re-entrant, new entrant counts; total unemployment denominator from `unemployment_level` | ChartSpec (job-loser share as %, Y/Y) or MultiLineSpec with job-loser + job-leaver as lines | Resolves the overview's employment/participation joint-move inference. A rising job-loser share is the direct layoff signal; the overview cannot show this. |
| 3 | R-Indicators (R3, R7, R8) | NEW: StatsCan LFS supplementary measures; Table 14-10-0074 (quarterly, Canada total); R3, R7, R8 vector IDs need confirmation | MultiLineSpec | The gap between R8 (broadest — includes involuntary part-time and marginally attached) and R3 (official) widens when slack is opening on margins the headline rate misses. Directly relevant to the BoC's SAN 2025-17 multi-indicator framework. |
| 4 | Long-Term Unemployment Share (≥27 weeks) | NEW: StatsCan Table 14-10-0029 or Table 14-10-0125, long-term unemployment sub-category | ChartSpec, Y/Y | Persistent-slack signal. Rises late in slack episodes; currently elevated relative to 2019. The overview tracks level and direction of headline unemployment — this tracks the duration dimension. |
| 5 | Youth (15–24) vs Prime-Age (25–54) Unemployment | NEW: StatsCan Table 14-10-0287 disaggregated by age group — vectors for 15–24 and 25–54 unemployment rates, SA | MultiLineSpec | Per Macklem June 2024 speech: newcomer unemployment and youth unemployment are rising faster than the headline. Both are direct BoC-tracked channels the overview cannot show. |
| 6 | Indeed Job Postings Index | Existing: `indeed_postings_ca_monthly.csv` (already fetched; chart wiring deferred pending MultiLineSpec secondary y-axis) | Needs MultiLineSpec secondary y-axis extension | Covers the JVWS COVID gap (Apr–Sep 2020); BoC has cited it in SAN 2021-18. Data is in `data/`; the only blocker is the secondary-y-axis architectural change. |
| 7 | EI Initial Claims and Beneficiaries | NEW: StatsCan Table 14-10-0005 (regular beneficiaries, SA) or Table 14-10-0010 (initial claims). Vectors to confirm. | MultiLineSpec | Highest-frequency real-time labour signal. Claims are available with 1–2 week lag; beneficiaries lag by ~2 weeks but track the claims series. BoC watches EI as a leading indicator. |

**Notes on tradeoffs:**
- Chart 3 (R-indicators): Table 14-10-0074 is quarterly; the overview is monthly. A quarterly series is still useful for the deep-dive but is a step down in resolution. Verify whether a monthly R-indicator table exists before committing to quarterly.
- Charts 2, 4, 5, 7 all require new StatsCan vector lookups — four separate probe scripts. Bundle these into a single `analyses/labour_deepdive_vectors.py` probe to confirm IDs before wiring fetch.py.
- The demographic decomposition in the placeholder mentions newcomer vs Canadian-born. StatsCan does publish immigrant status breakdown in LFS (Table 14-10-0080), but the immigrant subcategory series may not be available as a simple vector via WDS — this needs investigation. Deferred from this chart list pending that check; add as chart 8 if the vector confirms.

**Cross-page dependencies:** `hours_worked_monthly` fetched for GDP chart 3 is reused here for hours-worked. GDP and Labour deep-dives share one new fetch.

---

## 5. Housing — Housing Deep Dive

**Page-level question:** What does the full flow of housing activity — resale demand, mortgage stress, the supply-construction pipeline, and regional distribution — say about Canada's housing market that the overview's aggregate indicators cannot?

**Existing placeholder content:** Six sections — resale activity / CREA sales, mortgage rate spreads, mortgage debt-service ratio, units under construction, regional decomposition, CMHC supply-gap, mortgage renewal wave detail. All placeholder.

**Proposed chart list:**

| # | Title | Data series | Spec type | Justification |
|---|---|---|---|---|
| 1 | CREA Sales and Sales-to-New-Listings Ratio | NEW: `crea_sales` (BoC Valet or CREA data; national MLS sales monthly), `crea_snlr` (sales-to-new-listings ratio) — check BoC Financial Vulnerability Indicators series (`FVI_CREA_SALES_*`) | MultiLineSpec or ChartSpec with overlay | Overview tracks prices and construction but not transaction volumes. Sales-to-new-listings is a direct tightness indicator (above 0.65 = seller's market, below 0.45 = buyer's market); it leads price inflections by 1–2 months. |
| 2 | 5-Year Fixed Mortgage Rate vs 5-Year GoC Bond Yield | NEW: `mortgage_rate_5yr` (BoC Valet `BD.CDN.5YR.MTG.DQ.YLD` or similar; verify key) + existing-adjacent `yield_5yr` from Policy deep-dive | MultiLineSpec, spread toggle | The spread between 5-year fixed mortgage and 5-year GoC is the lender risk premium. Per BoC FSR, this spread has been elevated post-2020. The overview shows the BoC affordability ratio but not its rate input directly. |
| 3 | Units Under Construction | NEW: `units_under_construction` (CMHC; StatsCan Table 34-10-0158 has "under construction" alongside starts — same table, different row; vector ID to confirm) | ChartSpec, SAAR level | Under-construction count is a 12–24 month supply pipeline signal distinct from starts. In 2024, starts fell faster than under-construction stayed elevated — the two diverged in a way the overview's starts chart alone cannot show. |
| 4 | Regional Housing Starts (Toronto, Vancouver, Calgary) | NEW: StatsCan Table 34-10-0158, CMA-level starts vectors for Toronto, Vancouver, Calgary | MultiLineSpec | Toronto + Vancouver account for ~60% of the national supply gap per CMHC Spring 2026. Regional starts diverge materially from the national aggregate; Calgary's 2022-onwards outperformance vs Toronto is the current divergence story. |
| 5 | CMHC Affordability-Restoring Pace vs Actual Starts | Existing: `housing_starts`. Static reference lines at 430k and 194k thresholds (hardcoded) | ChartSpec with reference line | Shows how far Canada is from the CMHC-defined affordability-restoring construction pace (430–480k/yr per the June 2025 report). The overview shows starts level against trend; this adds the forward-looking policy target as the benchmark. Implementation note: verify CMHC June 2025 figures are the correct citation before hardcoding — the 2023 report uses a 2030 target of 3.5M units; the June 2025 report targets 4.8M by 2035 at 430-480k/yr; these are different numbers from different reports per the verification log. |
| 6 | Mortgage Renewal Cohort Payment Shock | Static/hardcoded data from BoC SAN 2025-21 | Static HTML table or simple bar chart | The renewal cohorts are quantified BoC data; the deep-dive can render them as a simple visualization of per-cohort payment increases (~60% renewing 2025-26; 5-year fixed average +15-20%). Static data; no fetch required. Lowest implementation cost of the six charts. |

**Notes on tradeoffs:**
- Chart 1: BoC FVI series may include CREA sales volume data; check `FVI_CREA_*` keys on the Valet list before adding a separate CREA data source. If the Valet key exists, this is a one-line addition to `BOC_VALET_SERIES`.
- Chart 2 (mortgage spread): BoC Valet key for 5-year fixed mortgage rate needs verification — the key `BD.CDN.5YR.MTG.DQ.YLD` is plausible but unconfirmed. This also requires `yield_5yr` from the Policy deep-dive, creating an ordering dependency: Policy page vectors should be confirmed first.
- Chart 4: regional starts vectors are multiple per city (single-detached, semi, row, apartment segments + total); pull total starts only per CMA.

**Cross-page dependencies:** Chart 2 depends on `yield_5yr` fetched for Policy chart 1.

---

## 6. Financial Conditions — Financial Deep Dive

**Page-level question:** What does Canada's full external financial picture look like — multilateral FX, credit conditions, equity-market signals, terms of trade — beyond the bilateral USDCAD and oil the overview tracks?

**Existing placeholder content:** Six sections — CEER (multilateral CAD), credit spreads, equity markets, FX risk premium, terms of trade, WCS-WTI differential context. All placeholder.

**Proposed chart list:**

| # | Title | Data series | Spec type | Justification |
|---|---|---|---|---|
| 1 | CEER vs USDCAD (indexed to common base) | NEW: `ceer` (BoC Valet `STATIC_FX_V8702` or similar — confirm key; monthly index) + existing `usdcad` rebased | MultiLineSpec, both rebased to 2019=100 | FX pass-through to CPI runs off the multilateral CEER, not bilateral USDCAD. In some 2025 episodes USDCAD weakened while CEER was roughly flat. This divergence is the analytical point; neither series alone can show it. |
| 2 | Canadian IG Corporate Spreads | NEW: `can_ig_spreads` (FRED `BAMLC0A0CM` is US IG; Canadian equivalent may be via FRED `IRLTLT01CAM156N` or a Bank of Canada CORRA-OIS spread as proxy; alternatively ICE BofA Canadian Corporate index — check FRED availability) | ChartSpec, level | BoC tracks credit spreads as a financial-conditions signal in MPR Current Conditions. Widening = stress; narrowing = risk-on. The overview has no credit-spread indicator. Data availability is the key uncertainty — FRED Canada-specific corporate spread coverage needs verification. |
| 3 | TSX Composite + TSX vs S&P 500 (relative performance) | NEW: `tsx` (FRED `DCOILWTICO` pattern: search for TSX in FRED, or use Yahoo Finance `^GSPTSE`, or BoC Valet) | MultiLineSpec | TSX is 30% financials, 20% energy, 10% materials — it carries commodity-cycle and rate-sensitive sector exposure the S&P 500 doesn't. The TSX/SPX ratio is a real-income proxy for Canada relative to the US. Data source needs confirmation; FRED may carry TSX via `SPTSXINL`. |
| 4 | Terms of Trade (Export Price Index ÷ Import Price Index) | NEW: StatsCan Table 36-10-0121 (Export Price Index) and Table 36-10-0120 (Import Price Index) — quarterly. Vectors to confirm. | ChartSpec, derived ratio, quarterly | Terms-of-trade improvement = real-income transfer to Canada from rest of world; deterioration = transfer out. Partially distinct from FX and oil; the WCS-WTI differential is one component but terms of trade is broader (includes manufactured imports). Directly relevant to the current tariff-shock analysis. |
| 5 | WCS-WTI Spread Context | Existing: `wcs`, `wti` — derived spread computed at build time | ChartSpec with reference bands at $10–15 (normal) and $20 (constrained) | Overview mentions WCS-WTI differential in the blurb but shows individual oil prices only. The deep-dive renders the spread directly with the pipeline-constraint benchmark bands. Data already fetched; purely a build.py addition. |
| 6 | BoC−Fed Spread and BoC−ECB Spread | Existing: `overnight_rate`, `fed_funds`. NEW: ECB deposit facility rate via FRED `ECBDFR` (also fetched for Policy chart 6) | MultiLineSpec | Overview shows BoC−Fed spread as a toggle; the deep-dive adds the BoC−ECB spread to show whether BoC divergence is Fed-specific or broader. Cross-page economy: `ecb_rate` fetched once for both Policy and Financial deep-dives. |

**Notes on tradeoffs:**
- Chart 2 (credit spreads): Canadian-specific corporate spread data in a free API is uncertain. FRED carries the US BofA IG series (`BAMLC0A0CMEY`) cleanly; the Canadian equivalent is not confirmed. The BoC Financial Stability Indicators page may expose a credit-spread series via Valet — needs a lookup probe against the Valet series list. If unavailable freely, consider the US IG spread as a stand-in with an explicit footnote that it reflects global risk-on/off, not Canada-specific credit conditions.
- Chart 3 (TSX): Yahoo Finance data is accessible via `yfinance` Python package but adding a new dependency to `fetch.py` has maintenance implications. Alternatively, BoC Valet may carry TSX via a `FVI_*` key. Check Valet series list before adding a new data source.
- Chart 1: CEER key on BoC Valet may be `BD.CDN.CEER.DQ.YLD` or similar — confirm before wiring. Historical CEER is also available as a downloadable table on the BoC website.

**Cross-page dependencies:** `ecb_rate` shared with Policy chart 6. `yield_5yr` shared with Housing chart 2.

---

## 7. Trade — NEW PAGE (no existing scaffolding)

**Page-level question:** What is Canada's trade exposure — by commodity, by sector, and bilaterally to the US — and what do terms-of-trade and tariff-shock indicators say about the current risk?

**Existing placeholder content:** New page — no existing content.

**Proposed chart list:**

| # | Title | Data series | Spec type | Justification |
|---|---|---|---|---|
| 1 | Exports and Imports — Total and by Category | NEW: StatsCan Table 12-10-0011 (exports of goods, monthly, by SITC or end-use category); Table 12-10-0012 (imports). Key vectors: total exports (v62307720 or equivalent), energy exports, auto/parts, aircraft/machinery, agricultural | StackedBarSpec or MultiLineSpec, monthly, C$ billions | The GDP contributions chart on the overview shows net trade's contribution to growth but not the gross flows or sectoral composition. Sectoral decomposition is what the Trade deep-dive adds. |
| 2 | Canada–US Bilateral Trade Balance | NEW: StatsCan Table 12-10-0009 (international merchandise trade, Canada–US bilateral; monthly) | ChartSpec, monthly, C$ billions | Canada–US bilateral balance is the direct tariff-shock exposure indicator. The BoC has cited US demand as the dominant driver of Canadian export cycles; the current tariff-episode context makes this the most policy-relevant single indicator on the page. |
| 3 | Goods Exports Excluding Gold | NEW: StatsCan Table 12-10-0011 goods exports, excluding gold re-exports | ChartSpec or ChartSpec with overlay | Canada's goods-export trend is materially distorted by gold re-export volatility; ex-gold is the BoC's preferred read on underlying goods export strength. Cited explicitly in the HANDOFF wishlist (item 8). |
| 4 | Terms of Trade | As described in Financial deep-dive chart 4 — cross-page dependency if Trade page is implemented | ChartSpec, derived ratio, quarterly | If the Trade page is implemented, terms of trade belongs here more naturally than on the Financial page. Decision: pick one home; Financial deep-dive is the fallback if Trade doesn't land. |
| 5 | Canadian Export Shares to Major Partners (Canada–US, Canada–EU, Canada–China) | NEW: StatsCan Table 12-10-0011 by destination country — annual or quarterly. Likely available in Table 12-10-0034 (trade by country, annual) | MultiLineSpec or stacked area (StackedBarSpec with % shares) | Concentration risk: over 75% of Canadian goods exports go to the US, making tariff exposure structurally asymmetric relative to GDP peers. The share trend (US, EU, China, rest) shows whether diversification has occurred. |

**New data fetches required (Trade page):**
- `exports_total_monthly` — StatsCan Table 12-10-0011, Canada total merchandise exports, monthly, seasonally adjusted. Candidate vector: confirm via `getCubeMetadata(1210001101)` — Table 12-10-0011 product ID is 1210001100. Vector IDs by category to identify in a probe script.
- `exports_energy`, `exports_auto`, `exports_arable` — sub-category vectors from same table.
- `imports_total_monthly` — StatsCan Table 12-10-0012, analogous vector.
- `bilateral_ca_us_exports`, `bilateral_ca_us_imports` — StatsCan Table 12-10-0009, Canada–US bilateral monthly. Product ID 1210000900.
- Terms of trade: StatsCan Table 36-10-0121 (Export Price Index) and Table 36-10-0120 (Import Price Index), quarterly. Product IDs 3610012100 and 3610012000 respectively.
- Trade-partner shares: StatsCan Table 12-10-0034 (annual) or equivalent.

**Estimated work:**
- `fetch.py`: +8–10 series entries in `STATSCAN_SERIES` (or a dedicated `fetch_trade()` function for more complex multi-vector fetches); ~40–60 lines including comments.
- `build.py`: 5 new chart specs + new `trade.html` entry in DEEP_DIVES; ~80–100 lines. Terms of trade requires a derived series computed at build time (division of two quarterly series).
- One-off probe script in `analyses/` to confirm all vector IDs before wiring: ~30 lines.
- **Total: medium effort** (~150–200 lines across both files, plus probe).

---

## 8. Demographics — NEW PAGE (no existing scaffolding)

**Page-level question:** What does Canada's population and age structure say about the labour-supply trajectory and the structural capacity constraints that monetary policy cannot resolve?

**Existing placeholder content:** New page — no existing content.

**Proposed chart list:**

| # | Title | Data series | Spec type | Justification |
|---|---|---|---|---|
| 1 | Population Growth Rate — Total and by Component | NEW: StatsCan Table 17-10-0009 (quarterly population estimates, Canada total, births, deaths, net international migration, net interprovincial migration); key vectors for population level and major components | StackedBarSpec (components) or MultiLineSpec | Population growth is running at historically elevated rates (~3%/yr 2022–2024) primarily from immigration, then pulling back sharply per the federal immigration-target cut. This directly shifts the denominator of every per-capita labour and housing indicator. The BoC (SAN 2025-14) explicitly decomposes potential output into trend labour input (TLI), which immigration drives. |
| 2 | Net International Migration — Permanent + Temporary | NEW: StatsCan Table 17-10-0009 or IRCC data (quarterly; permanent residents + non-permanent residents = international students + temporary workers). Vectors in Table 17-10-0009 include net immigration component. | MultiLineSpec, quarterly | Non-permanent residents (students, TFWP, IMP) drove the post-2022 immigration surge more than permanent residents; federal policy has now targeted both. The split matters because NPR status affects labour-market attachment and skill-mismatch dynamics. |
| 3 | Working-Age Population (15–64) and Dependency Ratio | NEW: StatsCan Table 17-10-0005 (annual; population by age group) or Table 17-10-0009 (quarterly estimates if age-group disaggregation is available) | ChartSpec or MultiLineSpec, annual | Working-age population share drives structural potential growth; the dependency ratio (non-working-age / working-age) captures the demographic headwind from aging. The BoC's SAN 2025-14 TLI decomposition is driven by this. |
| 4 | Youth, Prime-Age, and 55+ Share of Labour Force | NEW: StatsCan Table 14-10-0027 (LFS employment by age group, SA) — vectors for 15–24, 25–54, 55+ employment and participation rates | MultiLineSpec | The 55+ cohort's participation rate is structurally declining (retirement); the youth and prime-age trajectories encode different cyclical and structural signals. The immigration surge shifted the prime-age share in ways that matter for productivity measurement (new arrivals in prime-age cohort, often in jobs below their skill level). |
| 5 | Population Projections vs Actual (StatsCan + IRCC) | NEW: hardcoded StatsCan demographic projection scenarios (Table 17-10-0057, Population Projections for Canada, provinces and territories) vs realized quarterly population level | ChartSpec with static projection ranges | The federal target cut for 2025–2027 shifts the population trajectory materially below the medium-growth projection. This is the most important structural change for potential output and housing demand; the gap between projections and realizations is the analytical signal. Projection data would be hardcoded (annual StatsCan release); realized data from Table 17-10-0009. |

**New data fetches required (Demographics page):**
- `population_quarterly` — StatsCan Table 17-10-0009, Canada total population estimate, quarterly. Product ID 1710000900. Candidate vector: ~v1(not confirmed; use `getCubeMetadata(1710000900)` to extract).
- `population_net_migration` — from same table, net international migration component vector.
- `population_births`, `population_deaths` — natural increase components.
- `population_working_age` — working-age population (15–64); either from Table 17-10-0009 disaggregated or Table 17-10-0005 (annual). Annual cadence if quarterly unavailable.
- `lfs_by_age_group` — StatsCan Table 14-10-0027, employment/participation by age group (youth, prime, 55+). Vectors to identify in a probe.
- Population projections (chart 5): hardcoded from StatsCan Table 17-10-0057's medium scenario — no fetch needed; update manually on new projection release.

**Estimated work:**
- `fetch.py`: +5–7 series entries in `STATSCAN_SERIES`; some may require a multi-vector custom fetcher if Table 17-10-0009 doesn't expose all components as individual vector IDs; ~50–70 lines.
- `build.py`: 5 new chart specs + new `demographics.html` entry in DEEP_DIVES; ~70–90 lines. Chart 5 requires static data inlined in build.py.
- One-off probe script (`analyses/demographics_vectors.py`): confirm all Table 17-10-0009 and 14-10-0027 vector IDs; ~30 lines.
- **Total: medium effort** (~150–170 lines across both files, plus probe).

---

## Summary

### Totals

| Metric | Count |
|---|---|
| Total charts proposed across 8 pages | 43 |
| Charts using only existing data (no new fetches) | 15 |
| Charts using existing data + derived series | 8 |
| Charts requiring at least one new fetch | 20 |
| New StatsCan series (net, after deduplication) | ~22–26 |
| New BoC Valet series (net) | ~6–8 |
| New FRED series (net) | ~2–3 |

### Implementation cost per deep-dive

| Page | Effort | Main cost driver |
|---|---|---|
| Policy | Medium | 3 new Valet fetches (5Y/10Y/30Y GoC yields, CORRA); stacked balance sheet build |
| Inflation | Medium | CPI ex-indirect-taxes vector lookup; component-contribution stacked bar (new spec) |
| GDP | Medium | Hours-worked fetch; output gap data path decision; capacity utilization vector lookup |
| Labour | Medium | 4 new StatsCan table lookups; MultiLineSpec secondary-y-axis for Indeed |
| Housing | Small-Medium | Mostly existing data or one-line Valet additions; regional starts vector lookup |
| Financial | Medium | CEER/TSX data source confirmation; credit-spread availability check |
| Trade | Medium | 8–10 new StatsCan series; new page in build.py |
| Demographics | Medium | 5–7 new StatsCan series; new page in build.py; projection data hardcoded |

All 8 pages are "medium" by themselves; implementation order that minimizes blocked dependencies: (1) Policy (yields needed by Housing); (2) Housing (yield_5yr confirmed); (3) GDP and Labour together (share hours-worked fetch); (4) Inflation; (5) Financial (shares ecb_rate with Policy); (6) Trade and Demographics (standalone new fetches).

### Remaining judgment calls for user

1. **Output gap (GDP chart 1):** Static array updated manually each MPR vs. scraper vs. skip for now. This is the single highest-value missing indicator in the framework.
2. **CPI ex-indirect-taxes vector ID (Inflation chart 1):** Needs a probe to confirm StatsCan or Valet key before wiring.
3. **Component contribution visualization (Inflation chart 3):** Proper Plotly StackedBarSpec (new spec type, ~150 lines) vs. static HTML table (quicker). The data is already in `data/`.
4. **Terms of trade — Trade page or Financial page:** Assign one home before implementation; building it in both would be redundant.
5. **Credit spreads data source (Financial chart 2):** Confirm BoC Valet FVI availability before adding a new dependency (FRED US IG as stand-in is an option with explicit footnote).
6. **TSX data source (Financial chart 3):** BoC Valet FVI vs `yfinance` new dependency vs FRED. New dependencies to `fetch.py` carry maintenance cost.
7. **CORRA Valet key (Policy chart 4):** BoC Valet key `AVG.INTWO` is the standard CORRA key but needs confirmation.
8. **Histogram spec for CPI distribution (Inflation chart 5):** Build a new spec type or defer indefinitely. This is the lowest-priority chart on the list and the only one with no precedent in the existing spec architecture.
9. **Trade page prioritization:** All five Trade charts need new data. If the tariff-shock context remains dominant in the analytical questions, Trade should move up in implementation order. If not, it's a lower-priority addition than cleaning up the six existing deep-dives.
