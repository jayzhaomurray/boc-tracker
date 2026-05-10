"""
plotly_theme_v2.py — BoC Tracker v2 design-system theme for Plotly figures.

Usage:
    from plotly_theme_v2 import apply_v2_theme
    fig = go.Figure(...)
    apply_v2_theme(fig, line_roles={"Canada CPI": "primary", "US CPI": "secondary"})

See apply_v2_theme() docstring for full API.
"""

from __future__ import annotations

import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Design-token color palette
# All values are OKLCH -> sRGB conversions from design-system/colors_and_type.css.
# ---------------------------------------------------------------------------

# Surfaces
_PAPER      = "#f5f7f9"   # oklch(97.5% 0.004 250) — page background
_VELLUM     = "#eceff2"   # oklch(95%   0.005 250)
_CARD       = "#ffffff"   # oklch(100%  0     0)

# Ink hierarchy
_INK        = "#101622"   # oklch(20%   0.025 265) — primary text
_INK_SUB    = "#424853"   # oklch(40%   0.020 265) — secondary, axis labels
_INK_QUIET  = "#767a84"   # oklch(58%   0.015 265) — tertiary, footnotes
_INK_FAINT  = "#a1a5ab"   # oklch(72%   0.010 265) — disabled

# Hairlines
_RULE       = "#d5d8db"   # oklch(88%   0.006 250) — standard gridlines
_RULE_STRONG = "#b0b5b9"  # oklch(77%   0.008 250)
_RULE_EMPHASIS = "#424853" # oklch(40%   0.020 265)

# Anchor accents — promoted from chart_style_guide.md
_COBALT     = "#1950a9"   # oklch(45%   0.155 260) — Canada / BoC / primary
_VERMILLION = "#b43628"   # oklch(52%   0.165 30)  — US / Fed / secondary / editorial

# Categorical palette (independent series: food, energy, goods, services, etc.)
_CAT_AMBER  = "#d88000"   # oklch(68%   0.155 65)
_CAT_TEAL   = "#008384"   # oklch(55%   0.100 195)
_CAT_PLUM   = "#793089"   # oklch(45%   0.155 320)
_CAT_PINE   = "#38853e"   # oklch(55%   0.130 145)
_CAT_WALNUT = "#5c4132"   # oklch(40%   0.045 50)  — 5th, use sparingly

# Semantic aliases (point at the same hues as their CSS counterparts)
_ABOVE_TARGET = _VERMILLION
_ON_TARGET    = _COBALT
_BELOW_TARGET = _CAT_TEAL
_EASING       = _CAT_PINE
_TIGHTENING   = _CAT_AMBER

# Tooltip background — pure card white with a barely-warm cast
_HOVER_BG = "#ffffff"

# Categorical sequence for auto-assignment (excludes cobalt and vermillion)
_CAT_SEQUENCE = [_CAT_AMBER, _CAT_TEAL, _CAT_PLUM, _CAT_PINE, _CAT_WALNUT]

# ---------------------------------------------------------------------------
# Type tokens (CSS font-family strings — v2 page loads these via Google Fonts)
# ---------------------------------------------------------------------------
_FONT_DISPLAY = "'Bricolage Grotesque', 'Instrument Sans', system-ui, sans-serif"
_FONT_SANS    = "'Instrument Sans', 'Segoe UI', system-ui, sans-serif"
_FONT_MONO    = "'Cascadia Mono', 'Cascadia Code', Consolas, ui-monospace, monospace"

# ---------------------------------------------------------------------------
# Role -> color map
# ---------------------------------------------------------------------------
_ROLE_COLORS: dict[str, str] = {
    # Primary / Canada / BoC
    "primary":   _COBALT,
    "canada":    _COBALT,
    "boc":       _COBALT,
    # Secondary / US / Fed
    "secondary": _VERMILLION,
    "us":        _VERMILLION,
    "fed":       _VERMILLION,
    # Categorical
    "category-1": _CAT_AMBER,
    "category-2": _CAT_TEAL,
    "category-3": _CAT_PLUM,
    "category-4": _CAT_PINE,
    "category-5": _CAT_WALNUT,
    # Semantic
    "above-target": _ABOVE_TARGET,
    "below-target": _BELOW_TARGET,
    "on-target":    _ON_TARGET,
    "easing":       _EASING,
    "tightening":   _TIGHTENING,
    # Muted / comparator
    "muted":      _INK_QUIET,
    "comparator": _INK_QUIET,
}

