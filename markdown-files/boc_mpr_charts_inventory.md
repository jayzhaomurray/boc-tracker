# Bank of Canada Monetary Policy Reports — Chart Inventory & Replicability

**Period covered:** Past year of MPRs (released quarterly):
- **July 2025** (scenario-based; no base-case projection)
- **October 2025** (return to base-case projection)
- **January 2026**
- **April 2026** (most recent)

Approx. **120 charts total**, plus 8–10 statistical tables. The Bank also publishes the underlying data as a CSV/JSON release tied to each report (see `bankofcanada.ca/valet/observations/group/MPR_YYYYMM/csv`), so much of what's plotted is downloadable in clean form. However, a chart being "in the data release" is not the same thing as being replicable — many series in the release are themselves Bank model outputs.

The categorization below sorts charts by what it would actually take to redraw them from scratch.

---

## Tier 1 — Trivially replicable (raw data, no methodology)

These are essentially "plot a public series." Everything you need is on the Bank's Valet API, Statistics Canada, FRED, Bloomberg/Refinitiv, or PolicyUncertainty.com.

### Recurring across most or all four reports
- **CPI inflation, headline + ex-indirect-taxes** (Jul Ch.6, Oct Ch.10, Jan Ch.5, Apr Ch.5) — StatsCan series, Bank just adds a target line.
- **Core inflation measures (CPI-trim, CPI-median, CPIX, CPIXFET)** (Jul Ch.10, Oct Ch.34, Jan Ch.7, Apr) — StatsCan publishes all four; the "range of core measures" is just the min/max envelope.
- **Oil prices: Brent / WTI / WCS** (Jan Ch.8, Apr Ch.9) — NYMEX/ICE futures, Bloomberg, or EIA.
- **Equity indexes** (Jul Ch.26, Oct Ch.17, Jan Ch.9, Apr Ch.13b) — S&P 500, S&P/TSX, EURO STOXX 50, MSCI World, Nikkei. Pure Bloomberg/Yahoo.
- **Government bond yields, 2y and 10y** (Oct Ch.16, Apr Ch.13a) — Bloomberg/Refinitiv.
- **US policy uncertainty indexes** (Jul Ch.21, Oct Ch.26) — Direct download from policyuncertainty.com.
- **Inflation expectations** (Jul Ch.12, Oct Ch.13, Apr Ch.8) — BOS, BLP, CSCE, Consensus Economics. Bank's own surveys are public; Consensus is paywalled but otherwise just data.
- **Comparison of two MPR projections (e.g., "October vs January Report")** (Oct Ch.33, Jan Ch.21, Apr Ch.23) — Just plotting two paths from the published Valet datasets. Trivial *if* you already have the projections (the projections themselves are in Tier 4 — see below).

### Single-report
- **US imports by origin** (Jul Ch.22, Oct Ch.27, Jan Ch.18) — US Census Bureau.
- **US CPI inflation** (Jul Ch.23, Oct Ch.29) — BLS.
- **Global PMI / euro area PMI** (Jul Ch.19, Jan Ch.19) — S&P Global, public release.
- **China's exports by destination** (Jul Ch.24, Oct Ch.31) — China Customs, available via Haver/CEIC.
- **China activity indicators** (Oct Ch.32) — National Bureau of Statistics China.
- **China trade balance / GDP** (Jan Ch.20) — SAFE/NBS.
- **CPI inflation across countries** (Apr Ch.21) — StatsCan, BEA, Eurostat, ONS.
- **Brent spot vs front-month futures spread** (Apr Ch.10) — LSEG; subtraction of two daily series.
- **Natural gas: Henry Hub / TTF / JKM** (Apr Ch.11) — Public futures markets.
- **Non-energy commodity prices** (Oct Ch.15 gold/cattle/lumber/canola; Apr Ch.12 lumber/ag/base metals/gold) — All daily futures or spot prices, just rebased to a common index.
- **Housing starts and resales by region** (Oct Ch.3) — CMHC + CREA.
- **Hiring intentions, BOS** (Jan Ch.4) — Direct from the BOS release.
- **US CPI subcomponents** (Oct Ch.29 goods vs services contributions) — BLS, simple decomposition.
- **US labour market: unemployment + non-farm payrolls** (Apr Ch.22) — BLS.
- **Sectoral exports for tariffed industries** (Apr Ch.26: steel, aluminum, motor vehicles, copper, lumber) — StatsCan trade data, indexed.

---

## Tier 2 — Easy with a small amount of work

Public data, but requires either a simple definitional choice the Bank has made transparently, or basic transformations. A competent analyst could redo these in an afternoon.

