"""
Read saved CSV data and build HTML dashboard pages.

Run fetch.py first to download data, then run this any time you change
chart layout, styling, or the PAGES config below.

Run:    python build.py
Output: index.html  (plus any other files defined in PAGES)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone

import json
import math
import pandas as pd
import plotly.graph_objects as go

BLURBS_PATH = Path("data/blurbs.json")

SECTION_HEADINGS = {
    "policy":    "Monetary Policy",
    "inflation": "Inflation",
    "labour":    "Labour Market",
    "financial": "Financial Conditions",
}

DATA_DIR = Path("data")
AUTHOR_DISPLAY_NAME = "jayzhaomurray"

# ── Shared formatting constants ───────────────────────────────────────────────
_CHART_HEIGHT  = 260
_CHART_MARGINS = dict(l=48, r=16, t=8, b=32)
_FONT_STACK    = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def _title_block_html(title: str, unit: str, div_id: str) -> str:
    """Build the title-block HTML: chart title with unit label as a subtitle
    underneath. The subtitle div has id `unit-{div_id}` so JS can update its
    text on transform change for charts whose units differ across transforms."""
    subtitle = (
        '<div class="chart-subtitle" id="unit-' + div_id + '">' + unit + '</div>'
        if unit else ''
    )
    return (
        '<div class="chart-title-block">'
        '<div class="chart-title">' + title + '</div>'
        + subtitle +
        '</div>'
    )


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class ChartSpec:
    series: str               # matches CSV filename in data/ without .csv
    title: str                # panel heading
    frequency: str            # daily | weekly | monthly | quarterly | annual | irregular
    color: str                # hex line color
    static: bool = False      # if True, no transform buttons shown
    default_transform: str = "level"
    default_years: int | None = None  # initial date range; None means Max
    footnote: str = ""
    unit_label: str = "%"     # text shown in top-left of plot area (e.g. %, CAD per USD)
    hover_decimals: int = 2   # precision in hover tooltip — see chart_style_guide.md §5


@dataclass
class PageSpec:
    title: str
    tagline: str
    output_file: str
    charts: list  # ChartSpec | CoreInflationSpec | ...
    # Map chart-index -> section_id; renders a heading + blurb above that chart.
    sections: dict = field(default_factory=dict)


@dataclass
class CoreInflationSpec:
    """One-off composite chart: headline CPI + core measures range + individual toggles."""
    title: str
    footnote: str = ""
    default_years: int | None = None
    SERIES = ["cpi_all_items", "cpi_trim", "cpi_median", "cpi_common", "cpix", "cpixfet"]


@dataclass
class CpiBreadthSpec:
    """Weighted share of CPI basket (60 depth-3 components) with Y/Y > 3% and < 1%."""
    title: str
    footnote: str = ""


@dataclass
class LineConfig:
    series: str          # CSV filename without .csv
    label: str           # legend label
    color: str           # hex color
    visible: bool = True
    smooth: bool = True  # False = keep raw data in smooth mode (e.g. monthly series on a daily chart)


@dataclass
class WageSpec:
    """Composite chart: range band across wage measures + individual toggles + Services CPI overlay."""
    title: str
    footnote: str = ""
    default_years: int | None = 10
    SERIES = ["lfs_wages_all", "lfs_wages_permanent", "seph_earnings", "lfs_micro", "cpi_services"]


@dataclass
class CpiLine:
    series: str          # CSV filename without .csv
    label: str           # legend label
    color: str           # hex color
    visible: bool = False


@dataclass
class CpiSpec:
    """CPI chart with multiple series (headline + breakdown), transform buttons, legend toggle.
    Each line gets each transform computed; visibility = (active transform) AND (legend on)."""
    title: str
    lines: list                       # list[CpiLine]
    footnote: str = ""
    default_transform: str = "yoy"    # one of: level, mom, ar_3m, yoy
    default_years: int | None = 10

    @property
    def SERIES(self):
        return [l.series for l in self.lines]


@dataclass
class MultiLineSpec:
    """Generic multi-line chart with per-line toggle buttons."""
    title: str
    lines: list               # list[LineConfig]
    ticksuffix: str = "%"     # used in HOVER only (axis ticks are bare per style guide)
    hoverformat: str = ".2f"
    default_years: int | None = None
    line_shape: str = "linear"          # "linear" | "hv" (step)
    smooth_window: int | None = None    # rolling average window; None = no smooth button
    date_fmt: str = "%b %Y"            # hover date format
    footnote: str = ""
    ymin: float | None = None           # hard floor for y-axis (pre-computed ranges + autorange)
    unit_label: str = "%"               # text shown in top-left of plot area


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


def _hover_template(transform: str, frequency: str, decimals: int = 2) -> str:
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
    return f"%{{x|{date_fmt}}}<br>%{{y:.{decimals}f}}{suffix}<extra></extra>"


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


def _ytick_format(vals: pd.Series) -> str:
    """Minimum decimal places that remain consistent across all y-axis ticks."""
    v = vals.dropna()
    if v.empty:
        return ".1f"
    span = float(v.max() - v.min())
    step = span / 4 if span > 0 else 1.0   # ~5 ticks → 4 intervals
    if step >= 1.0:
        return ".0f"
    elif step >= 0.1:
        return ".1f"
    else:
        return ".2f"


def _nice_dtick(ymin: float, ymax: float, target: int = 5) -> float:
    """Round-number tick interval giving at least target ticks over [ymin, ymax].
    Rounds DOWN to the nearest nice step so tick count stays >= target."""
    span = ymax - ymin
    if span <= 0:
        return 1.0
    rough = span / target
    mag = 10 ** math.floor(math.log10(rough))
    norm = rough / mag
    # Round DOWN: pick the largest nice number that is <= norm
    if norm >= 5.0:   nice = 5.0
    elif norm >= 2.5: nice = 2.5
    elif norm >= 2.0: nice = 2.0
    elif norm >= 1.0: nice = 1.0
    else:             nice = 0.5
    return nice * mag


def _dtick_format(dtick: float) -> str:
    """Tickformat string whose precision matches dtick (so all ticks show the same decimals)."""
    s = f"{dtick:.10f}".rstrip("0")
    if "." not in s or s.endswith("."):
        return ".0f"
    decimals = len(s.split(".")[1])
    return f".{min(decimals, 2)}f"


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
            hovertemplate=_hover_template(transform_key, chart.frequency, chart.hover_decimals),
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

    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False, nticks=7)

    return fig


# ── HTML button helpers ───────────────────────────────────────────────────────

def _range_buttons_html(div_id: str, default_years=None) -> str:
    out = '<div class="btn-group" id="rb-' + div_id + '">'
    for label, years in [("2Y", 2), ("5Y", 5), ("10Y", 10), ("Max", None)]:
        active = " active" if years == default_years else ""
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

    range_btns = _range_buttons_html(div_id, default_years=chart.default_years)
    xform_btns = _transform_buttons_html(chart, div_id)

    controls = '<div class="chart-controls">'
    if xform_btns:
        controls += xform_btns + '<div class="btn-sep"></div>'
    controls += range_btns + "</div>"

    footnote_html = (
        '<div class="chart-footnote">' + chart.footnote + '</div>'
        if chart.footnote else ""
    )
    return (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        + _title_block_html(chart.title, chart.unit_label, div_id)
        + controls +
        "</div>"
        + plotly_frag
        + footnote_html
        + "</div>\n"
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
        line=dict(color="#1565c0", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>Total CPI</extra>",
        showlegend=False, visible=True,
    ))
    # Trace 3: CPI-trim (hidden by default)
    fig.add_trace(go.Scatter(
        x=trim.index, y=trim.values,
        line=dict(color="#546e7a", width=1.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>CPI-trim</extra>",
        showlegend=False, visible=False,
    ))
    # Trace 4: CPI-median (hidden by default)
    fig.add_trace(go.Scatter(
        x=median.index, y=median.values,
        line=dict(color="#78909c", width=1.5),
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
    _ci_today = pd.Timestamp.now().normalize()
    _ci_cutoff = _ci_today - pd.DateOffset(years=chart.default_years or 10)
    _ci_all = pd.concat([headline_yoy.rename("a"), trim.rename("b"), median.rename("c"),
                         common.rename("d"), cpix.rename("e"), cpixfet.rename("f")], axis=1)
    _ci_ref = _ci_all[_ci_all.index >= _ci_cutoff].stack().dropna()
    if not _ci_ref.empty:
        _ci_min, _ci_max = float(_ci_ref.min()), float(_ci_ref.max())
        _ci_pad = max((_ci_max - _ci_min) * 0.08, 0.1)
        _ci_dtick = _nice_dtick(_ci_min - _ci_pad, _ci_max + _ci_pad)
        _ci_tickfmt = _dtick_format(_ci_dtick)
    else:
        _ci_dtick, _ci_tickfmt = 1.0, ".0f"
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False,
                     tick0=0, dtick=_ci_dtick, tickformat=_ci_tickfmt)

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    controls = (
        '<div class="chart-controls">' + _range_buttons_html(div_id, default_years=chart.default_years) + '</div>'
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
        + _swatch_line("#1565c0") + 'Total CPI</button>'
        + '<button class="legend-item"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[3])">'
        + _swatch_line("#546e7a") + 'CPI-trim</button>'
        + '<button class="legend-item"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[4])">'
        + _swatch_line("#78909c") + 'CPI-median</button>'
        + '<button class="legend-item active"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[0,1])">'
        + swatch_range + 'Range of core measures</button>'
        + '</div>'
    )

    footnote_html = (
        '<div class="chart-footnote">' + chart.footnote + '</div>'
        if chart.footnote else ""
    )
    html = (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        + _title_block_html(chart.title, "%", div_id)
        + controls + '</div>'
        + plotly_frag
        + legend
        + footnote_html + '</div>\n'
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

    # Drop components whose data starts after Jan 1995 — they'd break the 1996 display
    # cutoff after the 12-month Y/Y lag. Dropped weight is absorbed by re-normalising.
    active_cols = [c for c in comp_df.columns
                   if comp_df[c].first_valid_index() <= pd.Timestamp("1995-01-01")]
    comp_df = comp_df[active_cols]

    yoy_df = comp_df.pct_change(12) * 100
    w = weights.reindex(yoy_df.columns).fillna(0)
    w = w / w.sum()  # re-normalise after dropping late-starting components

    above_3_raw = yoy_df.gt(3).multiply(w, axis=1).sum(axis=1) * 100
    below_1_raw = yoy_df.lt(1).multiply(w, axis=1).sum(axis=1) * 100

    valid = yoy_df.notna().all(axis=1)
    above_3_raw = above_3_raw[valid]
    below_1_raw = below_1_raw[valid]

    # Deviation from 1996–2019 historical average (pre-COVID, matches display start)
    ha_above = above_3_raw["1996":"2019"].mean()
    ha_below = below_1_raw["1996":"2019"].mean()
    above_3 = (above_3_raw - ha_above).loc["1996":]
    below_1 = (below_1_raw - ha_below).loc["1996":]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=above_3.index, y=above_3.values,
        name="above_3", line=dict(color="#c62828", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f} pp<extra>Above 3%</extra>",
        showlegend=False, visible=True,
    ))
    fig.add_trace(go.Scatter(
        x=below_1.index, y=below_1.values,
        name="below_1", line=dict(color="#1565c0", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f} pp<extra>Below 1%</extra>",
        showlegend=False, visible=True,
    ))
    fig.add_hline(y=0, line_color="#aaa", line_width=1)
    fig.update_layout(
        height=_CHART_HEIGHT, showlegend=False,
        paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS, font=dict(family=_FONT_STACK),
    )
    _cb_today = pd.Timestamp.now().normalize()
    _cb_cutoff = _cb_today - pd.DateOffset(years=10)
    _cb_ref = pd.concat([above_3, below_1], axis=1).loc[_cb_cutoff:].stack().dropna()
    if not _cb_ref.empty:
        _cb_min, _cb_max = float(_cb_ref.min()), float(_cb_ref.max())
        _cb_pad = max((_cb_max - _cb_min) * 0.08, 1.0)
        _cb_dtick = _nice_dtick(_cb_min - _cb_pad, _cb_max + _cb_pad)
        _cb_tickfmt = _dtick_format(_cb_dtick)
    else:
        _cb_dtick, _cb_tickfmt = 5.0, ".0f"
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False,
                     tickformat=_cb_tickfmt, tick0=0, dtick=_cb_dtick)

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    controls = '<div class="chart-controls">' + _range_buttons_html(div_id, default_years=10) + '</div>'

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
        + _swatch("#c62828") + 'Share above 3%</button>'
        + '<button class="legend-item active"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[1])">'
        + _swatch("#1565c0") + 'Share below 1%</button>'
        + '</div>'
    )

    footnote_html = (
        '<div class="chart-footnote">' + chart.footnote + '</div>'
        if chart.footnote else ""
    )
    html = (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        + _title_block_html(chart.title, "pp", div_id)
        + controls + '</div>'
        + plotly_frag
        + legend
        + footnote_html + '</div>\n'
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
        yr_dict[years] = [round(ymin - pad, 2), round(ymax + pad, 2)]
    y_ranges = {str(i): yr_dict for i in range(2)}

    return html, y_ranges


# ── Wage growth chart ────────────────────────────────────────────────────────

def _build_wage_panel(chart: "WageSpec", data: dict,
                      chart_idx: int, include_plotlyjs: bool) -> tuple:
    div_id = "chart-" + str(chart_idx)

    # Y/Y % for level series; lfs_micro is already Y/Y from BoC Valet
    lfs_all   = data["lfs_wages_all"].set_index("date")["value"].pct_change(12) * 100
    lfs_perm  = data["lfs_wages_permanent"].set_index("date")["value"].pct_change(12) * 100
    seph      = data["seph_earnings"].set_index("date")["value"].pct_change(12) * 100
    lfs_micro = data["lfs_micro"].set_index("date")["value"]
    svc_cpi   = data["cpi_services"].set_index("date")["value"].pct_change(12) * 100

    # Clip Services CPI to the earliest date any wage measure has valid data
    wage_start = min(
        s.first_valid_index()
        for s in [lfs_all, lfs_perm, seph, lfs_micro]
        if s.first_valid_index() is not None
    )
    svc_cpi = svc_cpi[svc_cpi.index >= wage_start]

    # Range band: min/max across the four wage measures (NaN-tolerant)
    wage_df   = pd.concat([lfs_all, lfs_perm, seph, lfs_micro], axis=1, sort=True)
    range_max = wage_df.max(axis=1).dropna()
    range_min = wage_df.min(axis=1).dropna()

    fig = go.Figure()
    # Trace 0: range lower (no fill)
    fig.add_trace(go.Scatter(
        x=range_min.index, y=range_min.values,
        line=dict(width=0), fill=None,
        showlegend=False, hoverinfo="skip", visible=True,
    ))
    # Trace 1: range upper (fills to trace 0)
    fig.add_trace(go.Scatter(
        x=range_max.index, y=range_max.values,
        fill="tonexty", fillcolor="rgba(180,180,180,0.35)",
        line=dict(width=0),
        showlegend=False, hoverinfo="skip", visible=True,
    ))
    # Trace 2: LFS all employees (visible)
    fig.add_trace(go.Scatter(
        x=lfs_all.index, y=lfs_all.values,
        line=dict(color="#1565c0", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>LFS All Employees</extra>",
        showlegend=False, visible=True,
    ))
    # Trace 3: LFS permanent employees (hidden)
    fig.add_trace(go.Scatter(
        x=lfs_perm.index, y=lfs_perm.values,
        line=dict(color="#546e7a", width=1.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>LFS Permanent</extra>",
        showlegend=False, visible=False,
    ))
    # Trace 4: SEPH average weekly earnings (hidden)
    fig.add_trace(go.Scatter(
        x=seph.index, y=seph.values,
        line=dict(color="#78909c", width=1.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>SEPH Weekly Earnings</extra>",
        showlegend=False, visible=False,
    ))
    # Trace 5: LFS-Micro composition-adjusted (hidden)
    fig.add_trace(go.Scatter(
        x=lfs_micro.index, y=lfs_micro.values,
        line=dict(color="#4a148c", width=1.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>LFS-Micro (BoC)</extra>",
        showlegend=False, visible=False,
    ))
    # Trace 6: Services CPI Y/Y (visible by default — overlay for wage-price context)
    fig.add_trace(go.Scatter(
        x=svc_cpi.index, y=svc_cpi.values,
        line=dict(color="#c62828", width=1.5, dash="dot"),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>Services CPI</extra>",
        showlegend=False, visible=True,
    ))

    fig.add_hline(y=0, line_color="#aaa", line_width=1)
    fig.update_layout(
        height=_CHART_HEIGHT, showlegend=False,
        paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS, font=dict(family=_FONT_STACK),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    _wg_today = pd.Timestamp.now().normalize()
    _wg_cutoff = _wg_today - pd.DateOffset(years=chart.default_years or 10)
    _wg_ref = pd.concat([lfs_all.rename("a"), lfs_perm.rename("b"), seph.rename("c"),
                         lfs_micro.rename("d"), svc_cpi.rename("e")], axis=1, sort=True)
    _wg_ref = _wg_ref[_wg_ref.index >= _wg_cutoff].stack().dropna()
    if not _wg_ref.empty:
        _wg_min, _wg_max = float(_wg_ref.min()), float(_wg_ref.max())
        _wg_pad = max((_wg_max - _wg_min) * 0.08, 0.1)
        _wg_dtick = _nice_dtick(_wg_min - _wg_pad, _wg_max + _wg_pad)
        _wg_tickfmt = _dtick_format(_wg_dtick)
    else:
        _wg_dtick, _wg_tickfmt = 1.0, ".0f"
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False,
                     tick0=0, dtick=_wg_dtick, tickformat=_wg_tickfmt)

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    controls = '<div class="chart-controls">' + _range_buttons_html(div_id, default_years=chart.default_years) + '</div>'

    def _swatch_line(color: str, dash: bool = False) -> str:
        border = "border-top: 2px dashed " + color + ";" if dash else ""
        bg = "" if dash else "background:" + color + ";"
        return (
            '<span style="display:inline-block;width:22px;height:2.5px;'
            + bg + border +
            'border-radius:1px;vertical-align:middle;margin-right:5px"></span>'
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
        + _swatch_line("#1565c0") + 'LFS All Employees</button>'
        + '<button class="legend-item"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[3])">'
        + _swatch_line("#546e7a") + 'LFS Permanent</button>'
        + '<button class="legend-item"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[4])">'
        + _swatch_line("#78909c") + 'SEPH Weekly Earnings</button>'
        + '<button class="legend-item"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[5])">'
        + _swatch_line("#4a148c") + 'LFS-Micro (BoC)</button>'
        + '<button class="legend-item active"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[6])">'
        + _swatch_line("#c62828", dash=True) + 'Services CPI</button>'
        + '<button class="legend-item active"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[0,1])">'
        + swatch_range + 'Range</button>'
        + '</div>'
    )

    footnote_html = (
        '<div class="chart-footnote">' + chart.footnote + '</div>'
        if chart.footnote else ""
    )
    html = (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        + _title_block_html(chart.title, "%", div_id)
        + controls + '</div>'
        + plotly_frag
        + legend
        + footnote_html + '</div>\n'
    )

    # Pre-compute y-ranges for all 6 traces
    today = pd.Timestamp.now().normalize()
    all_yoy = pd.concat([
        lfs_all.rename("lfs_all"), lfs_perm.rename("lfs_perm"),
        seph.rename("seph"), lfs_micro.rename("lfs_micro"), svc_cpi.rename("svc_cpi"),
    ], axis=1, sort=True)
    yr_dict: dict = {}
    for years in [2, 5, 10]:
        cutoff = today - pd.DateOffset(years=years)
        vals = all_yoy[all_yoy.index >= cutoff].stack().dropna()
        if vals.empty:
            continue
        ymin, ymax = float(vals.min()), float(vals.max())
        pad = max((ymax - ymin) * 0.08, 0.1)
        yr_dict[years] = [round(ymin - pad, 4), round(ymax + pad, 4)]
    y_ranges = {str(i): yr_dict for i in range(7)}

    return html, y_ranges


# ── CPI All Items chart (SA + NSA, transforms + legend toggle) ───────────────

_CPI_TRANSFORMS = ["level", "mom", "ar_3m", "yoy"]
_CPI_TRANSFORM_LABELS = {"level": "Level", "mom": "M/M", "ar_3m": "3M AR", "yoy": "Y/Y"}
_CPI_TRANSFORM_UNITS  = {"level": "Index", "mom": "%", "ar_3m": "%", "yoy": "%"}
_CPI_TRANSFORM_DECIMALS = {"level": 1, "mom": 2, "ar_3m": 1, "yoy": 1}


def _cpi_compute_transform(v: pd.Series, key: str) -> pd.Series:
    if key == "level":  return v
    if key == "mom":    return v.pct_change(1) * 100
    if key == "ar_3m":  return ((v / v.shift(3)) ** 4 - 1) * 100
    if key == "yoy":    return v.pct_change(12) * 100
    raise ValueError(key)


def _build_cpi_panel(chart: "CpiSpec", data: dict,
                     chart_idx: int, include_plotlyjs: bool) -> tuple:
    div_id = "chart-" + str(chart_idx)
    lines = chart.lines
    n_lines = len(lines)
    n_t = len(_CPI_TRANSFORMS)
    default_t_idx = _CPI_TRANSFORMS.index(chart.default_transform)

    # Pre-compute every transform for every line
    transformed = {}
    for line in lines:
        s = data[line.series].set_index("date")["value"]
        transformed[line.series] = {
            t: _cpi_compute_transform(s, t) for t in _CPI_TRANSFORMS
        }

    # Build N_LINES × N_TRANSFORMS = N traces. Trace order: line-major.
    # Index i = line_idx * n_t + transform_idx
    fig = go.Figure()
    for line_idx, line in enumerate(lines):
        for t_idx, t_key in enumerate(_CPI_TRANSFORMS):
            s = transformed[line.series][t_key]
            visible = line.visible and (t_idx == default_t_idx)
            pct_t = t_key in {"mom", "ar_3m", "yoy"}
            suffix = "%" if pct_t else ""
            decimals = _CPI_TRANSFORM_DECIMALS[t_key]
            fig.add_trace(go.Scatter(
                x=s.index, y=s.values,
                line=dict(color=line.color, width=2),
                visible=visible,
                hovertemplate="%{x|%b %Y}<br>%{y:." + str(decimals) + "f}" + suffix + "<extra>"
                              + line.label + " " + _CPI_TRANSFORM_LABELS[t_key]
                              + "</extra>",
                showlegend=False,
            ))

    fig.update_layout(
        height=_CHART_HEIGHT, showlegend=False,
        paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS, font=dict(family=_FONT_STACK),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False, nticks=7)

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    # Transform buttons
    xform_btns = '<div class="btn-group" id="xb-' + div_id + '">'
    for t_idx, t_key in enumerate(_CPI_TRANSFORMS):
        active = " active" if t_idx == default_t_idx else ""
        label = _CPI_TRANSFORM_LABELS[t_key]
        unit  = _CPI_TRANSFORM_UNITS[t_key]
        xform_btns += (
            '<button class="ctrl-btn' + active + '"'
            ' onclick="cpiXformClick(this,\'' + div_id + '\',' + str(t_idx)
            + ",'" + unit + "')\">"
            + label + '</button>'
        )
    xform_btns += '</div>'

    range_btns = _range_buttons_html(div_id, default_years=chart.default_years)
    controls = ('<div class="chart-controls">' + xform_btns
                + '<div class="btn-sep"></div>' + range_btns + '</div>')

    def _swatch(color: str) -> str:
        return ('<span style="display:inline-block;width:22px;height:2.5px;'
                'background:' + color + ';border-radius:1px;vertical-align:middle;'
                'margin-right:5px"></span>')

    legend_items = []
    for line_idx, line in enumerate(lines):
        active = " active" if line.visible else ""
        legend_items.append(
            '<button class="legend-item' + active + '"'
            ' onclick="cpiLineToggle(this,\'' + div_id + '\',' + str(line_idx) + ')">'
            + _swatch(line.color) + line.label + '</button>'
        )
    legend = '<div class="chart-legend" id="leg-' + div_id + '">' + "".join(legend_items) + '</div>'

    footnote_html = (
        '<div class="chart-footnote">' + chart.footnote + '</div>'
        if chart.footnote else ""
    )
    html = (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        + _title_block_html(chart.title, _CPI_TRANSFORM_UNITS[chart.default_transform], div_id)
        + controls + '</div>'
        + plotly_frag
        + legend
        + footnote_html + '</div>\n'
    )

    # Y-ranges per (line, transform, window). For each transform, compute the
    # range covering all lines together, and store the same range under every
    # trace index of that transform — so the JS lookup picks the same value
    # regardless of which line is the first visible.
    today = pd.Timestamp.now().normalize()
    y_ranges: dict = {}
    for t_idx, t_key in enumerate(_CPI_TRANSFORMS):
        per_window: dict = {}
        for years in [2, 5, 10]:
            cutoff = today - pd.DateOffset(years=years)
            chunks = []
            for line in lines:
                s = transformed[line.series][t_key]
                chunks.append(s[s.index >= cutoff].dropna())
            merged = pd.concat(chunks) if chunks else pd.Series(dtype=float)
            if merged.empty:
                continue
            ymin, ymax = float(merged.min()), float(merged.max())
            pad = max((ymax - ymin) * 0.08, 0.05)
            per_window[years] = [round(ymin - pad, 4), round(ymax + pad, 4)]
        for line_idx in range(n_lines):
            trace_idx = line_idx * n_t + t_idx
            y_ranges[str(trace_idx)] = per_window

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

  .section-divider { margin-top: 28px; margin-bottom: 14px; }
  .section-divider:first-of-type { margin-top: 8px; }
  .section-heading {
    font-size: 0.72rem;
    font-weight: 700;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #eee;
  }
  .section-blurb {
    font-size: 0.9rem;
    color: #333;
    line-height: 1.65;
    margin: 0 0 8px;
  }

  .chart-panel { margin-bottom: 24px; }
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 2px;
  }
  .chart-title-block {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 0;
  }
  .chart-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #222;
  }
  .chart-subtitle {
    font-size: 0.75rem;
    color: #555;
    line-height: 1.1;
    margin-top: 1px;
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

  .chart-footnote {
    font-size: 0.72rem;
    color: #999;
    margin-top: 4px;
    padding: 0 2px;
    line-height: 1.5;
  }

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
var DEFAULT_RANGES = {default_ranges_js};
var Y_FLOORS = {y_floors_js};
document.addEventListener("DOMContentLoaded", function() {
  Object.keys(DEFAULT_RANGES).forEach(function(id) {
    applyRange(id, DEFAULT_RANGES[id]);
  });
});

function _toMillis(x) {
  if (x instanceof Date) return x.getTime();
  return new Date(x).getTime();
}

// Plotly may serialize numeric trace arrays as typed-array objects
// {dtype: "f8", bdata: "<base64>"} for efficiency. _decodeY normalises
// either format to an indexable array. Decoded result is cached on the trace.
function _decodeY(trace) {
  if (trace._decodedY) return trace._decodedY;
  var y = trace.y;
  if (y == null) return null;
  if (typeof y.length === "number" && !y.bdata) {
    trace._decodedY = y;
    return y;
  }
  if (y.bdata && y.dtype) {
    try {
      var bin = atob(y.bdata);
      var buf = new ArrayBuffer(bin.length);
      var bytes = new Uint8Array(buf);
      for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      var arr;
      switch (y.dtype) {
        case "f8": arr = new Float64Array(buf); break;
        case "f4": arr = new Float32Array(buf); break;
        case "i4": arr = new Int32Array(buf);   break;
        case "i2": arr = new Int16Array(buf);   break;
        case "i1": arr = new Int8Array(buf);    break;
        case "u4": arr = new Uint32Array(buf);  break;
        case "u2": arr = new Uint16Array(buf);  break;
        case "u1": arr = new Uint8Array(buf);   break;
        default: return null;
      }
      trace._decodedY = arr;
      return arr;
    } catch (e) {
      return null;
    }
  }
  return null;
}

function _niceDtick(ymin, ymax, target) {
  target = target || 5;
  var span = ymax - ymin;
  if (span <= 0) return 1;
  var rough = span / target;
  var mag = Math.pow(10, Math.floor(Math.log10(rough)));
  var norm = rough / mag;
  var nice;
  if (norm >= 5) nice = 5;
  else if (norm >= 2.5) nice = 2.5;
  else if (norm >= 2) nice = 2;
  else if (norm >= 1) nice = 1;
  else nice = 0.5;
  return nice * mag;
}

function _dtickFormat(dt) {
  var s = dt.toString();
  var dotIdx = s.indexOf('.');
  if (dotIdx === -1) return '.0f';
  var decimals = s.length - dotIdx - 1;
  return '.' + Math.min(decimals, 2) + 'f';
}

function _computeYRange(div, xStartMs, xEndMs) {
  var ymin = Infinity, ymax = -Infinity, found = false;
  for (var i = 0; i < div.data.length; i++) {
    var v = div.data[i].visible;
    // Plotly's visible can be true/false/undefined/'legendonly'; only count drawn traces.
    if (v === false || v === 'legendonly') continue;
    var trace = div.data[i];
    var xs = trace.x;
    var ys = _decodeY(trace);
    if (!xs || !ys) continue;
    var n = Math.min(xs.length, ys.length);
    for (var j = 0; j < n; j++) {
      if (xStartMs != null) {
        var xt = _toMillis(xs[j]);
        if (xt < xStartMs || xt > xEndMs) continue;
      }
      var y = ys[j];
      if (y === null || y === undefined || isNaN(y)) continue;
      if (y < ymin) ymin = y;
      if (y > ymax) ymax = y;
      found = true;
    }
  }
  if (!found) return null;
  // Pad is a small fraction of the visible span so tight-range series like
  // USD/CAD don't get drowned in whitespace. No absolute minimum: zoom in.
  var span = ymax - ymin;
  var pad = span > 0 ? span * 0.05 : 0.001;
  var floor = (Y_FLOORS && typeof Y_FLOORS[div.id] === "number") ? Y_FLOORS[div.id] : null;
  var lo = ymin - pad;
  if (floor !== null) lo = Math.max(lo, floor);
  return [lo, ymax + pad];
}

function _applyComputedYAxis(div, update, yr) {
  update["yaxis.range"] = yr;
  update["yaxis.autorange"] = false;
  var dt = _niceDtick(yr[0], yr[1]);
  update["yaxis.tick0"] = 0;
  update["yaxis.dtick"] = dt;
  update["yaxis.tickformat"] = _dtickFormat(dt);
}

function applyRange(chartId, years) {
  var div = document.getElementById(chartId);
  if (!div) return;
  var update = {};
  var yr;
  if (years === null) {
    update["xaxis.autorange"] = true;
    yr = _computeYRange(div, null, null);
  } else {
    var e = new Date(), s = new Date(e);
    s.setFullYear(s.getFullYear() - years);
    update["xaxis.range"] = [s.toISOString().slice(0, 10), e.toISOString().slice(0, 10)];
    update["xaxis.autorange"] = false;
    yr = _computeYRange(div, s.getTime(), e.getTime());
  }
  if (yr) _applyComputedYAxis(div, update, yr);
  else update["yaxis.autorange"] = true;
  Plotly.relayout(div, update);
}

function _refreshYAxis(chartId) {
  var rb = document.getElementById("rb-" + chartId);
  if (!rb) {
    applyRange(chartId, null);
    return;
  }
  var ab = rb.querySelector(".ctrl-btn.active");
  if (!ab) { applyRange(chartId, null); return; }
  var m = ab.getAttribute("onclick").match(/,(\\w+)\\)$/);
  if (!m) { applyRange(chartId, null); return; }
  var years = m[1] === "null" ? null : parseInt(m[1]);
  applyRange(chartId, years);
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
  _refreshYAxis(chartId);
}

function mlXformClick(btn, chartId, mode, lineCount) {
  var div = document.getElementById(chartId);
  btn.closest(".btn-group").querySelectorAll(".ctrl-btn").forEach(function(b) {
    b.classList.remove("active");
  });
  btn.classList.add("active");
  div._mlMode = mode;
  var vis = div.data.map(function() { return false; });
  var leg = document.getElementById("leg-" + chartId);
  if (leg) {
    leg.querySelectorAll(".legend-item").forEach(function(item, i) {
      if (item.classList.contains("active")) {
        if (mode === "raw") vis[i] = true;
        else vis[lineCount + i] = true;
      }
    });
  }
  Plotly.restyle(div, {visible: vis});
  var rb = document.getElementById("rb-" + chartId);
  if (rb) {
    var ab = rb.querySelector(".ctrl-btn.active");
    if (ab) {
      var m = ab.getAttribute("onclick").match(/,(\\w+)\\)$/);
      if (m && m[1] !== "null") applyRange(chartId, parseInt(m[1]));
    }
  }
}

function mlToggle(btn, chartId, lineIdx, lineCount) {
  var div = document.getElementById(chartId);
  var isActive = btn.classList.contains("active");
  btn.classList.toggle("active");
  var mode = div._mlMode || "raw";
  var vis = div.data.map(function(t) { return t.visible !== false; });
  vis[lineIdx] = !isActive && mode === "raw";
  vis[lineCount + lineIdx] = !isActive && mode === "smooth";
  Plotly.restyle(div, {visible: vis});
  _refreshYAxis(chartId);
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

function _cpiInitVisible(div) {
  if (div._cpiVisible) return;
  var nT = 4;
  var nLines = div.data.length / nT;
  div._cpiVisible = [];
  for (var k = 0; k < nLines; k++) {
    var anyOn = false;
    for (var t = 0; t < nT; t++) {
      if (div.data[k * nT + t].visible !== false) { anyOn = true; break; }
    }
    div._cpiVisible.push(anyOn);
  }
}

function _cpiApplyVisibility(div) {
  _cpiInitVisible(div);
  var nT = 4;
  var t = (div._cpiTransform === undefined) ? 3 : div._cpiTransform;
  var v = div._cpiVisible;
  var vis = [];
  for (var i = 0; i < div.data.length; i++) {
    var tIdx = i % nT;
    var vIdx = Math.floor(i / nT);
    vis.push(tIdx === t && v[vIdx]);
  }
  Plotly.restyle(div, {visible: vis});
}

function cpiXformClick(btn, chartId, transformIdx, unitLabel) {
  var div = document.getElementById(chartId);
  btn.closest(".btn-group").querySelectorAll(".ctrl-btn").forEach(function(b) {
    b.classList.remove("active");
  });
  btn.classList.add("active");
  div._cpiTransform = transformIdx;
  _cpiApplyVisibility(div);
  var subtitleDiv = document.getElementById("unit-" + chartId);
  if (subtitleDiv) subtitleDiv.textContent = unitLabel;
  var rb = document.getElementById("rb-" + chartId);
  if (rb) {
    var ab = rb.querySelector(".ctrl-btn.active");
    if (ab) {
      var m = ab.getAttribute("onclick").match(/,(\\w+)\\)$/);
      if (m && m[1] !== "null") applyRange(chartId, parseInt(m[1]));
    }
  }
}

function cpiLineToggle(btn, chartId, lineIdx) {
  var div = document.getElementById(chartId);
  _cpiInitVisible(div);
  var isActive = btn.classList.contains("active");
  btn.classList.toggle("active");
  div._cpiVisible[lineIdx] = !isActive;
  _cpiApplyVisibility(div);
  _refreshYAxis(chartId);
}
</script>
"""


