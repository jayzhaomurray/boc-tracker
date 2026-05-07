# BoC Tracker — Project Handoff

This document captures the full state of the project, every architectural decision, and the next steps. Written so a fresh session can continue without any prior context.

---

## What this project is

A personal data dashboard that tracks the economic indicators the Bank of Canada watches between its quarterly Monetary Policy Reports (MPRs). The output is a single interactive HTML file hosted publicly on GitHub Pages.

**Live URL:** https://jayzhaomurray.github.io/boc-tracker/
**GitHub repo:** https://github.com/jayzhaomurray/boc-tracker
**Owner GitHub handle:** jayzhaomurray

**Tech stack:** Python → Plotly → static HTML → GitHub Pages
**Data sources:** Statistics Canada WDS API, Bank of Canada Valet API, Federal Reserve (FRED) API, Alberta Economic Dashboard API

---

## File structure

```
boc-tracker/
├── fetch.py                ← pulls data from APIs, saves CSVs to data/
├── build.py                ← reads CSVs, builds index.html
├── requirements.txt        ← requests, pandas, plotly
├── .gitignore              ← __pycache__/, *.pyc, .claude/, probe_*.py, table-*.json
├── index.html              ← generated output; do not edit by hand
├── data/                   ← all fetched CSVs (source-of-truth for build.py)
│   ├── cpi_all_items.csv         ← SA, vector 41690914
│   ├── cpi_all_items_nsa.csv     ← NSA, vector 41690973
│   ├── cpi_services.csv          ← NSA, vector 41691230
│   ├── cpi_trim.csv / cpi_median.csv / cpi_common.csv
│   ├── cpix.csv / cpixfet.csv
│   ├── cpi_components.csv        ← wide CSV: 60 depth-3 components × ~500 months
│   ├── cpi_breadth_mapping.json  ← component metadata: vector IDs, basket weights, names
│   ├── unemployment_rate.csv
│   ├── lfs_wages_all.csv         ← LFS avg hourly wages, all employees, SA
│   ├── lfs_wages_permanent.csv   ← LFS avg hourly wages, permanent employees, SA
│   ├── seph_earnings.csv         ← SEPH avg weekly earnings, SA
│   ├── lfs_micro.csv             ← BoC LFS-Micro composition-adjusted Y/Y
│   ├── overnight_rate.csv        ← BoC overnight rate target, monthly
│   ├── fed_funds.csv             ← Fed funds target midpoint, mixed monthly/daily
│   ├── yield_2yr.csv             ← Canada 2Y benchmark, daily
│   ├── us_2yr.csv                ← US 2Y Treasury, daily
│   ├── usdcad.csv                ← FRED DEXCAUS, CAD per USD, daily
│   ├── wti.csv / brent.csv       ← FRED daily oil
│   └── wcs.csv                   ← Western Canada Select, monthly (Alberta API)
├── analyses/                ← one-off research scripts and reference data; NOT run by pipeline
│   ├── trim_vs_median_skewness.py        ← empirical test on a framework claim
│   ├── trim_vs_median_skewness_results.csv
│   ├── trim_vs_median_skewness_plot.png
│   └── boc_speech_breadth_reference.csv  ← BoC's own published breadth chart data
└── markdown-files/          ← reference docs and this handoff
    ├── HANDOFF.md
    ├── analysis_framework.md             ← internal analytical brief for blurb generation
    ├── reading_guide.md                  ← human-readable interpretation guide per chart
    ├── boc_mpr_charts_inventory.md       ← original ~120-chart MPR inventory
    ├── boc_mpr_tracking_priority.md      ← A/B/C/D priority ranking
    └── boc_mpr_data_methodology.md       ← per-chart difficulty + API notes
```

The `analyses/` folder is for one-off research and reference data. Scripts there are run manually, never by `fetch.py` or `build.py`. Each analysis is a self-contained `.py` file that reads from `data/` and writes its own outputs (CSV/PNG) into `analyses/`. Discovery scripts (`probe_*.py`) and curl artifacts (`table-*.json`) are gitignored — keep new probes inside `analyses/` with descriptive names.

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

`build.py` is offline. Only `fetch.py` makes network calls.