- **GDP growth contribution charts** (Jul Ch.1, Oct Ch.1, Jan Ch.12, Apr Ch.1, Apr Ch.15) — StatsCan publishes the expenditure breakdown; just need to chain-volume contributions and annualize. The forecast quarters are Bank projections (Tier 4), but the historical bars are plug-and-play.
- **Goods exports excluding gold** (Oct Ch.4, Jan Ch.2, Apr Ch.2) — StatsCan customs data; you just have to identify and strip out NAICS 21222 / HS 7108 (gold). The "sectors directly affected by tariffs" decomposition (motor vehicles, steel/aluminum, copper, lumber, furniture) requires picking HS codes but the Bank tells you which.
- **Wage growth, multiple measures** (Jul Ch.5, Oct Ch.9) — LFS average wage and SEPH average weekly earnings are direct from StatsCan. Unit labour cost too. *But* the "LFS microdata, quality-adjusted" series requires running the Bank's regression on the LFS public-use microdata file (their Staff Note 2024-23 has the methodology — moderately involved but published).
- **Employment by sector reliance on US exports** (Jul Ch.4, Oct Ch.7, Jan Ch.3) — StatsCan employment by NAICS, then group sectors using the Bank's 35%-of-jobs-rely-on-US-demand cutoff. The cutoff is published; the underlying employment-by-NAICS breakdown is public.
- **"Pace that keeps the employment rate constant"** (Oct Ch.8, Apr Ch.4) — Just population growth × prior month's employment rate. Trivial calculation, but you need the Bank's framing.
- **Share of CPI components above 3% / below 1%** (Jul Ch.11, Oct Ch.12 right axis, Apr Ch.6) — Compute from the 156 CPI subcomponents directly. StatsCan publishes the components and weights.
- **US tariff rate, long historical series** (Jul Ch.20, Oct Ch.25) — US International Trade Commission publishes the historical weighted-average tariff rate (the famous Smoot-Hawley chart). Public.
- **Cumulative change in Canada's exports by destination** (Oct Ch.5, Jan Ch.23) — StatsCan trade by partner country and HS code.
- **Consumer spending per person by category** (Oct Ch.2) — StatsCan quarterly consumption by COICOP, divided by population aged 15+.
- **GDP growth revisions chart** (Jan Ch.22) — Plot the StatsCan vintage from the previous report against the current vintage. Simple if you saved the prior vintage.
- **Share of non-US imports re-routed through the US** (Jan Ch.24) — StatsCan + US Census reconciliation; conceptually simple but requires careful matching of commodity flow data.

---

## Tier 3 — Requires methodology / proprietary methodology, but documented

The Bank has published staff notes explaining how to build these. With effort, an outsider can replicate them. Most of the "heatmap" charts fall here.

- **Labour market heatmap** (Jul Ch.3, Oct Ch.6, Apr Ch.3) — Six labour-market indicators standardized against benchmark ranges using Ens/See/Luu (Staff Analytical Note 2023-07). The methodology is public, but the benchmark midpoints and standard deviations are calculated using a 2003–2019 reference window the Bank specifies. Replicable but tedious.
- **CPI components heatmap** (Jul Ch.7, Oct Ch.11, Jan Ch.6, Apr Ch.7) — Each of ~25 CPI categories standardized by 1996–2019 mean and standard deviation. Mechanical but lots of moving parts; weights need updating each basket vintage.
- **Cost pressures heatmap** (Oct Ch.36) — Same standardization framework applied to import prices, IPPIs, shipping costs, ULC, etc. Many input series, all individually public.
- **Tariff rate calculations** (Jul Ch.13, Oct Ch.18, Jan Ch.10, Apr Ch.14) — The chart shows the weighted-average increase in tariff rates by country. The Bank's October report includes a full "How the average tariff rates are calculated" methodology box. Replicating it requires HS-level trade weights and tariff schedules, plus assumptions about CUSMA compliance and remissions. Doable, but the Bank has a richer dataset than a typical outside analyst.
- **Breadth of inflation regression chart** (Oct Ch.35) — Linear regression of ex-tax CPI inflation on (share above 3% – share below 1%) over 1995–2025. Replicable but you need the full 30-year history of CPI subcomponents.
- **AI-related US investment contribution to GDP** (Jan Ch.17) — Splits computer/peripheral equipment, software IP, R&D and data-centre structures out of NIPA. Definitional; replicable from BEA NIPA tables once you fix the AI definition.
- **Pass-through expectations and price-change expectations from BOS** (Oct Ch.38, Ch.39) — The Bank publishes these BOS results in its quarterly BOS publication. Replicable as long as the question is asked.

---

## Tier 4 — Requires the Bank's in-house models (genuinely hard to replicate)

