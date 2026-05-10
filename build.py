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
import numpy as np
import pandas as pd
import plotly.graph_objects as go

try:
    from statsmodels.tsa.filters.hp_filter import hpfilter as _sm_hpfilter
    def _hp_filter(series: pd.Series, lamb: int = 129600) -> pd.Series:
        """Return the HP-filter trend (potential) component."""
        cycle, trend = _sm_hpfilter(series.values, lamb=lamb)
        return pd.Series(trend, index=series.index)
except ImportError:
    def _hp_filter(series: pd.Series, lamb: int = 129600) -> pd.Series:
        """Manual HP filter via banded-matrix solve (Hodrick-Prescott 1997).
        lambda=129600 is the monthly convention (= 1600 × 3^4)."""
        n = len(series)
        y = series.values.astype(float)
        # Build the second-difference matrix D (shape (n-2) × n)
        # and solve (I + λ D'D) τ = y
        e = np.ones(n)
        d2 = np.diag(e, 0) - 2 * np.diag(e[:-1], -1) + np.diag(e[:-2], -2)
        d2 = d2[2:]  # drop first 2 rows to get (n-2) × n
        A = np.eye(n) + lamb * d2.T @ d2
        trend = np.linalg.solve(A, y)
        return pd.Series(trend, index=series.index)

BLURBS_PATH = Path("data/blurbs.json")