The `--wait` flag on `fetch.py` activates a retry loop for StatsCan series: compares the latest date in the API response to the saved CSV; if no update is detected it sleeps 30 seconds and retries (up to 10 times). Used by the 8:30 AM ET scheduled runs; not needed for the BoC daily run.

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
| `cpi_services` | StatsCan | Vector 41691230 | Services CPI, Canada, NSA (Table 18-10-0004-01) | Monthly |
| `cpi_trim` | BoC Valet | `CPI_TRIM` | CPI-trim, Y/Y % | Monthly |
| `cpi_median` | BoC Valet | `CPI_MEDIAN` | CPI-median, Y/Y % | Monthly |
| `cpi_common` | BoC Valet | `CPI_COMMON` | CPI-common, Y/Y % | Monthly |
| `cpix` | BoC Valet | `ATOM_V41693242` | CPIX (excl. 8 volatile), Y/Y % | Monthly |
| `cpixfet` | BoC Valet | `STATIC_CPIXFET` | CPIXFET (excl. food & energy), Y/Y % | Monthly |
| `cpi_components` | StatsCan | 60 vectors (see mapping JSON) | Wide CSV: one column per CPI component | Monthly |
| `unemployment_rate` | StatsCan | Vector 2062815 | Unemployment rate, Canada, SA | Monthly |
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

---

## Architecture: spec dataclasses

All chart and page configuration lives in the `PAGES` list at the bottom of `build.py`. To add a chart, add a spec to a page's `charts` list. To add a page, add a `PageSpec` to `PAGES`.

### ChartSpec

Single-series chart with a transform toggle. Used for static or simple charts (e.g. unemployment_rate).

```python
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
```

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

### WageSpec

Composite chart: range band across four wage measures + individual toggles for each + Services CPI overlay. Built by `_build_wage_panel`. Trace map:
- 0/1: range bounds across LFS-all, LFS-permanent, SEPH, LFS-Micro
- 2–5: the four wage measures
- 6: Services CPI Y/Y (overlay, dashed red)

Services CPI is clipped to start at the earliest valid wage date so Max view doesn't show 50 years of services-only data.

### CpiAllItemsSpec

CPI All Items with both SA and NSA series, transform buttons + legend toggle. Built by `_build_cpi_all_items_panel`. Trace map:
- 0–3: SA × {Level, M/M, 3M AR, Y/Y}
- 4–7: NSA × {Level, M/M, 3M AR, Y/Y}

Transform button group + 2-item legend (SA, NSA). Visibility = (active transform) AND (legend item on). Default: SA on, NSA off, M/M view, 2Y window. Y_RANGES are computed per transform per window covering both SA and NSA jointly so the y-axis range looks right regardless of which series are visible.

### PageSpec

```python
@dataclass
class PageSpec:
    title: str
    tagline: str
    output_file: str
    charts: list   # ChartSpec | MultiLineSpec | WageSpec | CpiAllItemsSpec | CoreInflationSpec | CpiBreadthSpec
```

### Current PAGES definition (9 charts)

```
PageSpec("Bank of Canada Tracker", ...)
  CoreInflationSpec        — Core Inflation (range band + headline + trim/median toggle)
  CpiBreadthSpec           — CPI Breadth (deviation from 1996–2019 avg)
  MultiLineSpec            — Policy Rates (BoC overnight + Fed funds, hv step, 10Y default)
  MultiLineSpec            — 2-Year Yields (Canada + US, smooth toggle, 10Y default)
  CpiAllItemsSpec          — CPI All Items (SA + NSA toggle, M/M default, 2Y default)
  ChartSpec                — Unemployment Rate (static, 10Y default)
  WageSpec                 — Wage Growth (range band + 4 measures + Services CPI overlay)
  MultiLineSpec            — Oil Prices (WTI + Brent + WCS, smooth toggle, ymin=0, 10Y default)
  ChartSpec                — USD/CAD (daily, 10Y default)
```

All charts default to 10Y window except CPI All Items (2Y, since M/M behaviour over 10 years is hard to read).

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

All transforms are pre-computed at build time and embedded as separate Plotly traces. Only the default is initially visible. Toggle buttons use Plotly `restyle` to swap visibility. Buttons are plain HTML, not Plotly `updatemenus`. **No live calculation at click time.**

