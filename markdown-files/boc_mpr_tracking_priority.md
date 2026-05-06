# BoC MPR Charts — Ranked by Usefulness for Between-MPR Tracking

**Purpose:** Of the ~50 charts in Tiers 1–3 (the replicable ones from the previous note), which are worth actually maintaining as a real-time tracker, and which are essentially context that you only refresh when the next MPR drops?

I've graded each on a 4-tier scale based on:
1. **How often it changes meaningfully** (data release frequency × actual signal)
2. **Whether the BoC explicitly cites it in the MPR or in deliberations**
3. **Whether it's a leading or coincident indicator of the variables that drive policy**
4. **Whether the underlying message moves between reports or just gets re-noted**

| Symbol | Tier | What it means |
|---|---|---|
| 🟢 | **A — Essential** | Maintain on a live dashboard; refresh on every release |
| 🟡 | **B — Useful** | Worth checking monthly or after major news; provides context |
| 🔴 | **C — Low priority** | Useful occasionally (regime shifts, one-off shocks); not for routine tracking |
| ⚫ | **D — Archival** | Mostly historical or conceptual; refresh when the next MPR drops |

---

## A — Essential (must-track dashboard)

These are the charts where the BoC's decision-making is most visible, and where new data points should change your prior between meetings.

| Chart | Frequency | Why it's essential |
|---|---|---|
| **Headline CPI + CPI ex-indirect-taxes** (T1) | Monthly | The target variable. Single most important release. |
| **Core inflation: CPI-trim, CPI-median, CPIX, CPIXFET** (T1) | Monthly | The Bank's *preferred* measures are CPI-trim and CPI-median. Their move from ~3% in mid-2025 to ~2.5% by Dec 2025 is the central inflation story. |
| **Share of CPI components above 3% / below 1%** (T2) | Monthly | The Bank's preferred breadth measure — explicitly part of the "underlying inflation" framework (Oct 2025 In Focus). Tracks dispersion when averages mislead. |
| **Inflation expectations: BOS, BLP, CSCE, Consensus** (T1) | Mixed (BLP monthly, BOS/CSCE quarterly) | The Bank cites these directly in every Council deliberation. Short-term expectations are especially watched right now because of tariff pass-through and the Middle East oil shock. |
| **Oil prices: Brent / WTI / WCS** (T1) | Daily | Direct input to the inflation forecast. The April 2026 MPR is essentially built around the oil-price assumption ($90 → $75 by mid-2027). WCS matters separately for terms of trade. |
| **2-year government bond yields (Canada vs US)** (T1) | Daily | Markets' read on the policy path. The 2-year is the cleanest summary of "what does the curve think about the next year of BoC decisions." |
| **GDP growth contributions, quarterly** (T2) | Quarterly | Tells you whether headline growth is driven by exports, consumption, government, or inventories. The Bank's narrative hinges on this decomposition every report. |
| **Wage growth (LFS average, SEPH, BLP/BOS)** (T2) | Monthly | Cited every MPR. The "convergence below 3%" is the explicit signal the Bank looks for to judge underlying inflation. |
| **Employment by sector reliance on US exports** (T2) | Monthly | The cleanest read on tariff transmission to jobs. Sectors with ≥35% US-export reliance are explicitly broken out. |
| **Goods exports excluding gold** (T2) | Monthly | The Bank shows this every report because gold flows distort the trade story. The post-tariff path is the central tradable story. |
| **Hiring intentions, BOS** (T1) | Quarterly | The BoC's own survey. Gets cited in opening statements. Quarterly drop is a near-MPR-level event. |
| **Pass-through and price-change expectations, BOS** (T3) | Quarterly | Directly informs the Bank's tariff cost-pass-through assumption. Watch shifts in the share of firms saying "fully passing through" vs "absorbing." |
| **Tariff rate calculations** (T3) | Updated as US trade actions occur | Maintain this yourself between reports — it's the cleanest summary of the actual trade environment. The Bank publishes its calculation method in Oct 2025; outside analysts can replicate. |

That's 13 charts. They form a tight monitoring set: most are public, several have free APIs, and they cover the four things the Bank cares about — inflation level, inflation breadth, labour slack, and trade transmission.

