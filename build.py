"""
Read saved CSV data and build HTML dashboard pages.

Run fetch.py first to download data, then run this any time you change
chart layout, styling, or the PAGES config below.

Run:    python build.py
Output: index.html  (plus any other files defined in PAGES)
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_DIR = Path("data")
AUTHOR_DISPLAY_NAME = "jayzhaomurray"


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class ChartSpec:
    series: str               # matches CSV filename in data/ without .csv
    title: str                # panel heading
    frequency: str            # daily | weekly | monthly | quarterly | annual | irregular
    color: str                # hex line color
    static: bool = False      # if True, no transform buttons shown
    default_transform: str = "level"


@dataclass
class PageSpec:
    title: str
    tagline: str
    output_file: str
    charts: list[ChartSpec]


# ── Transform system ──────────────────────────────────────────────────────────

FREQ_TRANSFORMS: dict[str, list[str]] = {
    "daily":     ["level", "rolling_20d"],
    "weekly":    ["level", "rolling_4w", "yoy"],
    "monthly":   ["level", "mom", "ar_3m", "yoy"],
    "quarterly": ["level", "qoq", "qoq_ar", "yoy"],
    "annual":    ["level", "yoy"],
    "irregular": ["level"],
}

BUTTON_LABELS: dict[str, str] = {
    "level":       "Level",
    "rolling_20d": "20d Avg",
    "rolling_4w":  "4W Avg",
    "mom":         "M/M",
    "ar_3m":       "3M AR",
    "qoq":         "Q/Q",
    "qoq_ar":      "Q/Q AR",
    "yoy":         "Y/Y",
}

_YOY_PERIODS: dict[str, int] = {
    "monthly": 12, "weekly": 52, "quarterly": 4, "annual": 1,
}


def compute_transforms(df: pd.DataFrame, frequency: str) -> dict[str, pd.Series]:
    v = df.set_index("date")["value"]
    available = FREQ_TRANSFORMS[frequency]
    out: dict[str, pd.Series] = {}

    if "level"      in available: out["level"]       = v
    if "rolling_20d" in available: out["rolling_20d"] = v.rolling(20).mean()
    if "rolling_4w" in available: out["rolling_4w"]  = v.rolling(4).mean()
    if "mom"        in available: out["mom"]         = v.pct_change(1) * 100
    if "ar_3m"      in available: out["ar_3m"]       = ((v / v.shift(3)) ** 4 - 1) * 100
    if "qoq"        in available: out["qoq"]         = v.pct_change(1) * 100
    if "qoq_ar"     in available: out["qoq_ar"]      = ((v / v.shift(1)) ** 4 - 1) * 100
    if "yoy"        in available:
        periods = _YOY_PERIODS.get(frequency, 12)
        out["yoy"] = v.pct_change(periods) * 100

    return out


def _hover_template(transform: str, frequency: str) -> str:
    date_fmt = {
        "daily":     "%b %d, %Y",
        "weekly":    "%b %d, %Y",
        "monthly":   "%b %Y",
        "quarterly": "%Y",
        "annual":    "%Y",
        "irregular": "%Y-%m-%d",
    }.get(frequency, "%Y-%m-%d")

    pct_transforms = {"mom", "ar_3m", "qoq", "qoq_ar", "yoy"}
    suffix = "%" if transform in pct_transforms else ""
    return f"%{{x|{date_fmt}}}<br>%{{y:.2f}}{suffix}<extra></extra>"


def _resolve_default(chart: ChartSpec) -> str:
    available = FREQ_TRANSFORMS[chart.frequency]
    if chart.default_transform in available:
        return chart.default_transform
    print(
        f"Warning: default_transform='{chart.default_transform}' is not valid "
        f"for frequency='{chart.frequency}'. Falling back to 'level'."
    )
    return "level"


# ── Figure builder ────────────────────────────────────────────────────────────

def build_figure(page: PageSpec, data: dict[str, pd.DataFrame]) -> go.Figure:
    n_rows = len(page.charts)
    vertical_spacing = 0.10

    fig = make_subplots(
        rows=n_rows, cols=1,
        subplot_titles=[c.title for c in page.charts],
        vertical_spacing=vertical_spacing,
    )

    # trace_registry[i] = (chart_index, transform_key) for the i-th trace added
    trace_registry: list[tuple[int, str]] = []

    # Pass 1 — add all traces (one per transform per chart)
    for chart_idx, chart in enumerate(page.charts):
        df = data[chart.series]
        transforms = compute_transforms(df, chart.frequency)
        available = FREQ_TRANSFORMS[chart.frequency]
        default = "level" if chart.static else _resolve_default(chart)

        for transform_key in available:
            if transform_key not in transforms:
                continue
            s = transforms[transform_key]
            fig.add_trace(go.Scatter(
                x=s.index,
                y=s.values,
                name=f"{chart.series}_{transform_key}",
                visible=(transform_key == default),
                line=dict(color=chart.color, width=2),
                hovertemplate=_hover_template(transform_key, chart.frequency),
                showlegend=False,
            ), row=chart_idx + 1, col=1)
            trace_registry.append((chart_idx, transform_key))

    # Pass 2 — build one updatemenus group per non-static chart with >1 transform
    updatemenus = []

    for chart_idx, chart in enumerate(page.charts):
        if chart.static:
            continue
        available = FREQ_TRANSFORMS[chart.frequency]
        if len(available) <= 1:
            continue

        default = _resolve_default(chart)
        active_idx = available.index(default) if default in available else 0

        # Indices into trace_registry (= Plotly trace indices) for this chart
        chart_trace_indices = [
            i for i, (ci, _) in enumerate(trace_registry) if ci == chart_idx
        ]

        buttons = []
        for transform_key in available:
            # Visibility list covers only this chart's traces — other charts untouched
            vis = [
                t_key == transform_key
                for (ci, t_key) in trace_registry
                if ci == chart_idx
            ]
            buttons.append(dict(
                label=BUTTON_LABELS.get(transform_key, transform_key),
                method="restyle",
                args=[{"visible": vis}, chart_trace_indices],
            ))

        # Position buttons at the top of this subplot's y-domain
        yaxis_key = "yaxis" if chart_idx == 0 else f"yaxis{chart_idx + 1}"
        y_top = fig.layout[yaxis_key].domain[1]

        updatemenus.append(dict(
            type="buttons",
            direction="left",
            buttons=buttons,
            active=active_idx,
            x=1.0,
            xanchor="right",
            y=y_top,
            yanchor="bottom",
            pad={"r": 0, "t": 4},
            bgcolor="#f5f5f5",
            bordercolor="#ddd",
            borderwidth=1,
            font=dict(size=11, color="#333"),
            showactive=True,
        ))

    fig.update_layout(
        height=280 * n_rows + 60,
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        margin=dict(l=16, r=16, t=48, b=16),
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
        updatemenus=updatemenus,
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False)

    return fig


# ── HTML assembly ─────────────────────────────────────────────────────────────

_CSS = """\
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 980px;
    margin: 0 auto;
    padding: 36px 20px 64px;
    background: #ffffff;
    color: #1a1a1a;
  }
  .site-header { margin-bottom: 28px; }
  .site-header h1 { font-size: 1.45rem; font-weight: 700; margin: 0 0 6px; }
  .site-header .tagline { font-size: 0.88rem; color: #666; margin: 0 0 4px; }
  .site-header .updated { font-size: 0.78rem; color: #bbb; margin: 0; }
  .about {
    margin-top: 40px;
    padding: 13px 17px;
    background: #f7f7f7;
    border-left: 3px solid #ddd;
    font-size: 0.8rem;
    color: #666;
    line-height: 1.7;
  }
  .about a { color: #1a5276; text-decoration: none; }
  .about a:hover { text-decoration: underline; }
"""


def _inject_html(raw_html: str, page: PageSpec, last_updated: str) -> str:
    header = (
        '<div class="site-header">\n'
        '  <h1>' + page.title + '</h1>\n'
        '  <p class="tagline">' + page.tagline + '</p>\n'
        '  <p class="updated">Last updated: ' + last_updated + '</p>\n'
        '</div>\n'
    )
    about = (
        '<div class="about">\n'
        '  <strong>About this dashboard</strong> &mdash;\n'
        '  Built by <a href="https://github.com/' + AUTHOR_DISPLAY_NAME + '">'
        + AUTHOR_DISPLAY_NAME + '</a> using public data from\n'
        '  <a href="https://www150.statcan.gc.ca">Statistics Canada</a> and the\n'
        '  <a href="https://www.bankofcanada.ca/valet/docs">Bank of Canada Valet API</a>.\n'
        '  Raw data available as CSV in the\n'
        '  <a href="https://github.com/' + AUTHOR_DISPLAY_NAME + '/boc-tracker/tree/main/data">'
        'GitHub repository</a>.\n'
        '</div>\n'
    )
    raw_html = raw_html.replace("</head>", "<style>\n" + _CSS + "</style>\n</head>", 1)
    raw_html = raw_html.replace("<body>", "<body>\n" + header, 1)
    raw_html = raw_html.replace("</body>", about + "</body>", 1)
    return raw_html


# ── Page definitions ──────────────────────────────────────────────────────────
#
# To add a new page: add a PageSpec to PAGES.
# To add a new chart: add a ChartSpec to a page's charts list.
# Each series key must match a CSV file in data/ (without .csv).
# Run fetch.py first to make sure the CSV exists.

PAGES = [
    PageSpec(
        title="Bank of Canada Tracker",
        tagline="Tracking the indicators behind Bank of Canada policy decisions",
        output_file="index.html",
        charts=[
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


# ── Main ──────────────────────────────────────────────────────────────────────

def build_page(page: PageSpec, data: dict[str, pd.DataFrame]) -> None:
    fig = build_figure(page, data)
    fig.write_html(page.output_file, include_plotlyjs="cdn", full_html=True)

    with open(page.output_file, "r", encoding="utf-8") as f:
        html = f.read()

    last_updated = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    html = _inject_html(html, page, last_updated)

    with open(page.output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  -> {page.output_file}")


def main():
    print("Loading data...")
    all_series = {chart.series for page in PAGES for chart in page.charts}
    data: dict[str, pd.DataFrame] = {}
    for name in sorted(all_series):
        path = DATA_DIR / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing {path} — run fetch.py first.")
        data[name] = pd.read_csv(path, parse_dates=["date"])
        latest = data[name]["date"].max().strftime("%Y-%m-%d")
        print(f"  -> {name}: {len(data[name])} rows, latest {latest}")

    print("Building pages...")
    for page in PAGES:
        build_page(page, data)

    print("Done.")


if __name__ == "__main__":
    main()