**JavaScript functions:**
- `xformClick(btn, chartId, idx)` — radio-style transform switch for ChartSpec
- `rangeClick(btn, chartId, years)` — set date range for one chart
- `gcRange(years, btn)` — override date range across all charts
- `toggleTrace(btn, chartId, indices)` — generic trace show/hide (CoreInflation, CpiBreadth)
- `mlXformClick(btn, chartId, mode, lineCount)` / `mlToggle(...)` — MultiLineSpec smooth-mode handling
- `cpiXformClick(btn, chartId, transformIdx, ticksuffix)` / `cpiVersionToggle(...)` / `_cpiApplyVisibility(div)` — CpiAllItemsSpec dual-axis (transform × version) state machine

State per chart is stored on the div element: `div._mlMode`, `div._cpiTransform`, `div._cpiVisible`.

### Y-axis scaling on date range change

Pre-computed Y_RANGES embedded in the page JS. `applyRange(chartId, years)` finds the first visible trace, looks up `Y_RANGES[chartId][traceIdx][years]`, applies as `yaxis.range`. For Max it sets `yaxis.autorange: true`.

`DEFAULT_RANGES` initializes each chart's window on `DOMContentLoaded`.

Padding formula: `max((ymax - ymin) * 0.08, 0.1)` applied symmetrically.

### Y-axis tick density and decimal consistency

Earlier the project used `_ytick_format(vals)` (decimals based on data span) plus Plotly's automatic ticks. That produced charts with as few as three labels and decimal inconsistency between ticks (e.g. "1.3" next to "1.35" on the same axis).

Current approach in `build.py`:

- **`_nice_dtick(ymin, ymax, target=5)`** — round-DOWN nice tick interval (1, 2, 2.5, 5 × 10^k) sized so at least `target` ticks fit in the displayed range. Round-down guarantees ≥ target ticks; round-up was tried first and produced too few.
- **`_dtick_format(dtick)`** — tickformat string whose precision matches the dtick value, so all ticks display the same number of decimal places.
- For multi-series charts (MultiLineSpec, WageSpec, CoreInflation, CpiBreadth): dtick is computed from the **displayed range** (data + padding), not raw data. `tick0=0` anchors the tick grid to integer multiples.
- For ChartSpec: no fixed dtick — uses `nticks=7` instead, because different transforms (Level vs M/M) have wildly different scales and a global dtick is wrong for at least one.

### Color palette

| Usage | Hex |
|---|---|
| Canada / BoC / primary series | `#1565c0` |
| US / Fed / opposing series | `#c62828` |
| CPI-trim overlay | `#546e7a` |
| CPI-median overlay | `#78909c` |
| LFS-Micro (BoC composition-adjusted) | `#4a148c` |
| WTI / Brent / WCS | `#c62828` / `#e57373` / `#6d4c41` |

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