---

## B — Useful (refresh monthly or on news)

Worth checking, but they're context rather than direct policy signals. Most are public, monthly, and inform interpretation.

| Chart | Frequency | Comment |
|---|---|---|
| **CPI components heatmap** (T3) | Monthly | A dense way to see which of the 25 main categories are running hot vs cool relative to history. Useful as a "what's actually moving" diagnostic, but each cell is just a CPI subcomponent — you can read it from the StatsCan release. |
| **Labour market heatmap** (T3) | Monthly | Aggregates six labour indicators (unemployment rate, vacancy/unemployment, separations, finding rate, employment ratio, hours). Methodology is published. Each cell can be looked at individually too. |
| **Cost pressures heatmap** (T3) | Monthly–quarterly | Combines import prices, IPPIs, shipping, ULC, business services. Tells you if cost pressures are easing or rebuilding. The Bank's narrative on whether tariff costs will pass through depends on this. |
| **Sectoral exports for tariffed industries** (T1) | Monthly | The April 2026 "one year later" treatment of steel, aluminum, copper, lumber, motor vehicles is exactly the right granularity. Useful for understanding which sectors are absorbing vs passing-through tariff costs. |
| **Equity indexes** (T1) | Daily | Financial-conditions indicator. High value in stress (e.g., April 2025 and the April 2026 oil shock) but background noise in calm periods. |
| **Pace that keeps the employment rate constant** (T2) | Monthly | A handy framing once you've already looked at the LFS print. The 5,000-jobs/month figure for end-2025 is a useful baseline. |
| **Non-energy commodity prices (BCNEx)** (T1) | Daily | Cleaner read on terms of trade than gold-and-oil-only narratives. Rises in metals tell you something about global demand; gold tells you something about geopolitical risk. |
| **Housing starts and resales by region** (T1) | Monthly | The shelter-inflation transmission depends on this, but its relevance is fading as rent inflation moderates. |
| **Consumer spending per person by category** (T2) | Quarterly | Drops with the GDP release. Useful for separating headline consumption growth from population growth — important right now because population growth has slowed sharply. |
| **US labour market: unemployment + non-farm payrolls** (T1) | Monthly | Affects the "US demand for Canadian exports" assumption. Watch when payrolls deviate substantially from trend. |
| **US imports by origin** (T1) | Monthly | The trade-reconfiguration story. Slow-moving but central. |
| **Global PMI / euro area PMI** (T1) | Monthly | Leading indicator of external demand. A composite read across services and manufacturing, especially useful for the China and euro area outlooks. |
| **Cumulative change in Canada's exports by destination** (T2) | Monthly | The diversification story. The "$10bn into rest-of-world to offset $30bn lost to US" framing in Oct 2025 is the key one. |
| **Share of non-US imports re-routed through US** (T2) | Monthly | Tracks whether the US is being bypassed in supply chains. Slow-moving but informative for cost story. |
| **Brent spot vs front-month futures spread** (T1) | Daily | Only matters when there's stress. Right now (April 2026 oil shock) it's a key signal of physical-market dislocation. Park it; check it when oil moves. |
| **US policy uncertainty indexes** (T1) | Daily | The Bank cites this. But it's noisy and high-frequency news-based. Low signal-to-noise except at regime shifts (e.g., April 2025 spike). |

---

## C — Low priority (occasional reference)

Useful for one-off questions or regime-shift moments, but not for routine tracking. The signal moves slowly relative to the noise of refreshing them.

| Chart | Why low-priority |
|---|---|
| **CPI inflation across countries** (T1) | Cross-country comparison. Cute but the BoC sets policy on Canadian CPI, not the spread to other G7. |
| **US CPI subcomponents (goods vs services)** (T1) | Useful one-off for the tariff pass-through story; not for tracking. |
| **China's exports by destination** (T1) | The redirection-from-US story moves slowly; quarterly check is plenty. |
| **China activity indicators (industrial production, retail, FAI, home sales)** (T1) | Broad context for global demand; rarely policy-moving for the BoC directly. |
| **Natural gas: Henry Hub / TTF / JKM** (T1) | Niche; matters for Canadian fuel costs only indirectly. Useful only when there's a regional gas dislocation (April 2026). |
| **Breadth of inflation regression scatter** (T3) | Conceptual one-off; the message ("inflation around 2½% given current breadth") is in the breadth chart already. |
| **AI-related US investment contribution to GDP** (T3) | Thematic; affects the US potential-output story but doesn't move quarter to quarter. |
| **Comparison of two MPR projections** | Useful only when a new MPR drops; nothing to track between reports. |

