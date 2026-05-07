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

import json
import pandas as pd
import plotly.graph_objects as go

DATA_DIR = Path("data")
AUTHOR_DISPLAY_NAME = "jayzhaomurray"

# ── Shared formatting constants ───────────────────────────────────────────────
_CHART_HEIGHT  = 260
_CHART_MARGINS = dict(l=48, r=16, t=8, b=32)
_FONT_STACK    = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


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
    charts: list  # ChartSpec | CoreInflationSpec


@dataclass
class CoreInflationSpec:
    """One-off composite chart: headline CPI + core measures range + individual toggles."""
    title: str
    SERIES = ["cpi_all_items", "cpi_trim", "cpi_median", "cpi_common", "cpix", "cpixfet"]


@dataclass
class CpiBreadthSpec:
    """Weighted share of CPI basket (60 depth-3 components) with Y/Y > 3% and < 1%."""
    title: str


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

    if "level"       in available: out["level"]       = v
    if "rolling_20d" in available: out["rolling_20d"] = v.rolling(20).mean()
    if "rolling_4w"  in available: out["rolling_4w"]  = v.rolling(4).mean()
    if "mom"         in available: out["mom"]         = v.pct_change(1) * 100
    if "ar_3m"       in available: out["ar_3m"]       = ((v / v.shift(3)) ** 4 - 1) * 100
    if "qoq"         in available: out["qoq"]         = v.pct_change(1) * 100
    if "qoq_ar"      in available: out["qoq_ar"]      = ((v / v.shift(1)) ** 4 - 1) * 100
    if "yoy"         in available:
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


def _compute_y_ranges(chart: ChartSpec, df: pd.DataFrame) -> dict:
    """Pre-compute y-axis ranges per transform index and time window at build time."""
    transforms = compute_transforms(df, chart.frequency)
    available = FREQ_TRANSFORMS[chart.frequency]
    today = pd.Timestamp.now().normalize()
    result = {}
    for i, key in enumerate(available):
        s = transforms.get(key)
        if s is None:
            continue
        s = s.dropna()
        if s.empty:
            continue
        by_years = {}
        for years in [2, 5, 10]:
            cutoff = today - pd.DateOffset(years=years)
            sub = s[s.index >= cutoff].dropna()
            if sub.empty:
                continue
            ymin, ymax = float(sub.min()), float(sub.max())
            pad = max((ymax - ymin) * 0.08, abs(ymax) * 0.02, 0.01)
            by_years[years] = [round(ymin - pad, 4), round(ymax + pad, 4)]
        result[i] = by_years
    return result


def _resolve_default(chart: ChartSpec) -> str:
    available = FREQ_TRANSFORMS[chart.frequency]
    if chart.default_transform in available:
        return chart.default_transform
    print(
        f"Warning: default_transform='{chart.default_transform}' is not valid "
        f"for frequency='{chart.frequency}'. Falling back to 'level'."
    )
    return "level"


# ── Per-chart figure builder ──────────────────────────────────────────────────

def _build_chart_fig(chart: ChartSpec, df: pd.DataFrame) -> go.Figure:
    transforms = compute_transforms(df, chart.frequency)
    available = FREQ_TRANSFORMS[chart.frequency]
    default = "level" if chart.static else _resolve_default(chart)

    fig = go.Figure()
    for transform_key in available:
        if transform_key not in transforms:
            continue
        s = transforms[transform_key]
        fig.add_trace(go.Scatter(
            x=s.index,
            y=s.values,
            name=transform_key,
            visible=(transform_key == default),
            line=dict(color=chart.color, width=2),
            hovertemplate=_hover_template(transform_key, chart.frequency),
            showlegend=False,
        ))

    fig.update_layout(
        height=_CHART_HEIGHT,
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS,
        font=dict(family=_FONT_STACK),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False)

    return fig


# ── HTML button helpers ───────────────────────────────────────────────────────

