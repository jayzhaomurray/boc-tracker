# BoC MPR Tracking — Methodology & Data Accessibility, by Theme

Covers the 13 A-tier and 16 B-tier charts from the previous note. Each chart is rated on three dimensions:

**Tier** — how essential to watch:
- **A** = must-track, drives policy directly
- **B** = useful context, refresh on news or monthly

**Methodology difficulty** (to actually rebuild the chart yourself):
- **1** Trivial — plot a published series
- **2** Easy — simple aggregation, indexing, or year-over-year transformation
- **3** Moderate — defined methodology with judgment calls (e.g., the Bank's heatmaps)
- **4** Hard — requires custom code following a published staff note, or matching across datasets
- **5** Very hard — proprietary data or undocumented methodology

**Data access**:
- 🟢 **Free API** — public REST API, scriptable, no subscription
- 🟡 **Free release** — public data but no real API; requires CSV/PDF download or scraping
- 🟠 **Free with effort** — public in principle but stitched together from multiple sources
- 🔴 **Paid** — requires Bloomberg, Refinitiv, Haver, Consensus, or similar

---

## 1. Inflation: levels and breadth

The single most important theme. Everything here is monthly with the StatsCan CPI release.

| Chart | Tier | Method | Data | Source | Notes |
|---|---|---|---|---|---|
| Headline CPI + CPI ex-indirect-taxes | A | 1 | 🟢 | StatsCan WDS Table 18-10-0004; BoC Valet | Both series are pre-published. |
| Core inflation: CPI-trim, CPI-median, CPIX, CPIXFET | A | 1 | 🟢 | BoC Valet (CPI-trim, CPI-median); StatsCan (CPIX, CPIXFET) | All four are computed and published by StatsCan/BoC. |
| Share of CPI components above 3% / below 1% | A | 2 | 🟢 | StatsCan WDS Table 18-10-0006 | Need to fetch all ~150 CPI subcomponents and apply thresholds. Few hours to set up; trivial to maintain. |
| CPI components heatmap | B | 3 | 🟢 | StatsCan WDS Table 18-10-0006 | Standardize each component by 1996–2019 mean/std. Methodology described in MPR notes. The dispersion this captures is usually visible in the simpler share-above-3% chart. |

**Tracker effort overall**: low. Once the StatsCan CPI fetch is wired up, all four charts update with one monthly job.

---

## 2. Inflation expectations

Quarterly and monthly. The BoC cites these directly in deliberations.

| Chart | Tier | Method | Data | Source | Notes |
|---|---|---|---|---|---|
| Inflation expectations (BOS, BLP, CSCE, Consensus) | A | 2 | 🟡 (BoC surveys), 🔴 (Consensus) | BoC publications page; Consensus Economics | BoC publishes BOS, BLP, CSCE results as PDFs with companion CSVs — no real API but data is downloadable. Consensus Economics requires a subscription. The three BoC surveys alone are sufficient for tracking; Consensus is nice-to-have. |

**Tracker effort overall**: low–medium. The BoC publishes survey results to a predictable URL pattern; you can scrape the CSV companions on release day. Quarterly cadence for BOS/CSCE; monthly for BLP. **Consensus is the one paid input** — but you can substitute median professional forecasts from public sources (e.g., the Department of Finance's quarterly economist survey) as a free proxy.

---

## 3. Labour market

The Labour Force Survey (first Friday of each month) is the major between-MPR event.

| Chart | Tier | Method | Data | Source | Notes |
|---|---|---|---|---|---|
| Wage growth (LFS average, SEPH, ULC) | A | 2 (3 for microdata version) | 🟢 | StatsCan WDS Table 14-10-0064 (LFS), 14-10-0203 (SEPH), 36-10-0480 (ULC) | The headline LFS and SEPH wage series are straight pulls. The "LFS microdata, quality-adjusted" series in the BoC's chart requires running the regression in Staff Analytical Note 2024-23 on the LFS public-use microdata file — meaningfully more work, but the headline series alone tells most of the story. |
| Employment by sector reliance on US exports | A | 3 | 🟢 | StatsCan LFS Table 14-10-0023 + StatsCan input-output tables | Need to identify which 3-digit NAICS industries have ≥35% of jobs dependent on US demand using IO tables, then split the LFS employment series accordingly. The Bank doesn't publish exactly which industries it includes, so there's some judgment. One-time setup of moderate complexity. |
| Hiring intentions, BOS | A | 1 | 🟡 | Bank of Canada quarterly BOS publication | Direct chart in the BOS release; no transformation needed. |
| Labour market heatmap | B | 3 | 🟢 | StatsCan: LFS, Job Vacancy and Wage Survey, productivity tables | Six indicators standardized over benchmark windows (Staff Analytical Note 2023-07). Each underlying indicator is also useful on its own. |
| Pace that keeps the employment rate constant | B | 2 | 🟢 | StatsCan LFS | Just population growth × prior-month employment rate. Mechanical once you have the LFS. |
| US labour market (unemployment, payrolls) | B | 1 | 🟢 | BLS API or FRED API | Free with registration. |

**Tracker effort overall**: medium. The wage series and pace-to-keep-rate-constant are easy. The sector-reliance chart and the heatmap each take a day of setup but then run automatically.

---

## 4. Real activity and demand

Quarterly GDP plus its monthly proxy (GDP-by-industry).

| Chart | Tier | Method | Data | Source | Notes |
|---|---|---|---|---|---|
| GDP growth contributions, quarterly | A | 2 | 🟢 | StatsCan WDS Table 36-10-0104 | Need to compute chained-volume contributions to growth and annualize. Standard formula but fiddly. |
| Consumer spending per person by category | B | 2 | 🟢 | StatsCan Table 36-10-0124 (consumption by category) + Table 17-10-0009 (population aged 15+) | Quarterly. |
| Housing starts and resales by region | B | 1 | 🟢 (starts), 🟡 (resales) | CMHC for starts; CREA for resales | CMHC publishes a clean monthly release. CREA national statistics are public but not API-friendly. |

**Tracker effort overall**: medium. The contribution math for GDP needs care; the rest is straightforward.

---

## 5. Trade and tariff transmission

The defining theme of the past year of MPRs. Most data is monthly via StatsCan trade releases.

| Chart | Tier | Method | Data | Source | Notes |
|---|---|---|---|---|---|
| Goods exports excluding gold | A | 2 | 🟢 | StatsCan WDS Table 12-10-0011 (by HS code) | Strip HS 7108 (gold) from totals. |
| Tariff rate calculations (US-on-Canada, etc.) | A | 4 | 🟠 | US Census trade data + USITC Harmonized Tariff Schedule + CBSA tariff schedule | Bank publishes its calculation methodology in Oct 2025 MPR. Replicating it requires HS-level trade weights, sectoral tariff rates, CUSMA compliance assumptions, and remission adjustments. **Highest setup effort of any chart on this list** — but only needs to be updated when US trade actions occur, not on a fixed cadence. |
| Pass-through and price-change expectations, BOS | A | 1 | 🟡 | BoC quarterly BOS publication | Direct chart in the BOS release. |
| Sectoral exports for tariffed industries | B | 2 | 🟢 | StatsCan trade data by HS code | Need to identify HS codes for steel, aluminum, copper, lumber, motor vehicles, then index to a base period. The April 2026 chart is a strong template. |
| Cumulative change in exports by destination | B | 2 | 🟢 | StatsCan trade data by partner country | Sum trade values over a window; subtract base period. |
| Share of non-US imports re-routed through US | B | 4 | 🟠 | StatsCan import data + US Census export data | Reconciling the two datasets at the commodity level is non-trivial. Slow-moving so doesn't need to be updated often. |
| US imports by origin | B | 1 | 🟢 | US Census Bureau API or FRED | Free. |

**Tracker effort overall**: medium to high. Most charts in this theme are easy individually but the tariff-rate calculation is genuinely complex. The advantage is that once you've built it, the structural updates are infrequent (only when US policy changes).

---

## 6. Costs, commodities, oil

Daily for prices, monthly for cost indices.

| Chart | Tier | Method | Data | Source | Notes |
|---|---|---|---|---|---|
| Oil prices: Brent / WTI / WCS | A | 1 | 🟢 (Brent, WTI), 🟡 (WCS) | EIA API for WTI and Brent; WCS via Government of Alberta or via Bloomberg ($) | EIA provides daily spot Brent and WTI for free. WCS has no clean free API; you can scrape the Government of Alberta's daily price page or use the futures contract listed on NYMEX. |
| Brent spot vs front-month futures spread | B | 2 | 🟢 | EIA spot Brent + CME front-month Brent | Both daily, both free. Subtract. |
| Cost pressures heatmap | B | 4 | 🟠 | StatsCan IPPIs and import prices, productivity tables (ULC); Baltic Exchange / Drewry shipping indices; energy from EIA | Same standardization framework as the CPI heatmap, applied to multiple input cost series. Some shipping indices are paid, but headline shipping indicators (Baltic Dry, Freightos FBX) are public. |
| Non-energy commodity prices (BCNEx) | B | 1 | 🟢 | BoC Valet | The Bank publishes its own non-energy commodity index daily. Free and real-time. |

**Tracker effort overall**: low for prices, medium-high for the cost heatmap.

---

## 7. Financial conditions

Daily, all free.

| Chart | Tier | Method | Data | Source | Notes |
|---|---|---|---|---|---|
| 2-year government bond yields (Canada vs US) | A | 1 | 🟢 | BoC Valet (Canada); FRED or Treasury Direct (US) | Free, daily. |
| Equity indexes (S&P/TSX, S&P 500) | B | 1 | 🟢 | Yahoo Finance via `yfinance`; FRED for end-of-day | Free for daily closes; intraday is paid but not necessary for tracking. |
| US policy uncertainty indexes | B | 1 | 🟡 | policyuncertainty.com | Free CSV download; updated daily. No real API but the URL structure is stable. |

**Tracker effort overall**: very low. This whole theme can be set up in an afternoon.

---

## 8. External / global indicators

Monthly. Mostly free.

| Chart | Tier | Method | Data | Source | Notes |
|---|---|---|---|---|---|
| Global / euro area PMI | B | 1 | 🟡 (headline), 🔴 (subcomponents) | S&P Global press releases (headline); Eurostat for euro area aggregate | S&P Global publishes the headline composite, manufacturing, and services PMI numbers in a free press release. The detailed sub-indices (input prices, employment, etc.) are paid. ISM is the US equivalent and is free. |

**Tracker effort overall**: low if you only need headlines.

---

## Summary view

### By methodology difficulty

| Difficulty | Count | Charts |
|---|---|---|
| 1 (trivial) | 11 | Headline CPI, core measures, BOS hiring intentions, BOS pass-through, oil prices, 2y yields, equity indexes, US policy uncertainty, BCNEx, US labour market, US imports, PMI |
| 2 (easy) | 9 | Share above 3% / below 1%, inflation expectations, wage growth, pace to keep employment rate constant, GDP contributions, consumer spending per person, goods exports excluding gold, sectoral exports, cumulative exports by destination, Brent spread |
| 3 (moderate) | 4 | CPI heatmap, employment by US-export reliance, labour market heatmap, housing |
| 4 (hard) | 4 | Tariff rate calculations, share of non-US imports re-routed, cost pressures heatmap |

### By data accessibility

| Access | Count | Comment |
|---|---|---|
| 🟢 Free API | 17 | Most StatsCan, BoC Valet, FRED, BLS, US Census, EIA series |
| 🟡 Free release (no API) | 7 | BoC surveys, S&P Global PMI headlines, CREA, policyuncertainty.com, BoC BOS pass-through |
| 🟠 Free with effort | 3 | Tariff calculations, share re-routed, cost pressures heatmap (multiple data sources to stitch together) |
| 🔴 Paid | 1 partial | Consensus Economics (substitutable with free proxies); PMI subcomponents (only if you want detail beyond headline) |

The honest bottom line is that **none of these charts strictly require a paid data subscription** to track at the level the BoC tracks them. Consensus Economics is the only meaningful exception, and you can substitute the BoC's own CSCE and BOS expectation measures plus a free professional-forecaster aggregate.

### Effort to build the full A-tier dashboard from scratch

Estimated time investment for a competent analyst with Python:
- StatsCan and BoC Valet integrations: **half a day**
- BoC surveys (BOS, BLP, CSCE) scraper: **half a day**
- US data (BLS, Census, EIA, FRED): **a couple of hours**
- Sector-reliance employment chart (one-time IO-table mapping): **half a day**
- Tariff rate calculation engine: **two to three days** (the only really complex one)
- Charting and dashboard layout: **a day**

Roughly a working week to build a free, fully replicating tracker for everything in tier A, with another two or three days to add the tier B charts that aren't redundant with tier A signals.

### What to build first

If you want a minimum viable tracker that captures most of the signal:

1. **StatsCan CPI fetch** — gives you headline, ex-indirect-taxes, all four core measures, and the share-above-3% calculation in one job.
2. **StatsCan LFS fetch** — gives you wage growth, unemployment, employment by industry, and the pace-to-keep-rate calculation.
3. **BoC Valet fetch** — gives you 2y yields, BCNEx, all the BoC publishes.
4. **EIA + FRED fetch** — oil prices and US data.
5. **BoC BOS / BLP / CSCE scraper** — quarterly and monthly survey results.
6. **StatsCan trade data fetch by HS code** — goods exports ex-gold, sectoral exports, exports by destination.

That's six jobs covering 10 of the 13 A-tier charts and most of the B-tier ones. The remaining three A-tier items (employment by US-export reliance, tariff rate calculations) and a couple of B-tier items (cost pressures heatmap, share re-routed through US) take more setup but are infrequently updated.