These are the Bank's outputs — projections, output gaps, scenario impulse responses, decompositions — produced by ToTEM (Terms-of-Trade Economic Model), LENS (Large Empirical and Semi-structural model), MUSE (US satellite model), the BoC-GEM-FIN open-economy DSGE, and various staff models for potential output, neutral rate, and underlying inflation. You can't reproduce these from public data alone.

### Forecast / projection charts
- **GDP growth and level projections** (every report — Jul Ch.14/15/16, Oct Ch.19/20/21/22/23, Jan Ch.11/12/13/14, Apr Ch.15/16/17). Even the historical bars are sometimes the Bank's "estimates" for the just-finished quarter that is not yet in StatsCan data.
- **Non-commodity exports projection** (Jul Ch.16, Oct Ch.21, Jan Ch.13, Apr Ch.16) — Projection comes from ToTEM; the historical part is StatsCan.
- **Consumption growth contribution decomposition (per-person × population)** (Oct Ch.22, Jan Ch.14, Apr Ch.17).
- **Business investment, oil & gas vs non-oil & gas** (Oct Ch.23).
- **CPI inflation projection paths** (every report — Jul Ch.17/18, Oct Ch.24/33, Jan Ch.15/21, Apr Ch.18/23).

### Decompositions (the real model output)
- **CPI inflation contributions: counter-tariffs / costs / output gap / carbon-tax removal / other** (Oct Ch.24 and Ch.37, Jan Ch.16, Apr Ch.19, Apr Ch.20). These slice inflation deviations into structural drivers using Bank model elasticities. Without ToTEM-style decomposition you cannot get this.
- **Tariff impact on CPI level (~0.4%, ~0.8%)** — Quantitative pass-through estimate from the Bank's calibrated trade model.
- **Output gap range (-1.5% to -0.5%)** — Bank's multi-model estimate based on extended multivariate filter, growth-accounting and structural VAR. Mentioned in every report; the underlying potential-output series is published once a year (Staff Analytical Note "Potential output in Canada: 2025/2026 assessment").

### Scenarios
- **July 2025 scenarios — current tariff, de-escalation, escalation** (Jul Ch.27/28/29/30) — Each is a full ToTEM run conditional on a tariff path. Not replicable without the model.
- **April 2026 illustrative scenario with persistent oil at $100** (Apr Ch.24, Ch.25) — Same story. The scenario shows how policy rate, GDP and inflation respond — that's a structural-model exercise.

### Potential output and neutral rate (Appendix in April 2026)
- **Canadian potential output growth** (Apr Ch.A-1) — Bank's potential output assessment; published once a year. Decomposes into trend labour input and trend labour productivity using Bank-internal smoothers.
- **Global potential output growth** (Apr Ch.A-2) — Same, applied to US, euro area, China.
- **Neutral rate range (2.25%–3.25%)** — Bank's annual neutral-rate update. Combines four or five different models (term-structure, semi-structural, OLG-calibrated). Genuinely hard to reproduce.

---

## Practical takeaway

If you're trying to track the Bank in real time:

- **About 60% of the charts** (Tiers 1 and 2) you can rebuild from Statistics Canada, BLS, US Census, Bloomberg/LSEG, and a few public commodity feeds. These are mostly the "current conditions" charts: realised CPI, GDP back-data, exports, financial markets, oil, employment.
- **About 20–25%** (Tier 3) require a published Bank methodology — labour-market heatmap, CPI heatmap, tariff weighting. Doable but requires reading the staff notes and being patient with data plumbing.
- **The remaining 15–20%** (Tier 4) are the actual point of the MPR: forecast paths, output-gap estimates, inflation decompositions, scenario impulse responses, and the annual potential-output / neutral-rate updates. These are genuinely produced by the Bank's models and can't be redone from outside.

The Bank's *Valet API* publishes the time series for every chart at the report's release (`MPR_YYYYMMDD` group), so you can extract the projection numbers themselves even though you can't reproduce the model that generated them.

---

## Source URLs

- Landing page: https://www.bankofcanada.ca/publications/mpr/
- April 2026 MPR PDF: https://static.bankofcanada.ca/uploads/pdf/mpr-2026-04-29.pdf
- January 2026 MPR PDF: https://www.bankofcanada.ca/wp-content/uploads/2026/01/mpr-2026-01-28.pdf
- October 2025 MPR PDF: https://www.bankofcanada.ca/wp-content/uploads/2025/10/mpr-2025-10-29.pdf
- July 2025 MPR PDF: https://www.bankofcanada.ca/wp-content/uploads/2025/07/mpr-2025-07-30.pdf
- Valet API docs: https://www.bankofcanada.ca/valet/docs
