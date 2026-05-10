"""
build_v2.py -- v2 splash page builder.

Emits v2/index.html using real data from data/ CSVs.
Uses Jinja2 for HTML templating and Plotly for charts (matching existing infrastructure).

Run:
    python build_v2.py

Output:
    v2/index.html
    v2/colors_and_type.css  (copied from design-system/)

Theme hook: apply_v2_theme(fig) is called on every Plotly figure.
When the parallel theme module lands, replace the stub below with:
    from plotly_theme_v2 import apply_v2_theme
"""

from __future__ import annotations

import math
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
TEMPLATES_DIR = ROOT / "v2_templates"
OUTPUT_DIR = ROOT / "v2"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Theme hook (stub -- replace with import when plotly_theme_v2 module lands)
# ---------------------------------------------------------------------------
try:
    from plotly_theme_v2 import apply_v2_theme  # type: ignore
except ImportError:
    def apply_v2_theme(fig: go.Figure) -> go.Figure:
        """No-op stub. Replace with the real module once it lands."""
        return fig

# ---------------------------------------------------------------------------
# Reuse HP-filter from build.py
# ---------------------------------------------------------------------------
try:
    from statsmodels.tsa.filters.hp_filter import hpfilter as _sm_hpfilter
    def _hp_filter(series: pd.Series, lamb: int = 129600) -> pd.Series:
        cycle, trend = _sm_hpfilter(series.values, lamb=lamb)
        return pd.Series(trend, index=series.index)
except ImportError:
    def _hp_filter(series: pd.Series, lamb: int = 129600) -> pd.Series:
        n = len(series)
        y = series.values.astype(float)
        e = np.ones(n)
        d2 = np.diag(e, 0) - 2 * np.diag(e[:-1], -1) + np.diag(e[:-2], -2)
        d2 = d2[2:]
        A = np.eye(n) + lamb * d2.T @ d2
        trend = np.linalg.solve(A, y)
        return pd.Series(trend, index=series.index)

# ---------------------------------------------------------------------------
# Chart appearance constants (Plotly defaults for now; theme module will override)
# ---------------------------------------------------------------------------
_CHART_HEIGHT = 300
_CHART_MARGINS = dict(l=52, r=20, t=12, b=36)
_FONT_STACK = "'Instrument Sans', 'Segoe UI', system-ui, sans-serif"
_PAPER_BG = "#ffffff"           # --card (white)
_PLOT_BG  = "#f6f7f9"           # --paper (light ice-toned)
_GRID_COLOR = "#dde0e6"         # --rule (hairline)

# Plotly-safe color palette (hex/rgb only -- oklch not supported by Plotly validators)
_COBALT     = "#2a5abf"         # oklch(45% 0.155 260) approx
_VERMILLION = "#c0402a"         # oklch(52% 0.165 30) approx
_TEAL       = "#3a8a80"         # oklch(52% 0.090 175) approx
_INK_QUIET  = "#7a8096"         # oklch(58% 0.015 265) approx
_INK_SUB    = "#4a506a"         # oklch(40% 0.020 265) approx
_BAND_FILL  = "rgba(160,165,180,0.30)"
_GRAY_55    = "#8a8e9a"


def _compact_x_dates(fig: go.Figure) -> None:
    for trace in fig.data:
        x = getattr(trace, "x", None)
        if x is None or len(x) == 0:
            continue
        try:
            trace.x = pd.to_datetime(x).strftime("%Y-%m-%d").tolist()
        except (ValueError, TypeError):
            pass


def _nice_dtick(ymin: float, ymax: float, target: int = 5) -> float:
    span = ymax - ymin
    if span <= 0:
        return 1.0
    rough = span / target
    mag = 10 ** math.floor(math.log10(rough))
    norm = rough / mag
    if norm >= 5.0:   nice = 5.0
    elif norm >= 2.5: nice = 2.5
    elif norm >= 2.0: nice = 2.0
    else:             nice = 1.0
    return nice * mag


def _dtick_format(dtick: float) -> str:
    s = f"{dtick:.10f}".rstrip("0")
    if "." not in s or s.endswith("."):
        return ".0f"
    decimals = len(s.split(".")[1])
    return f".{min(decimals, 2)}f"


