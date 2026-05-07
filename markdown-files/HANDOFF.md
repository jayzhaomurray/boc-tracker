# BoC Tracker — Project Handoff

This document captures the full state of the project, every architectural decision, and the next steps. Written so a fresh session can continue without any prior context.

---

## What this project is

A personal data dashboard that tracks the economic indicators the Bank of Canada watches between its quarterly Monetary Policy Reports (MPRs). The output is a single interactive HTML file hosted publicly on GitHub Pages.

**Live URL:** https://jayzhaomurray.github.io/boc-tracker/  
**GitHub repo:** https://github.com/jayzhaomurray/boc-tracker  
**Owner GitHub handle:** jayzhaomurray

**Tech stack:** Python → Plotly → static HTML → GitHub Pages  
**Data sources:** Statistics Canada WDS API, Bank of Canada Valet API, Federal Reserve (FRED) API

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
│   ├── overnight_rate.csv       ← BoC overnight rate target, monthly
│   ├── fed_funds.csv            ← Fed funds target midpoint, mixed monthly/daily
│   ├── us_2yr.csv               ← US 2-year Treasury yield, daily
│   ├── cpi_trim.csv
│   ├── cpi_median.csv
│   ├── cpi_common.csv
│   ├── cpix.csv
│   ├── cpixfet.csv
│   ├── cpi_components.csv       ← wide CSV: 500 months × 60 depth-3 CPI components
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
$env:FRED_API_KEY = "c0c26d8fd7f30f1d70d59bbaa2002836"   # PowerShell; set once per session
python fetch.py

# Step 2: regenerate the dashboard from saved CSVs (run when you change the code)
python build.py