# ── Multi-line chart ─────────────────────────────────────────────────────────

def _build_multiline_panel(chart: "MultiLineSpec", data: dict,
                           chart_idx: int, include_plotlyjs: bool) -> tuple:
    div_id = "chart-" + str(chart_idx)
    lines = [line for line in chart.lines if line.series in data]
    n = len(lines)
    has_smooth = chart.smooth_window is not None and n > 0

    fig = go.Figure()

    # Raw traces (indices 0..n-1)
    for line in lines:
        df = data[line.series]
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["value"],
            name=line.label,
            line=dict(color=line.color, width=2),
            line_shape=chart.line_shape,
            visible=True if line.visible else "legendonly",
            hovertemplate="%{x|" + chart.date_fmt + "}<br>%{y:" + chart.hoverformat + "}" + chart.ticksuffix + "<extra>" + line.label + "</extra>",
            showlegend=False,
        ))

    # Smooth traces (indices n..2n-1), hidden by default
    if has_smooth:
        for line in lines:
            df = data[line.series]
            if line.smooth:
                smooth = df["value"].rolling(chart.smooth_window, min_periods=chart.smooth_window // 2).mean()
                smooth_label = line.label + " (" + str(chart.smooth_window) + "d avg)"
            else:
                smooth = df["value"]  # already low-frequency; show raw in smooth mode
                smooth_label = line.label
            fig.add_trace(go.Scatter(
                x=df["date"], y=smooth,
                name=smooth_label,
                line=dict(color=line.color, width=2),
                line_shape="linear",
                visible=False,
                hovertemplate="%{x|" + chart.date_fmt + "}<br>%{y:" + chart.hoverformat + "}" + chart.ticksuffix + "<extra>" + smooth_label + "</extra>",
                showlegend=False,
            ))

    fig.update_layout(
        height=_CHART_HEIGHT, showlegend=False,
        paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS, font=dict(family=_FONT_STACK),
    )
    _fmt_today = pd.Timestamp.now().normalize()
    _fmt_vals: list = []
    for _line in lines:
        _df = data[_line.series]
        if chart.default_years:
            _cutoff = _fmt_today - pd.DateOffset(years=chart.default_years)
            _fmt_vals.append(_df["value"][_df["date"] >= _cutoff])
        else:
            _fmt_vals.append(_df["value"])
    ref_vals = pd.concat(_fmt_vals).dropna() if _fmt_vals else pd.Series(dtype=float)
    ymin_floor = chart.ymin if chart.ymin is not None else float("-inf")
    if not ref_vals.empty:
        rv_min_data = max(float(ref_vals.min()), ymin_floor)
        rv_max_data = float(ref_vals.max())
        rv_pad = max((rv_max_data - rv_min_data) * 0.08, 0.1)
        disp_lo = max(rv_min_data - rv_pad, chart.ymin) if chart.ymin is not None else rv_min_data - rv_pad
        disp_hi = rv_max_data + rv_pad
        ml_dtick = _nice_dtick(disp_lo, disp_hi)
        ml_tickfmt = _dtick_format(ml_dtick)
    else:
        ml_dtick, ml_tickfmt = 1.0, ".0f"

    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb", zeroline=False,
                     tickformat=ml_tickfmt,
                     tick0=0, dtick=ml_dtick,
                     rangemode="nonnegative" if chart.ymin == 0 else "normal")

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    range_btns = _range_buttons_html(div_id, default_years=chart.default_years)
    if has_smooth:
        xform_btns = (
            '<div class="btn-group" id="xb-' + div_id + '">'
            + '<button class="ctrl-btn active" onclick="mlXformClick(this,\'' + div_id + '\',\'raw\',' + str(n) + ')">Level</button>'
            + '<button class="ctrl-btn" onclick="mlXformClick(this,\'' + div_id + '\',\'smooth\',' + str(n) + ')">' + str(chart.smooth_window) + 'd Avg</button>'
            + '</div>'
        )
        controls = '<div class="chart-controls">' + xform_btns + '<div class="btn-sep"></div>' + range_btns + '</div>'
    else:
        controls = '<div class="chart-controls">' + range_btns + '</div>'

    def _swatch(color: str) -> str:
        return (
            '<span style="display:inline-block;width:22px;height:2.5px;'
            'background:' + color + ';border-radius:1px;vertical-align:middle;'
            'margin-right:5px"></span>'
        )

    legend_items = []
    for i, line in enumerate(lines):
        active = " active" if line.visible else ""
        if has_smooth:
            handler = 'mlToggle(this,\'' + div_id + '\',' + str(i) + ',' + str(n) + ')'
        else:
            handler = 'toggleTrace(this,\'' + div_id + '\',[' + str(i) + '])'
        legend_items.append(
            '<button class="legend-item' + active + '"'
            ' onclick="' + handler + '">'
            + _swatch(line.color) + line.label + '</button>'
        )
    legend = '<div class="chart-legend" id="leg-' + div_id + '">' + "".join(legend_items) + '</div>'

    footnote_html = (
        '<div class="chart-footnote">' + chart.footnote + '</div>'
        if chart.footnote else ""
    )
    html = (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        + _title_block_html(chart.title, chart.unit_label, div_id)
        + controls + '</div>'
        + plotly_frag
        + legend
        + footnote_html + '</div>\n'
    )

    # Y-ranges: union of all lines for each window, stored under all trace indices
    total_traces = 2 * n if has_smooth else n
    today = pd.Timestamp.now().normalize()
    yr_dict: dict = {}
    for years in [2, 5, 10]:
        cutoff = today - pd.DateOffset(years=years)
        vals = pd.concat([
            data[line.series]["value"][data[line.series]["date"] >= cutoff]
            for line in lines
        ]).dropna()
        if vals.empty:
            continue
        ymin, ymax = float(vals.min()), float(vals.max())
        if chart.ymin is not None:
            ymin = max(ymin, chart.ymin)
        pad = max((ymax - ymin) * 0.08, 0.1)
        lo = ymin - pad if chart.ymin is None else max(ymin - pad, chart.ymin)
        yr_dict[years] = [round(lo, 4), round(ymax + pad, 4)]
    y_ranges = {str(i): yr_dict for i in range(total_traces)}

    return html, y_ranges