def _base_layout() -> dict:
    return dict(
        height=_CHART_HEIGHT,
        showlegend=False,
        paper_bgcolor=_PAPER_BG,
        plot_bgcolor=_PLOT_BG,
        margin=_CHART_MARGINS,
        font=dict(family=_FONT_STACK, size=11),
    )


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
SERIES_NEEDED = [
    "overnight_rate",
    "fed_funds",
    "cpi_trim",
    "cpi_median",
    "cpi_common",
    "cpix",
    "cpixfet",
    "cpi_all_items",
    "gdp_monthly",
    "unemployment_rate",
    "job_vacancy_rate",
    "lfs_micro",
    "lfs_wages_all",
    "lfs_wages_permanent",
    "seph_earnings",
    "cpi_services",
    "usdcad",
]


def load_data() -> dict[str, pd.DataFrame]:
    data: dict[str, pd.DataFrame] = {}
    for name in SERIES_NEEDED:
        path = DATA_DIR / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing {path} -- run fetch.py first.")
        df = pd.read_csv(path, parse_dates=["date"])
        data[name] = df.sort_values("date").reset_index(drop=True)
        latest = df["date"].max().strftime("%Y-%m-%d")
        print(f"  -> {name}: {len(df)} rows, latest {latest}")

    # Derived: job_vacancy_rate_12m (12-month rolling mean)
    jvr = data["job_vacancy_rate"].copy()
    jvr["value"] = jvr["value"].rolling(12).mean()
    data["job_vacancy_rate_12m"] = jvr.dropna().reset_index(drop=True)

    # Derived: YoY series needed for BandSpec comparators / wage band
    for src, dst in [
        ("cpi_all_items",      "cpi_all_items_yoy"),
        ("lfs_wages_all",      "lfs_wages_all_yoy"),
        ("lfs_wages_permanent","lfs_wages_permanent_yoy"),
        ("seph_earnings",      "seph_earnings_yoy"),
        ("cpi_services",       "cpi_services_yoy"),
    ]:
        df = data[src].copy()
        df["value"] = df["value"].pct_change(12) * 100
        data[dst] = df.dropna().reset_index(drop=True)

    # Derived: gdp_potential_hp
    gdp = data["gdp_monthly"].set_index("date")["value"]
    hp_trend = _hp_filter(gdp)
    data["gdp_potential_hp"] = pd.DataFrame({
        "date": hp_trend.index,
        "value": hp_trend.values,
    }).reset_index(drop=True)

    return data


# ---------------------------------------------------------------------------
# KPI tile computation
# ---------------------------------------------------------------------------
def _latest_val(df: pd.DataFrame) -> tuple[pd.Timestamp, float]:
    last = df.dropna(subset=["value"]).iloc[-1]
    return last["date"], float(last["value"])


def _prev_val(df: pd.DataFrame, n: int = 1) -> float | None:
    clean = df.dropna(subset=["value"])
    if len(clean) <= n:
        return None
    return float(clean.iloc[-(n + 1)]["value"])


def _fmt_date_monthly(ts: pd.Timestamp) -> str:
    return ts.strftime("%b %Y")


def _fmt_date_daily(ts: pd.Timestamp) -> str:
    return ts.strftime("%b %d")