# Role -> line width
_ROLE_WIDTHS: dict[str, float] = {
    "primary":   2.0,
    "canada":    2.0,
    "boc":       2.0,
    "secondary": 1.5,
    "us":        1.5,
    "fed":       1.5,
    "muted":     1.0,
    "comparator": 1.0,
}
_DEFAULT_LINE_WIDTH = 1.4


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_v2_theme(
    fig: go.Figure,
    *,
    line_roles: dict[str, str] | None = None,
    is_sparkline: bool = False,
) -> go.Figure:
    """Style a Plotly figure to the BoC Tracker v2 design system.

    Args:
        fig: existing Plotly figure (any trace type — line, band, bar, etc.)
        line_roles: optional mapping of trace name -> semantic role:
            "primary" / "canada" / "boc"           -> cobalt
            "secondary" / "us" / "fed"              -> vermillion
            "category-1" .. "category-5"            -> categorical palette
            "above-target" / "below-target"
              / "on-target" / "easing" / "tightening" -> semantic colours
            "muted" / "comparator"                  -> ink-quiet grey
            Unmapped traces receive colours from the categorical palette
            in the order they appear, cycling if there are more than 5.
        is_sparkline: minimal-chrome variant for KPI-strip sparklines.
            Strips axes, grid, hovers, and legend entirely. Returns a
            compact chart suited to a ~120 px wide tile.

    Returns:
        The same figure object with in-place styling applied.
    """
    roles = line_roles or {}

    # -- Trace styling -------------------------------------------------------
    cat_index = 0  # rolling index into _CAT_SEQUENCE for unmapped traces

    for trace in fig.data:
        name = getattr(trace, "name", None) or ""
        role = roles.get(name, "").lower()

        color = _ROLE_COLORS.get(role)
        width = _ROLE_WIDTHS.get(role, _DEFAULT_LINE_WIDTH)

        if color is None:
            # Auto-assign from categorical palette in order
            color = _CAT_SEQUENCE[cat_index % len(_CAT_SEQUENCE)]
            cat_index += 1

        # Sparkline forced width override
        if is_sparkline:
            width = 1.5

        trace_type = type(trace).__name__

        if trace_type == "Scatter":
            # Update line properties
            existing_line = getattr(trace, "line", None) or {}
            line_props: dict = {}
            if hasattr(existing_line, "to_plotly_json"):
                line_props = {
                    k: v for k, v in existing_line.to_plotly_json().items()
                    if v is not None
                }
            line_props["color"] = color
            line_props.setdefault("width", width)
            line_props.setdefault("shape", "linear")
            trace.update(line=line_props)

            if is_sparkline:
                trace.update(
                    hoverinfo="skip",
                    mode="lines",
                )

        elif trace_type == "Bar":
            trace.update(marker_color=color)

        elif trace_type in ("Candlestick", "Ohlc"):
            pass  # leave broker-style traces to their own conventions

    # -- Layout ---------------------------------------------------------------
    if is_sparkline:
        _apply_sparkline_layout(fig)
    else:
        _apply_full_layout(fig)

    return fig


# ---------------------------------------------------------------------------
# Internal layout helpers
# ---------------------------------------------------------------------------

def _apply_full_layout(fig: go.Figure) -> None:
    """Apply full-chart layout: fonts, gridlines, axes, hover, margins."""
    fig.update_layout(
        # Transparent so the card background shows through
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        # Title font — Bricolage Grotesque (display)
        title_font={
            "family": _FONT_DISPLAY,
            "size": 14,
            "color": _INK,
        },

        # Suppress Plotly's built-in legend; v2 uses custom HTML legend chips
        showlegend=False,

        # Tight margins — equivalent to padX=36 padBot=26 from the JSX refs
        margin={"l": 40, "r": 20, "t": 20, "b": 30},

        # Hover label
        hoverlabel={
            "bgcolor": _HOVER_BG,
            "bordercolor": _RULE,
            "font": {
                "family": _FONT_MONO,
                "size": 11,
                "color": _INK,
            },
            "align": "left",
        },

        # Font default for everything else that hasn't been overridden
        font={
            "family": _FONT_SANS,
            "size": 11,
            "color": _INK_SUB,
        },
    )

    # X-axis — no gridlines, no axis line, Cascadia Mono ticks
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        tickfont={
            "family": _FONT_MONO,
            "size": 10,
            "color": _INK_QUIET,
        },
        title_font={
            "family": _FONT_SANS,
            "size": 11,
            "color": _INK_SUB,
        },
        ticks="outside",
        ticklen=3,
        tickcolor=_RULE,
    )

    # Y-axis — hairline horizontal gridlines, no axis line
    fig.update_yaxes(
        showgrid=True,
        gridcolor=_RULE,
        gridwidth=1,
        zeroline=True,
        zerolinecolor=_RULE_STRONG,
        zerolinewidth=1,
        showline=False,
        tickfont={
            "family": _FONT_MONO,
            "size": 10,
            "color": _INK_QUIET,
        },
        title_font={
            "family": _FONT_SANS,
            "size": 11,
            "color": _INK_SUB,
        },
        ticks="outside",
        ticklen=3,
        tickcolor=_RULE,
    )