Each chart panel:
```
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

The About section lists all four data sources (StatsCan, BoC Valet, FRED, Alberta Economic Dashboard).

---

## Analysis framework system (in progress)

The longer-term plan: when new data lands each month, Claude reads the data against an internal analytical brief, generates 4 short interpretive blurbs (one per dashboard section), and `build.py` injects them into the HTML before each section heading. Readers see prose like *"Wage growth is cooling but still running ahead of services CPI…"* — not a how-to-read-it explainer, just synthesis.

### Two layers

- **Internal (private):** `markdown-files/analysis_framework.md` — defines the question per section, the signals/relationships to evaluate, the thresholds, and what to surface in the output. This is Claude's brief, never seen by readers.
- **External (on the page):** Natural prose blurbs, generated at fetch+build time. Not yet wired into `build.py`.

### Sections and natural groupings

1. **Inflation** — Core Inflation, CPI Breadth, CPI All Items
2. **Policy Rates** — Policy Rates, 2-Year Yields
3. **Labour Market** — Unemployment, Wage Growth
4. **External Conditions** — Oil Prices, USD/CAD

(Heading wording is final; "External Conditions" was preferred over "Global Inputs" because it reads correctly for both the commodity and FX side.)

### Verification process

Framework claims must be either sourced to a primary publication (BoC, StatsCan, academic literature) or empirically tested against the data we already have. One-off analyses go in `analyses/`. Items verified so far:

- **Trim vs median directional signal** — REMOVED. No reputable analyst uses it; Cleveland Fed research contradicts the simple interpretation; empirical sign-agreement is 45–50% (coin flip). See `analyses/trim_vs_median_skewness.py`.
- **CPIXFET vs CPI-trim as goods/services diagnostic** — REMOVED. CPIXFET is a legacy measure (BoC moved away from it in 2001 → CPIX → 2016 trim/median/common). No analyst usage; logical mapping is weak.
- **0.17%/month threshold for 2% annualized** — KEPT. Mathematically (1.0017)^12 = 2.06%; precise figure is 0.165%. **Important methodological finding:** vector 41690914 was mislabelled "NSA" in `fetch.py` but is actually SA. Confirmed by inspecting M/M seasonal pattern. The threshold therefore applies cleanly to our existing chart data. NSA series added separately as `cpi_all_items_nsa` (vector 41690973) for legend-toggle comparison.

### Items still to verify, in order

1. Breadth chart's 1996–2019 baseline (defensible window? alternative?) — `analyses/boc_speech_breadth_reference.csv` is on hand for empirical validation
2. Neutral rate range (~2.5–3% for Canada) — needs current BoC r* citation
3. NAIRU (~5–5.5% for Canada) — needs current source; estimates have moved
4. Productivity assumption (~1%) embedded in the 3% wage-growth threshold — Canadian productivity has been weak; this may be too generous
5. CAD pass-through rule of thumb (~10% depreciation → 1–2% goods CPI) — needs source
6. Petrocurrency relationship characterization — when has it broken down historically?
7. WCS-WTI normal differential — should this be a tracked spread or just a footnote?

### Pipeline implementation (not yet built)

When the framework is locked, the plan is:

- A new `analyze.py` script (or step in the GitHub Actions workflow) that runs after `fetch.py`
- Reads latest CSVs, constructs a prompt with the analysis framework + key computed values, calls Claude API
- Recommended model: **Claude Opus 4.7** (`claude-opus-4-7`). Quality matters more than cost given monthly run frequency.
- Optionally pass the previous run's blurbs as context, so the model can note what changed since last release rather than describing the current state in isolation
- Output: `data/blurbs.json` keyed by section
- `build.py` reads `data/blurbs.json` and injects the appropriate blurb above each section heading
- The dashboard carries an unobtrusive disclaimer ("Analysis generated by AI from public data. Not investment advice.")

---

## What has been implemented

- [x] `fetch.py` — pulls StatsCan, BoC Valet, FRED, Alberta Economic Dashboard
- [x] `build.py` — config-driven, builds 9-chart `index.html` from CSVs
- [x] Full transformation system for all frequencies
- [x] Spec dataclasses (Chart, MultiLine, CoreInflation, CpiBreadth, Wage, CpiAllItems, Page)
- [x] GitHub Pages deployment + GitHub Actions cron (3 schedules + dispatch)
- [x] StatsCan retry/poll logic via `--wait`
- [x] **Core Inflation panel** — range band of 5 core measures + headline + toggles
- [x] **CPI Breadth chart** — calibrated against BoC published chart
- [x] **Policy Rates** — BoC + Fed, step rendering, 10Y default
- [x] **2-Year Yields** — Canada + US, smooth toggle, 10Y default
- [x] **CPI All Items (dual SA/NSA)** — transform toggle × legend toggle, M/M default, 2Y default
- [x] **Unemployment Rate** — static, 10Y default
- [x] **Wage Growth** — range band + 4 measures + Services CPI overlay
- [x] **Oil Prices** — WTI/Brent/WCS, smooth toggle, ymin=0 floor for the April-2020 anomaly
- [x] **USD/CAD** — daily, 10Y default
- [x] Pre-computed Y_RANGES + `applyRange` for correct y-axis on range change
- [x] `_nice_dtick` + `_dtick_format` for tick density and decimal consistency
- [x] About section credits all four data sources
- [x] `analyses/` folder convention; `probe_*.py` and `table-*.json` gitignored
- [x] Analysis framework draft (`markdown-files/analysis_framework.md`); items 1–3 verified

## What has NOT been implemented

- [ ] **Framework verification** — items 4–10 still to verify (breadth baseline, neutral rate, NAIRU, productivity, CAD pass-through, petrocurrency, WCS spread)
- [ ] **Blurb generation pipeline** — `analyze.py`, prompt construction, `data/blurbs.json`, `build.py` injection
- [ ] **Section headings on the dashboard** — once blurbs exist, add static headings ("Inflation", "Policy Rates", "Labour Market", "External Conditions") with blurb above
- [ ] **AI-generated content disclaimer** — short note in the About section
- [ ] **Multiple pages** — PAGES list has one entry; infrastructure is ready
- [ ] **Navigation bar** — only relevant after multi-page split
- [ ] **Custom domain**

---

## Next steps, in priority order

### 1. Continue framework verification

One item at a time, primary sources where available, empirical tests where appropriate. Items 4–10 listed above. The user's instruction is to do the research collaboratively — the agent does the legwork and brings findings back; the user reviews and signs off.

### 2. Build the blurb generation pipeline

Once the framework is locked (or close to it):
- `analyze.py` — read CSVs, compute the key values referenced in the framework, build a prompt, call Claude Opus 4.7, parse the response
- `data/blurbs.json` — section → prose
- Update `build.py` to read blurbs and inject above section dividers
- Add disclaimer to About section
- Wire `analyze.py` into the GitHub Actions workflow after each successful `fetch.py`

### 3. Add section headings + blurbs to the dashboard layout

Static thematic headings (`Inflation`, `Policy Rates`, `Labour Market`, `External Conditions`), with the blurb rendered above each heading. Visual style: subtle dividers, not editorial-prominent.

### 4. Multi-page split (eventually)

When chart count grows past ~12, split into themed pages. Planned:
- `index.html` — inflation
- `financial.html` — policy/markets
- `labour.html` — employment + wages
- `trade.html` — exports, tariff, imports

### 5. Charts still on the wishlist

The original A-tier roadmap items not yet built:

| Chart | Data |
|---|---|
| Headline CPI + CPI ex-indirect-taxes overlay | StatsCan / BoC Valet |
| Inflation expectations: BOS, BLP, CSCE | BoC publications page (CSVs) |
| GDP growth contributions | StatsCan Table 36-10-0104; quarterly |
| Employment by sector reliant on US exports | StatsCan LFS Table 14-10-0023 + IO tables |
| Goods exports excluding gold | StatsCan Table 12-10-0011 |
| BOS hiring intentions / pass-through | BoC quarterly BOS publication |

---

## Known issues and open questions

1. **`fed_funds` frequency mixing** — CSV is monthly pre-2009, daily post-2009. Step-function rendering on Policy Rates handles it visually. No problems in practice.

2. **Hover format for level series** — `_hover_template()` infers suffix from transform. Unemployment level shows "6.70" with no `%`. Add a `hover_format` field to ChartSpec if a chart looks wrong.

3. **`_nice_dtick` / `_dtick_format` are computed once at build time** — they assume the default-window's data range. When a user switches the date window via the range buttons, the dtick stays fixed. Plotly's auto-tick wouldn't re-compute either, so this is acceptable, but extreme zooms (e.g. 2Y vs Max) on a transformed axis can look slightly off.

4. **CPI breadth basket weights** — 2024-vintage hardcoded in `data/cpi_breadth_mapping.json`. When StatsCan publishes a new basket (~every 2 years), regenerate. The original probe is gitignored; write a fresh one in `analyses/` next time.

5. **BoC breadth reference** — `analyses/boc_speech_breadth_reference.csv` is from an Oct 2025 BoC speech (Mendes); useful for one-time validation that our breadth methodology matches the BoC's. Re-download from `https://www.bankofcanada.ca/?p=248443` if needed.

6. **`DFEDTAR` unavailable** — FRED's daily single fed-funds target series returns HTTP 500. Pre-2009 history uses monthly `FEDFUNDS` (effective rate) instead.

7. **CPI All Items dual-toggle UX** — the SA/NSA distinction matters most in M/M view; in Y/Y the two series are essentially identical. Showing both in Y/Y is harmless but uninformative. Consider a hint or auto-hide of NSA in Y/Y if it becomes a usability issue.

8. **fetch.py table-number comments** — the comment for `cpi_services` was historically wrong (claimed 18-10-0006-01, actually 18-10-0004-01); same kind of error existed for `cpi_all_items` (claimed NSA, actually SA). Both fixed in the recent commit. **Verify any new vector ID against the cube metadata before adding it.**

9. **Author display name** — `AUTHOR_DISPLAY_NAME = "jayzhaomurray"` in `build.py`.