---

## D — Archival (refresh when the next MPR drops)

Conceptual or historical; the underlying data doesn't really evolve in a way that helps you anticipate the BoC.

| Chart | Why archival |
|---|---|
| **US tariff rate, long historical series (Smoot-Hawley)** (T1) | The historical context; updates only when the BoC re-shows it. |
| **GDP growth revisions chart** (T2) | Only matters at StatsCan benchmark-revision moments (annual). |
| **China trade balance share of GDP** (T1) | Slow-moving structural indicator. |

---

## Suggested between-MPR dashboard

If I were building a single dashboard to track what the BoC is going to do between meetings, I would have:

**Daily updates** (financial conditions and oil):
1. Brent / WTI / WCS oil prices, with the futures curve
2. 2-year Canada and US bond yields
3. CAD/USD
4. S&P/TSX, S&P 500 (background)

**On each StatsCan CPI release** (mid-month):
5. Headline CPI + CPI ex-indirect-taxes vs target
6. CPI-trim and CPI-median (year-over-year, and 3-month annualized)
7. CPIX and CPIXFET
8. Share of CPI components above 3% / below 1%
9. CPI components heatmap (or a stripped-down "what's hot vs cool" version)

**On each Labour Force Survey release** (first Friday of the month):
10. Unemployment rate, employment growth (3-month moving average)
11. Employment in US-export-reliant sectors vs the rest
12. Wage growth (LFS average, microdata if you've built that)
13. Job vacancies and the vacancy-to-unemployment ratio

**On each StatsCan trade release** (early in the month):
14. Goods exports excluding gold, by tariffed-vs-non-tariffed sector
15. Imports by origin (US share of imports)

**On each StatsCan GDP release** (monthly + quarterly):
16. Quarterly GDP growth contributions
17. Consumer spending per person

**Each BOS / CSCE / BLP release**:
18. Inflation expectations across all four sources
19. Hiring intentions
20. BOS pass-through expectations and price-change expectations

**Maintained manually as US trade actions occur**:
21. Average tariff rate (US-on-Canada, Canada-on-US, US-on-world) — using the Bank's published methodology

That's 21 chart-equivalents, almost all of which are derivable from public Canadian and US statistical agencies plus a couple of free APIs.

---

## What to drop if you want a slimmer version

If 21 is too many and you want a 10-chart core dashboard:

1. CPI ex-indirect-taxes vs target
2. CPI-trim and CPI-median
3. Share of CPI components above 3%
4. Inflation expectations (BOS + BLP combined)
5. Unemployment rate + wage growth
6. Employment in US-trade-reliant sectors
7. Goods exports excluding gold
8. Quarterly GDP growth contributions
9. 2-year bond yield (Canada)
10. Brent oil + WCS

That's enough to know whether your priors about the next MPR need updating.

---

## What the Bank watches that *isn't* in this list

A few things worth flagging that the BoC clearly tracks but that aren't really in any single chart in the MPRs:

- **Mortgage renewal flows.** Mentioned periodically in opening statements. There's no chart, but the BoC pays attention to the wall of fixed-rate renewals coming through 2025–27.
- **Bank lending standards (Senior Loan Officer Survey).** Quarterly Bank publication separate from the MPR.
- **Financial Stability Report indicators.** Annual, but the underlying credit and household-vulnerability data is monitored continuously.
- **Population growth / immigration.** The Bank's outlook hinges heavily on this assumption, but they cite it as a number, not a chart. Watch IRCC permit data and Statistics Canada population estimates.
- **CUSMA negotiation news.** Treated as a discrete risk; no chart, but the most important non-data input to the next year of policy.
