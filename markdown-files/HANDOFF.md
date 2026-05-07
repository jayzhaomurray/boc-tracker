# BoC Tracker — Project Handoff

This document captures the full state of the project, every architectural decision, and the next steps. Written so a fresh session can continue without any prior context.

---

## What this project is

A personal data dashboard that tracks the economic indicators the Bank of Canada watches between its quarterly Monetary Policy Reports (MPRs). The output is a single interactive HTML file hosted publicly on GitHub Pages.

**Live URL:** https://jayzhaomurray.github.io/boc-tracker/  
**GitHub repo:** https://github.com/jayzhaomurray/boc-tracker  
**Owner GitHub handle:** jayzhaomurray (display name on the page — real name not confirmed)

**Tech stack:** Python → Plotly → static HTML → GitHub Pages  
**Data sources:** Statistics Canada WDS API, Bank of Canada Valet API (primary); EIA, FRED, BLS planned for future charts

---

## File structure

```
boc-tracker/
├── fetch.py              ← pulls data from APIs, saves CSVs to data/
├── build.py              ← reads CSVs, builds index.html
├── requirements.txt      ← requests, pandas, plotly
├── .gitignore            ← __pycache__/, *.pyc
├── index.html            ← generated output; do not edit by hand
├── data/
│   ├── cpi_all_items.csv
│   ├── unemployment_rate.csv
│   ├── yield_2yr.csv
│   ├── cpi_trim.csv
│   ├── cpi_median.csv
│   ├── cpi_common.csv
│   ├── cpix.csv
│   ├── cpixfet.csv
│   ├── cpi_components.csv       ← wide CSV: 500 months × 59 depth-3 CPI components
│   └── cpi_breadth_mapping.json ← component metadata: vector IDs, basket weights, names
└── markdown-files/       ← reference docs and this handoff
    ├── HANDOFF.md
    ├── boc_mpr_charts_inventory.md
    ├── boc_mpr_tracking_priority.md
    └── boc_mpr_data_methodology.md
```

The `markdown-files/` folder contains three reference documents prepared before the build started, plus this handoff:
- **charts_inventory**: Full inventory of ~120 charts from the past 4 MPRs, tiered by replicability (Tier 1–4)
- **tracking_priority**: A/B/C/D priority ranking for between-MPR tracking; includes a 10-chart slim list and a 21-chart full list
- **data_methodology**: Per-chart data source, methodology difficulty (1–5), and API accessibility

These are the planning documents. Consult them when deciding what to add next.

---

## How to run

```bash
# Step 1: download fresh data from APIs (run when you want to update data)
python fetch.py

# Step 2: regenerate the dashboard from saved CSVs (run when you change the code)
python build.py

# Step 3: view locally
start index.html          # Windows
open index.html           # Mac
```

You can run `build.py` repeatedly without hitting any APIs. Only `fetch.py` makes network calls.

---

## Data APIs

### Statistics Canada WDS

**Endpoint:** `POST https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods`  
**Body:** `[{"vectorId": <int>, "latestN": <int>}]`  
**Content-Type:** `application/json`

Response structure:
```json
[{
  "status": "SUCCESS",
  "object": {
    "vectorId": 41690914,
    "productId": 18100006,
    "vectorDataPoint": [
      {"refPer": "2026-03-01", "value": 167.3, ...}
    ]
  }
}]
```

Note: the response is a JSON **array** (matching the input array). Even for one vector, `r.json()` returns a list, so access via `payload[0]`.

To find a vector ID: navigate to a table at www150.statcan.gc.ca, click a specific data series, and look for "Vector" (format: V followed by digits).

### Bank of Canada Valet API

**Endpoint:** `GET https://www.bankofcanada.ca/valet/observations/{series_key}/json`  
**Query params:** `start_date=YYYY-MM-DD`

Browse all series keys at: https://www.bankofcanada.ca/valet/lists/series/json  
API docs: https://www.bankofcanada.ca/valet/docs

Response structure:
```json
{
  "observations": [
    {"d": "2026-05-05", "BD.CDN.2YR.DQ.YLD": {"v": "3.01"}}
  ]
}
```

