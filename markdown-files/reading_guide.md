# Dashboard reading guide

A short orientation for what the Bank of Canada Tracker shows and what each section answers. For the analytical conventions and writing rules behind generated section blurbs, see `analysis_framework.md`. For chart formatting decisions, see `chart_style_guide.md`.

---

## Monetary Policy

Three charts — Policy Rates, 2-Year Yields, and BoC Balance Sheet — answering *"what is the BoC doing across both of its policy tools, and where does the market think they're going?"*

- **Where the BoC sits in the rate cycle.** Policy Rates chart shows the BoC overnight rate against a shaded 2.25–3.25% neutral-rate band (BoC's official range from their annual r* update). Above the band = restrictive policy, actively slowing the economy. Inside = roughly neutral. Below = accommodative.
- **How the BoC compares to the Fed.** Policy Rates chart's two lines plus a toggleable **BoC − Fed spread**. Negative = BoC below Fed (CAD-negative via interest rate parity); ±100bp is historically unusual.
- **What the market expects from the BoC.** 2-Year Yields chart's toggleable **Canada 2Y − Overnight** spread. Negative = market pricing net cuts over 2 years; positive = pricing hold or hikes. The 2Y embeds term premium, so magnitudes are directional rather than precise forecasts.
- **Cross-country yield differential.** 2-Year Yields chart's toggleable **Canada 2Y − US 2Y** spread. Negative = Canadian rates expected lower than US (CAD-negative). Should track roughly with the BoC − Fed policy spread; divergence implies the market is pricing a future change in the relative-policy stance.
- **Balance sheet — QE or QT, and at what pace.** BoC Balance Sheet chart shows total assets (headline) and GoC bond holdings (the active QE/QT instrument) by default, with settlement balances available as a toggle. Pre-COVID baseline of total assets was ~$120B; QE peak was ~$575B (April 2022). Passive QT has been running since then. When total assets and GoC bonds move together, the change is pure QE/QT; when they diverge, non-policy operations (FX, term repos, emergency facilities) are happening. Settlement balances anchor the floor-system operating regime (declared permanent in 2025).

Not yet on the dashboard: market-implied rate path from OIS or event contracts (next priority — the 2Y proxy is rough), longer-tenor yield curve (2Y vs 10Y), inflation expectations, real rates, CORRA tracking target.

---

## Inflation

Three charts — Core Inflation, CPI Components, CPI Breadth — answering *"is inflation at the BoC's 2% target, and what's the underlying trend?"*

- **Core measures vs target.** Core Inflation chart shows the band of five core measures (trim, median, common, CPIX, CPIXFET) plus headline CPI Y/Y. A 2% line marks target.
- **What's driving headline.** CPI Components chart shows headline plus food, energy, goods, services breakdowns at the same Y/Y view. Food and energy on by default — those are the volatile components most likely to explain short-term headline movements.
- **How broad the price pressure is.** CPI Breadth chart shows the share of basket components running well above 3% and well below 1% Y/Y, expressed as deviation from the 1996–2019 historical average.

This section has a generated blurb above it that synthesizes these three reads into a takeaway.

---

## Labour Market

Two charts — Unemployment Rate and Wage Growth — answering *"is the labour market tight or loose, and is wage pressure consistent with target inflation?"*

- **Tightness.** Unemployment Rate chart, monthly, seasonally adjusted. NAIRU is commonly cited at ~5–5.5% for Canada (not yet drawn on the chart pending verification).
- **Wage pressure.** Wage Growth chart with four wage measures (LFS all employees, LFS permanent, SEPH weekly earnings, BoC's LFS-Micro composition-adjusted) plus a Services CPI overlay. The wage-vs-services-CPI relationship is the key wage-price-spiral read.

Not yet on the dashboard: hours worked, participation rate, sectoral breakdown, regional labour markets.

---

## Financial Conditions

Two charts — Oil Prices and USD/CAD — answering *"how are commodity prices and the exchange rate affecting Canada?"*

- **Oil.** WTI, Brent, and WCS lines (USD per barrel). 20-day smooth toggle for trend through daily noise. WCS is monthly so doesn't smooth further.
- **CAD.** USD/CAD level (CAD per USD; higher = weaker CAD).

Future additions: equities (TSX, S&P 500), credit spreads, broader market conditions. Section is named "Financial Conditions" rather than the narrower "Commodities and FX" so it can absorb these as they're added.

---

## What the dashboard doesn't try to do

- Forecast where rates, inflation, or any series will go
- Make policy recommendations
- Replace economist commentary or BoC publications

Section blurbs (currently only on Inflation) are AI-generated from the latest data using the rules in `analysis_framework.md`. They describe what the data says, not where it's headed. As the framework is verified for the other three sections, blurbs for Monetary Policy, Labour Market, and Financial Conditions will be added.