def _range_buttons_html(div_id: str) -> str:
    out = '<div class="btn-group" id="rb-' + div_id + '">'
    for label, years in [("2Y", 2), ("5Y", 5), ("10Y", 10), ("Max", None)]:
        active = " active" if years is None else ""
        y_arg = "null" if years is None else str(years)
        out += (
            '<button class="ctrl-btn' + active + '"'
            ' onclick="rangeClick(this,\'' + div_id + '\',' + y_arg + ')">'
            + label + "</button>"
        )
    out += "</div>"
    return out


def _transform_buttons_html(chart: ChartSpec, div_id: str) -> str:
    if chart.static:
        return ""
    available = FREQ_TRANSFORMS[chart.frequency]
    if len(available) <= 1:
        return ""
    default = _resolve_default(chart)
    out = '<div class="btn-group" id="xb-' + div_id + '">'
    for i, transform_key in enumerate(available):
        label = BUTTON_LABELS.get(transform_key, transform_key)
        active = " active" if transform_key == default else ""
        out += (
            '<button class="ctrl-btn' + active + '"'
            ' onclick="xformClick(this,\'' + div_id + '\',' + str(i) + ')">'
            + label + "</button>"
        )
    out += "</div>"
    return out


# ── Chart panel HTML ──────────────────────────────────────────────────────────

def _chart_panel_html(chart: ChartSpec, df: pd.DataFrame, chart_idx: int,
                      include_plotlyjs: bool) -> str:
    div_id = "chart-" + str(chart_idx)
    fig = _build_chart_fig(chart, df)
    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    range_btns = _range_buttons_html(div_id)
    xform_btns = _transform_buttons_html(chart, div_id)

    controls = '<div class="chart-controls">'
    if xform_btns:
        controls += xform_btns + '<div class="btn-sep"></div>'
    controls += range_btns + "</div>"

    return (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        '<div class="chart-title">' + chart.title + "</div>"
        + controls +
        "</div>"
        + plotly_frag +
        "</div>\n"
    )


# ── Core inflation one-off chart ─────────────────────────────────────────────