def build_kpi_tiles(data: dict) -> list[dict]:
    tiles = []

    # ------------------------------------------------------------------
    # 1. Monetary policy — overnight rate (monthly, step series)
    # ------------------------------------------------------------------
    df_ov = data["overnight_rate"]
    ts, val = _latest_val(df_ov)
    prev = _prev_val(df_ov)
    delta_pp = val - prev if prev is not None else None
    bp = int(round(delta_pp * 100)) if delta_pp is not None else 0
    # Count consecutive meetings at the same rate
    vals_rev = df_ov["value"].iloc[::-1].values
    hold_count = 1
    for v in vals_rev[1:]:
        if abs(v - val) < 1e-6:
            hold_count += 1
        else:
            break

    if abs(bp) < 1:
        delta_str = f"0 bp · {hold_count} mtgs flat"
        delta_dir = "down"
    elif bp > 0:
        delta_str = f"+{bp} bp m/m"
        delta_dir = "up"
    else:
        delta_str = f"{bp} bp m/m"
        delta_dir = "down"

    # Position relative to neutral band 2.25-3.25
    if val < 2.25:
        pill, pill_tone, sub_text = "Below neutral", "below", "Below 2.25–3.25% band."
    elif val > 3.25:
        pill, pill_tone, sub_text = "Above neutral", "above", "Above 2.25–3.25% band."
    else:
        # Within band -- report which edge
        mid = (val - 2.25) / 1.0  # 0=lower, 1=upper
        if mid > 0.5:
            edge = "Upper edge"
        else:
            edge = "Lower edge"
        pill, pill_tone = "In band", "on"
        sub_text = f"{edge} of 2.25–3.25%."

    tiles.append({
        "label": "Monetary policy",
        "stamp": _fmt_date_monthly(ts),
        "value": f"{val:.2f}",
        "unit": "%",
        "delta": delta_str,
        "delta_dir": delta_dir,
        "sub": {"pill": pill, "tone": pill_tone, "text": sub_text},
    })

    # ------------------------------------------------------------------
    # 2. Core inflation -- use CPI-trim as headline proxy; show band avg
    # ------------------------------------------------------------------
    # Headline CPI Y/Y
    df_cpi = data["cpi_all_items"]
    yoy_s = df_cpi.set_index("date")["value"].pct_change(12) * 100
    yoy_df = yoy_s.dropna()
    ts_cpi = yoy_df.index[-1]
    cpi_yoy = float(yoy_df.iloc[-1])
    cpi_yoy_prev = float(yoy_df.iloc[-2]) if len(yoy_df) >= 2 else cpi_yoy
    cpi_delta = cpi_yoy - cpi_yoy_prev

    # Core band average (trim + median, most recent common date)
    trim_s = data["cpi_trim"].set_index("date")["value"]
    med_s  = data["cpi_median"].set_index("date")["value"]
    core_avg = float(pd.concat([trim_s, med_s], axis=1).mean(axis=1).dropna().iloc[-1])

    if cpi_yoy > 2.0:
        cpi_pill, cpi_tone = "Above 2%", "above"
    elif cpi_yoy < 1.0:
        cpi_pill, cpi_tone = "Below 1%", "below"
    else:
        cpi_pill, cpi_tone = "On target", "on"

    tiles.append({
        "label": "Headline CPI",
        "stamp": ts_cpi.strftime("%b %Y"),
        "value": f"{cpi_yoy:.1f}",
        "unit": "%",
        "delta": ("↑" if cpi_delta >= 0 else "↓") + f" {abs(cpi_delta):.1f} pp m/m",
        "delta_dir": "up" if cpi_delta >= 0 else "down",
        "sub": {
            "pill": cpi_pill,
            "tone": cpi_tone,
            "text": f"Trim {data['cpi_trim']['value'].iloc[-1]:.1f} · Median {data['cpi_median']['value'].iloc[-1]:.1f}.",
        },
    })

    # ------------------------------------------------------------------
    # 3. Real GDP (monthly, level; show Y/Y)
    # ------------------------------------------------------------------
    df_gdp = data["gdp_monthly"]
    yoy_gdp = df_gdp.set_index("date")["value"].pct_change(12) * 100
    yoy_gdp_df = yoy_gdp.dropna()
    ts_gdp = yoy_gdp_df.index[-1]
    gdp_yoy = float(yoy_gdp_df.iloc[-1])
    gdp_yoy_prev = float(yoy_gdp_df.iloc[-2]) if len(yoy_gdp_df) >= 2 else gdp_yoy
    gdp_delta = gdp_yoy - gdp_yoy_prev

    # Output gap proxy: (GDP - HP trend) / HP trend * 100
    gdp_lvl = df_gdp.set_index("date")["value"]
    hp = data["gdp_potential_hp"].set_index("date")["value"]
    common_idx = gdp_lvl.index.intersection(hp.index)
    if len(common_idx) > 0:
        gap = float(((gdp_lvl.loc[common_idx] - hp.loc[common_idx]) / hp.loc[common_idx] * 100).iloc[-1])
        gap_str = f"Output gap {gap:+.1f}%."
    else:
        gap_str = ""

    if gdp_yoy >= 1.5:
        gdp_pill, gdp_tone = "Near potential", "on"
    elif gdp_yoy < 0:
        gdp_pill, gdp_tone = "Contraction", "above"
    else:
        gdp_pill, gdp_tone = "Below potential", "below"

    tiles.append({
        "label": "Real GDP (Y/Y)",
        "stamp": ts_gdp.strftime("%b %Y"),
        "value": f"{gdp_yoy:.1f}",
        "unit": "%",
        "delta": ("↑" if gdp_delta >= 0 else "↓") + f" {abs(gdp_delta):.1f} pp m/m",
        "delta_dir": "up" if gdp_delta >= 0 else "down",
        "sub": {"pill": gdp_pill, "tone": gdp_tone, "text": gap_str},
    })

    # ------------------------------------------------------------------
    # 4. Unemployment & Vacancies
    # ------------------------------------------------------------------
    df_ur = data["unemployment_rate"]
    ts_ur, ur_val = _latest_val(df_ur)
    ur_prev = _prev_val(df_ur)
    ur_delta = (ur_val - ur_prev) if ur_prev is not None else 0.0

    # Percentile within 24-month range
    last24 = df_ur["value"].iloc[-24:] if len(df_ur) >= 24 else df_ur["value"]
    pct_rank = int(round((ur_val - last24.min()) / max(last24.max() - last24.min(), 0.01) * 100))

    # Vacancy rate (12m avg, latest)
    jvr12 = data["job_vacancy_rate_12m"]
    _, jvr_val = _latest_val(jvr12)

    if ur_val >= 6.5:
        ur_pill, ur_tone = "Slack", "below"
    elif ur_val <= 5.5:
        ur_pill, ur_tone = "Tight", "on"
    else:
        ur_pill, ur_tone = "Balanced", "on"

    tiles.append({
        "label": "Unemployment",
        "stamp": _fmt_date_monthly(ts_ur),
        "value": f"{ur_val:.1f}",
        "unit": "%",
        "delta": ("↑" if ur_delta >= 0 else "↓") + f" {abs(ur_delta):.1f} pp m/m",
        "delta_dir": "down" if ur_delta >= 0 else "up",   # higher unemployment = bad
        "sub": {
            "pill": ur_pill,
            "tone": ur_tone,
            "text": f"Vacancies {jvr_val:.1f}% (12m avg) · {pct_rank}th pct of 24m range.",
        },
    })

    # ------------------------------------------------------------------
    # 5. USDCAD (daily)
    # ------------------------------------------------------------------
    df_fx = data["usdcad"]
    ts_fx, fx_val = _latest_val(df_fx)
    # Month-ago delta: ~21 trading days
    look_back = min(21, len(df_fx) - 1)
    fx_prev_mo = float(df_fx["value"].iloc[-(look_back + 1)])
    fx_delta = fx_val - fx_prev_mo

    if fx_val < 1.35:
        fx_pill, fx_tone = "Strong CAD", "on"
    elif fx_val > 1.42:
        fx_pill, fx_tone = "Weak CAD", "above"
    else:
        fx_pill, fx_tone = "Stable", "on"

    tiles.append({
        "label": "USDCAD",
        "stamp": _fmt_date_daily(ts_fx),
        "value": f"{fx_val:.4f}",
        "unit": None,
        "delta": ("↑" if fx_delta >= 0 else "↓") + f" {abs(fx_delta):.3f} m/m",
        "delta_dir": "down" if fx_delta >= 0 else "up",  # higher USDCAD = weaker CAD
        "sub": {
            "pill": fx_pill,
            "tone": fx_tone,
            "text": "Stress corridor above 1.45.",
        },
    })

    return tiles


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------