# Step 3: view locally
start index.html          # Windows
open index.html           # Mac
```

You can run `build.py` repeatedly without hitting any APIs. Only `fetch.py` makes network calls.

The `--wait` flag on `fetch.py` activates a retry loop for StatsCan series: it compares the latest date in the API response to the saved CSV, and if no update is detected it sleeps 30 seconds and retries (up to 10 times). Use this on the 8:30 AM ET scheduled runs; do not use it on the BoC daily run.

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

### Federal Reserve (FRED) API

**Endpoint:** `GET https://api.stlouisfed.org/fred/series/observations`  
**Query params:** `series_id`, `observation_start`, `api_key`, `file_type=json`  
**Key:** stored in environment variable `FRED_API_KEY`. For GitHub Actions, stored as a repo secret.  
**Registration:** fred.stlouisfed.org (free, takes ~10 minutes)  
**Current key:** `c0c26d8fd7f30f1d70d59bbaa2002836` (jayzhaomurray's account)

Response structure:
```json
{
  "observations": [
    {"date": "2026-05-05", "value": "4.33"}
  ]
}
```

Missing values are returned as `"."` (string dot) and filtered out in `fetch_fred()`.

---

## Current series

| CSV filename | Source | Identifier | Description | Frequency |
|---|---|---|---|---|
| `cpi_all_items` | StatsCan | Vector 41690914 | All-items CPI, Canada, not SA (Table 18-10-0006-01) | Monthly |
| `unemployment_rate` | StatsCan | Vector 2062815 | Unemployment rate, Canada, SA (Table 14-10-0287-01) | Monthly |
| `cpi_trim` | BoC Valet | `CPI_TRIM` | CPI-trim, Y/Y % | Monthly |
| `cpi_median` | BoC Valet | `CPI_MEDIAN` | CPI-median, Y/Y % | Monthly |
| `cpi_common` | BoC Valet | `CPI_COMMON` | CPI-common, Y/Y % | Monthly |
| `cpix` | BoC Valet | `ATOM_V41693242` | CPIX (excl. 8 volatile), Y/Y % | Monthly |
| `cpixfet` | BoC Valet | `STATIC_CPIXFET` | CPIXFET (excl. food & energy), Y/Y % | Monthly |
| `yield_2yr` | BoC Valet | `BD.CDN.2YR.DQ.YLD` | 2-yr GoC benchmark bond yield | Daily |
| `overnight_rate` | BoC Valet | `STATIC_ATABLE_V39079` | BoC overnight rate target | Monthly (end-of-month) |
| `us_2yr` | FRED | `DGS2` | US 2-year Treasury constant maturity yield | Daily |
| `fed_funds` | FRED (special) | See below | Fed funds target midpoint | Mixed (monthly pre-2009, daily post-2009) |
| `cpi_components` | StatsCan | 60 vectors (see mapping JSON) | Wide CSV: one column per CPI component | Monthly |

**`fed_funds` construction:** `FEDFUNDS` monthly effective rate (1990–Dec 2008) prepended to `(DFEDTARU + DFEDTARL) / 2` daily midpoint (Dec 2008–present). Built by `fetch_fed_funds_target()` in `fetch.py`. `DFEDTAR` (discontinued daily single target) is not used — FRED returns HTTP 500 for it.

---

## GitHub Actions workflow

`.github/workflows/update.yml` — three scheduled triggers:

```
30 12 * * *   → 8:30 AM EDT (summer) — StatsCan release window
30 13 * * *   → 8:30 AM EST (winter) — StatsCan release window
 0 15 * * *   → 11:00 AM EDT / 10:00 AM EST — BoC daily yields
```

The DST problem: no single UTC time is 8:30 AM ET year-round. Two cron lines handle this — one fires early (harmless on the other season), one fires exactly right.

Both StatsCan crons use `python fetch.py --wait` (retry loop); the BoC cron uses `python fetch.py` (one-shot).

The workflow also supports `workflow_dispatch` (manual trigger from GitHub UI).

`FRED_API_KEY` is passed as an environment variable from a GitHub Actions secret. The secret is already configured in the repo.

---

## Architecture: spec dataclasses

All chart and page configuration lives in the `PAGES` list at the bottom of `build.py`. Nothing else needs to change when adding charts or pages.

### ChartSpec

```python
@dataclass
class ChartSpec:
    series: str               # key into data dict; must match CSV filename without .csv
    title: str                # panel heading
    frequency: str            # "daily" | "weekly" | "monthly" | "quarterly" | "annual" | "irregular"
    color: str                # hex color for the line
    static: bool = False      # if True, no transform buttons shown
    default_transform: str = "level"
    default_years: int | None = None  # initial date range; None means Max
    footnote: str = ""        # optional note rendered below the chart in small gray text
```

### CoreInflationSpec

A one-off composite chart. Configured only with `title` and optional `footnote`. Hardcoded to load `cpi_all_items`, `cpi_trim`, `cpi_median`, `cpi_common`, `cpix`, `cpixfet`. Built by `_build_core_inflation_panel()`.

**Trace index map:**
| Index | Series | Default visibility |
|---|---|---|
| 0 | range lower bound (min of 5 core measures) | visible |
| 1 | range upper bound (max of 5 core measures, fills to trace 0) | visible |
| 2 | Total CPI Y/Y (`#1565c0`) | visible |
| 3 | CPI-trim (`#546e7a`) | hidden |
| 4 | CPI-median (`#78909c`) | hidden |

Y_RANGES stored under all trace indices 0–4 (identical values) so the lookup works regardless of which trace is first visible.

### CpiBreadthSpec

A one-off composite chart. Configured only with `title` and optional `footnote`. Built by `_build_cpi_breadth_panel()`.

**Methodology:**
- Source: `data/cpi_components.csv` — wide CSV: months × 60 depth-3 components
- Weights: 2024-vintage from StatsCan Table 18-10-0007, stored in `data/cpi_breadth_mapping.json`
- Late-starter filter: components whose first valid date is after 1995-01-01 are dropped (only the tobacco component hits this currently)
- Computation: for each month, Y/Y for each component → weighted share where Y/Y > 3% (`above_3_raw`) and < 1% (`below_1_raw`)
- Historical average: mean of above/below over 1996–2019 (pre-COVID inflation-targeting era)
- Display: deviation from that average from 1996 onward. Above-3% in red (`#c62828`), below-1% in blue (`#1565c0`). Y-axis in pp.
- Default view: 10Y
- Calibration: 2022 peak (+46 pp) matches BoC published chart (speech SPEECH_MEND20251002, Oct 2025) within 1 pp

### LineConfig and MultiLineSpec

Generic multi-line chart type with per-line toggle buttons. Used for policy rates and 2-year yields. Add any number of lines via `LineConfig`.

```python
@dataclass
class LineConfig:
    series: str          # CSV filename without .csv
    label: str           # legend label
    color: str           # hex color
    visible: bool = True

@dataclass
class MultiLineSpec:
    title: str
    lines: list               # list[LineConfig]
    ticksuffix: str = "%"
    hoverformat: str = ".2f"
    default_years: int | None = None
    line_shape: str = "linear"          # "linear" or "hv" (step — use for policy rates)
    smooth_window: int | None = None    # if set, adds Level / Nd Avg toggle buttons
    date_fmt: str = "%b %Y"            # hover date format ("%b %d, %Y" for daily data)
    footnote: str = ""
```

**Smooth window:** when `smooth_window` is set, the builder creates 2N traces — raw traces (0..N-1) and smoothed traces (N..2N-1). "Level" and "Nd Avg" buttons switch between the two sets via `mlXformClick`. Legend toggle buttons use `mlToggle` to preserve which lines are active across mode switches.

**Y_RANGES:** stored under all trace indices (0..2N-1 if smooth, 0..N-1 otherwise) so `applyRange` finds the right range regardless of which trace is currently first visible.

### PageSpec

```python
@dataclass
class PageSpec:
    title: str
    tagline: str
    output_file: str
    charts: list
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
                title="Core Inflation",
                footnote="Year-over-year %. Shaded band shows range across BoC core measures (trim, median, common, CPIX, CPIXFET).",
            ),
            CpiBreadthSpec(
                title="CPI Breadth",
                footnote="Deviation from 1996–2019 average. Weighted share of 60 basket components with year-over-year change above 3% or below 1%.",
            ),
            MultiLineSpec(
                title="Policy Rates",
                lines=[
                    LineConfig("overnight_rate", "BoC", "#1565c0"),
                    LineConfig("fed_funds",       "Fed", "#c62828"),
                ],
                default_years=10,
                line_shape="hv",
                footnote="BoC overnight rate target; Fed funds midpoint of target range.",
            ),
            MultiLineSpec(
                title="2-Year Yields",
                lines=[
                    LineConfig("yield_2yr", "Canada 2Y", "#1565c0"),
                    LineConfig("us_2yr",    "US 2Y",     "#c62828"),
                ],
                default_years=10,
                smooth_window=20,
                date_fmt="%b %d, %Y",
                footnote="2-year benchmark government bond yields.",
            ),
            ChartSpec(
                series="cpi_all_items",
                title="CPI — All Items",
                frequency="monthly",
                color="#1565c0",
                default_transform="mom",
                default_years=2,
                footnote="All-items CPI index, Canada, 2002=100, not seasonally adjusted.",
            ),
            ChartSpec(
                series="unemployment_rate",
                title="Unemployment Rate",
                frequency="monthly",
                color="#1565c0",
                static=True,
                footnote="Canada, seasonally adjusted.",
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
| `yoy` | `v.pct_change(N) * 100` where N = 12/52/4/1 depending on frequency |

### How toggles are implemented

All transforms are computed at build time and embedded in the HTML as separate Plotly traces. Only the default transform is initially visible. Toggle buttons use Plotly's `restyle` method targeting specific trace indices — clicking a button on one chart does not affect other charts.

**Buttons are plain HTML `<button>` elements**, not Plotly `updatemenus`. They sit outside the Plotly canvas in a `.chart-controls` div in the chart header. Plotly's native controls were abandoned after they couldn't be positioned reliably outside the chart area.

**JavaScript functions:**
- `xformClick(btn, chartId, idx)` — switches between transform traces (radio style, one active)
- `rangeClick(btn, chartId, years)` — sets date range for one chart
- `gcRange(years, btn)` — overrides date range on all charts simultaneously
- `toggleTrace(btn, chartId, indices)` — show/hide a specific trace or group of traces (used by CoreInflationSpec and CpiBreadthSpec legends)
- `mlXformClick(btn, chartId, mode, lineCount)` — switches between Level/smooth for MultiLineSpec; reads active legend items to preserve which lines are on
- `mlToggle(btn, chartId, lineIdx, lineCount)` — toggles one line in a MultiLineSpec, respecting current Level/smooth mode

For `mlXformClick`, the current mode is stored on the div element as `div._mlMode` (`"raw"` or `"smooth"`). The legend div for MultiLineSpec charts gets `id="leg-{div_id}"` so `mlXformClick` can query it.

This is a deliberate decision: **no live calculation at click time**. All data is pre-baked into the HTML.

### Y-axis scaling on date range change

Plotly's `yaxis.autorange: true` computes the range from the full dataset regardless of the visible x window. Three browser-side approaches failed.

**Current solution: pre-computed y-ranges baked into the HTML.**

`_compute_y_ranges(chart, df)` runs at build time and computes y min/max for each (transform index, time window) combination. Results are embedded as `var Y_RANGES = {...}` in the page JS.

`applyRange(chartId, years)` finds the first visible trace, looks up `Y_RANGES[chartId][traceIdx][years]`, and passes it directly to `Plotly.relayout` as `yaxis.range`. For `Max` it calls with `yaxis.autorange: true`.

**Default ranges:** charts with `default_years` set are initialized on `DOMContentLoaded` via:
```javascript
var DEFAULT_RANGES = {...};
document.addEventListener("DOMContentLoaded", function() {
  Object.keys(DEFAULT_RANGES).forEach(function(id) { applyRange(id, DEFAULT_RANGES[id]); });
});
```
This correctly sets both axes on load (the Python-side `fig.update_xaxes(range=...)` approach only restricts x; y still autoscales from the full dataset).

Padding formula: `max((ymax - ymin) * 0.08, 0.1)` applied symmetrically.

### Y-axis tick formatting

`_ytick_format(vals: pd.Series) -> str` determines the minimum number of decimal places needed, applied consistently across all ticks on a given axis:

```
span / 4 >= 1.0  →  ".0f"   (ticks at integers: 0, 1, 2, 3...)
span / 4 >= 0.1  →  ".1f"   (ticks at tenths: 0.5, 1.0, 1.5...)
else             →  ".2f"   (ticks at hundredths)
```

Applied to MultiLineSpec and CpiBreadthSpec at build time, using data from the `default_years` window. ChartSpec charts use Plotly's default auto-format.

### Color palette

One blue, one red, used consistently across all charts:

| Usage | Hex |
|---|---|
| Canada / BoC / primary series | `#1565c0` |
| US / Fed / opposing series | `#c62828` |
| CPI-trim (overlay) | `#546e7a` |
| CPI-median (overlay) | `#78909c` |

---

## Architecture: HTML generation

`build.py` assembles the full HTML page as a single string:

```
<!DOCTYPE html>
  <head> CSS </head>
  <body>
    site-header (title, tagline, last-updated)
    global-controls (All charts — 2Y / 5Y / 10Y / Max)
    [chart panels, one per chart in page.charts]
    about section
    <script> JS including Y_RANGES, DEFAULT_RANGES, ALL_CHARTS </script>
  </body>
```

Each chart panel structure:
```
<div class="chart-panel">
  <div class="chart-header">
    <div class="chart-title">…</div>
    <div class="chart-controls">[transform buttons] [sep] [range buttons]</div>
  </div>
  [Plotly div]
  <div class="chart-legend">…</div>   ← only on multi-trace charts
  <div class="chart-footnote">…</div> ← if footnote is set
</div>
```

Plotly JS is loaded from CDN for the first chart only; subsequent charts pass `include_plotlyjs=False`. `config={"displayModeBar": False}` disables Plotly's hover toolbar.

---

## What has been implemented

- [x] `fetch.py` — fetches StatsCan, BoC Valet, and FRED series; saves to CSV
- [x] `build.py` — config-driven, reads CSVs, builds HTML with toggles
- [x] Full transformation system for all frequencies
- [x] ChartSpec / PageSpec config structure
- [x] Multi-page infrastructure (PAGES list, build_page loop)
- [x] Custom page header, tagline, last-updated timestamp, About section
- [x] GitHub repo and GitHub Pages deployment
- [x] **GitHub Actions workflow** — 3 DST-aware crons + workflow_dispatch; FRED_API_KEY secret configured
- [x] **StatsCan retry logic** — `--wait` flag polls until new data appears (up to 10 retries × 30s)
- [x] **Core inflation panel** — headline CPI Y/Y + shaded range of 5 core measures + toggle-able trim/median
- [x] **CPI breadth chart** — 59 weighted depth-3 components, deviation from 1996–2019 avg; calibrated against BoC published chart
- [x] **Policy rates chart** — BoC overnight target + Fed funds target midpoint, step-function rendering, 10Y default
- [x] **2-year yields chart** — Canada + US, with Level / 20d Avg smooth toggle, 10Y default
- [x] **CPI — All Items** — opens M/M, 2Y default
- [x] **Unemployment Rate** — static display
- [x] **Pre-computed Y_RANGES** — correct y-axis on date range change and on initial load
- [x] **`_ytick_format()`** — minimum consistent decimal places on y-axis
- [x] **Short titles + footnotes** — titles are minimal; context in per-chart footnote field
- [x] **Unified color palette** — `#1565c0` and `#c62828` used consistently

## What has NOT been implemented

- [ ] **More charts** — the dashboard has 6 charts. The A-tier priority list has 13. See expansion roadmap below.
- [ ] **Multiple pages** — the PAGES list has one entry. Infrastructure is ready.
- [ ] **Navigation bar** — if multiple pages are added, there's no nav between them yet.
- [ ] **Custom domain** — GitHub Pages URL is currently the public URL.

---

## Next steps, in priority order

### 1. Add charts — in recommended build order

**Step A — Remaining BoC Valet additions**

Non-energy commodity index (BCNEx) is a straight Valet pull. Add to `BOC_VALET_SERIES` and a `ChartSpec` in `build.py`.

**Step B — StatsCan Labour Force Survey**

Wage growth (Table 14-10-0064) and employment by industry (Table 14-10-0023). Straight vector pulls into ChartSpec.

**Step C — BoC survey publications (BOS, BLP, CSCE)**

No REST API. The BoC publishes CSVs alongside PDFs at predictable URL patterns on bankofcanada.ca. Quarterly for BOS and CSCE; monthly for BLP.

**Step D — StatsCan trade data by HS code**

Table 12-10-0011 for goods exports. Strip HS 7108 (gold) for exports ex-gold.

### 2. Multi-page split (when chart count warrants it)

Planned theme split:
- `index.html` — inflation (CPI, core measures, breadth)
- `financial.html` — financial conditions (policy rates, yields, oil, equities)
- `labour.html` — labour market (unemployment, wages, employment by sector)
- `trade.html` — trade (exports ex-gold, tariff rate, imports)

---

## Full expansion roadmap

### A-tier: must-track

| Chart | Theme | Difficulty | Data access | Source | Notes |
|---|---|---|---|---|---|
| ~~Headline CPI~~ | ~~Inflation~~ | — | — | — | **Done.** Opens M/M, 2Y default. |
| ~~Core inflation: CPI-trim, CPI-median, CPIX, CPIXFET~~ | ~~Inflation~~ | — | — | — | **Done.** `CoreInflationSpec` with range band and individual toggles. |
| ~~Share of CPI components above 3% / below 1%~~ | ~~Inflation~~ | — | — | — | **Done.** `CpiBreadthSpec`; 59 weighted depth-3 components. |
| ~~Policy rates (BoC + Fed)~~ | ~~Financial~~ | — | — | — | **Done.** BoC overnight target + Fed funds midpoint, `MultiLineSpec` with step rendering. |
| ~~2-year government bond yields (Canada + US)~~ | ~~Financial~~ | — | — | — | **Done.** `MultiLineSpec` with 20d smooth toggle. |
| Headline CPI + CPI ex-indirect-taxes | Inflation | 1 | Free API | StatsCan / BoC Valet | Add as a second line on the all-items chart or a new MultiLineSpec. |
| Inflation expectations (BOS, BLP, CSCE) | Inflation | 2 | Free release | BoC publications page | CSVs published alongside PDFs. Quarterly (BOS, CSCE) and monthly (BLP). |
| Oil prices: Brent / WTI | Costs/commodities | 1 | Free API | EIA API | Free registration at eia.gov. Series: `PET.RBRTE.D` (Brent), `PET.RCLC1.D` (WTI). |
| GDP growth contributions | Real activity | 2 | Free API | StatsCan Table 36-10-0104 | Compute chained-volume contributions and annualize. `frequency="quarterly"`. |
| Wage growth (LFS / SEPH) | Labour | 2 | Free API | StatsCan Tables 14-10-0064 and 14-10-0203 | Headline series are straight pulls. |
| Employment by sector reliant on US exports | Labour | 3 | Free API | StatsCan LFS Table 14-10-0023 + IO tables | One-time IO table setup to identify US-reliant NAICS industries. |
| Goods exports excluding gold | Trade | 2 | Free API | StatsCan Table 12-10-0011 (by HS code) | Strip HS 7108 (gold bullion). |
| Hiring intentions / pass-through expectations (BOS) | Labour / Trade | 1 | Free release | BoC quarterly BOS publication | Direct chart from BOS. `static=True`. |

### B-tier: useful context

| Chart | Theme | Difficulty | Notes |
|---|---|---|---|
| Non-energy commodity prices (BCNEx) | Costs | 1 | BoC Valet — straight pull |
| US labour market (unemployment + payrolls) | External | 1 | FRED `UNRATE`, `PAYEMS` |
| Equity indexes (S&P/TSX, S&P 500) | Financial | 1 | `yfinance` or FRED daily closes |
| CPI components heatmap | Inflation | 3 | 25 categories standardized over 1996–2019 |
| Labour market heatmap | Labour | 3 | Six indicators (Staff Note 2023-07 methodology) |
| Housing starts | Real activity | 1 | CMHC monthly API |
| Global / euro area PMI | External | 1 | S&P Global press releases (headline only free) |
| US policy uncertainty index | Financial | 1 | policyuncertainty.com — free CSV download |

---

## Known issues and open questions

1. **`fed_funds` frequency mixing** — the CSV is monthly pre-2009 and daily post-2009. The policy rates chart uses `line_shape="hv"` (step function) which handles this visually. Y_RANGES are computed from the combined series, which is fine. No issues in practice.

2. **Hover format for level series** — unemployment level shows "6.70" with no `%` sign. The hover template is inferred from transform and frequency. Add `hover_format: str = ""` to ChartSpec and thread it through `_hover_template()` if a chart looks wrong.

3. **Y-axis tickformat on transform switch** — `_ytick_format()` is computed once at build time from the default transform's data. If the user switches from Level (range ~100) to M/M (range ~2), the tickformat will still be the Level format. Plotly's auto-tick algorithm picks sensible values so this rarely causes visible problems, but it's not technically correct.

4. **CPI breadth basket weights** — 2024-vintage weights are hardcoded in `data/cpi_breadth_mapping.json`. When StatsCan publishes a new basket (every ~2 years), re-run the probe and regenerate the mapping. The probe logic is not in the repo — refer to the session that built it (2026-05-06).

5. **`DFEDTAR` unavailable** — FRED's daily single fed-funds target series (`DFEDTAR`) returns HTTP 500. Pre-2009 history uses monthly `FEDFUNDS` (effective rate) as an approximation, which is accurate to within a few basis points of the actual target for that era.

6. **Author display name** — `AUTHOR_DISPLAY_NAME = "jayzhaomurray"` in `build.py`.

7. **BoC breadth calibration reference** — `data/SPEECH_MEND20251002_C3.csv` is a manually downloaded CSV from a BoC speech (Deputy Governor Mend, Oct 2, 2025). Not fetched by `fetch.py`, not in git. Used to validate the breadth methodology. Re-download from `https://www.bankofcanada.ca/?p=248443` if needed.