---

## Current series

Defined in `fetch.py` under `STATSCAN_SERIES` and `BOC_VALET_SERIES`:

| CSV filename | Source | Identifier | Description |
|---|---|---|---|
| `cpi_all_items` | StatsCan | Vector 41690914 | All-items CPI, Canada, not SA (Table 18-10-0006-01) |
| `unemployment_rate` | StatsCan | Vector 2062815 | Unemployment rate, Canada, SA (Table 14-10-0287-01) |
| `yield_2yr` | BoC Valet | `BD.CDN.2YR.DQ.YLD` | 2-yr GoC benchmark bond yield, daily |
| `cpi_trim` | BoC Valet | `CPI_TRIM` | CPI-trim, Y/Y %, monthly |
| `cpi_median` | BoC Valet | `CPI_MEDIAN` | CPI-median, Y/Y %, monthly |
| `cpi_common` | BoC Valet | `CPI_COMMON` | CPI-common, Y/Y %, monthly |
| `cpix` | BoC Valet | `ATOM_V41693242` | CPIX (excl. 8 volatile), Y/Y %, monthly |
| `cpixfet` | BoC Valet | `STATIC_CPIXFET` | CPIXFET (excl. food & energy), Y/Y %, monthly |
| `cpi_components` | StatsCan | 59 vectors (see mapping JSON) | Wide CSV: one column per CPI component, 500 months |

To add a new StatsCan series: add an entry to `STATSCAN_SERIES` in `fetch.py`, run `fetch.py`, then add a `ChartSpec` in `build.py`.

To add a new Valet series: add an entry to `BOC_VALET_SERIES` in `fetch.py` with `(series_key, start_date)`, same process.

---

## Architecture: ChartSpec and PageSpec

All chart and page configuration lives in the `PAGES` list at the bottom of `build.py`. Nothing else needs to change when adding charts or pages.

### ChartSpec

```python
@dataclass
class ChartSpec:
    series: str               # key into data dict; must match CSV filename without .csv
    title: str                # panel heading displayed in the dashboard
    frequency: str            # "daily" | "weekly" | "monthly" | "quarterly" | "annual" | "irregular"
    color: str                # hex color for the line
    static: bool = False      # if True, no transform buttons shown regardless of frequency
    default_transform: str = "level"  # which transform the chart opens on
```

`static=True` is for derived or calculated charts (e.g., a heatmap, a breadth measure) where the transformation toggles don't make sense. The `frequency` field still needs to be set correctly for these charts.

`default_transform` must be a valid key for the given `frequency` (see table below). If it's invalid, `build.py` prints a warning and falls back to `"level"`.

### CoreInflationSpec

A one-off composite chart for the core inflation panel. No configurable fields beyond `title`. Hardcoded to load `cpi_all_items`, `cpi_trim`, `cpi_median`, `cpi_common`, `cpix`, `cpixfet`. Displays headline CPI Y/Y as a blue line, a shaded band showing the min–max range of the five core measures, and toggle-able individual lines for trim and median. Add a `CoreInflationSpec` to any page's `charts` list to include it.

### CpiBreadthSpec

A one-off composite chart for the CPI breadth panel. No configurable fields beyond `title`. Implemented in `_build_cpi_breadth_panel()`.