# ── Page assembly ─────────────────────────────────────────────────────────────

def _assemble_page(page: PageSpec, chart_panels: list[str],
                   chart_ids: list[str], last_updated: str,
                   default_ranges: dict, y_floors: dict) -> str:
    chart_ids_js = "[" + ",".join('"' + cid + '"' for cid in chart_ids) + "]"
    default_ranges_js = json.dumps(default_ranges)
    y_floors_js = json.dumps(y_floors)
    js = (
        _JS_TEMPLATE
        .replace("{chart_ids_js}", chart_ids_js)
        .replace("{default_ranges_js}", default_ranges_js)
        .replace("{y_floors_js}", y_floors_js)
    )

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
        '<button class="ctrl-btn active" onclick="gcRange(10,this)">10Y</button>'
        '<button class="ctrl-btn" onclick="gcRange(null,this)">Max</button>'
        "</div></div>\n"
    )

    about = (
        '<div class="about">'
        "<strong>About this dashboard</strong> &mdash; "
        'Built by <a href="https://github.com/' + AUTHOR_DISPLAY_NAME + '">'
        + AUTHOR_DISPLAY_NAME + "</a> using public data from "
        '<a href="https://www150.statcan.gc.ca">Statistics Canada</a>, the '
        '<a href="https://www.bankofcanada.ca/valet/docs">Bank of Canada Valet API</a>, '
        'the <a href="https://fred.stlouisfed.org">Federal Reserve (FRED)</a>, '
        'and the <a href="https://economicdashboard.alberta.ca">Alberta Economic Dashboard</a>. '
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
        sections={0: "policy", 2: "inflation", 5: "labour", 7: "financial"},
        charts=[
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
            CoreInflationSpec(
                title="Core Inflation",
                footnote="Year-over-year %. Shaded band shows range across BoC core measures (trim, median, common, CPIX, CPIXFET).",
                default_years=10,
            ),
            CpiSpec(
                title="CPI Components",
                lines=[
                    CpiLine("cpi_all_items",      "Headline",       "#1565c0", visible=True),
                    CpiLine("cpi_all_items_nsa",  "Headline (NSA)", "#90a4ae"),
                    CpiLine("cpi_food",           "Food",           "#ef6c00", visible=True),
                    CpiLine("cpi_energy",         "Energy",         "#7b1fa2", visible=True),
                    CpiLine("cpi_goods",          "Goods",          "#00897b"),
                    CpiLine("cpi_services",       "Services",       "#388e3c"),
                ],
                default_transform="yoy",
                default_years=10,
                footnote="Canada CPI by category.",
            ),
            CpiBreadthSpec(
                title="CPI Breadth",
                footnote="Deviation from 1996–2019 average. Weighted share of 60 basket components with year-over-year change above 3% or below 1%.",
            ),
            ChartSpec(
                series="unemployment_rate",
                title="Unemployment Rate",
                frequency="monthly",
                color="#1565c0",
                static=True,
                default_years=10,
                hover_decimals=1,
                footnote="Canada, seasonally adjusted.",
            ),
            WageSpec(
                title="Wage Growth",
                footnote="Year-over-year %. LFS: average hourly wages. SEPH: average weekly earnings, all industries. LFS-Micro: BoC composition-adjusted measure. Services CPI overlay for wage-price context.",
            ),
            MultiLineSpec(
                title="Oil Prices",
                lines=[
                    LineConfig("wti",   "WTI",   "#ef6c00"),
                    LineConfig("brent", "Brent", "#00897b", visible=False),
                    LineConfig("wcs",   "WCS",   "#7b1fa2", visible=False, smooth=False),
                ],
                ticksuffix="",
                hoverformat=".2f",
                default_years=10,
                smooth_window=20,
                date_fmt="%b %d, %Y",
                ymin=0,
                unit_label="USD/barrel",
                footnote="Crude oil prices, USD per barrel. WTI and Brent are daily; WCS (Western Canada Select) is monthly. WTI briefly traded negative in April 2020 (futures contract anomaly); not shown.",
            ),
            ChartSpec(
                series="usdcad",
                title="USD/CAD",
                frequency="daily",
                color="#1565c0",
                default_years=10,
                unit_label="CAD per USD",
                footnote="Canadian dollars per US dollar. Higher = weaker CAD.",
            ),
        ],
    ),
]