def _apply_sparkline_layout(fig: go.Figure) -> None:
    """Apply minimal-chrome sparkline layout for KPI tiles (~120 px wide)."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin={"l": 0, "r": 0, "t": 2, "b": 2, "pad": 0},
        hovermode=False,
        # No title in sparkline context
        title_text="",
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        showticklabels=False,
        ticks="",
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        showline=False,
        showticklabels=False,
        ticks="",
    )


# ---------------------------------------------------------------------------
# Convenience: export the palette dict for other modules
# ---------------------------------------------------------------------------
PALETTE = {
    "cobalt":     _COBALT,
    "vermillion": _VERMILLION,
    "cat_amber":  _CAT_AMBER,
    "cat_teal":   _CAT_TEAL,
    "cat_plum":   _CAT_PLUM,
    "cat_pine":   _CAT_PINE,
    "cat_walnut": _CAT_WALNUT,
    "ink":        _INK,
    "ink_sub":    _INK_SUB,
    "ink_quiet":  _INK_QUIET,
    "ink_faint":  _INK_FAINT,
    "rule":       _RULE,
    "paper":      _PAPER,
    "card":       _CARD,
}


# ---------------------------------------------------------------------------
# __main__ — generate v2/_theme_demo.html for visual verification
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    import numpy as np
    import plotly.graph_objects as go

    rng = np.random.default_rng(42)
    x = list(range(48))  # 48 months of synthetic data

    # Synthetic series
    canada = [2.5 + 0.4 * i / 47 + 0.3 * rng.standard_normal() for i in x]
    us     = [3.0 + 0.2 * i / 47 + 0.3 * rng.standard_normal() for i in x]
    comp   = [2.0 - 0.1 * i / 47 + 0.2 * rng.standard_normal() for i in x]

    # -----------------------------------------------------------------------
    # 1. Full chart demo
    # -----------------------------------------------------------------------
    fig_full = go.Figure()
    fig_full.add_trace(go.Scatter(x=x, y=canada, mode="lines", name="Canada CPI"))
    fig_full.add_trace(go.Scatter(x=x, y=us,     mode="lines", name="US CPI"))
    fig_full.add_trace(go.Scatter(x=x, y=comp,   mode="lines", name="Comparator"))
    fig_full.update_layout(title_text="CPI Y/Y (synthetic)", height=280)

    apply_v2_theme(
        fig_full,
        line_roles={
            "Canada CPI":  "primary",
            "US CPI":      "secondary",
            "Comparator":  "muted",
        },
    )

    # -----------------------------------------------------------------------
    # 2. Sparkline demo
    # -----------------------------------------------------------------------
    spark_data = [2.5 + 0.3 * rng.standard_normal() for _ in range(24)]
    fig_spark = go.Figure()
    fig_spark.add_trace(go.Scatter(
        x=list(range(len(spark_data))),
        y=spark_data,
        mode="lines",
        name="BoC rate",
    ))
    fig_spark.update_layout(height=32, width=120)

    apply_v2_theme(
        fig_spark,
        line_roles={"BoC rate": "primary"},
        is_sparkline=True,
    )

    # -----------------------------------------------------------------------
    # 3. Categorical demo (no line_roles — auto-assign from palette)
    # -----------------------------------------------------------------------
    fig_cat = go.Figure()
    labels = ["Food", "Energy", "Goods", "Services", "Shelter"]
    for label in labels:
        trace_y = [rng.standard_normal() * 0.5 + 2.0 for _ in x]
        fig_cat.add_trace(go.Scatter(x=x, y=trace_y, mode="lines", name=label))
    fig_cat.update_layout(title_text="CPI Components (auto-palette, synthetic)", height=280)

    apply_v2_theme(fig_cat)  # no roles → categorical auto-assignment

    # -----------------------------------------------------------------------
    # Write demo HTML
    # -----------------------------------------------------------------------
    out_dir = os.path.join(os.path.dirname(__file__), "v2")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "_theme_demo.html")

    # Assemble all three figures into one HTML page
    full_html  = fig_full.to_html(full_html=False, include_plotlyjs=False)
    spark_html = fig_spark.to_html(full_html=False, include_plotlyjs=False)
    cat_html   = fig_cat.to_html(full_html=False, include_plotlyjs=False)

    google_fonts = (
        "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque"
        ":opsz,wght@12..96,400;12..96,500;12..96,600;12..96,700"
        "&family=Instrument+Sans:wght@400;500;600;700"
        "&family=Cascadia+Mono:wght@400;500;600"
        "&display=swap"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>BoC Tracker v2 — Theme Demo</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="stylesheet" href="{google_fonts}">
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: {_PAPER};
      color: {_INK};
      font-family: 'Instrument Sans', system-ui, sans-serif;
      font-size: 15px;
      line-height: 1.55;
      padding: 32px;
    }}
    h1 {{
      font-family: 'Bricolage Grotesque', sans-serif;
      font-size: 24px;
      font-weight: 600;
      color: {_INK};
      margin-bottom: 4px;
    }}
    .eyebrow {{
      font-family: 'Instrument Sans', system-ui, sans-serif;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: {_INK_QUIET};
      margin-bottom: 24px;
    }}
    .section {{
      margin-bottom: 48px;
    }}
    .section-label {{
      font-family: 'Instrument Sans', system-ui, sans-serif;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: {_INK_QUIET};
      margin-bottom: 12px;
    }}
    .card {{
      background: {_CARD};
      border: 1px solid {_RULE};
      border-radius: 4px;
      padding: 16px;
    }}
    .legend-row {{
      display: flex;
      gap: 20px;
      margin-top: 12px;
      font-family: 'Instrument Sans', system-ui, sans-serif;
      font-size: 12px;
      color: {_INK_SUB};
    }}
    .legend-chip {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .legend-swatch {{
      width: 24px;
      height: 2px;
      border-radius: 1px;
    }}
    .sparkline-tile {{
      display: inline-flex;
      flex-direction: column;
      background: {_CARD};
      border: 1px solid {_RULE};
      border-radius: 4px;
      padding: 12px 14px;
      gap: 4px;
      min-width: 160px;
    }}
    .kpi-label {{
      font-family: 'Instrument Sans', system-ui, sans-serif;
      font-size: 11px;
      color: {_INK_QUIET};
      text-transform: uppercase;
      letter-spacing: 0.1em;
      font-weight: 600;
    }}
    .kpi-value {{
      font-family: 'Cascadia Mono', monospace;
      font-size: 24px;
      font-weight: 500;
      color: {_INK};
      font-variant-numeric: tabular-nums;
    }}
    .palette-row {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 8px;
    }}
    .swatch {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
    }}
    .swatch-box {{
      width: 48px;
      height: 32px;
      border-radius: 3px;
      border: 1px solid {_RULE};
    }}
    .swatch-label {{
      font-family: 'Cascadia Mono', monospace;
      font-size: 9px;
      color: {_INK_QUIET};
    }}
    .foil-rule {{ height: 2px; background: linear-gradient(115deg,
      #c4562c 0%, #be3a7a 18%, #7a44c8 38%, #2a6ec0 58%, #18908a 78%, #8ab020 100%);
      margin-bottom: 32px; }}
  </style>
</head>
<body>
  <div class="eyebrow">BoC Tracker · Design System v2</div>
  <h1>Plotly Theme Demo</h1>
  <div class="foil-rule" style="margin-top:8px;"></div>

  <!-- 1. Full chart — primary + secondary + muted -->
  <div class="section">
    <div class="section-label">Full chart — primary (cobalt) / secondary (vermillion) / muted</div>
    <div class="card">
      {full_html}
      <div class="legend-row">
        <div class="legend-chip">
          <div class="legend-swatch" style="background:{_COBALT};height:2px;"></div>
          <span>Canada CPI</span>
        </div>
        <div class="legend-chip">
          <div class="legend-swatch" style="background:{_VERMILLION};height:1.5px;"></div>
          <span>US CPI</span>
        </div>
        <div class="legend-chip">
          <div class="legend-swatch" style="background:{_INK_QUIET};height:1px;"></div>
          <span>Comparator</span>
        </div>
      </div>
    </div>
  </div>

  <!-- 2. Sparkline — minimal chrome -->
  <div class="section">
    <div class="section-label">Sparkline variant — is_sparkline=True (KPI tile)</div>
    <div class="sparkline-tile">
      <div class="kpi-label">BoC Overnight</div>
      <div class="kpi-value">2.75%</div>
      {spark_html}
    </div>
  </div>

  <!-- 3. Categorical auto-palette -->
  <div class="section">
    <div class="section-label">Categorical auto-palette (no line_roles specified)</div>
    <div class="card">
      {cat_html}
      <div class="legend-row">
        <div class="legend-chip">
          <div class="legend-swatch" style="background:{_CAT_AMBER};height:1.4px;"></div>
          <span>Food</span>
        </div>
        <div class="legend-chip">
          <div class="legend-swatch" style="background:{_CAT_TEAL};height:1.4px;"></div>
          <span>Energy</span>
        </div>
        <div class="legend-chip">
          <div class="legend-swatch" style="background:{_CAT_PLUM};height:1.4px;"></div>
          <span>Goods</span>
        </div>
        <div class="legend-chip">
          <div class="legend-swatch" style="background:{_CAT_PINE};height:1.4px;"></div>
          <span>Services</span>
        </div>
        <div class="legend-chip">
          <div class="legend-swatch" style="background:{_CAT_WALNUT};height:1.4px;"></div>
          <span>Shelter</span>
        </div>
      </div>
    </div>
  </div>

  <!-- 4. Token reference palette -->
  <div class="section">
    <div class="section-label">Token palette reference</div>
    <div class="palette-row">
      <div class="swatch">
        <div class="swatch-box" style="background:{_COBALT};"></div>
        <div class="swatch-label">cobalt</div>
        <div class="swatch-label">{_COBALT}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_VERMILLION};"></div>
        <div class="swatch-label">vermillion</div>
        <div class="swatch-label">{_VERMILLION}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_CAT_AMBER};"></div>
        <div class="swatch-label">amber</div>
        <div class="swatch-label">{_CAT_AMBER}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_CAT_TEAL};"></div>
        <div class="swatch-label">teal</div>
        <div class="swatch-label">{_CAT_TEAL}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_CAT_PLUM};"></div>
        <div class="swatch-label">plum</div>
        <div class="swatch-label">{_CAT_PLUM}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_CAT_PINE};"></div>
        <div class="swatch-label">pine</div>
        <div class="swatch-label">{_CAT_PINE}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_CAT_WALNUT};"></div>
        <div class="swatch-label">walnut</div>
        <div class="swatch-label">{_CAT_WALNUT}</div>
      </div>
    </div>
    <div class="palette-row" style="margin-top:16px;">
      <div class="swatch">
        <div class="swatch-box" style="background:{_INK};"></div>
        <div class="swatch-label">ink</div>
        <div class="swatch-label">{_INK}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_INK_SUB};"></div>
        <div class="swatch-label">ink-sub</div>
        <div class="swatch-label">{_INK_SUB}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_INK_QUIET};"></div>
        <div class="swatch-label">ink-quiet</div>
        <div class="swatch-label">{_INK_QUIET}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_INK_FAINT};border:1px solid {_RULE};"></div>
        <div class="swatch-label">ink-faint</div>
        <div class="swatch-label">{_INK_FAINT}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_RULE};border:1px solid {_RULE_STRONG};"></div>
        <div class="swatch-label">rule</div>
        <div class="swatch-label">{_RULE}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_PAPER};border:1px solid {_RULE};"></div>
        <div class="swatch-label">paper</div>
        <div class="swatch-label">{_PAPER}</div>
      </div>
      <div class="swatch">
        <div class="swatch-box" style="background:{_CARD};border:1px solid {_RULE};"></div>
        <div class="swatch-label">card</div>
        <div class="swatch-label">{_CARD}</div>
      </div>
    </div>
  </div>

</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Demo written: {out_path}")
    print()
    print("Token hex values:")
    from plotly_theme_v2 import PALETTE
    for name, hex_val in PALETTE.items():
        print(f"  {name:<12}: {hex_val}")