def _build_core_inflation_panel(chart: "CoreInflationSpec", data: dict,
                                chart_idx: int, include_plotlyjs: bool) -> tuple:
    div_id = "chart-" + str(chart_idx)

    headline_yoy = (
        data["cpi_all_items"].set_index("date")["value"]
        .pct_change(12) * 100
    )
    trim    = data["cpi_trim"].set_index("date")["value"]
    median  = data["cpi_median"].set_index("date")["value"]
    common  = data["cpi_common"].set_index("date")["value"]
    cpix    = data["cpix"].set_index("date")["value"]
    cpixfet = data["cpixfet"].set_index("date")["value"]

    core_df  = pd.concat([trim, median, common, cpix, cpixfet], axis=1)
    range_max = core_df.max(axis=1).dropna()
    range_min = core_df.min(axis=1).dropna()

    fig = go.Figure()

    # Trace 0: range lower (no fill, invisible line)
    fig.add_trace(go.Scatter(
        x=range_min.index, y=range_min.values,
        line=dict(width=0), fill=None,
        showlegend=False, hoverinfo="skip", visible=True,
    ))
    # Trace 1: range upper (fill to lower = shaded band)
    fig.add_trace(go.Scatter(
        x=range_max.index, y=range_max.values,
        fill="tonexty", fillcolor="rgba(180,180,180,0.35)",
        line=dict(width=0),
        showlegend=False, hoverinfo="skip", visible=True,
    ))
    # Trace 2: headline CPI Y/Y (always visible)
    fig.add_trace(go.Scatter(
        x=headline_yoy.index, y=headline_yoy.values,
        line=dict(color="#1f6aa5", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>Total CPI</extra>",
        showlegend=False, visible=True,
    ))
    # Trace 3: CPI-trim (hidden by default)
    fig.add_trace(go.Scatter(
        x=trim.index, y=trim.values,
        line=dict(color="#444444", width=1.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>CPI-trim</extra>",
        showlegend=False, visible=False,
    ))
    # Trace 4: CPI-median (hidden by default)
    fig.add_trace(go.Scatter(
        x=median.index, y=median.values,
        line=dict(color="#888888", width=1.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>CPI-median</extra>",
        showlegend=False, visible=False,
    ))

    fig.add_hline(y=2, line_color="#555", line_width=1)
    fig.update_layout(
        height=_CHART_HEIGHT, showlegend=False,
        paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS, font=dict(family=_FONT_STACK),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False,
                     ticksuffix="%")

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    controls = (
        '<div class="chart-controls">' + _range_buttons_html(div_id) + '</div>'
    )

    def _swatch_line(color: str) -> str:
        return (
            '<span style="display:inline-block;width:22px;height:2.5px;'
            'background:' + color + ';border-radius:1px;vertical-align:middle;'
            'margin-right:5px"></span>'
        )

    swatch_range = (
        '<span style="display:inline-block;width:22px;height:11px;'
        'background:rgba(180,180,180,0.45);border-radius:2px;vertical-align:middle;'
        'margin-right:5px"></span>'
    )

    legend = (
        '<div class="chart-legend">'
        + '<button class="legend-item active"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[2])">'
        + _swatch_line("#1f6aa5") + 'Total CPI</button>'
        + '<button class="legend-item"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[3])">'
        + _swatch_line("#444444") + 'CPI-trim</button>'
        + '<button class="legend-item"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[4])">'
        + _swatch_line("#888888") + 'CPI-median</button>'
        + '<button class="legend-item active"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[0,1])">'
        + swatch_range + 'Range of core measures</button>'
        + '</div>'
    )

    html = (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        '<div class="chart-title">' + chart.title + '</div>'
        + controls + '</div>'
        + plotly_frag
        + legend + '</div>\n'
    )

    # Pre-compute y-ranges for date range buttons
    today = pd.Timestamp.now().normalize()
    all_yoy = pd.concat([
        headline_yoy.rename("headline"), trim.rename("trim"),
        median.rename("median"), common.rename("common"),
        cpix.rename("cpix"), cpixfet.rename("cpixfet"),
    ], axis=1)
    yr_dict: dict = {}
    for years in [2, 5, 10]:
        cutoff = today - pd.DateOffset(years=years)
        vals = all_yoy[all_yoy.index >= cutoff].stack().dropna()
        if vals.empty:
            continue
        ymin, ymax = float(vals.min()), float(vals.max())
        pad = max((ymax - ymin) * 0.08, 0.1)
        yr_dict[years] = [round(ymin - pad, 4), round(ymax + pad, 4)]
    # Store under all trace indices so lookup works regardless of which is first visible
    y_ranges = {str(i): yr_dict for i in range(5)}

    return html, y_ranges


# ── CPI breadth chart ────────────────────────────────────────────────────────

def _build_cpi_breadth_panel(chart: "CpiBreadthSpec", data: dict,
                              chart_idx: int, include_plotlyjs: bool) -> tuple:
    div_id = "chart-" + str(chart_idx)

    with open(DATA_DIR / "cpi_breadth_mapping.json") as f:
        mapping = json.load(f)
    raw = {m["name"]: m["wt_value"] for m in mapping if m["wt_value"] is not None}
    total = sum(raw.values())
    weights = pd.Series({name: w / total for name, w in raw.items()})

    comp_df = data["cpi_components"]
    yoy_df = comp_df.pct_change(12) * 100
    w = weights.reindex(yoy_df.columns).fillna(0)

    above_3 = yoy_df.gt(3).multiply(w, axis=1).sum(axis=1) * 100
    below_1 = yoy_df.lt(1).multiply(w, axis=1).sum(axis=1) * 100

    valid = yoy_df.notna().all(axis=1)
    above_3 = above_3[valid]
    below_1 = below_1[valid]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=above_3.index, y=above_3.values,
        name="above_3", line=dict(color="#e74c3c", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>Share above 3%</extra>",
        showlegend=False, visible=True,
    ))
    fig.add_trace(go.Scatter(
        x=below_1.index, y=below_1.values,
        name="below_1", line=dict(color="#2980b9", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>Share below 1%</extra>",
        showlegend=False, visible=True,
    ))
    fig.update_layout(
        height=_CHART_HEIGHT, showlegend=False,
        paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS, font=dict(family=_FONT_STACK),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False, ticksuffix="%")

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    controls = '<div class="chart-controls">' + _range_buttons_html(div_id) + '</div>'

    def _swatch(color: str) -> str:
        return (
            '<span style="display:inline-block;width:22px;height:2.5px;'
            'background:' + color + ';border-radius:1px;vertical-align:middle;'
            'margin-right:5px"></span>'
        )

    legend = (
        '<div class="chart-legend">'
        + '<button class="legend-item active"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[0])">'
        + _swatch("#e74c3c") + 'Share above 3%</button>'
        + '<button class="legend-item active"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[1])">'
        + _swatch("#2980b9") + 'Share below 1%</button>'
        + '</div>'
    )

    html = (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        '<div class="chart-title">' + chart.title + '</div>'
        + controls + '</div>'
        + plotly_frag + legend + '</div>\n'
    )

    today = pd.Timestamp.now().normalize()
    combined = pd.concat([above_3, below_1], axis=1)
    yr_dict: dict = {}
    for years in [2, 5, 10]:
        cutoff = today - pd.DateOffset(years=years)
        vals = combined[combined.index >= cutoff].stack().dropna()
        if vals.empty:
            continue
        ymin, ymax = float(vals.min()), float(vals.max())
        pad = max((ymax - ymin) * 0.08, 1.0)
        yr_dict[years] = [round(max(ymin - pad, 0), 2), round(min(ymax + pad, 100), 2)]
    y_ranges = {str(i): yr_dict for i in range(2)}

    return html, y_ranges


# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """\
  *, *::before, *::after { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 720px;
    margin: 0 auto;
    padding: 36px 20px 64px;
    background: #ffffff;
    color: #1a1a1a;
  }
  .site-header { margin-bottom: 10px; }
  .site-header h1 { font-size: 1.45rem; font-weight: 700; margin: 0 0 6px; }
  .site-header .tagline { font-size: 0.88rem; color: #666; margin: 0 0 4px; }
  .site-header .updated { font-size: 0.78rem; color: #bbb; margin: 0; }

  .global-controls {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 20px;
  }
  .gc-label { font-size: 0.75rem; color: #aaa; }

  .chart-panel { margin-bottom: 24px; }
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 2px;
  }
  .chart-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #222;
    flex: 1;
    min-width: 0;
  }
  .chart-controls {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;
  }
  .btn-group { display: flex; }
  .btn-sep { width: 8px; }

  .ctrl-btn {
    font-size: 10px;
    line-height: 1;
    padding: 3px 7px;
    border: 1px solid #ddd;
    border-right-width: 0;
    background: #f5f5f5;
    color: #555;
    cursor: pointer;
    font-family: inherit;
    white-space: nowrap;
    transition: background 0.1s;
  }
  .ctrl-btn:first-child { border-radius: 3px 0 0 3px; }
  .ctrl-btn:last-child  { border-radius: 0 3px 3px 0; border-right-width: 1px; }
  .btn-group .ctrl-btn:only-child { border-radius: 3px; border-right-width: 1px; }
  .ctrl-btn:hover { background: #e8e8e8; }
  .ctrl-btn.active { background: #dce9f7; border-color: #aac4e8; color: #1a5276; }
  .ctrl-btn.active + .ctrl-btn { border-left-color: #aac4e8; }

  .chart-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 14px;
    padding: 7px 2px 2px;
    border-top: 1px solid #eee;
    margin-top: 2px;
  }
  .legend-item {
    display: inline-flex;
    align-items: center;
    font-size: 0.75rem;
    color: #555;
    cursor: pointer;
    background: none;
    border: none;
    padding: 3px 5px;
    border-radius: 3px;
    opacity: 0.35;
    transition: opacity 0.15s, background 0.1s;
    font-family: inherit;
  }
  .legend-item.active { opacity: 1; }
  .legend-item:hover { background: #f0f0f0; }

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


# ── JavaScript ────────────────────────────────────────────────────────────────

_JS_TEMPLATE = """\
<script>
var ALL_CHARTS = {chart_ids_js};
var Y_RANGES = {y_ranges_js};

function applyRange(chartId, years) {
  var div = document.getElementById(chartId);
  if (!div) return;
  if (years === null) {
    Plotly.relayout(div, {"xaxis.autorange": true, "yaxis.autorange": true});
  } else {
    var e = new Date(), s = new Date(e);
    s.setFullYear(s.getFullYear() - years);
    var update = {
      "xaxis.range": [s.toISOString().slice(0, 10), e.toISOString().slice(0, 10)],
      "xaxis.autorange": false,
      "yaxis.autorange": false
    };
    var traceIdx = 0;
    for (var i = 0; i < (div.data || []).length; i++) {
      if (div.data[i].visible !== false) { traceIdx = i; break; }
    }
    var cr = Y_RANGES[chartId];
    if (cr && cr[String(traceIdx)] && cr[String(traceIdx)][String(years)]) {
      update["yaxis.range"] = cr[String(traceIdx)][String(years)];
    }
    Plotly.relayout(div, update);
  }
}

function rangeClick(btn, chartId, years) {
  btn.closest(".btn-group").querySelectorAll(".ctrl-btn").forEach(function(b) {
    b.classList.remove("active");
  });
  btn.classList.add("active");
  applyRange(chartId, years);
}

function xformClick(btn, chartId, idx) {
  var div = document.getElementById(chartId);
  btn.closest(".btn-group").querySelectorAll(".ctrl-btn").forEach(function(b) {
    b.classList.remove("active");
  });
  btn.classList.add("active");
  Plotly.restyle(div, {visible: div.data.map(function(_, i) { return i === idx; })});
  var rb = document.getElementById("rb-" + chartId);
  if (rb) {
    var activeRangeBtn = rb.querySelector(".ctrl-btn.active");
    if (activeRangeBtn) {
      var m = activeRangeBtn.getAttribute("onclick").match(/,(\\w+)\\)$/);
      if (m && m[1] !== "null") applyRange(chartId, parseInt(m[1]));
    }
  }
}

function toggleTrace(btn, chartId, indices) {
  var div = document.getElementById(chartId);
  if (!div) return;
  var isActive = btn.classList.contains("active");
  btn.classList.toggle("active");
  var vis = div.data.map(function(t) { return t.visible !== false; });
  indices.forEach(function(i) { vis[i] = !isActive; });
  Plotly.restyle(div, {visible: vis});
}

function gcRange(years, btn) {
  btn.closest(".btn-group").querySelectorAll(".ctrl-btn").forEach(function(b) {
    b.classList.remove("active");
  });
  btn.classList.add("active");
  ALL_CHARTS.forEach(function(id) {
    var rb = document.getElementById("rb-" + id);
    if (rb) {
      rb.querySelectorAll(".ctrl-btn").forEach(function(b) { b.classList.remove("active"); });
      rb.querySelectorAll(".ctrl-btn").forEach(function(b) {
        var m = b.getAttribute("onclick").match(/,(\\w+)\\)$/);
        if (m && (years === null ? m[1] === "null" : m[1] === String(years))) {
          b.classList.add("active");
        }
      });
    }
    applyRange(id, years);
  });
}
</script>
"""


# ── Page assembly ─────────────────────────────────────────────────────────────

def _assemble_page(page: PageSpec, chart_panels: list[str],
                   chart_ids: list[str], last_updated: str,
                   y_ranges: dict) -> str:
    chart_ids_js = "[" + ",".join('"' + cid + '"' for cid in chart_ids) + "]"
    y_ranges_js = json.dumps(y_ranges)
    js = _JS_TEMPLATE.replace("{chart_ids_js}", chart_ids_js).replace("{y_ranges_js}", y_ranges_js)

    header = (
        '<div class="site-header">'
        "<h1>" + page.title + "</h1>"
        '<p class="tagline">' + page.tagline + "</p>"
        '<p class="updated">Last updated: ' + last_updated + "</p>"
        "</div>\n"
    )

    gc = (
        '<div class="global-controls">'
        '<span class="gc-label">All charts &mdash;</span>'
        '<div class="btn-group" id="gc-range">'
        '<button class="ctrl-btn" onclick="gcRange(2,this)">2Y</button>'
        '<button class="ctrl-btn" onclick="gcRange(5,this)">5Y</button>'
        '<button class="ctrl-btn" onclick="gcRange(10,this)">10Y</button>'
        '<button class="ctrl-btn active" onclick="gcRange(null,this)">Max</button>'
        "</div></div>\n"
    )

    about = (
        '<div class="about">'
        "<strong>About this dashboard</strong> &mdash; "
        'Built by <a href="https://github.com/' + AUTHOR_DISPLAY_NAME + '">'
        + AUTHOR_DISPLAY_NAME + "</a> using public data from "
        '<a href="https://www150.statcan.gc.ca">Statistics Canada</a> and the '
        '<a href="https://www.bankofcanada.ca/valet/docs">Bank of Canada Valet API</a>. '
        'Raw data available as CSV in the '
        '<a href="https://github.com/' + AUTHOR_DISPLAY_NAME + '/boc-tracker/tree/main/data">'
        "GitHub repository</a>."
        "</div>\n"
    )

    return (
        "<!DOCTYPE html>\n<html>\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>" + page.title + "</title>\n"
        "<style>\n" + _CSS + "</style>\n"
        "</head>\n<body>\n"
        + header + gc
        + "".join(chart_panels)
        + about + js
        + "</body>\n</html>\n"
    )


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
            CoreInflationSpec(
                title="Core Inflation Measures — Canada (Year-over-year %)",
            ),
            CpiBreadthSpec(
                title="CPI Breadth — Share of Basket with Y/Y Inflation Above 3% or Below 1%",
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


# ── Main ──────────────────────────────────────────────────────────────────────

def build_page(page: PageSpec, data: dict[str, pd.DataFrame]) -> None:
    chart_ids = ["chart-" + str(i) for i in range(len(page.charts))]
    panels = []
    y_ranges: dict = {}
    for i, chart in enumerate(page.charts):
        cid = "chart-" + str(i)
        if isinstance(chart, CoreInflationSpec):
            panel, cyr = _build_core_inflation_panel(chart, data, i, i == 0)
            panels.append(panel)
            y_ranges[cid] = cyr
        elif isinstance(chart, CpiBreadthSpec):
            panel, cyr = _build_cpi_breadth_panel(chart, data, i, i == 0)
            panels.append(panel)
            y_ranges[cid] = cyr
        else:
            df = data[chart.series]
            panels.append(_chart_panel_html(chart, df, i, include_plotlyjs=(i == 0)))
            y_ranges[cid] = _compute_y_ranges(chart, df)

    last_updated = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    html = _assemble_page(page, panels, chart_ids, last_updated, y_ranges)

    with open(page.output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  -> {page.output_file}")


def main():
    print("Loading data...")
    all_series: set[str] = set()
    has_breadth = False
    for page in PAGES:
        for chart in page.charts:
            if isinstance(chart, CoreInflationSpec):
                all_series.update(CoreInflationSpec.SERIES)
            elif isinstance(chart, CpiBreadthSpec):
                has_breadth = True
            else:
                all_series.add(chart.series)
    data: dict[str, pd.DataFrame] = {}
    for name in sorted(all_series):
        path = DATA_DIR / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing {path} -- run fetch.py first.")
        data[name] = pd.read_csv(path, parse_dates=["date"])
        latest = data[name]["date"].max().strftime("%Y-%m-%d")
        print(f"  -> {name}: {len(data[name])} rows, latest {latest}")
    if has_breadth:
        path = DATA_DIR / "cpi_components.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing {path} -- run fetch.py first.")
        data["cpi_components"] = pd.read_csv(path, parse_dates=["date"], index_col="date")
        print(f"  -> cpi_components: {len(data['cpi_components'])} months × {len(data['cpi_components'].columns)} components")

    print("Building pages...")
    for page in PAGES:
        build_page(page, data)

    print("Done.")


if __name__ == "__main__":
    main()