# ── Main ──────────────────────────────────────────────────────────────────────

def _load_blurbs() -> dict:
    if not BLURBS_PATH.exists():
        return {}
    try:
        return json.loads(BLURBS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _render_section(section_id: str, blurbs: dict) -> str:
    heading = SECTION_HEADINGS.get(section_id, section_id.title())
    blurb = blurbs.get(section_id, {})
    text = blurb.get("text", "").strip()
    body = '<div class="section-blurb">' + text + '</div>' if text else ''
    return (
        '<div class="section-divider">'
        '<div class="section-heading">' + heading + '</div>'
        + body +
        '</div>\n'
    )


def build_page(page: PageSpec, data: dict[str, pd.DataFrame]) -> None:
    blurbs = _load_blurbs()
    chart_ids = ["chart-" + str(i) for i in range(len(page.charts))]
    panels = []
    y_ranges: dict = {}
    for i, chart in enumerate(page.charts):
        cid = "chart-" + str(i)
        # Insert a section heading + blurb above this chart, if configured.
        if i in page.sections:
            panels.append(_render_section(page.sections[i], blurbs))
        if isinstance(chart, CoreInflationSpec):
            panel, cyr = _build_core_inflation_panel(chart, data, i, i == 0)
            panels.append(panel)
            y_ranges[cid] = cyr
        elif isinstance(chart, CpiBreadthSpec):
            panel, cyr = _build_cpi_breadth_panel(chart, data, i, i == 0)
            panels.append(panel)
            y_ranges[cid] = cyr
        elif isinstance(chart, WageSpec):
            panel, cyr = _build_wage_panel(chart, data, i, i == 0)
            panels.append(panel)
            y_ranges[cid] = cyr
        elif isinstance(chart, CpiSpec):
            panel, cyr = _build_cpi_panel(chart, data, i, i == 0)
            panels.append(panel)
            y_ranges[cid] = cyr
        elif isinstance(chart, MultiLineSpec):
            panel, cyr = _build_multiline_panel(chart, data, i, i == 0)
            panels.append(panel)
            y_ranges[cid] = cyr
        else:
            df = data[chart.series]
            panels.append(_chart_panel_html(chart, df, i, include_plotlyjs=(i == 0)))
            y_ranges[cid] = _compute_y_ranges(chart, df)

    default_ranges: dict = {}
    y_floors: dict = {}
    for i, chart in enumerate(page.charts):
        cid = "chart-" + str(i)
        if isinstance(chart, CpiBreadthSpec):
            default_ranges[cid] = 10
        elif isinstance(chart, (ChartSpec, MultiLineSpec, WageSpec, CoreInflationSpec, CpiSpec)) and chart.default_years is not None:
            default_ranges[cid] = chart.default_years
        if isinstance(chart, MultiLineSpec) and chart.ymin is not None:
            y_floors[cid] = chart.ymin

    last_updated = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    html = _assemble_page(page, panels, chart_ids, last_updated, default_ranges, y_floors)

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
            elif isinstance(chart, WageSpec):
                all_series.update(WageSpec.SERIES)
            elif isinstance(chart, CpiSpec):
                all_series.update(chart.SERIES)
            elif isinstance(chart, CpiBreadthSpec):
                has_breadth = True
            elif isinstance(chart, MultiLineSpec):
                for line in chart.lines:
                    if (DATA_DIR / f"{line.series}.csv").exists():
                        all_series.add(line.series)
                    else:
                        print(f"  Warning: {line.series}.csv missing — run fetch.py. Line will be skipped.")
            else:
                all_series.add(chart.series)
    data: dict[str, pd.DataFrame] = {}
    for name in sorted(all_series):
        path = DATA_DIR / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing {path} -- run fetch.py first.")
        data[name] = pd.read_csv(path, parse_dates=["date"])
        if data[name].empty:
            print(f"  -> {name}: 0 rows (no data — chart will show empty traces)")
        else:
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