SECTION_HEADINGS = {
    "policy":    "Monetary Policy",
    "gdp":       "GDP & Activity",
    "housing":   "Housing",
    "inflation": "Inflation",
    "labour":    "Labour Market",
    "financial": "Financial Conditions",
    # Policy deep-dive section headings
    "policy_dd_yield_curve":  "GoC Yield Curve",
    "policy_dd_real_rates":   "Real Rates",
    "policy_dd_corra":        "CORRA vs Target",
    "policy_dd_assets":       "BoC Assets",
    "policy_dd_liabilities":  "BoC Liabilities",
    "policy_dd_peers":        "Peer Central Banks",
    # Housing deep-dive section headings
    "housing_dd_activity":      "Demand and Market Tightness",
    "housing_dd_mortgage":      "Mortgage Rates",
    "housing_dd_pipeline":      "Construction Pipeline",
    "housing_dd_affordability": "Starts vs Supply Target",
    "housing_dd_renewal":       "Mortgage Renewal Shock",
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
class OverlayConfig:
    """A single overlay line for a ChartSpec. Shares all transforms of the parent chart.
    Default visibility is 'legendonly' (off) so the primary series dominates on first load."""
    series: str          # CSV filename without .csv
    label: str           # legend label
    color: str           # hex color


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
    # Optional per-transform unit labels. When set, xformClick updates the subtitle
    # div on each transform button click. Keys are transform names (e.g. "level",
    # "yoy"); missing keys default to unit_label.
    transform_unit_labels: dict = field(default_factory=dict)
    # Optional overlay lines. Each shares the same frequency/transforms as the primary
    # series but renders as a separate toggleable line, off by default.
    overlays: list = field(default_factory=list)  # list[OverlayConfig]
    # In level mode with the main series toggled off, swap the overlays to an alternate
    # display unit. Used by Monthly GDP: trillions while the total is shown, billions
    # while only industry overlays are shown (industries naturally read in billions, not
    # fractional trillions). Both fields must be set for the swap to activate.
    overlay_level_alt_unit_label: str = ""
    overlay_level_alt_scale: float = 1.0


@dataclass
class PageSpec:
    title: str
    tagline: str
    output_file: str
    charts: list  # ChartSpec | CoreInflationSpec | ...
    # Map chart-index -> section_id; renders a heading + blurb above that chart.
    sections: dict = field(default_factory=dict)
    # When True, _assemble_page adds the "under construction" deep-dive banner.
    is_deep_dive: bool = False


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
    secondary_y: bool = False


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
    smooth_label: str | None = None     # override for the smooth button text; defaults to "{smooth_window}d Avg"
    date_fmt: str = "%b %Y"            # hover date format
    footnote: str = ""
    ymin: float | None = None           # hard floor for y-axis (pre-computed ranges + autorange)
    unit_label: str = "%"               # text shown in top-left of plot area
    hband: tuple | None = None          # (lo, hi) horizontal shaded reference band, e.g. neutral rate
    # Alt-mode toggle (e.g. Index ↔ Y/Y on Housing Prices). Mutually exclusive with smooth_window.
    # When set, the chart renders a button-bar above the chart that flips both series between
    # primary (lines) and alt (alt_lines) — switching y-axis units globally.
    alt_lines: list = field(default_factory=list)   # list[LineConfig], must match lines length 1:1
    primary_label: str = "Y/Y"                     # button text for primary view
    alt_label: str = "Index"                       # button text for alt view
    alt_unit_label: str = ""                        # unit_label when in alt mode
    alt_ticksuffix: str = ""                        # ticksuffix used in HOVER for alt-mode traces
    alt_hoverformat: str = ".1f"                    # hoverformat for alt-mode traces
    default_alt: bool = False                       # if True, alt mode is the default view
    # Secondary Y-axis support (added May 2026)
    secondary_unit_label: str = ""
    secondary_ticksuffix: str = ""
    secondary_hoverformat: str = ".2f"
    secondary_ymin: float | None = None


@dataclass
class StackedBarSpec:
    """Stacked bar chart with per-series legend toggles. Uses barmode='relative'
    so positive bars stack above zero and negative bars stack below — correct for
    contribution-to-growth charts where components can swing either direction.
    `overlay` (optional) renders an additional line trace (e.g. headline series)
    on top of the bars; default visible, has its own legend toggle."""
    title: str
    lines: list                       # list[LineConfig]; reused from MultiLineSpec
    ticksuffix: str = "%"
    hoverformat: str = ".2f"
    default_years: int | None = None
    date_fmt: str = "%b %Y"
    footnote: str = ""
    unit_label: str = "%"
    overlay: "LineConfig | None" = None  # optional headline-line overlay drawn on top of bars


@dataclass
class MortgageShockSpec:
    """Static horizontal bar chart with hardcoded payment-shock data (BoC SAN 2025-21).
    No transforms, no date range buttons — this is a static reference chart."""
    title: str
    footnote: str = ""


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


def _nice_dtick(ymin: float, ymax: float, target: int = 5) -> float:
    """Round-number tick interval giving at least target ticks over [ymin, ymax].
    Rounds DOWN to the nearest nice step so tick count stays >= target."""
    span = ymax - ymin
    if span <= 0:
        return 1.0
    rough = span / target
    mag = 10 ** math.floor(math.log10(rough))
    norm = rough / mag
    # Round DOWN: pick the largest nice number that is <= norm.
    # `norm` is in [1, 10) by construction (rough / 10^floor(log10(rough))),
    # so the final branch is `else`, not `>= 1.0`.
    if norm >= 5.0:   nice = 5.0
    elif norm >= 2.5: nice = 2.5
    elif norm >= 2.0: nice = 2.0
    else:             nice = 1.0
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

def _compact_x_dates(fig: go.Figure) -> None:
    # Plotly serializes pandas Timestamps as "YYYY-MM-DDT00:00:00.000000" (28 chars).
    # All x-axes here are date-only; the time component is noise that adds ~2.4 MB
    # to index.html. JS uses new Date(x) which parses YYYY-MM-DD identically.
    for trace in fig.data:
        x = getattr(trace, "x", None)
        if x is None or len(x) == 0:
            continue
        try:
            trace.x = pd.to_datetime(x).strftime("%Y-%m-%d").tolist()
        except (ValueError, TypeError):
            pass


def _build_chart_fig(chart: ChartSpec, df: pd.DataFrame,
                     overlay_data: dict | None = None) -> go.Figure:
    """Build the Plotly figure for a ChartSpec.

    Trace layout when overlays are present:
      Traces 0..N-1 : main series (one per transform)
      Traces N..2N-1: first overlay (one per transform, 'legendonly' by default)
      Traces 2N..3N-1: second overlay, etc.
    where N = len(available transforms).
    """
    transforms = compute_transforms(df, chart.frequency)
    available = FREQ_TRANSFORMS[chart.frequency]
    default = "level" if chart.static else _resolve_default(chart)

    fig = go.Figure()
    # Primary series traces
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

    # Overlay traces: N traces per overlay (one per transform), all 'legendonly' by default
    if chart.overlays and overlay_data:
        for ov in chart.overlays:
            ov_df = overlay_data.get(ov.series)
            if ov_df is None or ov_df.empty:
                # Emit placeholder traces so trace indices stay consistent
                for transform_key in available:
                    fig.add_trace(go.Scatter(
                        x=[], y=[], name=transform_key,
                        visible="legendonly",
                        line=dict(color=ov.color, width=1.5),
                        showlegend=False,
                    ))
                continue
            ov_transforms = compute_transforms(ov_df, chart.frequency)
            for transform_key in available:
                s = ov_transforms.get(transform_key)
                if s is None:
                    fig.add_trace(go.Scatter(x=[], y=[], name=transform_key,
                                             visible="legendonly",
                                             line=dict(color=ov.color, width=1.5),
                                             showlegend=False))
                    continue
                fig.add_trace(go.Scatter(
                    x=s.index,
                    y=s.values,
                    name=f"{ov.label} — {transform_key}",
                    visible="legendonly",
                    line=dict(color=ov.color, width=1.5),
                    hovertemplate=_hover_template(
                        transform_key, chart.frequency, chart.hover_decimals
                    ).replace("<extra></extra>", f"<extra>{ov.label}</extra>"),
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
    use_unit_labels = bool(chart.transform_unit_labels)
    has_overlays = bool(chart.overlays)
    n_transforms = len(available)
    n_overlays = len(chart.overlays)
    out = '<div class="btn-group" id="xb-' + div_id + '">'
    for i, transform_key in enumerate(available):
        label = BUTTON_LABELS.get(transform_key, transform_key)
        active = " active" if transform_key == default else ""
        if has_overlays:
            # xformClickOverlay manages both main and overlay trace visibility
            if use_unit_labels:
                unit = chart.transform_unit_labels.get(transform_key, chart.unit_label)
                onclick = f"xformClickOverlay(this,'{div_id}',{i},{n_transforms},{n_overlays},'{unit}')"
            else:
                onclick = f"xformClickOverlay(this,'{div_id}',{i},{n_transforms},{n_overlays})"
        elif use_unit_labels:
            unit = chart.transform_unit_labels.get(transform_key, chart.unit_label)
            onclick = f"xformClick(this,'{div_id}',{i},'{unit}')"
        else:
            onclick = f"xformClick(this,'{div_id}',{i})"
        out += (
            '<button class="ctrl-btn' + active + '"'
            ' onclick="' + onclick + '">'
            + label + "</button>"
        )
    out += "</div>"
    return out


# ── Chart panel HTML ──────────────────────────────────────────────────────────

def _chart_panel_html(chart: ChartSpec, df: pd.DataFrame, chart_idx: int,
                      include_plotlyjs: bool,
                      data: dict | None = None) -> str:
    div_id = "chart-" + str(chart_idx)
    n_transforms = len(FREQ_TRANSFORMS[chart.frequency])

    # Collect overlay DataFrames (keyed by series name)
    overlay_data: dict | None = None
    if chart.overlays and data is not None:
        overlay_data = {ov.series: data.get(ov.series) for ov in chart.overlays}

    fig = _build_chart_fig(chart, df, overlay_data=overlay_data)
    _compact_x_dates(fig)
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

    # Legend for overlay lines (only when overlays are defined)
    legend_html = ""
    if chart.overlays:
        def _swatch_line(color: str) -> str:
            return (
                '<span style="display:inline-block;width:22px;height:2.5px;'
                'background:' + color + ';border-radius:1px;vertical-align:middle;'
                'margin-right:5px"></span>'
            )
        legend_html = '<div class="chart-legend">'
        # Primary series legend button (always active, overlayIdx=-1 means main series)
        primary_label = chart.title.split("(")[0].strip() if "(" in chart.title else chart.title
        legend_html += (
            '<button class="legend-item active"'
            ' onclick="toggleOverlayTrace(this,\'' + div_id + '\',-1,' + str(n_transforms) + ')">'
            + _swatch_line(chart.color) + primary_label + '</button>'
        )
        # Overlay legend buttons (off by default)
        for k, ov in enumerate(chart.overlays):
            legend_html += (
                '<button class="legend-item"'
                ' onclick="toggleOverlayTrace(this,\'' + div_id + '\',' + str(k) + ',' + str(n_transforms) + ')">'
                + _swatch_line(ov.color) + ov.label + '</button>'
            )
        legend_html += '</div>'

    footnote_html = (
        '<div class="chart-footnote">' + chart.footnote + '</div>'
        if chart.footnote else ""
    )

    # Conditional alt-unit setup: stash the level-transform overlay y-values and the
    # alt unit/scale so JS can swap on main-series toggle. See ChartSpec.overlay_level_alt_*.
    alt_unit_script = ""
    if (chart.overlays and chart.overlay_level_alt_unit_label
            and chart.overlay_level_alt_scale != 1.0):
        import json as _json, math as _math
        level_idx = 0  # FREQ_TRANSFORMS lists "level" first for every frequency
        orig_y = {}
        for k in range(len(chart.overlays)):
            trace_idx = (k + 1) * n_transforms + level_idx
            if trace_idx < len(fig.data):
                y_vals = fig.data[trace_idx].y
                orig_y[str(trace_idx)] = [
                    None if (isinstance(v, float) and _math.isnan(v)) else v
                    for v in y_vals
                ]
        cfg = {
            "altUnitLabel": chart.overlay_level_alt_unit_label,
            "primaryUnitLabel": chart.unit_label,
            "altScale": chart.overlay_level_alt_scale,
            "levelTformIdx": level_idx,
            "origY": orig_y,
        }
        alt_unit_script = (
            '<script>'
            'window._chartConfig=window._chartConfig||{};'
            'window._chartConfig["' + div_id + '"]=' + _json.dumps(cfg) + ';'
            '</script>'
        )

    return (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        + _title_block_html(chart.title, chart.unit_label, div_id)
        + controls +
        "</div>"
        + plotly_frag
        + alt_unit_script
        + legend_html
        + footnote_html
        + "</div>\n"
    )


# ── Core inflation one-off chart ─────────────────────────────────────────────

def _build_core_inflation_panel(chart: "CoreInflationSpec", data: dict,
                                chart_idx: int, include_plotlyjs: bool) -> str:
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
    # Trace 5: CPI-common (hidden by default)
    fig.add_trace(go.Scatter(
        x=common.index, y=common.values,
        line=dict(color="#00897b", width=1.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>CPI-common</extra>",
        showlegend=False, visible=False,
    ))
    # Trace 6: CPIX (hidden by default)
    fig.add_trace(go.Scatter(
        x=cpix.index, y=cpix.values,
        line=dict(color="#6d4c41", width=1.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>CPIX</extra>",
        showlegend=False, visible=False,
    ))
    # Trace 7: CPIXFET (hidden by default)
    fig.add_trace(go.Scatter(
        x=cpixfet.index, y=cpixfet.values,
        line=dict(color="#8e24aa", width=1.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>CPIXFET</extra>",
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

    _compact_x_dates(fig)
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
        + '<button class="legend-item"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[5])">'
        + _swatch_line("#00897b") + 'CPI-common</button>'
        + '<button class="legend-item"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[6])">'
        + _swatch_line("#6d4c41") + 'CPIX</button>'
        + '<button class="legend-item"'
        + ' onclick="toggleTrace(this,\'' + div_id + '\',[7])">'
        + _swatch_line("#8e24aa") + 'CPIXFET</button>'
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

    return html


# ── CPI breadth chart ────────────────────────────────────────────────────────

def _build_cpi_breadth_panel(chart: "CpiBreadthSpec", data: dict,
                              chart_idx: int, include_plotlyjs: bool) -> str:
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

    _compact_x_dates(fig)
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

    return html


# ── Wage growth chart ────────────────────────────────────────────────────────

def _build_wage_panel(chart: "WageSpec", data: dict,
                      chart_idx: int, include_plotlyjs: bool) -> str:
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

    _compact_x_dates(fig)
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

    return html


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
                     chart_idx: int, include_plotlyjs: bool) -> str:
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

    _compact_x_dates(fig)
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

    return html


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

  .site-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 2px;
    margin: 14px 0 22px;
    padding: 6px 0;
    border-top: 1px solid #eee;
    border-bottom: 1px solid #eee;
  }
  .site-nav .nav-item {
    font-size: 0.78rem;
    color: #666;
    padding: 4px 10px;
    text-decoration: none;
    border-radius: 3px;
    white-space: nowrap;
    transition: background 0.1s, color 0.1s;
  }
  .site-nav .nav-item:hover { background: #f5f5f5; color: #1a5276; }
  .site-nav .nav-item.active { background: #dce9f7; color: #1a5276; font-weight: 600; }

  .dd-banner {
    background: #fff8e1;
    border: 1px solid #ffd54f;
    color: #8d6e08;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 0.78rem;
    margin: 0 0 18px;
  }
  .dd-intro {
    font-size: 0.9rem;
    color: #333;
    line-height: 1.65;
    margin: 0 0 22px;
  }
  .dd-section { margin-bottom: 26px; }
  .dd-section h2 {
    font-size: 0.95rem;
    font-weight: 600;
    margin: 0 0 8px;
    color: #222;
    border-bottom: 1px solid #eee;
    padding-bottom: 5px;
  }
  .dd-section p {
    font-size: 0.88rem;
    color: #333;
    line-height: 1.65;
    margin: 0 0 8px;
  }
  .dd-stub {
    color: #888;
    font-style: italic;
    background: #fafafa;
    padding: 10px 14px;
    border-left: 3px solid #ddd;
    border-radius: 2px 4px 4px 2px;
    font-size: 0.85rem;
    line-height: 1.55;
  }
  .dd-iframe-wrap {
    border: 1px solid #eee;
    border-radius: 4px;
    overflow: hidden;
    margin: 8px 0 12px;
    background: #fafafa;
  }
  .dd-iframe-wrap iframe {
    border: 0;
    width: 100%;
    height: 620px;
    display: block;
  }
  .dd-tag {
    display: inline-block;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 1px 6px;
    border-radius: 3px;
    margin-left: 6px;
    vertical-align: middle;
  }
  .dd-tag-real { background: #e8f5e9; color: #2e7d32; }
  .dd-tag-stub { background: #fafafa; color: #999; border: 1px solid #eee; }

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
  // norm is in [1, 10) by construction; final branch is `else`, not `>= 1`.
  if (norm >= 5) nice = 5;
  else if (norm >= 2.5) nice = 2.5;
  else if (norm >= 2) nice = 2;
  else nice = 1;
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

function xformClick(btn, chartId, idx, unitLabel) {
  var div = document.getElementById(chartId);
  btn.closest(".btn-group").querySelectorAll(".ctrl-btn").forEach(function(b) {
    b.classList.remove("active");
  });
  btn.classList.add("active");
  Plotly.restyle(div, {visible: div.data.map(function(_, i) { return i === idx; })});
  if (unitLabel !== undefined) {
    var subtitleDiv = document.getElementById("unit-" + chartId);
    if (subtitleDiv) subtitleDiv.textContent = unitLabel;
  }
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
  // Treat "legendonly" as off — only an explicit true counts as visible.
  // Otherwise lines spec'd visible=False (which Plotly stores as "legendonly")
  // would be promoted to true by restyle as a side effect of any toggle.
  var vis = div.data.map(function(t) { return t.visible === true; });
  indices.forEach(function(i) { vis[i] = !isActive; });
  Plotly.restyle(div, {visible: vis});
  _refreshYAxis(chartId);
}

function mlXformClick(btn, chartId, mode, lineCount, unitLabel) {
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
  if (unitLabel !== undefined) {
    var subtitleDiv = document.getElementById("unit-" + chartId);
    if (subtitleDiv) subtitleDiv.textContent = unitLabel;
  }
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
  // Mode is whichever xform button is currently active. Without this fallback, charts
  // that default to alt-mode (e.g. Housing Prices defaulting to Y/Y) would have
  // _mlMode unset until first xform-click, and legend toggles would target the
  // wrong trace group.
  var mode = div._mlMode;
  if (!mode) {
    var xb = document.getElementById("xb-" + chartId);
    if (xb) {
      var ab = xb.querySelector(".ctrl-btn.active");
      if (ab) {
        var m = ab.getAttribute("onclick").match(/'(raw|smooth)'/);
        if (m) { mode = m[1]; div._mlMode = mode; }
      }
    }
    if (!mode) mode = "raw";
  }
  // Treat "legendonly" as off — only an explicit true counts as visible.
  // See toggleTrace for the same fix; without this, lines spec'd visible=False
  // (Plotly stores them as "legendonly") get promoted to true by restyle when
  // any other line on the chart is toggled.
  var vis = div.data.map(function(t) { return t.visible === true; });
  vis[lineIdx] = !isActive && mode === "raw";
  vis[lineCount + lineIdx] = !isActive && mode === "smooth";
  Plotly.restyle(div, {visible: vis});
  _refreshYAxis(chartId);
}

// ── Overlay-aware transform and toggle helpers ────────────────────────────────
//
// Used by ChartSpec charts that carry overlay lines (e.g. GDP monthly industry overlays).
//
// Trace layout:
//   Indices 0..nT-1              : main series (one per transform)
//   Indices nT..2nT-1            : overlay 0 (one per transform)
//   Indices 2nT..3nT-1           : overlay 1, etc.
//
// xformClickOverlay: switch active transform while preserving overlay on/off state.
function xformClickOverlay(btn, chartId, idx, nTransforms, nOverlays, unitLabel) {
  var div = document.getElementById(chartId);
  btn.closest(".btn-group").querySelectorAll(".ctrl-btn").forEach(function(b) {
    b.classList.remove("active");
  });
  btn.classList.add("active");
  if (unitLabel !== undefined) {
    var subtitleDiv = document.getElementById("unit-" + chartId);
    if (subtitleDiv) subtitleDiv.textContent = unitLabel;
  }
  // Build visibility array: main trace at idx=true; for each overlay, show the
  // transform-matching trace only if that overlay is currently active.
  var vis = div.data.map(function() { return false; });
  vis[idx] = true;
  // Determine which overlays are active by inspecting their current visibility.
  // An overlay is "active" if any of its nT traces is currently visible (=true).
  for (var k = 0; k < nOverlays; k++) {
    var base = nTransforms + k * nTransforms;
    var isOn = false;
    for (var t = 0; t < nTransforms; t++) {
      if (div.data[base + t].visible === true) { isOn = true; break; }
    }
    if (isOn) vis[base + idx] = true;
  }
  Plotly.restyle(div, {visible: vis});
  _maybeSwapAltUnit(div, chartId, nTransforms);
  var rb = document.getElementById("rb-" + chartId);
  if (rb) {
    var activeRangeBtn = rb.querySelector(".ctrl-btn.active");
    if (activeRangeBtn) {
      var m = activeRangeBtn.getAttribute("onclick").match(/,(\\w+)\\)$/);
      if (m && m[1] !== "null") applyRange(chartId, parseInt(m[1]));
    }
  }
}

// _maybeSwapAltUnit: for charts configured with overlay_level_alt_unit_label,
// switch overlay y-values + subtitle between primary and alt scale based on whether
// the main series is currently visible (level transform only).
function _maybeSwapAltUnit(div, chartId, nTransforms) {
  var cfg = (window._chartConfig || {})[chartId];
  if (!cfg || !cfg.altUnitLabel) return;
  var xb = document.getElementById("xb-" + chartId);
  var activeTform = 0;
  if (xb) xb.querySelectorAll(".ctrl-btn").forEach(function(b, i) {
    if (b.classList.contains("active")) activeTform = i;
  });
  if (activeTform !== cfg.levelTformIdx) return;

  var mainOff = (div.data[cfg.levelTformIdx].visible !== true);
  var nOverlays = (div.data.length / nTransforms) - 1;
  var subtitleDiv = document.getElementById("unit-" + chartId);

  var traceIdxs = [];
  var newYs = [];
  for (var k = 0; k < nOverlays; k++) {
    var overlayLevelIdx = (k + 1) * nTransforms + cfg.levelTformIdx;
    var origY = cfg.origY[String(overlayLevelIdx)];
    if (!origY) continue;
    var newY = mainOff ? origY.map(function(v) { return v === null ? null : v * cfg.altScale; }) : origY.slice();
    newYs.push(newY);
    traceIdxs.push(overlayLevelIdx);
  }
  if (traceIdxs.length > 0) Plotly.restyle(div, {y: newYs}, traceIdxs);
  if (subtitleDiv) subtitleDiv.textContent = mainOff ? cfg.altUnitLabel : cfg.primaryUnitLabel;
}

// toggleOverlayTrace: turn an overlay (or the main series) on or off.
// overlayIdx=-1 means the main series (traces 0..nT-1).
// For overlays, only the currently-active transform trace is toggled on; all
// other transform traces for that overlay are set to false.
function toggleOverlayTrace(btn, chartId, overlayIdx, nTransforms) {
  var div = document.getElementById(chartId);
  if (!div) return;
  var isActive = btn.classList.contains("active");
  btn.classList.toggle("active");
  // Determine the current active transform index from the xform button group.
  var xb = document.getElementById("xb-" + chartId);
  var activeTform = 0;
  if (xb) {
    xb.querySelectorAll(".ctrl-btn").forEach(function(b, i) {
      if (b.classList.contains("active")) activeTform = i;
    });
  }
  var vis = div.data.map(function(t) { return t.visible === true; });
  if (overlayIdx === -1) {
    // Main series: toggle trace at activeTform
    vis[activeTform] = !isActive;
  } else {
    var base = nTransforms + overlayIdx * nTransforms;
    // Turn all transform variants for this overlay off first, then enable only
    // the currently-active transform if toggling on.
    for (var t = 0; t < nTransforms; t++) vis[base + t] = false;
    if (!isActive) vis[base + activeTform] = true;
  }
  Plotly.restyle(div, {visible: vis});
  if (overlayIdx === -1) _maybeSwapAltUnit(div, chartId, nTransforms);
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
  var nT = {n_cpi_transforms};
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
  var nT = {n_cpi_transforms};
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
                           chart_idx: int, include_plotlyjs: bool) -> str:
    div_id = "chart-" + str(chart_idx)
    lines = [line for line in chart.lines if line.series in data]
    n = len(lines)
    has_smooth = chart.smooth_window is not None and n > 0
    has_alt = bool(chart.alt_lines) and n > 0
    # Mutually exclusive modes
    if has_smooth and has_alt:
        raise ValueError("MultiLineSpec: smooth_window and alt_lines cannot both be set")
    default_alt = has_alt and chart.default_alt
    has_two_modes = has_smooth or has_alt

    fig = go.Figure()

    # Horizontal reference band (e.g. neutral rate range on Policy Rates).
    # Always visible, drawn under the data lines.
    if chart.hband is not None:
        fig.add_hrect(
            y0=chart.hband[0], y1=chart.hband[1],
            fillcolor="rgba(180,180,180,0.35)",
            line_width=0,
            layer="below",
        )

    # Primary traces (indices 0..n-1).
    # When default_alt is True, primary traces are hidden by default.
    for line in lines:
        df = data[line.series]
        if default_alt:
            initial_visible = False
        else:
            initial_visible = True if line.visible else "legendonly"
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["value"],
            name=line.label,
            line=dict(color=line.color, width=2),
            line_shape=chart.line_shape,
            visible=initial_visible,
            hovertemplate="%{x|" + chart.date_fmt + "}<br>%{y:" + chart.hoverformat + "}" + chart.ticksuffix + "<extra>" + line.label + "</extra>",
            showlegend=False,
        ))

    # Smooth traces (indices n..2n-1), hidden by default
    if has_smooth:
        for line in lines:
            df = data[line.series]
            if line.smooth:
                smooth = df["value"].rolling(chart.smooth_window, min_periods=chart.smooth_window // 2).mean()
                _sl = chart.smooth_label if chart.smooth_label is not None else str(chart.smooth_window) + "d avg"
                smooth_label = line.label + " (" + _sl + ")"
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

    # Alt-mode traces (indices n..2n-1). Each alt line corresponds positionally to a primary line.
    # Visibility: when default_alt is True and the matching primary line was visible, this alt
    # trace is visible by default; otherwise hidden.
    if has_alt:
        for i, line in enumerate(lines):
            alt_line = chart.alt_lines[i] if i < len(chart.alt_lines) else None
            if alt_line is None or alt_line.series not in data:
                # Add a placeholder empty trace to preserve index alignment.
                fig.add_trace(go.Scatter(
                    x=[], y=[],
                    name=line.label,
                    line=dict(color=line.color, width=2),
                    visible=False,
                    showlegend=False,
                ))
                continue
            df_alt = data[alt_line.series]
            if default_alt:
                initial_visible = True if line.visible else "legendonly"
            else:
                initial_visible = False
            fig.add_trace(go.Scatter(
                x=df_alt["date"], y=df_alt["value"],
                name=line.label,
                line=dict(color=line.color, width=2),
                line_shape=chart.line_shape,
                visible=initial_visible,
                hovertemplate="%{x|" + chart.date_fmt + "}<br>%{y:" + chart.alt_hoverformat + "}" + chart.alt_ticksuffix + "<extra>" + line.label + "</extra>",
                showlegend=False,
            ))

    fig.update_layout(
        height=_CHART_HEIGHT, showlegend=False,
        paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS, font=dict(family=_FONT_STACK),
    )
    _fmt_today = pd.Timestamp.now().normalize()
    _fmt_vals: list = []
    # When default_alt is True, the initial visible series is the alt set, not the primary.
    _ref_lines = chart.alt_lines if default_alt else lines
    for _line in _ref_lines:
        if _line is None or _line.series not in data:
            continue
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

    _compact_x_dates(fig)
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
            + '<button class="ctrl-btn" onclick="mlXformClick(this,\'' + div_id + '\',\'smooth\',' + str(n) + ')">' + (chart.smooth_label if chart.smooth_label is not None else str(chart.smooth_window) + 'd Avg') + '</button>'
            + '</div>'
        )
        controls = '<div class="chart-controls">' + xform_btns + '<div class="btn-sep"></div>' + range_btns + '</div>'
    elif has_alt:
        # Two-mode toggle: primary (e.g. Y/Y) vs alt (e.g. Index). Mode switch flips
        # which group of traces is visible AND swaps the unit_label in the plot subtitle.
        primary_args = (
            "this,'" + div_id + "','raw'," + str(n)
            + ",'" + chart.unit_label.replace("'", "\\'") + "'"
        )
        alt_args = (
            "this,'" + div_id + "','smooth'," + str(n)
            + ",'" + chart.alt_unit_label.replace("'", "\\'") + "'"
        )
        primary_active = "" if default_alt else " active"
        alt_active = " active" if default_alt else ""
        xform_btns = (
            '<div class="btn-group" id="xb-' + div_id + '">'
            + '<button class="ctrl-btn' + primary_active + '" onclick="mlXformClick(' + primary_args + ')">' + chart.primary_label + '</button>'
            + '<button class="ctrl-btn' + alt_active + '" onclick="mlXformClick(' + alt_args + ')">' + chart.alt_label + '</button>'
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
        if has_two_modes:
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
    initial_unit_label = chart.alt_unit_label if (has_alt and default_alt) else chart.unit_label
    html = (
        '<div class="chart-panel">'
        '<div class="chart-header">'
        + _title_block_html(chart.title, initial_unit_label, div_id)
        + controls + '</div>'
        + plotly_frag
        + legend
        + footnote_html + '</div>\n'
    )

    return html


def _build_mortgage_shock_panel(chart: "MortgageShockSpec", chart_idx: int,
                                include_plotlyjs: bool) -> str:
    """Static horizontal bar chart: mortgage renewal payment-shock estimates.
    Data hardcoded from BoC SAN 2025-21 and SAN 2023-19. No transforms or date range buttons."""
    div_id = "chart-" + str(chart_idx)

    labels = [
        "5-yr fixed holders",
        "Variable-rate fixed-payment",
        "Median payment increase<br>(2022 → end-2027)",
    ]
    values = [17.5, 54.0, 34.0]   # midpoint for 5-yr fixed (15–20%); direct for the others
    colors = ["#1565c0", "#1565c0", "#1565c0"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=colors),
        text=[f"~{v:.0f}%" if v != 17.5 else "~15–20%" for v in values],
        textposition="outside",
        hovertemplate="%{y}<br>%{x:.1f}%<extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        height=200,
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        margin=dict(l=220, r=60, t=8, b=32),
        font=dict(family=_FONT_STACK),
        xaxis=dict(
            title="Payment increase (%)",
            title_font=dict(size=11),
            showgrid=True, gridcolor="#ebebeb", zeroline=False,
            range=[0, 65],
            ticksuffix="%",
        ),
        yaxis=dict(
            showgrid=False, zeroline=False,
            automargin=True,
        ),
    )

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    title_html = _title_block_html(chart.title, "%", div_id)
    footnote_html = (
        '<div class="chart-footnote">' + chart.footnote + '</div>'
        if chart.footnote else ""
    )
    return (
        '<div class="chart-panel">'
        '<div class="chart-header">' + title_html + '</div>'
        + plotly_frag
        + footnote_html
        + '</div>\n'
    )


def _build_stackedbar_panel(chart: "StackedBarSpec", data: dict,
                            chart_idx: int, include_plotlyjs: bool) -> str:
    div_id = "chart-" + str(chart_idx)
    lines = [line for line in chart.lines if line.series in data]
    overlay = chart.overlay if (chart.overlay is not None and chart.overlay.series in data) else None

    fig = go.Figure()
    for line in lines:
        df = data[line.series]
        fig.add_trace(go.Bar(
            x=df["date"], y=df["value"],
            name=line.label,
            marker=dict(color=line.color),
            visible=True if line.visible else "legendonly",
            hovertemplate="%{x|" + chart.date_fmt + "}<br>%{y:" + chart.hoverformat + "}" + chart.ticksuffix + "<extra>" + line.label + "</extra>",
            showlegend=False,
        ))
    if overlay is not None:
        odf = data[overlay.series]
        fig.add_trace(go.Scatter(
            x=odf["date"], y=odf["value"],
            mode="lines+markers",
            name=overlay.label,
            line=dict(color=overlay.color, width=2),
            marker=dict(color=overlay.color, size=5),
            visible=True if overlay.visible else "legendonly",
            hovertemplate="%{x|" + chart.date_fmt + "}<br>%{y:" + chart.hoverformat + "}" + chart.ticksuffix + "<extra>" + overlay.label + "</extra>",
            showlegend=False,
        ))

    fig.update_layout(
        height=_CHART_HEIGHT, showlegend=False,
        paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS, font=dict(family=_FONT_STACK),
        barmode="relative",
        bargap=0.15,
    )

    # y-range: union of stack-sum bounds and per-series bounds, so toggling traces on
    # doesn't blow out the axis.
    _today = pd.Timestamp.now().normalize()
    all_series = []
    for line in lines:
        df = data[line.series].copy()
        if chart.default_years:
            df = df[df["date"] >= _today - pd.DateOffset(years=chart.default_years)]
        all_series.append(df.set_index("date")["value"].rename(line.series))
    combined = pd.concat(all_series, axis=1) if all_series else pd.DataFrame()
    if not combined.empty and combined.notna().any().any():
        pos_sum_max = float(combined.clip(lower=0).sum(axis=1).max())
        neg_sum_min = float(combined.clip(upper=0).sum(axis=1).min())
        per_max = float(combined.max().max())
        per_min = float(combined.min().min())
        rv_max = max(pos_sum_max, per_max, 0.0)
        rv_min = min(neg_sum_min, per_min, 0.0)
        rv_pad = max((rv_max - rv_min) * 0.08, 0.1)
        disp_lo = rv_min - rv_pad
        disp_hi = rv_max + rv_pad
        sb_dtick = _nice_dtick(disp_lo, disp_hi)
        sb_tickfmt = _dtick_format(sb_dtick)
    else:
        sb_dtick, sb_tickfmt = 1.0, ".0f"

    # Quarterly tick labels: each bar is a quarter, so x-axis reads "Q1 2025" rather
    # than "Apr 2025". Provided as explicit tickvals/ticktext because Plotly's bundled
    # d3-time-format in current versions does not implement %q for quarter.
    sb_tickvals: list[str] = []
    sb_ticktext: list[str] = []
    if lines:
        ref_dates = pd.to_datetime(data[lines[0].series]["date"]).sort_values().unique()
        for d in ref_dates:
            ts = pd.Timestamp(d)
            sb_tickvals.append(ts.strftime("%Y-%m-%d"))
            sb_ticktext.append(f"Q{(ts.month - 1) // 3 + 1} {ts.year}")

    fig.update_xaxes(
        showgrid=False, zeroline=False,
        tickvals=sb_tickvals, ticktext=sb_ticktext, tickangle=-45,
    )
    fig.update_yaxes(showgrid=True, gridcolor="#ebebeb",
                     zeroline=True, zerolinecolor="#bdbdbd", zerolinewidth=1,
                     tickformat=sb_tickfmt,
                     tick0=0, dtick=sb_dtick)

    _compact_x_dates(fig)
    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    range_btns = _range_buttons_html(div_id, default_years=chart.default_years)
    controls = '<div class="chart-controls">' + range_btns + '</div>'

    def _swatch(color: str) -> str:
        return (
            '<span style="display:inline-block;width:12px;height:12px;'
            'background:' + color + ';border-radius:2px;vertical-align:middle;'
            'margin-right:6px"></span>'
        )

    legend_items = []
    for i, line in enumerate(lines):
        active = " active" if line.visible else ""
        handler = 'toggleTrace(this,\'' + div_id + '\',[' + str(i) + '])'
        legend_items.append(
            '<button class="legend-item' + active + '"'
            ' onclick="' + handler + '">'
            + _swatch(line.color) + line.label + '</button>'
        )
    if overlay is not None:
        overlay_idx = len(lines)
        active = " active" if overlay.visible else ""
        handler = 'toggleTrace(this,\'' + div_id + '\',[' + str(overlay_idx) + '])'
        legend_items.append(
            '<button class="legend-item' + active + '"'
            ' onclick="' + handler + '">'
            + _swatch(overlay.color) + overlay.label + '</button>'
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

    return html


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
        .replace("{n_cpi_transforms}", str(len(_CPI_TRANSFORMS)))
    )

    header = (
        '<div class="site-header">'
        "<h1>" + page.title + "</h1>"
        '<p class="tagline">' + page.tagline + "</p>"
        '<p class="updated">Last updated: ' + last_updated + "</p>"
        "</div>\n"
    )
    nav = _build_nav_html(page.output_file)

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
        "GitHub repository</a>. "
        "<em>Section blurbs are AI-generated from public data using a fixed analytical framework verified against primary sources. "
        "Not investment advice.</em>"
        "</div>\n"
    )

    dd_banner = (
        '<div class="dd-banner">'
        "<strong>Deep dive — work in progress.</strong> "
        "Charts are being built out over time. "
        'See the <a href="index.html">overview page</a> for the complete dashboard.'
        "</div>\n"
        if page.is_deep_dive else ""
    )
    return (
        "<!DOCTYPE html>\n<html>\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>" + page.title + "</title>\n"
        "<style>\n" + _CSS + "</style>\n"
        "</head>\n<body>\n"
        + header + nav + dd_banner + gc
        + "".join(chart_panels)
        + about + js
        + "</body>\n</html>\n"
    )


# ── Site navigation ──────────────────────────────────────────────────────────
#
# Single source of truth for the cross-page nav bar. Same list used to render
# the nav on the main overview page AND every deep-dive placeholder page. The
# active item is the one whose output_file matches the page being assembled.

NAV = [
    ("Overview",             "index.html"),
    ("Monetary Policy",      "policy.html"),
    ("Inflation",            "inflation.html"),
    ("GDP & Activity",       "gdp.html"),
    ("Labour Market",        "labour.html"),
    ("Housing",              "housing.html"),
    ("Financial Conditions", "financial.html"),
    ("Trade",                "trade.html"),
    ("Demographics",         "demographics.html"),
]


def _build_nav_html(current_file: str) -> str:
    items = []
    for label, file in NAV:
        cls = "nav-item active" if file == current_file else "nav-item"
        items.append('<a class="' + cls + '" href="' + file + '">' + label + "</a>")
    return '<nav class="site-nav">' + "".join(items) + "</nav>\n"


# ── Deep-dive placeholder pages ──────────────────────────────────────────────
#
# These pages are scaffolding. Most content is structured placeholders ([Coming
# soon]) tagged against the planned charts/sections in HANDOFF item 5 (and the
# parked-but-tentative items for the other sections). Where a real chart
# already exists in analyses/ (notably the Beveridge curve), it gets embedded
# via iframe so the deep-dive isn't ALL placeholder.
#
# As real deep-dive charts get wired into the build pipeline, migrate them out
# of these placeholder bodies into proper PageSpecs with chart specs.

def _dd_section(heading: str, intro: str, stub: str, real: bool = False) -> str:
    tag = ('<span class="dd-tag dd-tag-real">live</span>' if real
           else '<span class="dd-tag dd-tag-stub">stub</span>')
    intro_html = ('<p>' + intro + '</p>') if intro else ''
    return (
        '<div class="dd-section">'
        '<h2>' + heading + tag + '</h2>'
        + intro_html +
        '<div class="dd-stub">' + stub + '</div>'
        '</div>\n'
    )


def _dd_iframe_section(heading: str, intro: str, src: str) -> str:
    tag = '<span class="dd-tag dd-tag-real">live</span>'
    intro_html = ('<p>' + intro + '</p>') if intro else ''
    return (
        '<div class="dd-section">'
        '<h2>' + heading + tag + '</h2>'
        + intro_html +
        '<div class="dd-iframe-wrap"><iframe src="' + src + '" loading="lazy"></iframe></div>'
        '</div>\n'
    )


def _assemble_deep_dive_page(title: str, tagline: str, output_file: str,
                              intro: str, body_html: str, last_updated: str) -> str:
    nav = _build_nav_html(output_file)
    header = (
        '<div class="site-header">'
        "<h1>" + title + "</h1>"
        '<p class="tagline">' + tagline + "</p>"
        '<p class="updated">Last updated: ' + last_updated + "</p>"
        "</div>\n"
    )
    banner = (
        '<div class="dd-banner">'
        '<strong>Draft / under construction.</strong> '
        'Most content here is placeholder scaffolding. The page exists so the multi-page architecture works end-to-end; '
        'real charts and analysis migrate in over time. See the labour Beveridge curve for an example of a real chart in this layout.'
        '</div>\n'
    )
    intro_html = '<p class="dd-intro">' + intro + '</p>\n'
    about = (
        '<div class="about">'
        "<strong>About this dashboard</strong> &mdash; "
        'Built by <a href="https://github.com/' + AUTHOR_DISPLAY_NAME + '">'
        + AUTHOR_DISPLAY_NAME + "</a> using public data from "
        '<a href="https://www150.statcan.gc.ca">Statistics Canada</a>, the '
        '<a href="https://www.bankofcanada.ca/valet/docs">Bank of Canada Valet API</a>, '
        'the <a href="https://fred.stlouisfed.org">Federal Reserve (FRED)</a>, '
        'and the <a href="https://economicdashboard.alberta.ca">Alberta Economic Dashboard</a>. '
        '<em>Deep-dive pages are work-in-progress scaffolding.</em>'
        "</div>\n"
    )
    return (
        "<!DOCTYPE html>\n<html>\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>" + title + "</title>\n"
        "<style>\n" + _CSS + "</style>\n"
        "</head>\n<body>\n"
        + header + nav + banner + intro_html + body_html + about
        + "</body>\n</html>\n"
    )


# ── Native deep-dive chart builders ─────────────────────────────────────────
#
# These generate self-contained Plotly chart HTML for embedding in the
# DEEP_DIVES scaffold pages. Unlike PAGES charts, they don't plug into the
# JS range/transform infrastructure — they are static Plotly figures with
# displayModeBar disabled. For phase-space charts (Beveridge curve) and charts
# that live inside the _assemble_deep_dive_page layout, this is correct.
#
# Each builder accepts the project `data` dict and returns an HTML string
# following the .chart-panel / .chart-header / .chart-title / plotly-div /
# .chart-footnote structure so they inherit existing CSS styling.


def _build_beveridge_curve_panel(data: dict, chart_idx: int,
                                  include_plotlyjs: bool) -> str:
    """Beveridge curve: vacancy rate (Y) vs unemployment rate (X), period-coloured.

    Scatter-plots the 3M moving averages for both series to denoise the NSA
    vacancy data. Period colouring shows the structural shift (pre-pandemic
    curve vs post-COVID outward shift). Does NOT use the range/transform
    button infrastructure — this is a phase-space chart with no time axis."""
    div_id = "chart-" + str(chart_idx)

    u_df = data.get("unemployment_rate")
    v_df = data.get("job_vacancy_rate")
    if u_df is None or v_df is None:
        return ""

    u = u_df.sort_values("date").set_index("date")["value"]
    v = v_df.sort_values("date").set_index("date")["value"]

    df = pd.DataFrame({"u": u, "v": v}).dropna()
    df["u_3m"] = df["u"].rolling(3, min_periods=2).mean()
    df["v_3m"] = df["v"].rolling(3, min_periods=2).mean()
    df = df.dropna()

    def _period(d: pd.Timestamp) -> str:
        if d < pd.Timestamp("2020-03-01"):
            return "Pre-pandemic (2015–Feb 2020)"
        if d < pd.Timestamp("2021-04-01"):
            return "COVID shock (Mar 2020–Mar 2021)"
        if d < pd.Timestamp("2023-01-01"):
            return "Post-COVID overheat (Apr 2021–Dec 2022)"
        if d < pd.Timestamp("2024-07-01"):
            return "Cooling (Jan 2023–Jun 2024)"
        return "Recent slack (Jul 2024–latest)"

    df["period"] = df.index.map(_period)

    period_order = [
        "Pre-pandemic (2015–Feb 2020)",
        "COVID shock (Mar 2020–Mar 2021)",
        "Post-COVID overheat (Apr 2021–Dec 2022)",
        "Cooling (Jan 2023–Jun 2024)",
        "Recent slack (Jul 2024–latest)",
    ]
    period_colors = {
        "Pre-pandemic (2015–Feb 2020)":            "#1565c0",
        "COVID shock (Mar 2020–Mar 2021)":         "#7b1fa2",
        "Post-COVID overheat (Apr 2021–Dec 2022)": "#c62828",
        "Cooling (Jan 2023–Jun 2024)":             "#ef6c00",
        "Recent slack (Jul 2024–latest)":          "#00897b",
    }

    fig = go.Figure()

    # Background grey trajectory line (chronological order)
    fig.add_trace(go.Scatter(
        x=df["u_3m"], y=df["v_3m"],
        mode="lines",
        line=dict(color="rgba(150,150,150,0.45)", width=1.5),
        showlegend=False,
        hoverinfo="skip",
    ))

    for p in period_order:
        sub = df[df["period"] == p]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["u_3m"], y=sub["v_3m"],
            mode="markers",
            name=p,
            marker=dict(size=7, color=period_colors[p],
                        line=dict(width=0.5, color="white")),
            text=[d.strftime("%b %Y") for d in sub.index],
            hovertemplate="%{text}<br>U = %{x:.2f}%<br>V = %{y:.2f}%<extra>" + p + "</extra>",
            showlegend=True,
        ))

    # Star marker for the most recent observation
    last = df.iloc[-1]
    last_label = df.index[-1].strftime("%b %Y")
    fig.add_trace(go.Scatter(
        x=[last["u_3m"]], y=[last["v_3m"]],
        mode="markers+text",
        marker=dict(size=12, color="black", symbol="star"),
        text=[f" Latest ({last_label})"],
        textposition="middle right",
        textfont=dict(size=10, color="black"),
        showlegend=False,
        hoverinfo="skip",
    ))

    # 45° V = U reference line
    line_max = max(df["u_3m"].max(), df["v_3m"].max()) * 1.05
    fig.add_trace(go.Scatter(
        x=[0, line_max], y=[0, line_max],
        mode="lines",
        line=dict(color="rgba(100,100,100,0.4)", width=1, dash="dot"),
        name="V = U (rough V/U ≈ 1 reference)",
        showlegend=True,
        hoverinfo="skip",
    ))

    fig.update_layout(
        height=340,
        showlegend=True,
        legend=dict(
            yanchor="top", y=0.98,
            xanchor="right", x=0.99,
            bgcolor="rgba(255,255,255,0.85)",
            font=dict(size=11),
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        margin=dict(l=52, r=16, t=8, b=40),
        font=dict(family=_FONT_STACK),
        hovermode="closest",
    )
    fig.update_xaxes(
        title_text="Unemployment rate (%, 3M MA)",
        title_font=dict(size=11),
        showgrid=True, gridcolor="#ebebeb", zeroline=False,
    )
    fig.update_yaxes(
        title_text="Vacancy rate (%, 3M MA)",
        title_font=dict(size=11),
        showgrid=True, gridcolor="#ebebeb", zeroline=False,
    )

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    title_html = (
        '<div class="chart-title-block">'
        '<div class="chart-title">Beveridge Curve</div>'
        '<div class="chart-subtitle">Vacancy rate vs Unemployment rate</div>'
        '</div>'
    )
    footnote = (
        "Vacancy rate: StatsCan Table 14-10-0371 (monthly NSA), 3M MA. "
        "Unemployment rate: StatsCan Table 14-10-0287 (monthly SA), 3M MA. "
        "Vacancy data begins April 2015. "
        "Post-COVID outward shift reflects reduced matching efficiency — "
        "likely structural (immigration-driven labour-force composition, skill mismatch)."
    )

    script_block = (
        '<script>\n'
        '(function(){\n'
        f"    var el = document.getElementById('{div_id}');\n"
        "    el.on('plotly_restyle', function(){\n"
        "        Plotly.relayout(el, {'xaxis.autorange': true, 'yaxis.autorange': true});\n"
        "    });\n"
        "})();\n"
        '</script>\n'
    )

    return (
        '<div class="chart-panel">'
        '<div class="chart-header">' + title_html + '</div>'
        + plotly_frag
        + script_block
        + '<div class="chart-footnote">' + footnote + '</div>'
        + '</div>\n'
    )


def _build_gdp_potential_panel(data: dict, chart_idx: int,
                                include_plotlyjs: bool) -> str:
    """Actual vs HP-filter potential GDP. Level only (C$ trillions). 10Y default window."""
    div_id = "chart-" + str(chart_idx)

    gdp_df = data.get("gdp_monthly")
    if gdp_df is None or gdp_df.empty:
        return ""

    gdp = gdp_df.sort_values("date").set_index("date")["value"].dropna()
    trend = _hp_filter(gdp, lamb=129600)

    today = pd.Timestamp.now().normalize()
    x_start = (today - pd.DateOffset(years=10)).strftime("%Y-%m-%d")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=gdp.index.strftime("%Y-%m-%d").tolist(),
        y=gdp.values.tolist(),
        name="Real GDP",
        line=dict(color="#1565c0", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.3f} C$ T<extra>Real GDP</extra>",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=trend.index.strftime("%Y-%m-%d").tolist(),
        y=trend.values.tolist(),
        name="Potential GDP (HP)",
        line=dict(color="#546e7a", width=1.5, dash="dash"),
        hovertemplate="%{x|%b %Y}<br>%{y:.3f} C$ T<extra>Potential (HP)</extra>",
        showlegend=False,
    ))

    # Compute y-axis range for the 10Y window
    cutoff = today - pd.DateOffset(years=10)
    mask = gdp.index >= cutoff
    combined_10y = pd.concat([gdp[mask], trend[mask]])
    if not combined_10y.empty:
        ymin_10y = float(combined_10y.min())
        ymax_10y = float(combined_10y.max())
        pad = max((ymax_10y - ymin_10y) * 0.08, 0.01)
        dtick = _nice_dtick(ymin_10y - pad, ymax_10y + pad)
        tickfmt = _dtick_format(dtick)
    else:
        dtick, tickfmt = 0.1, ".1f"

    fig.update_layout(
        height=_CHART_HEIGHT,
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS,
        font=dict(family=_FONT_STACK),
        xaxis=dict(range=[x_start, today.strftime("%Y-%m-%d")],
                   showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#ebebeb", zeroline=False,
                   tick0=0, dtick=dtick, tickformat=tickfmt),
    )

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    # Unit label top-left (style guide §2)
    unit_annotation = (
        '<div style="position:relative;">'
        '<span style="position:absolute;top:6px;left:52px;'
        'font-size:0.72rem;color:#888;z-index:1;pointer-events:none;">'
        'C$ trillions</span>'
        + plotly_frag +
        '</div>'
    )

    title_html = (
        '<div class="chart-title-block">'
        '<div class="chart-title">Real GDP vs Potential GDP (HP Filter)</div>'
        '</div>'
    )

    # Legend swatches
    def _swatch(color, dash=False):
        border = "border-top: 2px dashed " + color + ";" if dash else "background:" + color + ";"
        return (
            '<span style="display:inline-block;width:22px;height:' +
            ("0" if dash else "2.5px") + ';' + border +
            'vertical-align:middle;margin-right:5px"></span>'
        )

    legend_html = (
        '<div class="chart-legend">'
        '<span class="legend-item active" style="cursor:default;">'
        + _swatch("#1565c0") + 'Real GDP</span>'
        '<span class="legend-item active" style="cursor:default;">'
        + _swatch("#546e7a", dash=True) + 'Potential GDP (HP)</span>'
        '</div>'
    )

    footnote = (
        "Potential GDP estimated via HP filter (λ=129,600). "
        "HP filter is trend-only — it does not incorporate BoC’s structural model estimates."
    )

    return (
        '<div class="chart-panel">'
        '<div class="chart-header">' + title_html + '</div>'
        + unit_annotation
        + legend_html
        + '<div class="chart-footnote">' + footnote + '</div>'
        + '</div>\n'
    )


def _build_output_gap_panel(data: dict, chart_idx: int,
                             include_plotlyjs: bool) -> str:
    """Output gap = (actual GDP / potential GDP - 1) × 100. HP filter estimate. 10Y default."""
    div_id = "chart-" + str(chart_idx)

    gdp_df = data.get("gdp_monthly")
    if gdp_df is None or gdp_df.empty:
        return ""

    gdp = gdp_df.sort_values("date").set_index("date")["value"].dropna()
    trend = _hp_filter(gdp, lamb=129600)
    gap = (gdp / trend - 1.0) * 100.0

    today = pd.Timestamp.now().normalize()
    x_start = (today - pd.DateOffset(years=10)).strftime("%Y-%m-%d")

    fig = go.Figure()

    # Zero reference line
    fig.add_hline(y=0, line_color="#999", line_width=1, line_dash="dot")

    fig.add_trace(go.Scatter(
        x=gap.index.strftime("%Y-%m-%d").tolist(),
        y=gap.values.tolist(),
        name="Output Gap (HP)",
        line=dict(color="#1565c0", width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.2f}%<extra>Output Gap (HP)</extra>",
        showlegend=False,
    ))

    cutoff = today - pd.DateOffset(years=10)
    gap_10y = gap[gap.index >= cutoff]
    if not gap_10y.empty:
        ymin_10y = float(gap_10y.min())
        ymax_10y = float(gap_10y.max())
        pad = max((ymax_10y - ymin_10y) * 0.08, 0.1)
        dtick = _nice_dtick(ymin_10y - pad, ymax_10y + pad)
        tickfmt = _dtick_format(dtick)
    else:
        dtick, tickfmt = 1.0, ".0f"

    fig.update_layout(
        height=_CHART_HEIGHT,
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS,
        font=dict(family=_FONT_STACK),
        xaxis=dict(range=[x_start, today.strftime("%Y-%m-%d")],
                   showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#ebebeb", zeroline=False,
                   tick0=0, dtick=dtick, tickformat=tickfmt),
    )

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    unit_annotation = (
        '<div style="position:relative;">'
        '<span style="position:absolute;top:6px;left:52px;'
        'font-size:0.72rem;color:#888;z-index:1;pointer-events:none;">'
        '%</span>'
        + plotly_frag +
        '</div>'
    )

    title_html = (
        '<div class="chart-title-block">'
        '<div class="chart-title">Output Gap — HP Filter Estimate</div>'
        '</div>'
    )

    footnote = (
        "HP-filter-based estimate only. "
        "BoC publishes its own output gap estimates quarterly in MPR Appendix; "
        "this is a mechanical approximation."
    )

    return (
        '<div class="chart-panel">'
        '<div class="chart-header">' + title_html + '</div>'
        + unit_annotation
        + '<div class="chart-footnote">' + footnote + '</div>'
        + '</div>\n'
    )


def _build_core_inflation_individual_panel(data: dict, chart_idx: int,
                                            include_plotlyjs: bool) -> str:
    """Five individual core measure lines (CPI-trim, -median, -common, CPIX, CPIXFET).
    Static deep-dive chart; no range/transform buttons. 10Y window baked into x-axis."""
    div_id = "chart-" + str(chart_idx)

    series_cfg = [
        ("cpi_trim",    "CPI-trim",    "#1565c0", True),
        ("cpi_median",  "CPI-median",  "#546e7a", False),
        ("cpi_common",  "CPI-common",  "#78909c", False),
        ("cpix",        "CPIX",        "#ef6c00", False),
        ("cpixfet",     "CPIXFET",     "#00897b", False),
    ]

    today = pd.Timestamp.now().normalize()
    cutoff = today - pd.DateOffset(years=10)
    x_start = cutoff.strftime("%Y-%m-%d")

    fig = go.Figure()
    fig.add_hline(y=2, line_color="#555", line_width=1, line_dash="dot")

    all_vals_10y = []
    for key, label, color, visible in series_cfg:
        df = data.get(key)
        if df is None or df.empty:
            continue
        s = df.sort_values("date").set_index("date")["value"].dropna()
        fig.add_trace(go.Scatter(
            x=s.index.strftime("%Y-%m-%d").tolist(),
            y=s.values.tolist(),
            name=label,
            visible=True if visible else "legendonly",
            line=dict(color=color, width=2),
            hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>" + label + "</extra>",
            showlegend=False,
        ))
        vals_10y = s[s.index >= cutoff]
        if not vals_10y.empty:
            all_vals_10y.extend(vals_10y.values.tolist())

    if all_vals_10y:
        ymin_10y = min(all_vals_10y)
        ymax_10y = max(all_vals_10y)
        pad = max((ymax_10y - ymin_10y) * 0.08, 0.1)
        dtick = _nice_dtick(ymin_10y - pad, ymax_10y + pad)
        tickfmt = _dtick_format(dtick)
    else:
        dtick, tickfmt = 1.0, ".0f"

    fig.update_layout(
        height=_CHART_HEIGHT, showlegend=False,
        paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS, font=dict(family=_FONT_STACK),
        xaxis=dict(range=[x_start, today.strftime("%Y-%m-%d")],
                   showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#ebebeb", zeroline=False,
                   tick0=0, dtick=dtick, tickformat=tickfmt),
    )

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    unit_annotation = (
        '<div style="position:relative;">'
        '<span style="position:absolute;top:6px;left:52px;'
        'font-size:0.72rem;color:#888;z-index:1;pointer-events:none;">'
        '%</span>'
        + plotly_frag +
        '</div>'
    )

    title_html = (
        '<div class="chart-title-block">'
        '<div class="chart-title">Core Inflation — Individual Measures</div>'
        '</div>'
    )

    def _swatch_line(color: str) -> str:
        return (
            '<span style="display:inline-block;width:22px;height:2.5px;'
            'background:' + color + ';border-radius:1px;vertical-align:middle;'
            'margin-right:5px"></span>'
        )

    legend_html = (
        '<div class="chart-legend">'
        + ''.join(
            '<span class="legend-item' + (' active' if visible else '') + '" style="cursor:default;">'
            + _swatch_line(color) + label + '</span>'
            for _, label, color, visible in series_cfg
        )
        + '</div>'
    )

    footnote = (
        "CPI-trim and CPI-median are BoC staff measures published monthly. "
        "CPI-common is estimated via common-component extraction and is the smoothest of the three; "
        "it tends to lag turning points relative to trim and median. "
        "CPIX (ex-8 volatile + indirect taxes) and CPIXFET (ex-food, energy, indirect taxes) "
        "are older BoC measures, superseded by the current preferred trio but still published for continuity."
    )

    return (
        '<div class="chart-panel">'
        '<div class="chart-header">' + title_html + '</div>'
        + unit_annotation
        + legend_html
        + '<div class="chart-footnote">' + footnote + '</div>'
        + '</div>\n'
    )


def _build_wcs_wti_panel(data: dict, chart_idx: int,
                          include_plotlyjs: bool) -> str:
    """WCS-WTI differential (USD/barrel): WTI monthly mean minus WCS.
    Static deep-dive chart; no range/transform buttons. 10Y window baked in.
    Reference bands: $10–15 (normal), dashed line at $20 (pipeline-constrained)."""
    div_id = "chart-" + str(chart_idx)

    wcs_df = data.get("wcs")
    wti_df = data.get("wti")
    if wcs_df is None or wcs_df.empty or wti_df is None or wti_df.empty:
        return ""

    # Resample WTI (daily) to monthly mean, then subtract WCS
    wti = wti_df.sort_values("date").set_index("date")["value"].dropna()
    wti_monthly = wti.resample("MS").mean()  # month-start frequency
    wcs = wcs_df.sort_values("date").set_index("date")["value"].dropna()
    wcs.index = wcs.index.to_period("M").to_timestamp()  # normalise to month-start

    combined = pd.DataFrame({"wti": wti_monthly, "wcs": wcs}).dropna()
    diff = combined["wti"] - combined["wcs"]

    today = pd.Timestamp.now().normalize()
    cutoff = today - pd.DateOffset(years=10)
    x_start = cutoff.strftime("%Y-%m-%d")

    fig = go.Figure()

    # Normal range band: $10–15
    fig.add_hrect(
        y0=10, y1=15,
        fillcolor="rgba(180,180,180,0.35)", line_width=0,
        annotation_text="Normal range", annotation_position="top left",
        annotation_font=dict(size=10, color="#666"),
    )

    # Pipeline-constrained reference line at $20
    fig.add_hline(
        y=20, line_color="#c62828", line_width=1.5, line_dash="dash",
        annotation_text="Pipeline-constrained (~$20+)", annotation_position="top right",
        annotation_font=dict(size=10, color="#c62828"),
    )

    fig.add_trace(go.Scatter(
        x=diff.index.strftime("%Y-%m-%d").tolist(),
        y=diff.values.tolist(),
        name="WTI − WCS",
        line=dict(color="#1565c0", width=2),
        hovertemplate="%{x|%b %Y}<br>$%{y:.2f}/bbl<extra>WTI − WCS</extra>",
        showlegend=False,
    ))

    diff_10y = diff[diff.index >= cutoff]
    if not diff_10y.empty:
        ymin_10y = float(diff_10y.min())
        ymax_10y = float(diff_10y.max())
        pad = max((ymax_10y - ymin_10y) * 0.08, 0.5)
        dtick = _nice_dtick(max(ymin_10y - pad, 0), ymax_10y + pad)
        tickfmt = _dtick_format(dtick)
        y_floor = max(0.0, ymin_10y - pad)
        y_ceil = ymax_10y + pad
    else:
        dtick, tickfmt = 5.0, ".0f"
        y_floor, y_ceil = 0, 40

    fig.update_layout(
        height=_CHART_HEIGHT, showlegend=False,
        paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
        margin=_CHART_MARGINS, font=dict(family=_FONT_STACK),
        xaxis=dict(range=[x_start, today.strftime("%Y-%m-%d")],
                   showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#ebebeb", zeroline=False,
                   tick0=0, dtick=dtick, tickformat=tickfmt,
                   range=[y_floor, y_ceil]),
    )

    plotly_frag = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )

    unit_annotation = (
        '<div style="position:relative;">'
        '<span style="position:absolute;top:6px;left:52px;'
        'font-size:0.72rem;color:#888;z-index:1;pointer-events:none;">'
        'USD/barrel</span>'
        + plotly_frag +
        '</div>'
    )

    title_html = (
        '<div class="chart-title-block">'
        '<div class="chart-title">WTI − WCS Differential</div>'
        '</div>'
    )

    footnote = (
        "WTI monthly mean (Alberta Economic Dashboard) minus WCS monthly (CAPP/Alberta). "
        "Normal range ($10–15/bbl) reflects pre-2018 average differential before pipeline constraints. "
        "Differentials above $20 historically coincide with pipeline take-away binding; "
        "Trans Mountain Expansion (TMX) opening in May 2024 added ~590,000 bbl/d capacity and "
        "materially compressed the spread. Alberta royalties scale with realized WCS price."
    )

    return (
        '<div class="chart-panel">'
        '<div class="chart-header">' + title_html + '</div>'
        + unit_annotation
        + '<div class="chart-footnote">' + footnote + '</div>'
        + '</div>\n'
    )


# Per-section deep-dive specs. Each entry is a dict with title, tagline,
# output_file, intro, and body_html. Body_html is composed at module load time
# from _dd_section / _dd_iframe_section helpers so the structure stays uniform.
# Entries with a `body_fn` key instead of `body` receive the project `data` dict
# at build time and return the body HTML dynamically (used for native charts).

DEEP_DIVES = [
    {
        "title": "GDP & Activity — deep dive",
        "tagline": "Productivity, capacity, and the output gap",
        "output_file": "gdp.html",
        "intro": (
            "The overview tracks growth vs potential. The deep-dive opens up the underlying productivity story, "
            "the BoC's output-gap range, and the capacity-utilization data that feeds the slack assessment."
        ),
        "body_fn": lambda data: (
            _build_gdp_potential_panel(data, 0, include_plotlyjs=True)
            + _build_output_gap_panel(data, 1, include_plotlyjs=False)
            + _dd_section(
                "Output gap (live BoC range)",
                "BoC's quarterly published gap estimate from Indicators of Capacity and Inflation Pressures.",
                "[Coming soon] BoC publishes a range each MPR (currently roughly -1.5% to -0.5%). This is the operative slack measure, more directly relevant to monetary policy than GDP growth alone. Multiple methodologies (HP filter, Hamilton filter, EMVF, Integrated Framework); the range captures uncertainty.",
            )
            + _dd_section(
                "Productivity decomposition",
                "Output per hour worked vs trend; sectoral breakdown.",
                "[Coming soon] Real GDP per hour worked Y/Y. Canadian productivity has been structurally weak since 2015; 2022-2024 was historically poor (Macklem November 2024 speech). Compare manufacturing vs services productivity to identify where the gap originates.",
            )
            + _dd_section(
                "Capacity utilization",
                "StatsCan capacity utilization rate, by industry.",
                "[Coming soon] StatsCan Table 36-10-0007 — quarterly capacity utilization rate. Manufacturing utilization is the most cyclically informative; below 80% suggests slack, above 85% suggests tight capacity.",
            )
            + _dd_section(
                "Hours worked and labour input",
                "Aggregate hours worked, average hours, hours-worked productivity.",
                "[Coming soon] Total hours from LFS. Average weekly hours have been falling — partly demographic (services / part-time mix), partly cyclical. The shift from monthly GDP to hours-worked productivity gives a cleaner read on Canadian competitiveness.",
            )
            + _dd_section(
                "BoC potential-output decomposition",
                "Trend labour input × trend labour productivity (the official decomposition).",
                "[Coming soon] Per SAN 2025-14: potential output decomposes into trend labour input (TLI) and trend labour productivity (TLP). TLI captures demographic/immigration effects; TLP captures the productivity story. Plotting both lets you see which channel is moving over time.",
            )
        ),
    },
    {
        "title": "Trade & External Sector — Deep Dive",
        "tagline": "Canada's trade exposure, bilateral flows, and terms-of-trade conditions",
        "output_file": "trade.html",
        "intro": (
            "What is Canada's trade exposure — by commodity, sector, and bilaterally to the US — and what do "
            "terms-of-trade and tariff-shock indicators say about current risk?"
        ),
        "body": (
            _dd_section(
                "Goods Exports by Category",
                "Breakdown of merchandise exports by commodity category.",
                "[Coming soon] StatsCan Table 12-10-0011 — goods exports by category (energy, autos, agricultural, industrial goods, etc.). Concentration in energy and automotive is the structural vulnerability; the tariff-shock exposure differs materially by category.",
            )
            + _dd_section(
                "Canada–US Bilateral Trade Balance",
                "Monthly goods trade balance with the United States.",
                "[Coming soon] StatsCan Table 12-10-0011 — Canada-US bilateral goods exports and imports. The US accounts for roughly three-quarters of Canadian goods exports; bilateral balance shifts are the primary channel for tariff-shock transmission.",
            )
            + _dd_section(
                "Goods Exports Excluding Gold",
                "Export volumes stripped of gold-flow distortions.",
                "[Coming soon] Non-monetary gold shipments can swing the headline export figure by several billion dollars in a single month without reflecting underlying trade conditions. Excluding gold gives a cleaner read on real export momentum.",
            )
            + _dd_section(
                "Terms of Trade",
                "Export price index relative to import price index.",
                "[Coming soon] Terms of trade (export price index ÷ import price index) is a real-income signal partially distinct from FX. Improving terms of trade = real-income transfer to Canada from rest of world; deteriorating = transfer out. Commodity-price cycles are the dominant driver for Canada.",
            )
            + _dd_section(
                "Export Shares by Partner",
                "Geographic concentration of Canadian goods exports.",
                "[Coming soon] US share of Canadian exports has exceeded 75% in recent years; EU, UK, China, and other Asian markets make up most of the remainder. Partner-concentration risk is central to the tariff-shock narrative; any trade-diversion story needs the baseline share picture.",
            )
        ),
    },
    {
        "title": "Demographics & Labour Supply — Deep Dive",
        "tagline": "Population dynamics, immigration, and the structural capacity constraints monetary policy cannot resolve",
        "output_file": "demographics.html",
        "intro": (
            "What does Canada's population and age structure say about the labour-supply trajectory and "
            "structural capacity constraints?"
        ),
        "body": (
            _dd_section(
                "Population Growth by Component",
                "Natural increase, international migration, and interprovincial flows.",
                "[Coming soon] StatsCan Table 17-10-0008 — quarterly population estimates by component of growth. Natural increase (births minus deaths) has been declining for decades; international migration has become the dominant driver. The pace and composition of that shift matters for labour-supply forecasts.",
            )
            + _dd_section(
                "Net International Migration (Permanent + Temporary)",
                "Annual flows of permanent residents and net temporary residents.",
                "[Coming soon] StatsCan Table 17-10-0008 / IRCC — permanent resident admissions plus net change in temporary residents (international students, TFWs, etc.). The 2022-2024 surge in temporary residents drove much of the labour-force growth; the policy reversal in late 2024 is the structural inflection.",
            )
            + _dd_section(
                "Working-Age Population and Dependency Ratio",
                "15-64 population share; old-age dependency ratio.",
                "[Coming soon] StatsCan Table 17-10-0005 — population by age group. The working-age share has been declining since the mid-2000s as Boomers age out; dependency ratio is rising. Dependency ratio directly constrains trend growth in labour input, which feeds potential output.",
            )
            + _dd_section(
                "Labour Force by Age Group",
                "Participation and employment rates for youth, prime-age, and older workers.",
                "[Coming soon] StatsCan LFS Table 14-10-0287 by age group. Prime-age (25-54) participation is near its ceiling; youth (15-24) unemployment is highly cyclical; older-worker (55+) participation has trended up. Age-group composition shifts can move the headline rate without any change in underlying conditions.",
            )
            + _dd_section(
                "Population Projections vs Actual",
                "StatsCan medium-growth scenario vs realised population.",
                "[Coming soon] StatsCan Table 17-10-0057 — medium-growth projection scenario vs. actual realised population. Projections have repeatedly underestimated actual inflows; tracking the gap is informative for capacity-constraint assessments.",
            )
        ),
    },
]


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
        sections={0: "policy", 3: "inflation", 8: "gdp", 10: "labour", 14: "housing", 18: "financial"},
        charts=[
            MultiLineSpec(
                title="Policy Rates",
                lines=[
                    LineConfig("overnight_rate", "BoC", "#1565c0"),
                    LineConfig("fed_funds",      "Fed", "#c62828"),
                    LineConfig("bocfed_spread",  "BoC − Fed", "#7b1fa2", visible=False),
                ],
                default_years=10,
                line_shape="hv",
                hband=(2.25, 3.25),
                footnote="BoC overnight rate target; Fed funds midpoint of target range. Shaded band: BoC's estimated neutral-rate range, 2.25–3.25%.",
            ),
            MultiLineSpec(
                title="2-Year Yields",
                lines=[
                    LineConfig("yield_2yr",                "Canada 2Y",                "#1565c0"),
                    LineConfig("us_2yr",                   "US 2Y",                    "#c62828"),
                    LineConfig("can2y_overnight_spread",   "Canada 2Y − Overnight",    "#7b1fa2", visible=False, smooth=False),
                    LineConfig("can_us_2y_spread",         "Canada 2Y − US 2Y",        "#00897b", visible=False, smooth=False),
                ],
                default_years=10,
                smooth_window=20,
                date_fmt="%b %d, %Y",
                footnote="2-year benchmark government bond yields. Toggle 'Canada 2Y − Overnight' for a <em>directional</em> read of the market-implied BoC path — negative = pricing net cuts, positive = pricing hold or hikes. The 2Y embeds a term premium, so this is directional only; not a precise basis-point forecast. Treat with extra caution during QE/QT transitions or stress regimes when premium movements distort the signal. See the BoC's <a href=\"https://www.bankofcanada.ca/rates/indicators/financial-stability-indicators/\" target=\"_blank\" rel=\"noopener\">Financial Stability Indicators</a> for model-decomposed estimates. 'Canada 2Y − US 2Y' is the cross-country differential (negative = Canadian rates lower than US, broadly CAD-negative).",
            ),
            MultiLineSpec(
                title="BoC Balance Sheet",
                lines=[
                    LineConfig("boc_total_assets",         "Total assets",        "#1565c0"),
                    LineConfig("boc_goc_bonds",            "GoC bonds",           "#00897b"),
                    LineConfig("boc_settlement_balances",  "Settlement balances", "#7b1fa2", visible=False),
                ],
                ticksuffix="",
                hoverformat=".0f",
                default_years=10,
                line_shape="linear",
                date_fmt="%b %d, %Y",
                unit_label="C$ billions",
                footnote="BoC Statement of Financial Position (weekly). QE ran from April 2020 to April 2022 (assets peaked at ~$575B); passive QT (bonds rolling off as they mature) began April 2022. Total assets is the headline; GoC bonds is the active policy instrument; settlement balances (deposits banks hold at the BoC) is the liability mirror and operating-regime indicator — large balances reflect the BoC's floor system, declared permanent in 2025.",
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
                    CpiLine("cpi_shelter",        "Shelter",        "#6d4c41"),
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
            MultiLineSpec(
                title="Consumer Inflation Expectations",
                lines=[
                    LineConfig("infl_exp_consumer_1y", "Consumer 1y ahead", "#1565c0", smooth=False),
                    LineConfig("infl_exp_consumer_5y", "Consumer 5y ahead", "#7b1fa2", smooth=False),
                ],
                default_years=10,
                line_shape="linear",
                date_fmt="%b %Y",
                footnote="Bank of Canada Survey of Consumer Expectations (CSCE), mean expected inflation 1 year and 5 years ahead. Quarterly. The 2% inflation target is the policy anchor; material drift in 5-year-ahead expectations would signal anchor slippage.",
            ),
            MultiLineSpec(
                title="Business Inflation Expectations",
                lines=[
                    LineConfig("bos_dist_below1", "<1%",  "#1565c0", smooth=False),
                    LineConfig("bos_dist_1to2",   "1–2%", "#4fc3f7", smooth=False),
                    LineConfig("bos_dist_2to3",   "2–3%", "#2e7d32", smooth=False),
                    LineConfig("bos_dist_above3", ">3%",  "#c62828", smooth=False),
                    LineConfig("infl_exp_above3", ">3% (most-current vintage)", "#6d4c41", smooth=False, visible=False),
                ],
                default_years=10,
                line_shape="linear",
                date_fmt="%b %Y",
                footnote="Bank of Canada Business Outlook Survey: share of firms expecting CPI inflation to fall in each band over the next two years. The four buckets sum to ~100%. The 2–3% band is target-consistent; sustained mass in >3% signals anchoring stress on the upside. \"Most-current vintage\" is the same >3% concept but published faster than the vintage-aligned distribution; off by default.",
            ),
            ChartSpec(
                series="gdp_monthly",
                title="Real GDP (monthly)",
                frequency="monthly",
                color="#1565c0",
                default_transform="level",
                default_years=10,
                hover_decimals=3,
                unit_label="C$ trillions",
                transform_unit_labels={
                    "level": "C$ trillions",
                    "mom":   "%",
                    "ar_3m": "%",
                    "yoy":   "%",
                },
                footnote="Statistics Canada Table 36-10-0434: Monthly real GDP at basic prices, all industries, chained 2017 dollars, SAAR. Released roughly two months after the reference month with significant subsequent revisions. Industry overlays (off by default): toggle via legend.",
                overlays=[
                    OverlayConfig("gdp_industry_goods",        "Goods-producing",  "#388e3c"),
                    OverlayConfig("gdp_industry_services",     "Services-producing", "#00897b"),
                    OverlayConfig("gdp_industry_manufacturing","Manufacturing",     "#7b1fa2"),
                    OverlayConfig("gdp_industry_mining_oil",   "Mining & oil/gas",  "#d84315"),
                ],
                overlay_level_alt_unit_label="C$ billions",
                overlay_level_alt_scale=1000.0,
            ),
            StackedBarSpec(
                title="GDP Growth Contributions",
                lines=[
                    LineConfig("gdp_contrib_consumption", "Consumption",   "#1565c0", smooth=False),
                    LineConfig("gdp_contrib_investment",  "Investment",    "#00897b", smooth=False),
                    LineConfig("gdp_contrib_govt",        "Government",    "#7b1fa2", smooth=False),
                    LineConfig("gdp_contrib_exports",     "Exports",       "#388e3c", smooth=False),
                    LineConfig("gdp_contrib_imports",     "Less: imports", "#d84315", smooth=False),
                    LineConfig("gdp_contrib_inventories", "Inventories",   "#fdd835", smooth=False),
                ],
                overlay=LineConfig("gdp_total_contribution", "Headline GDP (AR)", "#212121"),
                default_years=2,
                date_fmt="%b %Y",
                ticksuffix="pp",
                unit_label="Percentage-point contributions to annualized Q/Q growth",
                footnote="Statistics Canada Table 36-10-0104. Bars are component contributions to annualized Q/Q real GDP growth; 'Less: imports' is sign-flipped so positive = imports fell. Headline GDP line is the published total contribution (vector 79448580). The StatsCan daily release reports non-annualized Q/Q (≈ AR ÷ 4). The small gap between the bar sum and the headline is non-profits plus statistical discrepancy, which this dashboard does not break out.",
            ),
            MultiLineSpec(
                title="Unemployment & Job Vacancies",
                lines=[
                    LineConfig("unemployment_rate",     "Unemployment",          "#1565c0", smooth=False),
                    LineConfig("job_vacancy_rate_12m",  "Vacancies (12M Avg)",   "#00897b", smooth=False),
                    LineConfig("job_vacancy_rate",      "Vacancies (raw NSA)",   "#80cbc4", smooth=False, visible=False),
                ],
                alt_lines=[
                    LineConfig("unemployment_level",     "Unemployment",          "#1565c0", smooth=False),
                    LineConfig("job_vacancy_level_12m",  "Vacancies (12M Avg)",   "#00897b", smooth=False),
                    LineConfig("job_vacancy_level",      "Vacancies (raw NSA)",   "#80cbc4", smooth=False, visible=False),
                ],
                primary_label="Rate",
                alt_label="Level",
                ticksuffix="%",
                hoverformat=".1f",
                alt_ticksuffix="M",
                alt_hoverformat=".2f",
                default_years=10,
                line_shape="linear",
                date_fmt="%b %Y",
                unit_label="%",
                alt_unit_label="millions of persons",
                footnote="Beveridge tightness pair. Unemployment: StatsCan Table 14-10-0287, monthly SA, 15+. Vacancies: StatsCan Table 14-10-0371, monthly NSA (no SA series exists), total economy; series begins 2015. Vacancies displayed as a 12M moving average by default to denoise the seasonal Sep-peak/Dec-trough; raw NSA available as a legend toggle. Rate view shares % units; Level view shares millions of persons (both natively in persons/thousands and scaled at fetch). High vacancies with low unemployment = tight labour market; the V/U ratio is the BoC's preferred composite tightness read.",
            ),
            WageSpec(
                title="Wage Growth",
                footnote="Year-over-year %. LFS: average hourly wages. SEPH: average weekly earnings, all industries. LFS-Micro: BoC composition-adjusted measure. Services CPI overlay for wage-price context.",
            ),
            MultiLineSpec(
                title="Labour Utilization",
                lines=[
                    LineConfig("employment_rate",    "Employment rate",    "#1565c0"),
                    LineConfig("participation_rate", "Participation rate", "#7b1fa2"),
                ],
                ticksuffix="%",
                hoverformat=".1f",
                default_years=10,
                line_shape="linear",
                date_fmt="%b %Y",
                unit_label="%",
                footnote="Statistics Canada Table 14-10-0287, seasonally adjusted, population 15+. Employment rate = employed / working-age population; participation rate = labour force / working-age population. Both are part of the BoC's multi-indicator labour-market benchmark (SAN 2025-17, June 2025). Tracking both isolates labour-supply moves (participation) from labour-demand moves (employment): falling employment with stable participation = layoffs absorbing slack; falling participation with stable employment = workers leaving the labour force.",
            ),
            ChartSpec(
                series="unit_labour_cost",
                title="Unit Labour Costs",
                frequency="quarterly",
                color="#c62828",
                default_transform="yoy",
                default_years=10,
                hover_decimals=2,
                unit_label="index",
                transform_unit_labels={
                    "level":  "index",
                    "qoq":    "%",
                    "qoq_ar": "%",
                    "yoy":    "%",
                },
                footnote="Statistics Canada Table 36-10-0206: Unit labour costs, business sector, Canada, quarterly seasonally adjusted (index, 2017=100). ULC = nominal labour compensation per unit of real output, i.e. wage growth net of productivity. The identity wage growth − productivity = ULC growth means ULC growth is a more direct read on whether labour costs are consistent with the 2% inflation target — sustained ULC growth materially above 2% with stable margins points toward goods/services price pressure. Default view is Y/Y; level is the underlying index.",
            ),
            MultiLineSpec(
                title="Housing Starts",
                # Three legend-as-toggle lines: Level, 3M Avg, 12M Avg.
                # Level off by default — CMHC, BoC MPR, and analyst notes read starts via
                # smoothed paths because the raw monthly is too noisy to read trend.
                # No Y/Y / M/M transforms exposed — growth rates of a noisy SAAR series
                # aren't reported in mainstream housing analysis.
                lines=[
                    LineConfig("housing_starts",     "Level (monthly)", "#90a4ae", visible=False),
                    LineConfig("housing_starts_3m",  "3M Avg",          "#1565c0", visible=True),
                    LineConfig("housing_starts_12m", "12M Avg",         "#7b1fa2", visible=False),
                ],
                ticksuffix="",
                hoverformat=".0f",
                default_years=10,
                date_fmt="%b %Y",
                unit_label="thousands SAAR",
                footnote="CMHC housing starts, Canada total, seasonally adjusted at annualized rates (thousands). Three views: raw monthly level, 3M moving average (CMHC standard short-trend smoother), 12M moving average (cycle view). Long-run average since 1977: ~194k. CMHC affordability-restoring pace: 430–500k/year. Growth rates aren't shown — Y/Y / M/M of a noisy SAAR series isn't read in practice.",
            ),
            MultiLineSpec(
                title="Housing Prices",
                # Two series, two views: Y/Y (default — the news number) and Index (rebased
                # to a common base for direct level comparison). Toggle is button-bar above
                # the chart because it changes y-axis units globally for both lines.
                lines=[
                    LineConfig("nhpi_yoy",         "NHPI (new homes)",       "#7b1fa2"),
                    LineConfig("crea_mls_hpi_yoy", "CREA MLS HPI (resale)",  "#1565c0"),
                ],
                alt_lines=[
                    LineConfig("nhpi_rebased",         "NHPI (new homes)",      "#7b1fa2"),
                    LineConfig("crea_mls_hpi_rebased", "CREA MLS HPI (resale)", "#1565c0"),
                ],
                primary_label="Y/Y",
                alt_label="Index",
                default_alt=False,
                ticksuffix="%",
                hoverformat=".1f",
                alt_ticksuffix="",
                alt_hoverformat=".1f",
                default_years=10,
                date_fmt="%b %Y",
                unit_label="Y/Y %",
                alt_unit_label="Index, Jan 2020 = 100",
                footnote="Y/Y: year-over-year % change in the underlying index. Index: each series rebased to Jan 2020 = 100 so the level paths are directly comparable. NHPI: StatsCan contractor-reported prices, new single-family homes, 27 CMAs (native base Dec 2016 = 100). CREA MLS HPI: BoC Financial Vulnerability Indicators, resale-dominant hedonic (native base 2019 = 100; available from 2014). Re-indexing happens at build time; source CSVs are unmodified.",
            ),
            ChartSpec(
                series="residential_permits_b",
                title="Residential Building Permits",
                frequency="monthly",
                color="#00897b",
                default_transform="level",
                default_years=None,  # Max — series only starts Jan 2018, so a 10Y window wastes space
                hover_decimals=1,
                unit_label="C$ billions",
                footnote="StatsCan Table 34-10-0292: total residential building permits, current C$ billions, seasonally adjusted. Source CSV is in $thousands; displayed in $B at build time for legibility. Leading indicator for housing construction: blended lag ~9–15 months (type-dependent — single-detached 2–10 months, multi-unit/high-rise 9–15+ months per CMHC Spring 2026). Series begins Jan 2018; default range is Max because the series only has ~8 years of history.",
            ),
            ChartSpec(
                series="housing_affordability",
                title="Housing Affordability",
                frequency="quarterly",
                color="#ef6c00",
                static=True,
                default_years=10,
                hover_decimals=3,
                unit_label="ratio",
                footnote="BoC housing affordability index (INDINF_AFFORD_Q): ratio of mortgage payment to household income. Higher = less affordable. Historical range 2000–2025: 0.28 (most affordable, 2002) to 0.55 (least affordable, Q3 2023). Incorporates MLS resale prices, qualifying mortgage rates, and NIAE income data.",
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
    PageSpec(
        title="Monetary Policy — Deep Dive",
        tagline="Term structure, real rates, balance-sheet detail, peer comparison",
        output_file="policy.html",
        is_deep_dive=True,
        sections={
            0: "policy_dd_yield_curve",
            2: "policy_dd_real_rates",
            3: "policy_dd_corra",
            4: "policy_dd_assets",
            5: "policy_dd_liabilities",
            6: "policy_dd_peers",
        },
        charts=[
            MultiLineSpec(
                title="GoC Yield Curve",
                lines=[
                    LineConfig("yield_2yr",  "2Y",  "#1565c0"),
                    LineConfig("yield_5yr",  "5Y",  "#2e7d32"),
                    LineConfig("yield_10yr", "10Y", "#e65100"),
                    LineConfig("yield_30yr", "30Y", "#6a1b9a"),
                ],
                ticksuffix="%",
                smooth_window=20,
                default_years=10,
                footnote="GoC benchmark bond yields. Source: Bank of Canada Valet.",
            ),
            MultiLineSpec(
                title="2Y–10Y Spread",
                lines=[
                    LineConfig("yield_10y_2y_spread", "10Y − 2Y", "#e65100"),
                ],
                ticksuffix="%",
                smooth_window=20,
                default_years=10,
                footnote="10-year minus 2-year GoC yield. Negative (inverted) has historically preceded Canadian recessions.",
            ),
            MultiLineSpec(
                title="Real Policy Rates (ex-post)",
                lines=[
                    LineConfig("real_overnight_rate", "Real overnight", "#1565c0"),
                    LineConfig("real_2yr_monthly",    "Real 2Y (month-end)", "#2e7d32"),
                ],
                ticksuffix="%",
                default_years=10,
                footnote="Nominal rate minus trailing headline CPI Y/Y. Ex-post measure; reflects backward-looking realized inflation, not forward expectations.",
            ),
            MultiLineSpec(
                title="CORRA vs Overnight Rate Target",
                lines=[
                    LineConfig("corra_daily",         "CORRA",         "#1565c0"),
                    LineConfig("overnight_rate_daily", "Target (daily)", "#c62828"),
                ],
                ticksuffix="%",
                smooth_window=20,
                default_years=2,
                footnote="CORRA (Canadian Overnight Repo Rate Average) vs the BoC overnight rate target. Under the floor system (April 2022–), CORRA trades at or just above the deposit rate.",
            ),
            MultiLineSpec(
                title="BoC Assets",
                lines=[
                    LineConfig("boc_total_assets", "Total assets",     "#1565c0"),
                    LineConfig("boc_goc_bonds",    "GoC bonds (held)", "#42a5f5"),
                ],
                ticksuffix="",
                hoverformat=".0f",
                default_years=10,
                footnote="C$ billions. Source: Bank of Canada Statement of Financial Position, weekly.",
            ),
            MultiLineSpec(
                title="BoC Liabilities — Settlement Balances",
                lines=[
                    LineConfig("boc_settlement_balances", "Settlement balances", "#6a1b9a"),
                ],
                ticksuffix="",
                hoverformat=".0f",
                default_years=10,
                footnote="C$ billions. Cash banks hold overnight at the BoC. Post-QT steady-state target: $20–60B (Gravelle, March 2024).",
            ),
            MultiLineSpec(
                title="Peer Central Bank Policy Rates",
                lines=[
                    LineConfig("overnight_rate", "BoC",  "#1565c0"),
                    LineConfig("fed_funds",       "Fed",  "#c62828"),
                    LineConfig("ecb_rate",        "ECB",  "#2e7d32"),
                    LineConfig("boe_rate",        "BoE",  "#e65100"),
                    LineConfig("rba_rate",        "RBA",  "#6a1b9a"),
                ],
                ticksuffix="%",
                line_shape="hv",
                default_years=10,
                date_fmt="%b %Y",
                footnote="BoC overnight rate; Fed funds target midpoint; ECB deposit facility rate (FRED ECBDFR); BoE Bank Rate and RBA cash rate (OECD/FRED monthly series).",
            ),
        ],
    ),
    PageSpec(
        title="Housing Market — Deep Dive",
        tagline="Construction pipeline, affordability dynamics, and demand signals",
        output_file="housing.html",
        is_deep_dive=True,
        sections={
            0: "housing_dd_activity",
            1: "housing_dd_mortgage",
            2: "housing_dd_pipeline",
            4: "housing_dd_affordability",
            5: "housing_dd_renewal",
        },
        charts=[
            MultiLineSpec(
                title="CREA Sales Activity",
                lines=[
                    LineConfig("crea_snlr",    "Sales-to-New-Listings (%)",  "#1565c0"),
                    LineConfig("crea_resales", "Resales Index (2019=100)",   "#7b1fa2", visible=False),
                ],
                ticksuffix="",
                hoverformat=".1f",
                default_years=10,
                line_shape="linear",
                date_fmt="%b %Y",
                unit_label="",
                footnote="CREA/BoC FVI. SNLR: above 65 = seller's market; below 45 = buyer's market; 45–65 = balanced. Resales Index: 2019 = 100 (different scale from SNLR — toggle to view alongside tightness).",
            ),
            MultiLineSpec(
                title="5-Year Mortgage Rate vs 5-Year GoC Bond",
                lines=[
                    LineConfig("mortgage_rate_5yr",           "5Y Mortgage",           "#c62828"),
                    LineConfig("yield_5yr",                   "5Y GoC Yield",          "#1565c0"),
                    LineConfig("mortgage_5yr_goc_5yr_spread", "Mortgage − GoC Spread", "#7b1fa2", visible=False, smooth=False),
                ],
                ticksuffix="%",
                hoverformat=".2f",
                smooth_window=4,
                default_years=10,
                date_fmt="%b %d, %Y",
                unit_label="%",
                footnote="5-year conventional mortgage rate (BoC Valet V80691335, weekly) vs 5-year GoC benchmark bond yield (daily). Toggle spread to see the lender risk premium — typically 150–200 bp. Spread compression or widening reflects lender credit conditions and pass-through of GoC yield moves into mortgage pricing.",
            ),
            ChartSpec(
                series="units_under_construction",
                title="Units Under Construction",
                frequency="monthly",
                color="#00897b",
                default_transform="level",
                default_years=10,
                hover_decimals=0,
                unit_label="thousands",
                footnote="CMHC housing units under construction, Canada total, SAAR (thousands) — StatsCan Table 34-10-0158. Distinct from starts: measures the active construction stock at a point in time. Post-2020 surge reflects apartment-heavy starts mix (longer build timelines vs single-detached). Vector v52300170: Tier 2 — inferred from value magnitude matching CMHC data; getSeriesInfoFromVector API unavailable.",
            ),
            MultiLineSpec(
                title="Resale Activity by CMA",
                lines=[
                    LineConfig("crea_resales_toronto",   "Toronto",   "#1565c0"),
                    LineConfig("crea_resales_vancouver",  "Vancouver", "#c62828"),
                    LineConfig("crea_resales_calgary",    "Calgary",   "#e65100"),
                ],
                ticksuffix="",
                hoverformat=".0f",
                default_years=10,
                line_shape="linear",
                date_fmt="%b %Y",
                unit_label="units (12M rolling)",
                footnote="CREA/BoC FVI: 12-month rolling resale counts by CMA (units). Toronto and Vancouver account for the majority of Canada's supply gap; Calgary has outperformed since 2022 on in-migration and relative affordability.",
            ),
            MultiLineSpec(
                title="Housing Starts — CMHC Supply Target Context",
                lines=[
                    LineConfig("housing_starts",     "Level (monthly)", "#90a4ae", visible=False),
                    LineConfig("housing_starts_3m",  "3M Avg",          "#1565c0", visible=True),
                    LineConfig("housing_starts_12m", "12M Avg",         "#7b1fa2", visible=False),
                ],
                ticksuffix="",
                hoverformat=".0f",
                default_years=10,
                date_fmt="%b %Y",
                unit_label="thousands SAAR",
                footnote="CMHC housing starts, Canada total, SAAR (thousands). CMHC's June 2025 Housing Supply Report targets 430,000–480,000 starts per year through 2035 to restore affordability (4.8M units needed). Current pace of ~235k is roughly half the target. Long-run average since 1977: ~194k.",
            ),
            MortgageShockSpec(
                title="Mortgage Renewal Payment Shock",
                footnote="BoC SAN 2025-21 (May 2025). ~15–20% of 5-year fixed holders face payment increases above 20% at renewal. Variable-rate fixed-payment holders already absorbed rate increases through extended amortization; the 54% figure is the share facing a contractual reset. Median payment increase of ~34% applies to mortgages originated 2020–2022 renewing through 2027.",
            ),
        ],
    ),
    PageSpec(
        title="Inflation — Deep Dive",
        tagline="Component-level decomposition and persistence detail",
        output_file="inflation.html",
        is_deep_dive=True,
        sections={
            1: "inflation_dd_core",
            2: "inflation_dd_contrib",
        },
        charts=[
            # Chart 1 placeholder
            MultiLineSpec(
                title="Headline vs Ex-Indirect-Taxes",
                lines=[
                    LineConfig("cpi_all_items", "Headline", "#1565c0"),
                ],
                ticksuffix="%",
                default_years=10,
                footnote="[Coming soon] Headline CPI Y/Y next to a CPI ex-indirect-taxes series. The carbon-tax repeal in early 2025 carved roughly 0.6 pp out of headline; this overlay shows the underlying inflation impulse independent of policy moves.",
            ),
            # Chart 2: Live
            MultiLineSpec(
                title="Core Inflation — Individual Measures",
                lines=[
                    LineConfig("cpi_trim",    "CPI-trim",    "#1565c0"),
                    LineConfig("cpi_median",  "CPI-median",  "#546e7a", visible=False),
                    LineConfig("cpi_common",  "CPI-common",  "#78909c", visible=False),
                    LineConfig("cpix",        "CPIX",        "#ef6c00", visible=False),
                    LineConfig("cpixfet",     "CPIXFET",     "#00897b", visible=False),
                ],
                ticksuffix="%",
                default_years=10,
                footnote="CPI-trim and CPI-median are BoC staff measures published monthly. CPI-common is estimated via common-component extraction and is the smoothest of the three; it tends to lag turning points relative to trim and median.",
            ),
            # Chart 3: Contributions (Requires custom builder or data prep)
            MultiLineSpec(
                title="CPI Component Contributions",
                lines=[], # Needs implementation
                footnote="[Coming soon] 60-component decomposition with per-component contribution. Rotation matters: shelter has dominated 2023-2024; transportation took over in early 2025.",
            ),
        ],
    ),
    PageSpec(
        title="Labour Market — Deep Dive",
        tagline="Direct-indicator triangulation, demographic decomposition, the Beveridge curve",
        output_file="labour.html",
        is_deep_dive=True,
        sections={
            0: "labour_dd_tightness",
            1: "labour_dd_layoffs",
            2: "labour_dd_r_indicators",
            4: "labour_dd_ei",
            5: "labour_dd_demographics",
            6: "labour_dd_postings",
        },
        charts=[
            # Beveridge Curve (already has a builder, we'll wrap it or call it)
            # For now, use the placeholder sections as defined in design doc
            MultiLineSpec(
                title="Unemployment by Age",
                lines=[
                    LineConfig("youth_unemployment_rate",     "Youth (15–24)",    "#c62828"),
                    LineConfig("prime_age_unemployment_rate", "Prime-age (25–54)", "#1565c0"),
                    LineConfig("unemployment_rate",           "Total (15+)",       "#546e7a", visible=False),
                ],
                ticksuffix="%",
                default_years=10,
                footnote="StatsCan Table 14-10-0287, monthly SA. Youth unemployment is highly cyclical and has risen faster than prime-age during the 2024–2025 cooling. Tracking the gap identifies where slack is most acute.",
            ),
            # Chart 2: Beveridge Curve - handled via body_fn or we convert it to a Spec
            # For simplicity, we'll keep it as a custom section or add a new Spec type
            MultiLineSpec(
                title="LFS Reason for Unemployment — Job-Loser Share",
                lines=[
                    LineConfig("unemployment_rate", "Total UR (reference)", "#90a4ae"),
                ],
                ticksuffix="%",
                default_years=10,
                footnote="[Coming soon] StatsCan Table 14-10-0125. Share of unemployed citing job loss vs. leaving or re-entering. Rising job-loser share is the cleanest layoff signal.",
            ),
            MultiLineSpec(
                title="LFS R-Indicators",
                lines=[
                    LineConfig("unemployment_rate", "R3 (Official + Waiting)", "#1565c0"),
                ],
                ticksuffix="%",
                default_years=10,
                footnote="[Coming soon] StatsCan Table 14-10-0074. R3 (official + waiting), R7 (+ marginally attached), R8 (+ involuntary part-time). Gap between R8 and R3 widens when underutilization grows on margins the headline rate misses.",
            ),
            MultiLineSpec(
                title="EI Claims vs Beneficiaries",
                lines=[
                    LineConfig("unemployment_rate", "Unemployment (ref)", "#90a4ae"),
                ],
                ticksuffix="",
                default_years=5,
                footnote="[Coming soon] StatsCan Table 14-10-0010 family. EI initial claims is the highest-frequency real-time labour signal. Beneficiaries lag claims by ~2 weeks.",
            ),
            MultiLineSpec(
                title="Indeed Job Postings Index",
                lines=[
                    LineConfig("job_vacancy_rate", "StatsCan Vacancy Rate", "#00897b"),
                ],
                ticksuffix="%",
                default_years=None,
                footnote="[Coming soon] Indeed Hiring Lab Canada postings (baseline Feb 1 2020 = 100). Secondary Y-axis support in build.py will allow overlaying this index with the official vacancy rate.",
            ),
        ],
    ),
    PageSpec(
        title="GDP & Activity — Deep Dive",
        tagline="Productivity, capacity, and the output gap",
        output_file="gdp.html",
        is_deep_dive=True,
        sections={
            2: "gdp_dd_gap",
            3: "gdp_dd_productivity",
            4: "gdp_dd_capacity",
            5: "gdp_dd_hours",
        },
        charts=[
            # Note: GDP potential and gap panels are currently using native builders.
            # I'll keep them as ChartSpecs or MultiLineSpecs if possible, or add them as native.
            # For now, I'll use placeholders that mention they are coming.
            MultiLineSpec(
                title="Real GDP vs Potential (HP Filter)",
                lines=[
                    LineConfig("gdp_monthly", "Real GDP", "#1565c0"),
                ],
                ticksuffix="",
                unit_label="C$ trillions",
                default_years=10,
                footnote="Potential GDP estimated via HP filter (λ=129,600). Trend-only estimate; does not incorporate structural model inputs. Level view in C$ trillions.",
            ),
            MultiLineSpec(
                title="Output Gap (HP Filter Estimate)",
                lines=[
                    LineConfig("gdp_monthly", "Gap (%)", "#1565c0"),
                ],
                ticksuffix="%",
                default_years=10,
                footnote="Mechanical HP-filter estimate. BoC publishes official range quarterly in MPR; typically -1.5% to +0.5% in recent cycles.",
            ),
            MultiLineSpec(
                title="Productivity Decomposition",
                lines=[], # Placeholder
                footnote="[Coming soon] Real GDP per hour worked. Canadian productivity has been structurally weak since 2015; trend divergence vs US is a key BoC concern.",
            ),
        ],
    ),
    PageSpec(
        title="Financial Conditions — Deep Dive",
        tagline="Multilateral CAD, credit spreads, FX risk premium, terms-of-trade",
        output_file="financial.html",
        is_deep_dive=True,
        sections={
            1: "financial_dd_ceer",
            2: "financial_dd_spreads",
            3: "financial_dd_equity",
            4: "financial_dd_fx_risk",
            6: "financial_dd_wcs",
        },
        charts=[
            ChartSpec(
                series="usdcad",
                title="USD/CAD (Bilateral)",
                frequency="daily",
                color="#1565c0",
                default_years=10,
                unit_label="CAD per USD",
                footnote="Bilateral exchange rate. Higher = weaker CAD.",
            ),
            MultiLineSpec(
                title="CEER (Trade-Weighted CAD)",
                lines=[], # Placeholder
                footnote="[Coming soon] BoC's Canadian-Dollar Effective Exchange Rate. Methodologically better for inflation pass-through than bilateral USDCAD.",
            ),
            MultiLineSpec(
                title="WTI − WCS Differential",
                lines=[
                    LineConfig("wti", "WTI (ref)", "#90a4ae"),
                    LineConfig("wcs", "WCS",      "#7b1fa2"),
                ],
                ticksuffix="",
                hoverformat=".2f",
                default_years=10,
                ymin=0,
                unit_label="USD/barrel",
                footnote="Differential between US and Canadian crude benchmarks. Spread compression since May 2024 reflects TMX capacity additions.",
            ),
        ],
    ),
    PageSpec(
        title="Trade & External Sector — Deep Dive",
        tagline="Canada's trade exposure, bilateral flows, and terms-of-trade conditions",
        output_file="trade.html",
        is_deep_dive=True,
        sections={},
        charts=[
            MultiLineSpec(
                title="Goods Exports by Category",
                lines=[],
                footnote="[Coming soon] StatsCan Table 12-10-0011 — goods exports by category. Concentration in energy and automotive is the structural vulnerability.",
            ),
            MultiLineSpec(
                title="Canada–US Bilateral Trade Balance",
                lines=[],
                footnote="[Coming soon] Monthly goods trade balance with the United States. Primary channel for tariff-shock transmission.",
            ),
        ],
    ),
    PageSpec(
        title="Demographics & Labour Supply — Deep Dive",
        tagline="Population dynamics, immigration, and structural capacity constraints",
        output_file="demographics.html",
        is_deep_dive=True,
        sections={},
        charts=[
            MultiLineSpec(
                title="Population Growth by Component",
                lines=[],
                footnote="[Coming soon] Natural increase vs international migration. Migration is now the dominant driver of labour-force growth.",
            ),
            MultiLineSpec(
                title="Labour Force by Age Group",
                lines=[
                    LineConfig("youth_unemployment_rate",     "Youth (15–24)",    "#c62828"),
                    LineConfig("prime_age_unemployment_rate", "Prime-age (25–54)", "#1565c0"),
                ],
                ticksuffix="%",
                default_years=10,
                footnote="Age-group unemployment rates. Repeated here from the Labour deep-dive for demographic context.",
            ),
        ],
    ),
]


# ── Main ──────────────────────────────────────────────────────────────────────

# Map from derived-series name (used in chart specs) to the source CSV series that
# must be loaded for _add_derived_series to compute it. Add a new entry here when a
# chart references a series computed at build time from one or more raw CSVs.
_DERIVED_SERIES_SOURCES: dict[str, list[str]] = {
    "bocfed_spread":         ["overnight_rate", "fed_funds"],
    "can2y_overnight_spread": ["yield_2yr", "overnight_rate"],
    "can_us_2y_spread":      ["yield_2yr", "us_2yr"],
    "nhpi_yoy":              ["new_housing_price_index"],
    "nhpi_rebased":          ["new_housing_price_index"],
    "crea_mls_hpi_yoy":      ["crea_mls_hpi"],
    "crea_mls_hpi_rebased":  ["crea_mls_hpi"],
    "housing_starts_3m":     ["housing_starts"],
    "housing_starts_12m":    ["housing_starts"],
    "residential_permits_b": ["residential_permits"],
    "job_vacancy_rate_12m":  ["job_vacancy_rate"],
    "job_vacancy_level_12m": ["job_vacancy_level"],
    # Policy deep-dive derived series
    "yield_10y_2y_spread":   ["yield_10yr", "yield_2yr"],
    "real_overnight_rate":   ["overnight_rate", "cpi_all_items_nsa"],
    "real_2yr_monthly":      ["yield_2yr", "cpi_all_items_nsa"],
    # Housing deep-dive derived series
    "mortgage_5yr_goc_5yr_spread": ["mortgage_rate_5yr", "yield_5yr"],
}


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


def _add_derived_series(data: dict[str, pd.DataFrame]) -> None:
    """Compute derived series (spreads, etc.) and add to data dict so chart specs
    can reference them by name like any other series."""
    # BoC overnight − Fed funds spread, monthly cadence aligned to overnight_rate
    if "overnight_rate" in data and "fed_funds" in data:
        ov = data["overnight_rate"].sort_values("date").reset_index(drop=True)
        ff = data["fed_funds"].sort_values("date").rename(columns={"value": "fed"}).reset_index(drop=True)
        merged = pd.merge_asof(ov, ff, on="date", direction="backward")
        spread = pd.DataFrame({
            "date":  merged["date"],
            "value": merged["value"] - merged["fed"],
        }).dropna().reset_index(drop=True)
        data["bocfed_spread"] = spread

    # Canada 2Y − BoC overnight spread, daily cadence with overnight forward-filled
    if "yield_2yr" in data and "overnight_rate" in data:
        y2 = data["yield_2yr"].sort_values("date").reset_index(drop=True)
        ov = data["overnight_rate"].sort_values("date").rename(columns={"value": "ov"}).reset_index(drop=True)
        merged = pd.merge_asof(y2, ov, on="date", direction="backward")
        spread = pd.DataFrame({
            "date":  merged["date"],
            "value": merged["value"] - merged["ov"],
        }).dropna().reset_index(drop=True)
        data["can2y_overnight_spread"] = spread

    # Canada 2Y − US 2Y spread (daily, both daily; align on Canadian dates)
    if "yield_2yr" in data and "us_2yr" in data:
        cy = data["yield_2yr"].sort_values("date").reset_index(drop=True)
        uy = data["us_2yr"].sort_values("date").rename(columns={"value": "us"}).reset_index(drop=True)
        merged = pd.merge_asof(cy, uy, on="date", direction="backward")
        spread = pd.DataFrame({
            "date":  merged["date"],
            "value": merged["value"] - merged["us"],
        }).dropna().reset_index(drop=True)
        data["can_us_2y_spread"] = spread

    # Housing price Y/Y series — pre-computed for the Housing Prices MultiLineSpec.
    # Both NHPI and CREA MLS HPI are stored as levels; Y/Y % makes them directly comparable.
    # Index-rebased copies (Jan 2020 = 100) feed the Index toggle on the same chart.
    _HOUSING_INDEX_BASE = pd.Timestamp("2020-01-01")
    if "new_housing_price_index" in data:
        df = data["new_housing_price_index"].sort_values("date").reset_index(drop=True)
        yoy = df["value"].pct_change(12) * 100
        data["nhpi_yoy"] = pd.DataFrame({"date": df["date"], "value": yoy}).dropna().reset_index(drop=True)
        base_row = df.loc[df["date"] == _HOUSING_INDEX_BASE, "value"]
        if not base_row.empty and base_row.iloc[0] != 0:
            base_val = float(base_row.iloc[0])
            data["nhpi_rebased"] = pd.DataFrame({
                "date": df["date"],
                "value": df["value"] / base_val * 100.0,
            }).dropna().reset_index(drop=True)

    if "crea_mls_hpi" in data:
        df = data["crea_mls_hpi"].sort_values("date").reset_index(drop=True)
        yoy = df["value"].pct_change(12) * 100
        data["crea_mls_hpi_yoy"] = pd.DataFrame({"date": df["date"], "value": yoy}).dropna().reset_index(drop=True)
        base_row = df.loc[df["date"] == _HOUSING_INDEX_BASE, "value"]
        if not base_row.empty and base_row.iloc[0] != 0:
            base_val = float(base_row.iloc[0])
            data["crea_mls_hpi_rebased"] = pd.DataFrame({
                "date": df["date"],
                "value": df["value"] / base_val * 100.0,
            }).dropna().reset_index(drop=True)

    # Housing Starts smoothed series for the legend-as-toggles design.
    # Three lines coexist: raw level (noisy month-to-month), 3M moving average (CMHC standard
    # short-trend smoother), 12M moving average (strips remaining seasonality + cycle noise).
    if "housing_starts" in data:
        df = data["housing_starts"].sort_values("date").reset_index(drop=True)
        for win, name in [(3, "housing_starts_3m"), (12, "housing_starts_12m")]:
            sm = df["value"].rolling(win, min_periods=max(1, win // 2)).mean()
            data[name] = pd.DataFrame({"date": df["date"], "value": sm}).dropna().reset_index(drop=True)

    # Residential permits in C$ billions (source CSV is in $thousands; / 1e6).
    # Display in $B avoids the seven-digit zero strings that $k produces.
    if "residential_permits" in data:
        df = data["residential_permits"].sort_values("date").reset_index(drop=True)
        data["residential_permits_b"] = pd.DataFrame({
            "date": df["date"],
            "value": df["value"] / 1_000_000.0,
        }).dropna().reset_index(drop=True)

    # Job vacancies 12-month moving averages: source vectors are monthly NSA (no SA series
    # exists), so a 12M MA denoises the seasonal Sep-peak/Dec-trough pattern. Default-visible
    # line on the Unemployment & Vacancies chart; raw NSA available as a legend toggle.
    for src in ("job_vacancy_rate", "job_vacancy_level"):
        if src in data:
            df = data[src].sort_values("date").reset_index(drop=True)
            sm = df["value"].rolling(12, min_periods=6).mean()
            data[src + "_12m"] = pd.DataFrame({"date": df["date"], "value": sm}).dropna().reset_index(drop=True)

    # Policy deep-dive: 10Y–2Y GoC yield spread (daily)
    if "yield_10yr" in data and "yield_2yr" in data:
        y10 = data["yield_10yr"].sort_values("date").reset_index(drop=True)
        y2  = data["yield_2yr"].sort_values("date").rename(columns={"value": "y2"}).reset_index(drop=True)
        merged = pd.merge_asof(y10, y2, on="date", direction="backward")
        data["yield_10y_2y_spread"] = pd.DataFrame({
            "date":  merged["date"],
            "value": merged["value"] - merged["y2"],
        }).dropna().reset_index(drop=True)

    # Policy deep-dive: ex-post real rates (nominal minus trailing CPI Y/Y, monthly)
    if "overnight_rate" in data and "cpi_all_items_nsa" in data:
        cpi = data["cpi_all_items_nsa"].sort_values("date").reset_index(drop=True)
        cpi_yoy = cpi["value"].pct_change(12) * 100
        cpi_df = pd.DataFrame({
            "ym":      cpi["date"].values.astype("datetime64[M]"),
            "cpi_yoy": cpi_yoy,
        }).dropna()
        ov = data["overnight_rate"].sort_values("date").reset_index(drop=True)
        ov_ym = ov.copy()
        ov_ym["ym"] = ov["date"].values.astype("datetime64[M]")
        merged = pd.merge(ov_ym[["date", "value", "ym"]], cpi_df, on="ym", how="inner")
        data["real_overnight_rate"] = pd.DataFrame({
            "date":  merged["date"],
            "value": merged["value"] - merged["cpi_yoy"],
        }).dropna().reset_index(drop=True)

        if "yield_2yr" in data:
            y2 = data["yield_2yr"].sort_values("date").set_index("date")
            y2_m = y2["value"].resample("ME").last().reset_index()
            y2_m["ym"] = y2_m["date"].values.astype("datetime64[M]")
            merged2 = pd.merge(y2_m[["date", "value", "ym"]], cpi_df, on="ym", how="inner")
            data["real_2yr_monthly"] = pd.DataFrame({
                "date":  merged2["date"],
                "value": merged2["value"] - merged2["cpi_yoy"],
            }).dropna().reset_index(drop=True)

    # Housing deep-dive: 5Y conventional mortgage minus 5Y GoC yield spread (weekly aligned)
    if "mortgage_rate_5yr" in data and "yield_5yr" in data:
        mtg = data["mortgage_rate_5yr"].sort_values("date").reset_index(drop=True)
        goc = data["yield_5yr"].sort_values("date").rename(columns={"value": "goc"}).reset_index(drop=True)
        merged = pd.merge_asof(mtg, goc, on="date", direction="backward")
        data["mortgage_5yr_goc_5yr_spread"] = pd.DataFrame({
            "date":  merged["date"],
            "value": merged["value"] - merged["goc"],
        }).dropna().reset_index(drop=True)


def build_page(page: PageSpec, data: dict[str, pd.DataFrame]) -> None:
    _add_derived_series(data)
    blurbs = _load_blurbs()
    chart_ids = ["chart-" + str(i) for i in range(len(page.charts))]
    panels = []
    for i, chart in enumerate(page.charts):
        if i in page.sections:
            panels.append(_render_section(page.sections[i], blurbs))
        if isinstance(chart, CoreInflationSpec):
            panels.append(_build_core_inflation_panel(chart, data, i, i == 0))
        elif isinstance(chart, CpiBreadthSpec):
            panels.append(_build_cpi_breadth_panel(chart, data, i, i == 0))
        elif isinstance(chart, WageSpec):
            panels.append(_build_wage_panel(chart, data, i, i == 0))
        elif isinstance(chart, CpiSpec):
            panels.append(_build_cpi_panel(chart, data, i, i == 0))
        elif isinstance(chart, MultiLineSpec):
            panels.append(_build_multiline_panel(chart, data, i, i == 0))
        elif isinstance(chart, StackedBarSpec):
            panels.append(_build_stackedbar_panel(chart, data, i, i == 0))
        elif isinstance(chart, MortgageShockSpec):
            panels.append(_build_mortgage_shock_panel(chart, i, i == 0))
        else:
            df = data[chart.series]
            panels.append(_chart_panel_html(chart, df, i, include_plotlyjs=(i == 0), data=data))

    default_ranges: dict = {}
    y_floors: dict = {}
    for i, chart in enumerate(page.charts):
        cid = "chart-" + str(i)
        if isinstance(chart, CpiBreadthSpec):
            default_ranges[cid] = 10
        elif isinstance(chart, (ChartSpec, MultiLineSpec, StackedBarSpec, WageSpec, CoreInflationSpec, CpiSpec)) and chart.default_years is not None:
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
            elif isinstance(chart, (MultiLineSpec, StackedBarSpec)):
                _line_iter = list(chart.lines)
                if isinstance(chart, MultiLineSpec):
                    _line_iter += list(chart.alt_lines)
                if isinstance(chart, StackedBarSpec) and chart.overlay is not None:
                    _line_iter.append(chart.overlay)
                for line in _line_iter:
                    if (DATA_DIR / f"{line.series}.csv").exists():
                        all_series.add(line.series)
                    elif line.series in _DERIVED_SERIES_SOURCES:
                        # Derived series: load source CSVs; _add_derived_series will compute it.
                        all_series.update(_DERIVED_SERIES_SOURCES[line.series])
                    else:
                        print(f"  Warning: {line.series}.csv missing — run fetch.py. Line will be skipped.")
            elif isinstance(chart, MortgageShockSpec):
                pass  # hardcoded data — no CSV needed
            else:
                # ChartSpec: series may be raw (CSV exists) or derived.
                if (DATA_DIR / f"{chart.series}.csv").exists():
                    all_series.add(chart.series)
                elif chart.series in _DERIVED_SERIES_SOURCES:
                    all_series.update(_DERIVED_SERIES_SOURCES[chart.series])
                else:
                    all_series.add(chart.series)  # let the load step raise the error
                # Also register any overlay series on a ChartSpec
                for ov in getattr(chart, "overlays", []):
                    all_series.add(ov.series)
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