**Methodology:**
- Source data: `data/cpi_components.csv` — a wide CSV with 500 months × 59 columns (one per component), fetched via `fetch_cpi_components()` in `fetch.py`
- Component selection: 59 of 60 depth-3 components from StatsCan Table 18-10-0004 (Canada geography, not SA). The 60th — "Other tobacco products and smokers' supplies" — is excluded because it only has data from 2013, breaking the pre-1995 history requirement.
- Basket weights: 2024-vintage from StatsCan Table 18-10-0007, "Weight at basket link month prices", "Distribution to selected geographies", Canada. Stored in `data/cpi_breadth_mapping.json` alongside vector IDs.
- Weight normalisation: weights from the mapping sum to ~96% (after dropping tobacco and the ~1% depth-3 coverage gap). They are re-normalised to 1.0 inside `_build_cpi_breadth_panel()` before use, so the breadth percentages represent "share of the tracked basket," not the full CPI.
- Computation: for each month, compute Y/Y for each component, then sum the (normalised) weights of components where Y/Y > 3% → `above_3_raw`; same for Y/Y < 1% → `below_1_raw`.
- Late-starter filter: components whose first valid date is after 1995-01-01 are dropped at build time (not at fetch time). Currently only the tobacco component hits this filter. The dropped weight is absorbed by re-normalisation.
- Historical average: mean of `above_3_raw` and `below_1_raw` over 1996–2019 (BoC inflation-targeting era, pre-COVID, matching the display start date).
- Display: deviation from that average, shown from 1996 onward. Two lines: above-3% in red (#e74c3c), below-1% in blue (#2980b9). Y-axis in percentage points (pp). A zero reference line marks the historical average.
- Validation: the 2022 peak deviation (+46 pp above 3%) aligns within 1 pp of the BoC's published version of this chart (from speech SPEECH_MEND20251002, Oct 2025).

**Mapping file (`data/cpi_breadth_mapping.json`):** a JSON array of 60 objects (including the excluded tobacco one). Each has:
- `cpi_pid` — product member ID in Table 18-10-0004
- `wt_pid` — product member ID in Table 18-10-0007
- `name` — component name (also the column header in `cpi_components.csv`)
- `cpi_vector` — StatsCan vector ID used to fetch the CPI series
- `wt_value` — basket weight (percentage points, raw from the API, sum ~99%)
- `wt_refPer` — reference period for the weight (2024-01-01 = latest vintage)

**To regenerate the mapping** (e.g., after a new basket revision): the mapping was built by probing Tables 18-10-0004 and 18-10-0007 via the StatsCan WDS `getCubeMetadata` and `getDataFromCubePidCoordAndLatestNPeriods` endpoints. The full probe logic is not in the repo — refer to the session that built it (2026-05-06). Key parameters: depth-3 in the product hierarchy, Canada geography, established series only (no post-2020 base-year markers, no terminated flag).

### PageSpec

```python
@dataclass
class PageSpec:
    title: str          # H1 heading on the page
    tagline: str        # subtitle line below the heading
    output_file: str    # filename to write (e.g., "index.html", "labour.html")
    charts: list[ChartSpec]
```

### Current PAGES definition

```python
PAGES = [
    PageSpec(
        title="Bank of Canada Tracker",
        tagline="Tracking the indicators behind Bank of Canada policy decisions",
        output_file="index.html",
        charts=[
            CoreInflationSpec(
                title="Core Inflation Measures — Canada (Year-over-year %)",
            ),
            CpiBreadthSpec(
                title="CPI Breadth — Deviation from 1996–2019 Average: Share of Basket Above 3% or Below 1% (pp)",
            ),
            ChartSpec(
                series="cpi_all_items",
                title="Consumer Price Index — All Items, Canada (2002=100)",
                frequency="monthly",
                color="#1f6aa5",
                default_transform="yoy",
            ),
            ChartSpec(
                series="unemployment_rate",
                title="Unemployment Rate — Canada, Seasonally Adjusted (%)",
                frequency="monthly",
                color="#c0392b",
                static=True,
            ),
            ChartSpec(
                series="yield_2yr",
                title="2-Year Government of Canada Benchmark Bond Yield (%)",
                frequency="daily",
                color="#27ae60",
            ),
        ],
    ),
]
```

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
| `ar_3m` | `((v / v.shift(3)) ** 4 - 1) * 100` — 3-month change annualized |
| `qoq` | `v.pct_change(1) * 100` |
| `qoq_ar` | `((v / v.shift(1)) ** 4 - 1) * 100` — quarterly annualized |
| `yoy` | `v.pct_change(N) * 100` where N = 12 (monthly), 52 (weekly), 4 (quarterly), 1 (annual) |

### How toggles are implemented

All transforms are computed at build time and embedded in the HTML as separate Plotly traces. Only the default transform is initially visible. Toggle buttons use Plotly's `restyle` method targeting specific trace indices — this means clicking a button on one chart does not affect other charts.

Each chart with `static=False` and more than one available transform gets its own `updatemenus` button group, positioned at the top of its subplot panel using paper coordinates derived from `fig.layout[yaxis_key].domain`.

This was a deliberate decision: **no live calculation at click time**. All data is pre-baked into the HTML. The file is heavier but completely self-contained once loaded.

### Decisions that were considered and rejected

- **Type-based transforms** (level/rate/financial types with different transform sets): rejected in favour of frequency-based transforms. Simpler, more predictable, no exceptions to remember.
- **`mom_ar` (month-over-month annualized)**: removed. Monthly transforms are `level`, `mom`, `ar_3m`, `yoy` only.

---

## Architecture: multi-page design

The infrastructure for multiple pages is already in place. `main()` in `build.py` iterates over `PAGES` and calls `build_page()` for each. `build_page()` is fully self-contained.

To add a second page (e.g., a labour market page at `labour.html`):
1. Add a `PageSpec` to `PAGES` with `output_file="labour.html"` and its own `charts` list
2. Run `python build.py`

No other code changes needed. Navigation between pages (a header nav bar) has not been built yet — pages would currently be standalone files with no links between them.

---

## Architecture: HTML generation

`build.py` uses Plotly's `fig.write_html()` with `include_plotlyjs="cdn"` to produce the base HTML, then post-processes it with string replacement to inject:
- Custom CSS (centered layout, font stack, header and about-section styles)
- A `.site-header` div above the chart (title, tagline, last-updated timestamp)
- A `.about` div below the chart (attribution, links to GitHub and data sources)

The three replacement anchors are `</head>`, `<body>`, and `</body>`. Plotly's output always contains these as bare tags so the replacements are reliable.

Using `include_plotlyjs="cdn"` keeps the HTML file small (~50KB vs ~3MB with embedded JS). The page requires an internet connection to load Plotly, which is acceptable since it's hosted on GitHub Pages.

---

## What has been implemented

- [x] `fetch.py` — fetches StatsCan and BoC Valet series, saves to CSV
- [x] `build.py` — config-driven, reads CSVs, builds HTML with toggles
- [x] Full transformation system for all frequencies
- [x] Pre-computed toggle buttons; independent per chart
- [x] ChartSpec / PageSpec config structure
- [x] Multi-page infrastructure (PAGES list, build_page loop)
- [x] Custom page header, tagline, last-updated timestamp, About section
- [x] GitHub repo and GitHub Pages deployment
- [x] **Core inflation panel** (`CoreInflationSpec`) — headline CPI Y/Y + shaded range of 5 core measures + toggle-able trim/median lines
- [x] **CPI breadth chart** (`CpiBreadthSpec`) — weighted share of 59 depth-3 components above 3% / below 1%, expressed as deviation from 1996–2019 average. Calibrated against BoC published chart (within 1 pp at 2022 peak).
- [x] **2-year yield** (BoC Valet)
- [x] **Unemployment rate** (StatsCan, static display)
- [x] **All-items CPI** (opens on Y/Y)

## What has NOT been implemented

- [ ] **GitHub Actions workflow** — daily automated refresh. The file `.github/workflows/update.yml` does not exist yet. Data must be refreshed manually by running `fetch.py` and `build.py` and pushing.
- [ ] **More charts** — the dashboard has 5 charts. The A-tier priority list has 13. See expansion roadmap below.
- [ ] **Multiple pages** — the PAGES list has one entry. Infrastructure is ready.
- [ ] **Navigation bar** — if multiple pages are added, there's no nav between them yet.
- [ ] **Custom domain** — planned for later; GitHub Pages URL is currently the public URL.
- [ ] **`hover_format` field on ChartSpec** — intentionally deferred. The current hover template is inferred from transform and frequency. If a specific chart looks wrong, add `hover_format: str = ""` to ChartSpec and pass it through `_hover_template()`.
- [ ] **Reference lines** — the 2% BoC inflation target line was in an early prototype but not carried forward. Easy to add: `fig.add_hline(y=2, ...)` inside `_build_chart_fig()`.

---

## Next steps, in priority order

### 1. Set up GitHub Actions for daily refresh

Create `.github/workflows/update.yml`:

```yaml
name: Update dashboard

on:
  schedule:
    - cron: "0 12 * * *"   # daily at 12:00 UTC
  workflow_dispatch:         # also allows manual trigger from GitHub UI

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python fetch.py
      - run: python build.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Auto-update: refresh data and rebuild dashboard"
```

This runs `fetch.py` and `build.py` on a schedule and auto-commits the updated CSVs and `index.html`. GitHub Pages then serves the new file automatically.

### 4. Add charts — in recommended build order

See the full expansion roadmap section below for the complete chart list. The recommended order:

**Step A — StatsCan CPI fetch (already done for headline; extend it)**

Everything in the inflation theme comes from the same StatsCan Table 18-10-0006-01. Adding the four core measures (CPI-trim, CPI-median, CPIX, CPIXFET) and the share-of-components-above-3% chart are all unlocked once you have that fetch wired up.

**Step B — BoC Valet additions**

CPI-trim and CPI-median are actually published directly by the BoC on Valet — no calculation needed. Look them up at https://www.bankofcanada.ca/valet/lists/series/json (search "trim" and "median"). The overnight policy rate and BCNEx (non-energy commodity index) are also on Valet.

**Step C — StatsCan Labour Force Survey**

Table 14-10-0064 (wage growth) and Table 14-10-0023 (employment by industry) come from the LFS. The pace-to-keep-employment-rate-constant is a calculation on top of LFS data.

**Step D — EIA and FRED**

Oil prices (Brent, WTI) via the EIA API require a free API key from eia.gov. US unemployment and payrolls via FRED also require a free key from fred.stlouisfed.org. Both take 10 minutes to register.

**Step E — BoC survey publications (BOS, BLP, CSCE)**

No REST API. The BoC publishes results as PDFs with companion CSV files at predictable URL patterns on bankofcanada.ca. Quarterly for BOS and CSCE; monthly for BLP.

**Step F — StatsCan trade data by HS code**

Table 12-10-0011 for goods exports. Stripping HS 7108 (gold) gives exports ex-gold. Grouping by HS codes for steel, aluminum, copper, lumber, motor vehicles gives sectoral exports.

### 5. Multi-page split (when chart count warrants it)

Planned theme split:
- `index.html` — inflation (CPI, core measures, breadth, expectations)
- `labour.html` — labour market (unemployment, wages, employment by sector)
- `trade.html` — trade (exports ex-gold, tariff rate, imports)
- `financial.html` — financial conditions (yields, oil, equities)

When ready: add three more `PageSpec` entries to `PAGES` in `build.py`, distribute `ChartSpec`s accordingly, and build a simple HTML nav bar (four links across the top of each page).

---

## Full expansion roadmap

Drawn from `boc_mpr_tracking_priority.md` and `boc_mpr_data_methodology.md`. Charts are listed in A-tier (essential) and B-tier (useful) order. Difficulty is 1–5 (1 = plot a published series; 5 = proprietary model). Data access is: Free API / Free release / Free with effort / Paid.

### A-tier: must-track (13 charts)

| Chart | Theme | Difficulty | Data access | Source | Notes |
|---|---|---|---|---|---|
| Headline CPI + CPI ex-indirect-taxes | Inflation | 1 | Free API | StatsCan WDS Table 18-10-0004; BoC Valet | Both series are pre-published. Headline CPI is already in the dashboard. |
| Core inflation: CPI-trim, CPI-median, CPIX, CPIXFET | Inflation | 1 | Free API | BoC Valet (trim, median); StatsCan (CPIX, CPIXFET) | All four are computed and published. BoC Valet series keys: search "trim" and "median" at the Valet series list. |
| Share of CPI components above 3% / below 1% | Inflation | 2 | Free API | StatsCan WDS Table 18-10-0006 | Fetch all ~150 subcomponents; count those above 3% and below 1% each month. Use `static=True` — the output is a single derived series, no toggles needed. |
| Inflation expectations (BOS, BLP, CSCE) | Inflation | 2 | Free release | BoC publications page | BoC publishes CSVs alongside PDFs. No REST API. BLP is monthly; BOS and CSCE are quarterly. Consensus Economics (paid) is substitutable with these three free BoC surveys. |
| Oil prices: Brent / WTI | Costs/commodities | 1 | Free API | EIA API | Free registration at eia.gov required. Series: `PET.RBRTE.D` (Brent), `PET.RCLC1.D` (WTI). Daily. |
| WCS (Western Canada Select) oil price | Costs/commodities | 1 | Free release | Government of Alberta daily price page | No clean API; scrape or download manually. WCS trades at a discount to WTI and matters for Canadian terms of trade specifically. |
| 2-year government bond yields (Canada vs US) | Financial | 1 | Free API | BoC Valet (Canada); FRED (US) | Canada is already in the dashboard. US 2-year: FRED series `DGS2`. |
| GDP growth contributions, quarterly | Real activity | 2 | Free API | StatsCan WDS Table 36-10-0104 | Compute chained-volume contributions and annualize. Quarterly frequency — use `frequency="quarterly"` in ChartSpec. |
| Wage growth (LFS average, SEPH) | Labour | 2 | Free API | StatsCan WDS Table 14-10-0064 (LFS wages), 14-10-0203 (SEPH wages) | Headline LFS and SEPH series are straight pulls. The Bank's microdata-quality-adjusted version requires running a regression on the public-use microdata file — skip that for now; headline tells most of the story. |
| Employment by sector reliant on US exports | Labour | 3 | Free API | StatsCan LFS Table 14-10-0023 + StatsCan IO tables | Identify which NAICS industries have ≥35% US-demand reliance using IO tables (one-time setup). Then plot LFS employment in those industries vs the rest. |
| Goods exports excluding gold | Trade | 2 | Free API | StatsCan WDS Table 12-10-0011 (by HS code) | Strip HS 7108 (gold bullion) from totals. Standard monthly transforms apply. |
| Hiring intentions (BOS) | Labour | 1 | Free release | BoC quarterly BOS publication | Direct chart from the BOS release. No transformation. Use `static=True` or `frequency="quarterly"`. |
| Pass-through and price-change expectations (BOS) | Trade | 1 | Free release | BoC quarterly BOS publication | Direct chart from BOS. Tracks share of firms saying they're fully passing through tariff costs. `static=True` or `frequency="quarterly"`. |

### B-tier: useful context (16 charts)

| Chart | Theme | Difficulty | Data access | Source | Notes |
|---|---|---|---|---|---|
| CPI components heatmap | Inflation | 3 | Free API | StatsCan WDS Table 18-10-0006 | Standardize each of the ~25 main categories by 1996–2019 mean/std. Methodology in MPR notes. Use `static=True`. |
| Labour market heatmap | Labour | 3 | Free API | StatsCan LFS, Job Vacancy and Wage Survey, productivity tables | Six indicators standardized over benchmark windows (Staff Note 2023-07). Use `static=True`. |
| Cost pressures heatmap | Costs | 4 | Free with effort | StatsCan IPPIs, EIA, Baltic Exchange / Freightos FBX | Multiple sources, some paid (shipping detail). Use Freightos FBX for a free shipping headline. Use `static=True`. |
| Sectoral exports (steel, aluminum, lumber, autos) | Trade | 2 | Free API | StatsCan Table 12-10-0011 by HS code | Index tariffed-sector export volumes to a pre-tariff base period. |
| Equity indexes (S&P/TSX, S&P 500) | Financial | 1 | Free API | `yfinance` Python library; or FRED for daily closes | `^GSPTSE` and `^GSPC` via yfinance. Daily. |
| Pace that keeps the employment rate constant | Labour | 2 | Free API | StatsCan LFS | Population growth × prior-month employment rate. Mechanical calculation on top of LFS. |
| Non-energy commodity prices (BCNEx) | Costs/commodities | 1 | Free API | BoC Valet | BoC publishes its own commodity index daily on Valet. |
| Housing starts and resales | Real activity | 1 | Free API / Free release | CMHC for starts (API); CREA for resales (no API) | CMHC has a clean monthly data release. CREA national stats are public but require manual download. |
| Consumer spending per person by category | Real activity | 2 | Free API | StatsCan Table 36-10-0124 (consumption) + Table 17-10-0009 (population) | Quarterly with the GDP release. |
| US labour market (unemployment + non-farm payrolls) | External | 1 | Free API | BLS API or FRED | Free registration. FRED series `UNRATE` (unemployment) and `PAYEMS` (payrolls). |
| US imports by origin | External/trade | 1 | Free API | US Census Bureau API or FRED | Tracks trade reconfiguration away from Canada. |
| Global / euro area PMI | External | 1 | Free release | S&P Global press releases (headline only) | Headlines are free in press releases; detailed sub-indices are paid. ISM (US) is free. |
| Cumulative change in exports by destination | Trade | 2 | Free API | StatsCan trade data by partner country | Sum trade values; subtract base period. Shows export-diversification story. |
| Share of non-US imports re-routed through US | Trade | 4 | Free with effort | StatsCan import data + US Census export data | Reconciling the two datasets at commodity level is non-trivial. Slow-moving; infrequent updates. |
| Brent spot vs front-month futures spread | Costs/commodities | 2 | Free API | EIA spot + CME front-month | Subtract. Only matters in stress periods (e.g., April 2026 oil shock). |
| US policy uncertainty index | Financial | 1 | Free release | policyuncertainty.com | Free CSV download. URL structure is stable. No REST API. |

### Notes on `static=True` charts

Several of the above charts output a derived number per period (a percentage, a count, a standardized score) rather than a raw economic series. Toggles like "Level vs Y/Y" don't add value because the derived value is already the point. Set `static=True` for:
- Share of CPI components above 3% / below 1%
- CPI components heatmap
- Labour market heatmap
- Cost pressures heatmap
- Hiring intentions (BOS) — the value is already an index or net balance
- Pass-through expectations (BOS)

---

## Known issues and open questions

1. **Author display name** — `AUTHOR_DISPLAY_NAME = "jayzhaomurray"` in `build.py`. Update to a real name if desired.

2. **Hover format for level series** — unemployment rate level shows "6.70" with no `%` sign. Adding `hover_format: str = ""` to ChartSpec and threading it through `_hover_template()` is the right fix — deferred until a chart actually looks bad.

3. **StatsCan `n_periods` for non-monthly series** — `fetch.py` fetches 10,000 periods for all StatsCan series (effectively "all available"). For quarterly series this gives decades of data. When quarterly series are added, this is fine but worth being aware of.

4. **CPI breadth basket weights** — the 2024 vintage from Table 18-10-0007 is hardcoded in `data/cpi_breadth_mapping.json`. When StatsCan publishes a new basket (every ~2 years), re-running the probe and regenerating the mapping would improve accuracy. The methodology is documented in the `CpiBreadthSpec` section above.

5. **CPI breadth component coverage** — 59 of 60 depth-3 components are used (96% of basket after dropping "Other tobacco products" which only starts in 2013). If future basket revisions introduce more late-starting components, the `first_valid_index() <= '1995-01-01'` filter in `_build_cpi_breadth_panel()` will automatically exclude them and re-normalise.

6. **EIA API registration** — the EIA API (for oil prices) requires a free API key from eia.gov. When adding oil charts, `fetch.py` will need to read the key from an environment variable (`EIA_API_KEY`) and the GitHub Actions workflow will need it as a secret.

7. **BoC survey data (BOS, BLP, CSCE)** — these are published as PDFs with companion CSV files at predictable URL patterns on bankofcanada.ca. There is no REST API. Fetching them requires downloading the CSV directly.

8. **Consensus Economics** — the only meaningful paid data source in the A-tier list. The BoC's own three surveys (BOS, BLP, CSCE) are a sufficient free substitute for tracking inflation expectations.