def _fig_to_html(fig: go.Figure, div_id: str) -> str:
    fig = apply_v2_theme(fig)
    _compact_x_dates(fig)
    return fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if div_id == "v2c-0" else False,
        div_id=div_id,
        config={"displayModeBar": False},
    )


def build_policy_chart(data: dict, div_id: str) -> dict:
    """Policy Rates: BoC overnight (step) + Fed funds (step, dashed) + neutral band."""
    df_boc = data["overnight_rate"].sort_values("date")
    df_fed = data["fed_funds"].sort_values("date")

    # 10-year window
    cutoff = pd.Timestamp.now().normalize() - pd.DateOffset(years=10)
    df_boc = df_boc[df_boc["date"] >= cutoff]
    df_fed = df_fed[df_fed["date"] >= cutoff]

    fig = go.Figure()

    # Neutral band 2.25-3.25 as horizontal rectangle
    fig.add_hrect(
        y0=2.25, y1=3.25,
        fillcolor="rgba(155,160,175,0.28)",
        line_width=0,
        annotation_text="Neutral 2.25–3.25%",
        annotation_position="right",
        annotation_font_size=10,
        annotation_font_color="#7a8096",
    )

    # Fed (editorial overlay, dashed vermillion)
    fig.add_trace(go.Scatter(
        x=df_fed["date"], y=df_fed["value"],
        name="Fed funds (upper)",
        line=dict(color=_VERMILLION, width=1.5, dash="dot", shape="hv"),
        hovertemplate="%{x|%b %d, %Y}<br>%{y:.2f}%<extra>Fed funds</extra>",
        showlegend=False,
    ))

    # BoC (primary cobalt, step)
    fig.add_trace(go.Scatter(
        x=df_boc["date"], y=df_boc["value"],
        name="BoC overnight",
        line=dict(color=_COBALT, width=2.5, shape="hv"),
        hovertemplate="%{x|%b %d, %Y}<br>%{y:.2f}%<extra>BoC overnight</extra>",
        showlegend=False,
    ))

    fig.update_layout(
        **_base_layout(),
        yaxis=dict(range=[0, 6.2]),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(
        showgrid=True, gridcolor=_GRID_COLOR, zeroline=False,
        ticksuffix="%", nticks=7,
    )

    return {
        "eyebrow": "Monetary policy · 01",
        "stamp": "V39079 (BoC) · FEDFUNDS (FRED)",
        "title": "Policy rates vs neutral band — BoC and the Fed, 10Y",
        "toolbar": [
            [{"label": "Level", "active": True}, {"label": "M/M", "active": False}, {"label": "Δ12m", "active": False}],
            [{"label": "2Y", "active": False}, {"label": "5Y", "active": False}, {"label": "10Y", "active": True}, {"label": "Max", "active": False}],
        ],
        "plotly_html": _fig_to_html(fig, div_id),
        "legend_items": [
            {"label": "BoC overnight", "color": "oklch(45% 0.155 260)", "kind": "line", "dash": False},
            {"label": "Fed funds (upper, editorial)", "color": "oklch(52% 0.165 30)", "kind": "line", "dash": True},
            {"label": "Neutral band (2.25–3.25%)", "color": "", "kind": "band", "dash": False},
        ],
        "footnote": (
            "BoC rate is a step series (discrete decisions); Fed is shown on the upper bound of the "
            "target range. Neutral band per Bank of Canada annual r* update."
        ),
    }


def build_core_inflation_chart(data: dict, div_id: str) -> dict:
    """Core Inflation band: CPI-trim, median, common, CPIX, CPIXFET + headline comparator."""
    band_series = {
        "CPI-trim":   (data["cpi_trim"],    "#4a7080"),
        "CPI-median": (data["cpi_median"],  "#507080"),
        "CPI-common": (data["cpi_common"],  _TEAL),
        "CPIX":       (data["cpix"],        "#6b5040"),
        "CPIXFET":    (data["cpixfet"],     "#7040a0"),
    }

    cutoff = pd.Timestamp.now().normalize() - pd.DateOffset(years=10)

    # Compute band envelope
    all_vals = []
    for label, (df, _) in band_series.items():
        s = df.set_index("date")["value"]
        s = s[s.index >= cutoff]
        all_vals.append(s.rename(label))

    band_df = pd.concat(all_vals, axis=1, sort=True).dropna(how="all")
    env_max = band_df.max(axis=1)
    env_min = band_df.min(axis=1)

    fig = go.Figure()

    # Band fill (tonexty)
    fig.add_trace(go.Scatter(
        x=env_min.index, y=env_min.values,
        line=dict(width=0), fill=None,
        showlegend=False, hoverinfo="skip", visible=True,
    ))
    fig.add_trace(go.Scatter(
        x=env_max.index, y=env_max.values,
        fill="tonexty", fillcolor="rgba(180,180,180,0.30)",
        line=dict(width=0),
        showlegend=False, hoverinfo="skip", visible=True,
    ))

    # Individual band members (hidden; band fill carries the read)
    for label, (df, color) in band_series.items():
        s = df.set_index("date")["value"]
        s = s[s.index >= cutoff]
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values,
            name=label,
            line=dict(color=color, width=1.2),
            hovertemplate=f"%{{x|%b %Y}}<br>%{{y:.1f}}%<extra>{label}</extra>",
            showlegend=False,
            visible="legendonly",
        ))

    # Headline CPI Y/Y comparator (primary cobalt, visible)
    headline_yoy = data["cpi_all_items_yoy"].set_index("date")["value"]
    headline_yoy = headline_yoy[headline_yoy.index >= cutoff]
    fig.add_trace(go.Scatter(
        x=headline_yoy.index, y=headline_yoy.values,
        name="Total CPI",
        line=dict(color=_COBALT, width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>Total CPI</extra>",
        showlegend=False, visible=True,
    ))

    # 2% reference line
    fig.add_hline(y=2.0, line_color=_INK_SUB, line_width=1,
                  line_dash="dot", opacity=0.6)

    fig.update_layout(**_base_layout())
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(
        showgrid=True, gridcolor=_GRID_COLOR, zeroline=False,
        ticksuffix="%", nticks=7,
    )

    return {
        "eyebrow": "Inflation · 02",
        "stamp": "Statistics Canada · Bank of Canada",
        "title": "Core inflation — BoC measures band + headline",
        "toolbar": None,
        "plotly_html": _fig_to_html(fig, div_id),
        "legend_items": [
            {"label": "Total CPI (Y/Y)", "color": "oklch(45% 0.155 260)", "kind": "line", "dash": False},
            {"label": "Core band (trim/median/common/CPIX/CPIXFET)", "color": "", "kind": "band", "dash": False},
            {"label": "2% target", "color": "oklch(40% 0.020 265)", "kind": "line", "dash": True},
        ],
        "footnote": (
            "Source: Bank of Canada; Statistics Canada. Year-over-year %. "
            "Band spans BoC core measures: CPI-trim, -median, -common, CPIX, CPIXFET."
        ),
    }


def build_gdp_chart(data: dict, div_id: str) -> dict:
    """Real GDP monthly level vs HP-filter potential."""
    cutoff = pd.Timestamp.now().normalize() - pd.DateOffset(years=10)

    df_gdp = data["gdp_monthly"].sort_values("date")
    df_gdp = df_gdp[df_gdp["date"] >= cutoff]

    df_hp = data["gdp_potential_hp"].sort_values("date")
    df_hp = df_hp[df_hp["date"] >= cutoff]

    fig = go.Figure()

    # Potential (dashed)
    fig.add_trace(go.Scatter(
        x=df_hp["date"], y=df_hp["value"],
        name="Potential GDP (HP)",
        line=dict(color="#6b7080", width=1.5, dash="dot"),
        hovertemplate="%{x|%b %Y}<br>%{y:.3f} C$T<extra>Potential (HP)</extra>",
        showlegend=False,
    ))

    # Real GDP
    fig.add_trace(go.Scatter(
        x=df_gdp["date"], y=df_gdp["value"],
        name="Real GDP",
        line=dict(color=_COBALT, width=2.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.3f} C$T<extra>Real GDP</extra>",
        showlegend=False,
    ))

    fig.update_layout(**_base_layout())
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(
        showgrid=True, gridcolor=_GRID_COLOR, zeroline=False,
        tickformat=".2f", nticks=7,
    )

    return {
        "eyebrow": "GDP & Activity · 03",
        "stamp": "Statistics Canada",
        "title": "Real GDP vs potential — monthly level, C$ trillions",
        "toolbar": None,
        "plotly_html": _fig_to_html(fig, div_id),
        "legend_items": [
            {"label": "Real GDP", "color": "oklch(45% 0.155 260)", "kind": "line", "dash": False},
            {"label": "Potential GDP (HP filter)", "color": "oklch(55% 0.020 265)", "kind": "line", "dash": True},
        ],
        "footnote": (
            "Source: Statistics Canada. Monthly real GDP by industry, chained 2017 dollars, SAAR. "
            "Potential output is an HP-filter trend (lambda=129600)."
        ),
    }


def build_labour_chart(data: dict, div_id: str) -> dict:
    """Unemployment rate + vacancy rate (12m avg)."""
    cutoff = pd.Timestamp.now().normalize() - pd.DateOffset(years=10)

    df_ur  = data["unemployment_rate"].sort_values("date")
    df_ur  = df_ur[df_ur["date"] >= cutoff]
    df_jvr = data["job_vacancy_rate_12m"].sort_values("date")
    df_jvr = df_jvr[df_jvr["date"] >= cutoff]

    fig = go.Figure()

    # Vacancy rate (secondary feel, teal)
    fig.add_trace(go.Scatter(
        x=df_jvr["date"], y=df_jvr["value"],
        name="Vacancies (12M Avg)",
        line=dict(color=_TEAL, width=1.8),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>Vacancies (12m avg)</extra>",
        showlegend=False,
    ))

    # Unemployment (primary cobalt)
    fig.add_trace(go.Scatter(
        x=df_ur["date"], y=df_ur["value"],
        name="Unemployment",
        line=dict(color=_COBALT, width=2.5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>Unemployment</extra>",
        showlegend=False,
    ))

    fig.update_layout(**_base_layout())
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(
        showgrid=True, gridcolor=_GRID_COLOR, zeroline=False,
        ticksuffix="%", nticks=7,
    )

    return {
        "eyebrow": "Labour · 04",
        "stamp": "Statistics Canada · LFS",
        "title": "Unemployment & job vacancies — rate, 10Y",
        "toolbar": None,
        "plotly_html": _fig_to_html(fig, div_id),
        "legend_items": [
            {"label": "Unemployment rate", "color": "oklch(45% 0.155 260)", "kind": "line", "dash": False},
            {"label": "Vacancy rate (12m avg)", "color": _TEAL, "kind": "line", "dash": False},
        ],
        "footnote": (
            "Source: Statistics Canada. Unemployment: monthly SA, 15+. "
            "Vacancies: monthly NSA; series begins 2015. Shown as 12-month moving average."
        ),
    }


def build_wage_chart(data: dict, div_id: str) -> dict:
    """Wage growth band: LFS-Micro (featured) + LFS All + LFS Permanent + SEPH + Services CPI comparator."""
    cutoff = pd.Timestamp.now().normalize() - pd.DateOffset(years=10)

    band_series_cfg = [
        ("lfs_micro",             "LFS-Micro (BoC)",    _COBALT, True),
        ("lfs_wages_all_yoy",     "LFS All Employees",  "#4040a0", False),
        ("lfs_wages_permanent_yoy","LFS Permanent",     "#5a6070", False),
        ("seph_earnings_yoy",     "SEPH Weekly Earnings","#686e7c", False),
    ]

    all_band = []
    for key, label, color, featured in band_series_cfg:
        s = data[key].set_index("date")["value"]
        s = s[s.index >= cutoff]
        all_band.append(s.rename(label))

    band_df = pd.concat(all_band, axis=1, sort=True).dropna(how="all")
    env_max = band_df.max(axis=1)
    env_min = band_df.min(axis=1)

    fig = go.Figure()

    # Band fill
    fig.add_trace(go.Scatter(
        x=env_min.index, y=env_min.values,
        line=dict(width=0), fill=None,
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=env_max.index, y=env_max.values,
        fill="tonexty", fillcolor="rgba(180,180,180,0.30)",
        line=dict(width=0),
        showlegend=False, hoverinfo="skip",
    ))

    # LFS-Micro featured line
    lfs_s = data["lfs_micro"].set_index("date")["value"]
    lfs_s = lfs_s[lfs_s.index >= cutoff]
    fig.add_trace(go.Scatter(
        x=lfs_s.index, y=lfs_s.values,
        name="LFS-Micro (BoC)",
        line=dict(color=_COBALT, width=2),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>LFS-Micro</extra>",
        showlegend=False, visible=True,
    ))

    # Services CPI comparator (dashed vermillion)
    svc_s = data["cpi_services_yoy"].set_index("date")["value"]
    svc_s = svc_s[svc_s.index >= cutoff]
    fig.add_trace(go.Scatter(
        x=svc_s.index, y=svc_s.values,
        name="Services CPI",
        line=dict(color=_VERMILLION, width=1.5, dash="dot"),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra>Services CPI</extra>",
        showlegend=False, visible=True,
    ))

    # Zero reference
    fig.add_hline(y=0, line_color="#aaa", line_width=1)

    fig.update_layout(**_base_layout())
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(
        showgrid=True, gridcolor=_GRID_COLOR, zeroline=False,
        ticksuffix="%", nticks=7,
    )

    return {
        "eyebrow": "Labour · 05",
        "stamp": "Statistics Canada",
        "title": "Wage growth — four measures band, Y/Y",
        "toolbar": None,
        "plotly_html": _fig_to_html(fig, div_id),
        "legend_items": [
            {"label": "LFS-Micro (BoC, featured)", "color": "oklch(45% 0.155 260)", "kind": "line", "dash": False},
            {"label": "Wage measures band (LFS All, Permanent, SEPH)", "color": "", "kind": "band", "dash": False},
            {"label": "Services CPI (Y/Y)", "color": "oklch(52% 0.165 30)", "kind": "line", "dash": True},
        ],
        "footnote": (
            "Source: Statistics Canada. Year-over-year %. "
            "LFS: average hourly wages, monthly SA. "
            "SEPH: average weekly earnings, all industries. "
            "LFS-Micro: BoC composition-adjusted measure."
        ),
    }


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------
def _get_refreshed_stamp(data: dict) -> str:
    """Use overnight_rate's latest date as the refresh marker."""
    ts = data["overnight_rate"]["date"].max()
    return ts.strftime("%b %Y")


def _build_headline_lede(data: dict, kpi_tiles: list[dict]) -> tuple[str, str]:
    """Derive headline and lede from live data."""
    ov_tile   = kpi_tiles[0]
    cpi_tile  = kpi_tiles[1]
    ur_tile   = kpi_tiles[3]

    policy_val = float(ov_tile["value"])
    cpi_val    = float(cpi_tile["value"])
    ur_val     = float(ur_tile["value"])

    # Headline -- rate stance
    if "In band" in ov_tile["sub"]["pill"]:
        if "Upper" in ov_tile["sub"]["text"]:
            stance = f"The Bank is on hold at the upper edge of neutral."
        elif "Lower" in ov_tile["sub"]["text"]:
            stance = f"The Bank is on hold at the lower edge of neutral."
        else:
            stance = f"The Bank is on hold within the neutral band."
    elif "Below" in ov_tile["sub"]["pill"]:
        stance = f"The Bank is on hold below neutral at {policy_val:.2f}%."
    else:
        stance = f"The Bank is on hold above neutral at {policy_val:.2f}%."

    headline = stance

    # Lede -- one sentence covering policy, inflation, labour
    cpi_read  = "above target" if cpi_val > 2.0 else ("below target" if cpi_val < 1.5 else "near target")
    ur_read   = "slack" if ur_val >= 6.5 else ("tight" if ur_val <= 5.5 else "balanced")

    lede = (
        f"Headline CPI at {cpi_val:.1f}% Y/Y is {cpi_read}; "
        f"the labour market is {ur_read} at {ur_val:.1f}% unemployment. "
        f"Policy rate at {policy_val:.2f}%."
    )

    return headline, lede


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Loading data...")
    data = load_data()

    print("Computing KPI tiles...")
    kpi_tiles = build_kpi_tiles(data)

    refreshed = _get_refreshed_stamp(data)
    headline, lede = _build_headline_lede(data, kpi_tiles)

    print("Building charts...")
    charts = [
        build_policy_chart(data, "v2c-0"),
        build_core_inflation_chart(data, "v2c-1"),
        build_gdp_chart(data, "v2c-2"),
        build_labour_chart(data, "v2c-3"),
        build_wage_chart(data, "v2c-4"),
    ]

    deep_dive_pages = [
        {"n": "03", "title": "Inflation",
         "lede": "Headline, core measures, breadth, sub-aggregates and inflation expectations.",
         "href": "#"},
        {"n": "04", "title": "GDP & activity",
         "lede": "Monthly real GDP, Q/Q AR, demand-side contribution decomposition.",
         "href": "#"},
        {"n": "05", "title": "Labour",
         "lede": "Unemployment trajectory, four wage measures, pass-through to services CPI.",
         "href": "#"},
        {"n": "06", "title": "Housing",
         "lede": "Starts, NHPI, permits as a leading indicator; CMHC supply gap.",
         "href": "#"},
        {"n": "07", "title": "Financial conditions",
         "lede": "WTI / Brent / WCS oil, USDCAD with stress corridor, BoC FX pass-through.",
         "href": "#"},
        {"n": "08", "title": "Trade",
         "lede": "Export composition; petrocurrency relationship; pass-through magnitudes.",
         "href": "#"},
    ]

    print("Rendering template...")
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)
    template = env.get_template("splash.html")
    html = template.render(
        refreshed_stamp=refreshed,
        headline=headline,
        lede=lede,
        kpi_tiles=kpi_tiles,
        charts=charts,
        deep_dive_pages=deep_dive_pages,
    )

    out_path = OUTPUT_DIR / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  -> {out_path}")

    # Copy the design-system CSS so v2/index.html can load it via ./colors_and_type.css
    css_src  = ROOT / "design-system" / "colors_and_type.css"
    css_dst  = OUTPUT_DIR / "colors_and_type.css"
    shutil.copy2(css_src, css_dst)
    print(f"  -> {css_dst}")

    print("Done.")


if __name__ == "__main__":
    main()
